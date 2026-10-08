Insert is the operation the whole tree is designed around, and it comes in four increasingly hard pieces: put a pair into a leaf (this stage), split a full leaf (next), split a full internal page, and do all of it concurrently. This stage covers the easy half of the first piece. A key goes into the right leaf in the right place; the **first** key of an empty tree creates the root. Pages never overflow yet: the tests stay below `max_size`.

It also introduces the write path's shape: take the header's **write** latch, then the write latches of every page on the way down, keeping them all in a stack (`Context::write_set`) until the operation is over. That is simple and correct and takes the whole tree exclusively; stage 9 makes it fast.

## Part 1 · Insert a pair into a leaf page

**Where this fits.** A leaf is a sorted array. Every insert in the tree ends here.

### The task

In `src/storage/page/b_plus_tree_leaf_page.rs` implement `insert(key, value, cmp) -> bool`: find the slot with `lower_bound`; if the key at that slot is **equal**, return `false` and change nothing; otherwise shift the later pairs right (`PageArray::insert_at`), store the pair, and count one more. (It does not check `max_size`: the tree splits a leaf the moment it reaches it, so there is always room for one more.)

### Tests

- Inserting `50, 20, 80, 10, 30, 90, 60` leaves the leaf sorted and each value next to its key.
- A duplicate key returns `false`; the size and the original value are unchanged.

### Syntax and methods

```rust
let at = self.lower_bound(key, cmp);
if at < size && cmp.compare(&self.key_at(at), key) == Ordering::Equal { return false; }
self.entries_mut().insert_at(at as usize, size as usize, &(key.clone(), value.clone()));   // 2a-03: shifts [at, size) right by one entry
self.set_size(size + 1);
```

### Notes

The comparison for "same key" is the **comparator's**, not `==` on the bytes: two keys may be equal for the index and differ in padding. Always ask `cmp.compare(a, b).is_eq()`.

### In BusTub

`Insert`: "if current tree is empty, start new tree, update root page id and insert entry; otherwise, insert into leaf page ... since we only support unique key, if user try to insert duplicate keys return false; otherwise, return true." BusTub's leaf page also carries a tombstone buffer (module 2d); this leaf does not yet.

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `memmove(array_ + i + 1, array_ + i, (size - i) * sizeof(MappingType))` | `copy_within` (inside `PageArray::insert_at`) |
| `std::lower_bound(...)` on the flexible array member | `lower_bound` from stage 2 |
| `if (comparator_(key, array_[i].first) == 0) return false;` | `cmp.compare(&k, key) == Ordering::Equal` |

### Learn more
- [`slice::copy_within`](https://doc.rust-lang.org/std/primitive.slice.html#method.copy_within) · C++ [`std::memmove`](https://en.cppreference.com/w/cpp/string/byte/memmove)

## Part 2 · Insert into the tree

**Where this fits.** The tree decides *which* leaf, and what to do when there is none.

### The task

In `src/storage/index/b_plus_tree.rs`:
- `descend_for_write(ctx, key, safe)`: starting from `ctx.root_page_id`, write-latch the page, find the child with `child_for` if it is internal, push the guard on `ctx.write_set`, and continue to the leaf. (`safe` is for stage 9; ignore it for now.)
- `insert(key, value)`: write-latch the header (`Context::new`); if the root is `INVALID`, allocate a page, make it a leaf (`init` with `leaf_max_size`), insert the pair and store the page as the root in the header (`ctx.set_root`); otherwise record `ctx.root_page_id`, descend, pop the leaf's guard and insert there. A duplicate key returns `false`.

### Tests

- The first insert creates a root that is a leaf with one pair, `max_size` set and no next leaf; the tree is no longer empty.
- Nine keys in shuffled order with `leaf_max_size = 10` stay in the root leaf, sorted; a duplicate is refused and the stored value is the first one.
- Negative and extreme keys sort as signed integers; after many inserts no page is pinned and the root can be write-latched at once.

### Syntax and methods

```rust
let mut ctx = Context::new(self.bpm.write_page(self.header_page_id));          // the header's write guard lives in the context
let root = Header::new(&ctx.header_page.as_ref().unwrap()[..]).root_page_id();
ctx.set_root(root_page_id);                                                    // given: writes the root id through that guard
let mut leaf_guard = ctx.write_set.pop().expect("the descent ends at a leaf"); // the leaf is the top of the stack
let mut leaf = Leaf::<_, K, V>::new(&mut leaf_guard[..]);                      // a view that can write
```

### Notes

**About `TOMBS`.** The template's `BPlusTree`, `IndexIterator` and leaf page carry a const generic `TOMBS` (default 0) for module 2d. Write `Leaf::<_, K, V>::new(..)` for now: it means `TOMBS = 0`, which is what every test of this module uses. Module 2d changes it to `Leaf::<_, K, V, TOMBS>`.

**Why a stack of guards.** Later a split needs the parent, and the parent's parent: the operation must still hold them when it gets there, so it keeps every guard it takes in the order it took them. `Vec<WritePageGuard>` is that stack, and dropping it (or clearing it) releases every latch.

**The empty-tree race.** Two threads inserting into an empty tree must not both create a root. Holding the header's **write** latch while checking `root == INVALID` and while storing the new root is what prevents it.

### In BusTub

`b_plus_tree.h`: "Context ... When you insert into / remove from the B+ tree, store the write guard of header page here. Remember to drop the header page guard and set it to nullopt when you want to unlock all. ... Store the write guards of the pages that you're modifying here."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::deque<WritePageGuard> write_set_;` in `Context` | `Vec<WritePageGuard<'a>>` (a stack; `pop` the last) |
| `std::optional<WritePageGuard> header_page_` and `header_page_ = std::nullopt` to unlock | `Option<WritePageGuard>`; `= None` drops (unlocks) it |
| `ctx.write_set_.back()` and `pop_back()` | `ctx.write_set.pop()` |

**Port rule:** an RAII guard stored in a container unlocks when the container drops or clears it; no explicit unlock call exists, which is why forgetting one is impossible.

### Learn more
- [`Vec::pop`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.pop) · [`Option::take`](https://doc.rust-lang.org/std/option/enum.Option.html#method.take) · CMU 15-445 "Index Concurrency Control"

## Performance

An insert into a leaf with room is one root-to-leaf descent (`h` page latches, taken exclusively) and one `memmove` of at most a page: `O(h + capacity)`. Holding write latches on every page of the path makes every other thread wait for the whole tree for the duration of the insert; at one thread that is free, at eight it serialises the index. Stage 9 removes that.

**Measure it.** Insert 100,000 sequential keys and 100,000 shuffled keys and compare; sequential inserts always hit the rightmost leaf (warm in the pool), shuffled ones spread over all leaves. Print `tree.bpm.get_writes()` per insert: it is the height of the tree, which is what stage 9 brings down to 1.

## Hints

### Insert before you count

`PageArray::insert_at(index, len, value)` takes the length *before* the insert and asserts room for one more; update the size afterwards. If an assertion fires about a full page, a test is inserting more than `max_size - 1` pairs: this stage's tests stay below, the next one handles the overflow.

### Where does the new root come from, and who stores it?

`bpm.new_page()` gives the id; `write_page(id)` the guard; `init(leaf_max_size)` makes it a leaf; and the **header** records it. Order matters only for visibility: because the header is write-latched, nobody can observe the root id before the leaf has its pair.

### The descent must not skip the root

The loop starts at `ctx.root_page_id`, latches that page, and only then decides whether it is a leaf; a root that is itself a leaf ends the loop at once. Write that case as a test with one key before you try three levels.
