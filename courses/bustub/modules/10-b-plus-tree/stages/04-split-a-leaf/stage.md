A leaf holds at most `max_size - 1` pairs at rest. The insert that brings it to `max_size` **splits** it: the upper half moves to a new leaf to its right, the two are chained, and the new leaf's first key is copied up into the parent as the separator. If the leaf was the root there is no parent, so the tree gets a new root with the two leaves as children, and **the tree is one level taller**. That is the only way a B+ tree ever grows, which is why all leaves are always at the same depth.

This stage handles splits whose parent has room. The next one handles a parent that is full too.

## Part 1 · Put a separator into an internal page

**Where this fits.** After a split the parent needs one more `(separator, child)` pair, in key order.

### The task

In `src/storage/page/b_plus_tree_internal_page.rs` implement `insert_child(key, child, cmp)`: find where `key` belongs among the keys of slots `1..size` (after the last key that is at most `key`), shift the later pairs right (`PageArray::insert_at`) and count one more. Panic if the page is already full (`size == max_size`) — the tree must split such a page instead.

### Tests

- Separators inserted at the end, in the middle and at the front of the keys keep keys and children paired (`insert_at` moves both); a full page panics.

### Syntax and methods

```rust
// the new pair goes after the last key that is <= `key`; search slots 1.. like child_for does
let at = keys.lower_bound(size as usize - 1, |(k, _)| if cmp.compare(k, key).is_le() { Less } else { Greater }) as u32 + 1;
self.entries_mut().insert_at(at as usize, size as usize, &(key.clone(), child));
```

### Notes

The new child goes **to the right of the child that split**: its separator is bigger than the old child's keys and smaller than the next separator. Finding the position with the same search as `child_for` (and adding the slot-0 offset back) means a page can never end up with keys out of order.

### In BusTub

`b_plus_tree_internal_page.h`: "Store n indexed keys and n + 1 child pointers (page_id) within internal page." An internal page that is already full cannot take another child: that is the next stage.

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `for (int i = size; i > pos; --i) { key_array_[i] = key_array_[i-1]; page_id_array_[i] = page_id_array_[i-1]; }` (two arrays, two shifts) | one `insert_at` on the pair array |
| `std::upper_bound(...)` | `lower_bound` with `<=` as the "less" test |

