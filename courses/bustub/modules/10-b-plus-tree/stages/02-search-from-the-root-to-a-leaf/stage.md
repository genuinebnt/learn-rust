A lookup in a B+ tree is a walk from the root down to one leaf: at each internal page, binary search the separator keys to pick the child whose range holds the key; at the leaf, binary search the pairs. This stage writes both searches and the tree's first real operations: `new`, `is_empty`, `get_root_page_id` and `get_value`. The tests build small trees **by hand** out of pages, so search is checked before any insert exists.

The walk is also the module's first latching rule: a reader holds a page only until it has latched the page it is about to visit ("latch crabbing"), so it never holds more than two pages and a writer deep in the tree is never waited on from the top.

## Part 1 · Choosing a child, finding a key

**Where this fits.** Everything the tree does starts with "which child?" and "which slot?". Both are binary searches over sorted keys, and both have one off-by-one that decides whether a key at a boundary is found.

### The task

In `src/storage/page/b_plus_tree_internal_page.rs` implement `child_for(key, cmp)`: the child `i` with `key(i) <= key < key(i + 1)`, i.e. the **last slot whose key is at most `key`** (slot 0 if there is none). Slot 0's key is never looked at; the keys of slots `1..size` are sorted.

In `src/storage/page/b_plus_tree_leaf_page.rs` implement `lower_bound(key, cmp)` (the first slot whose key is **not less** than `key`, `size` if all are less) and `lookup(key, cmp)` (`Some(value)` if that slot's key is equal).

### Tests

- With separators 10, 20, 30 every key from `i64::MIN` to `i64::MAX` routes to the right child, including the boundaries (10 goes right, 9 goes left); slot 0's key may be garbage; a 300-child page routes every probe correctly.
- `lower_bound` and `lookup` on `[10, 20, 30, 40]` for keys below, between, equal to and above the entries; an empty leaf finds nothing.

### Syntax and methods

```rust
// PageArray::lower_bound(len, |entry| ordering of entry vs the target): the first index whose ordering is not Less
let keys = PageArray::<_, (K, PageId)>::new(&self.page.as_ref()[INTERNAL_PAGE_HEADER_SIZE + <(K, PageId)>::SIZE..]);   // slots 1.. only
let first_greater = keys.lower_bound(self.size() as usize - 1, |(k, _)| if cmp.compare(k, key).is_le() { Less } else { Greater });
self.value_at(first_greater as u32)       // the child just before the first key that is greater
```

### Notes

**Two searches, one function.** `lower_bound` finds "the first entry not less than the target". For a leaf that is the slot of the key (if present). For an internal page you want "the first key *greater* than the target"; the trick is to tell `lower_bound` that every key `<=` the target is "less", so it stops at the first key that is strictly greater, and the child you want is the one just before it. Search the keys of slots `1..size` only (slice the page after slot 0) and the answer is already the child index.

**Equal keys go right.** A separator `k` is the smallest key of the subtree to its right, so searching for `k` itself must go right. Write the boundary test first.

### In BusTub

`b_plus_tree_internal_page.h`: "Pointer PAGE_ID(i) points to a subtree in which all keys K satisfy: K(i) <= K < K(i+1)". BusTub leaves the search to you (`GetValue`: "This method is used for point query ... true means key exists"), and its constructor does what `new` does here: it write-latches the header page and sets `root_page_id_ = INVALID_PAGE_ID`.

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::lower_bound(first, last, value, comp)` / `std::upper_bound` | `PageArray::lower_bound` (your 2a code), or `slice::partition_point` on a slice |
| `comparator(a, b) < 0` | `cmp.compare(a, b).is_lt()` on an `Ordering` |
| searching an array whose first element is invalid by "starting from `i = 1`" | slice off slot 0 and search the rest: the result is a child index |

**Port rule:** `upper_bound` is `lower_bound` with `<=` as the "less" test; write a binary search once and derive both.

### Learn more
- [`slice::partition_point`](https://doc.rust-lang.org/std/primitive.slice.html#method.partition_point) · [`Ordering`](https://doc.rust-lang.org/std/cmp/enum.Ordering.html) · CMU 15-445 "Tree Indexes"

## Part 2 · The tree: new, is_empty, get_value

**Where this fits.** `BPlusTree` is the object everything else hangs off: the buffer pool, the comparator, the sizes, and the id of the header page.

### The task

In `src/storage/index/b_plus_tree.rs`:
- `new(index_name, header_page_id, bpm, cmp, leaf_max_size, internal_max_size)`: panic unless `leaf_max_size >= 2` and `internal_max_size >= 3` and they fit a page; wrap the pool in a `TracedBufferPoolManager` (given: it counts latched pages); **format the header page** (the caller only allocated it);
- `get_root_page_id()` (read-latch the header; `INVALID` for an empty tree) and `is_empty()`;
- `find_leaf(key)` (`None` key means the leftmost leaf): read-latch the header, then the root (drop the header), then loop: while the page is internal, latch the child to follow and let go of the parent; return the leaf's guard;
- `get_value(key)`: the leaf for `key`, then `lookup`.

### Tests

- A new tree is empty, has root `INVALID`, answers lookups with nothing, and leaves no page pinned; a leaf of max size 1 is rejected.
- Hand-built trees (a root leaf; three levels) return every key's value and nothing for keys below, between and above them; no pin or latch is left behind afterwards.

### Syntax and methods

```rust
let header_guard = self.bpm.read_page(self.header_page_id);
let root = Header::new(&header_guard[..]).root_page_id();
let mut guard = self.bpm.read_page(root);
drop(header_guard);                                   // the root is latched: nobody can change the header's meaning for us now
while !Page::new(&guard[..]).is_leaf_page() {
    let child = Internal::<_, K>::new(&guard[..]).child_for(key, &self.cmp);
    guard = self.bpm.read_page(child);                // the right-hand side is evaluated first: the child is latched before the old guard drops
}
```

### Notes

**Crabbing in one line.** `guard = self.bpm.read_page(child)` latches the child *before* the assignment drops the parent's guard. If you wrote `drop(guard); guard = read_page(child)` there would be a window in which a writer could split the child away and the next `read_page` would visit a page that no longer holds the key's range.

**Why the header page is latched at all.** The root changes (a root split makes a new root). A reader that read the root id and was then delayed must not follow a stale id; holding the header's read latch until the root's is held closes that gap.

### In BusTub

`b_plus_tree.h`: "explicit BPlusTree(std::string name, page_id_t header_page_id, BufferPoolManager *buffer_pool_manager, const KeyComparator &comparator, int leaf_max_size = LEAF_PAGE_SLOT_CNT, int internal_max_size = INTERNAL_PAGE_SLOT_CNT);" and "Do not change this type to a BufferPoolManager!" (the traced pool).

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto guard = bpm_->ReadPage(id); ... guard = bpm_->ReadPage(child);` (move assignment drops the old guard after the new one exists) | the same: assignment evaluates the right side first |
| `guard.As<InternalPage>()` (a reinterpret cast of the page) | `Internal::<_, K>::new(&guard[..])` (a view) |
| `bool GetValue(const KeyType &key, std::vector<ValueType> *result)` | `get_value(&key) -> Vec<V>` (empty or one element: keys are unique) |

### Learn more
- CMU 15-445 "Index Concurrency Control" (latch crabbing) · [`Drop`](https://doc.rust-lang.org/std/ops/trait.Drop.html) order of assignments

## Performance

A lookup in a tree of height `h` costs `h` page reads and `h` binary searches: `O(h * log2(fan-out))` comparisons, and `h` is 3 or 4 for any practical table. The binary search over a 681-way page is about 10 comparisons; a linear scan averages 340. The latching adds 2 uncontended lock operations per level (the child's before the parent's release).

**Measure it.** Build a tree by hand (or after stage 5) with 100,000 keys, look up every key and divide the time by the number of lookups; count the page reads with `tree.bpm.get_reads()` and check it equals `height` per lookup. Then replace `lower_bound` with a linear scan and measure how much slower a lookup gets.

## Hints

### Which child does a key equal to a separator belong to?

The right one. A separator is the *smallest key of the subtree on its right* (a leaf split copies its first key up), so `key == separator` must go right. A binary search that stops at the first key `>= target` sends it left; one that stops at the first key `> target` and takes the child before it sends it right.

### Search the keys of slots 1.., and remember slot 0's child is the "less than everything" child

`key(0)` is garbage. If you feed it to the comparator the search can go wrong for a page whose slot 0 holds zeros or a stale key (the test puts `i64::MAX` there). Search only the keys that exist and let "no key is at most the target" mean child 0.

### Format the header in `new`, not in the test

`bpm.new_page()` returns a zeroed page, and an unformatted header says "the root is page 0". Writing `INVALID` is `new`'s job: the test allocates the page, calls `new`, and expects `is_empty()`.