### Learn more
- CMU 15-445 "Tree Indexes" (insertion) · [`slice::copy_within`](https://doc.rust-lang.org/std/primitive.slice.html#method.copy_within)

## Part 2 · Split a full leaf; the tree gets a root

**Where this fits.** `insert` from stage 3 ends with the pair in the leaf. Now it must notice that the leaf reached `max_size`.

### The task

In `src/storage/index/b_plus_tree.rs`, after a successful leaf insert, if `leaf.size() < leaf.max_size()` return `true`.

Otherwise the leaf is split. Afterwards two leaves hold the same pairs in the same order, the left with `ceil(size / 2)` of them and a new right leaf with the rest; the right leaf is chained as the left's `next` and takes over the left's old `next`; and the right leaf's first key is passed to `insert_into_parent` as the separator.

> [!ASIDE] The steps, if you would rather not work them out
> 1. allocate a new page, write-latch it, `init` it as a leaf with the same max size;
> 2. the left leaf keeps `ceil(size / 2)` pairs; the rest move to the new leaf (`set_entry_at` into slots `0..`, then `set_size` on both);
> 3. chain them: `new.next = old.next; old.next = Some(new_id)`;
> 4. call `insert_into_parent(ctx, left_id, new.key_at(0), new_id)`.

`insert_into_parent` pops the parent from `ctx.write_set`. **No parent** means the left page was the root: allocate a new internal page (`init` with `internal_max_size`), set slot 0 to `left` and slot 1 to `(key, right)`, size 2, and `ctx.set_root(new_root)`. **A parent with room** (`size < max_size`) takes `insert_child(key, right_id)` and the split is done.

### Tests

- With `leaf_max_size = 3`, inserting 1, 2 leaves a root leaf; inserting 3 makes `{3 [1,2] [3]}`: a new internal root, the old leaf as its left child, chained to the new right leaf.
- The left half keeps the extra pair for every `max_size` from 2 to 7 (`{4 [1,2,3] [4,5]}` for 5).
- Ascending, descending and shuffled inserts of up to 120 keys stay valid (sorted, uniform depth, correct chain, correct separators); duplicates after splits are refused; nothing stays pinned.

### Syntax and methods

```rust
let keep = size.div_ceil(2);                                     // the left half keeps the extra pair
for i in keep..size {
    let (k, v) = leaf.entry_at(i);                               // copy the upper half into the new page...
    right.set_entry_at(i - keep, &k, &v);
}
right.set_size(size - keep);
leaf.set_size(keep);                                             // ...and forget it in the old one (the bytes stay, the size says they are gone)
let Some(mut parent_guard) = ctx.write_set.pop() else { /* the root split: make a new root */ };
```

### Notes

**Copy up, not move up.** The separator is the new leaf's first key and stays in the leaf: leaves must hold every key, because the internal pages are only signposts. (When an *internal* page splits, the next stage, the middle key does move up.)

**Hold the left leaf until the parent knows.** The left leaf's write guard stays in your hands until `insert_into_parent` returns, so no reader or writer can reach the new right leaf through the parent before it is recorded there. The new page's guard can be dropped as soon as it is filled in.

**The root of the tree changes only here (and on shrinking).** A new root's id goes into the header page through the header guard that the operation has held since it started.

### In BusTub

BusTub leaves the splitting rule to you: its Project 2 design document asks "Briefly describe when you split, coalesce or redistribute, and which sibling you pick. Say what happens when the root splits or collapses." This course fixes the rule (a leaf splits when an insert brings it to `max_size`; the left half keeps `ceil`) so the tests can check exact shapes.

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `page_id_t new_page_id = bpm_->NewPage(); auto new_guard = bpm_->WritePage(new_page_id);` | the same calls; the guard is a local that drops (unlatches, unpins) at scope end |
| `new_leaf->SetNextPageId(leaf->GetNextPageId()); leaf->SetNextPageId(new_page_id);` | the same two steps with `Option<PageId>` |
| `std::copy(...)` / `memcpy` of the upper half to the new page | a loop of `entry_at` / `set_entry_at` (or `copy_within` across two views) |
| `ctx.write_set_.pop_back()` and `ctx.IsRootPage(id)` | `ctx.write_set.pop()` returning `None` for the root |

**Port rule:** C++ code that splits a node by `memcpy` of half its array becomes reads and writes through typed views; the bytes that remain after `set_size` are garbage by definition.

### Learn more
- CMU 15-445 "Tree Indexes" (insertion with splits) · [Wikipedia: B+ tree insertion](https://en.wikipedia.org/wiki/B%2B_tree#Insertion) · [`let ... else`](https://doc.rust-lang.org/rust-by-example/flow_control/let_else.html)

## Performance

A split reads nothing new and writes three pages: the old leaf, the new leaf and the parent (plus the header if the root changed). It copies half a page. Most inserts do not split at all: for a leaf holding `n` pairs, one insert in about `n / 2` splits, so the amortised cost of the structure is a small constant above a plain leaf insert. The tree grows at the **root** (every leaf stays at the same depth), so unlike a binary search tree it needs no rebalancing and its height is `O(log_f n)` however the keys arrive: ascending, descending or random.

The one thing that depends on arrival order is *fill*: ascending inserts leave every split leaf exactly half full (they never get another key), shuffled inserts converge to about 69% (ln 2) full on average. Real systems special-case the rightmost split to keep sequential loads dense.

**Measure it.** Insert 100,000 keys ascending, descending and shuffled with the real page size and count the leaves each time with `get_num_leaves` from the test utilities; compare with `n / capacity`. Then print `tree.bpm.get_writes()` per insert: most inserts write one page, a few write three.

## Hints

### Split first, then tell the parent: what must still be latched?

The left leaf, until the parent has the separator. The parent is already on your stack (`ctx.write_set`) because the descent pushed it; the tree's header is still in the context too, because a root split needs it. Do not release anything until `insert_into_parent` is done: stage 9 is where releasing early becomes safe.

### Which key goes up, and does it leave the leaf?

The first key of the **new right leaf**, and it stays there. Check with the shape: after inserting 1, 2, 3 with `max_size = 3` the leaves are `[1,2]` and `[3]` and the root has the key 3. A search for 3 must go right (stage 2's boundary rule), which only works if 3 is still in the right leaf.

### The chain is easy to break

After the split `old.next` must be the new leaf and `new.next` the old `next` (or `None`). Get the order wrong (set `old.next` before reading it) and the last leaves disappear from scans. The tests walk the chain from the leftmost leaf and compare it with the keys in sorted order.
