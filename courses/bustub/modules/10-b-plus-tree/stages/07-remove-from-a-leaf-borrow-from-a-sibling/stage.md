Remove is insert run backwards, and it has the same shape: take the pair out of its leaf, and if the leaf is now **too empty** (below `min_size`), fix it up. Fixing means first trying to **borrow** one entry from a neighbouring page that has one to spare; only when neither neighbour can lend does the tree **merge** (the next stage). Borrowing is local: it changes the two siblings and one key in their parent, never the shape of the tree.

This stage covers removal itself, the empty root, and borrowing, at the leaf level and (in the code, though the tests exercise it in the next stage) at the internal level.

## Part 1 · Page-level helpers

**Where this fits.** The tree code moves pairs between pages; the pages need the primitives.

### The task

- In `b_plus_tree_leaf_page.rs`: `remove(key, cmp) -> bool` (find the slot with `lower_bound`; if the key there is equal, shift the later pairs left (`PageArray::remove_at`) and count one fewer; `false` if absent), `remove_at(index)` and `insert_at_front(key, value)`.
- In `b_plus_tree_internal_page.rs`: `remove_at(index)` (shifting the later pairs down; removing slot 0 makes the next pair slot 0, so its key becomes the unused one) and `insert_at_front(key, child)` (the new pair becomes slot 0).

### Tests

- A leaf removes the first, middle and last keys keeping order, reports `false` for a missing or already removed key; `remove_at` and `insert_at_front` shift correctly.
- An internal page's `remove_at(2)` and `remove_at(0)` shift children and keys together; `insert_at_front` puts the child in slot 0.

### Syntax and methods

```rust
self.entries_mut().remove_at(at as usize, size as usize);     // 2a-03: shifts [at + 1, size) left by one entry
self.set_size(size - 1);
self.entries_mut().insert_at(0, size as usize, &(key.clone(), child));
```

### Notes

The pair that `remove_at` shifts away is not erased; it is simply beyond `size`. Never read beyond `size` (the accessors panic for that reason).

### In BusTub

`b_plus_tree_internal_page.h`/`.cpp` provide `KeyAt`, `SetKeyAt`, `ValueAt` and `ValueIndex` only: everything that shifts is yours.

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::copy(first + 1, last, first)` / `memmove` to close the gap | `copy_within` inside `PageArray::remove_at` |
| `--size_` and forgetting the stale last element | `set_size(size - 1)`; the accessors refuse to read past it |

### Learn more
- [`slice::copy_within`](https://doc.rust-lang.org/std/primitive.slice.html#method.copy_within) · [`Vec::remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.remove) (the same shift on a `Vec`)

## Part 2 · Remove from the tree; borrow from a sibling

**Where this fits.** The tree decides what a short page does.

### The task

In `src/storage/index/b_plus_tree.rs`:
- `remove(key)`: write-latch the header; an empty tree returns at once; otherwise record the root, `descend_for_write` (as for insert), pop the leaf and `remove` the key from it (missing key: nothing to do). Then:
  - the leaf **is the root** and now has size 0: the tree is empty again: `ctx.set_root(PageId::INVALID)` and the page is to be deleted;
  - the leaf is not the root and `size < min_size`: `rebalance(ctx, leaf_guard, &mut to_delete)`.
  After every guard is dropped, `bpm.delete_page` for each page in `to_delete` (a pinned page cannot be deleted).
- `rebalance` (borrowing half): pop the parent, find the node's slot with `value_index`, and take the left sibling's write latch (if the node is not the first child). If it has more than `min_size` entries, **borrow its last**: `borrow_from_left`. Otherwise try the right sibling the same way with `borrow_from_right`. (If neither can lend, the next stage merges.)
- `borrow_from_left` / `borrow_from_right`:
  - **leaf**: move the pair across; set the parent's separator to the first key of the right-hand page of the two;
  - **internal**: the child moves across and the parent's separator **rotates** down into the receiving page and the donor's neighbouring key rotates up.

### Tests

- Removing a missing key, or from an empty tree, changes nothing; removing from a leaf that stays at least half full just removes the pair.
- Removing the last pair of a root leaf empties the tree: root `INVALID`, the page deleted from the pool, and the tree is usable again.
- A short leaf borrows from the left sibling (`{4 [1,2,3] [4,5]}` minus 5 becomes `{3 [1,2] [3,4]}`) or, as the first child, from the right (`{4 [1,2,3] [4,5,6]}` minus 1 and 2 becomes `{5 [3,4] [5,6]}`); a 14-key tree borrowing from the right keeps the chain and all values.

### Syntax and methods

```rust
let (idx, parent_size) = { let p = Internal::<_, K>::new(&parent_guard[..]); (p.value_index(node_page_id).expect("the parent lists its child"), p.size()) };
let mut left = self.bpm.write_page(Internal::<_, K>::new(&parent_guard[..]).value_at(idx - 1));
if Page::new(&left[..]).size() > Page::new(&left[..]).min_size() { /* borrow */ return; }
```

### Notes

**Which sibling and in which order.** Always take sibling latches in **left-to-right** order, so two threads working on neighbouring pages can never wait on each other in a cycle.

**Borrowing at the leaf level**: the separator in the parent is the smallest key of the right-hand leaf; after moving the left leaf's last pair over, the parent key becomes *that pair's key*; after moving the right leaf's first pair over, the parent key becomes the right leaf's *new first key*.

**Borrowing at the internal level is a rotation.** Moving a child across also moves the separator: the parent's key comes *down* into the receiving page (it separates the old first child from the one that arrived) and the donor's key comes *up* to replace it. The keys travel through the parent like a rotation in a balanced binary tree.

**Deleting pages.** `delete_page` fails while a page is pinned, and a latched page is pinned. Collect the ids, release every guard (end of the block that owned the context), then delete.

### In BusTub

`b_plus_tree.cpp` (`Remove`): "If current tree is empty, return immediately. If not, User needs to first find the right leaf page as deletion target, then delete entry from leaf page. Remember to deal with redistribute or merge if necessary." `b_plus_tree_page.h` declares `GetMinSize()` and leaves its definition to you; stage 1 of this course defines it (leaves `max_size / 2`, internal pages `ceil(max_size / 2)` children).

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `bpm_->DeletePage(page_id)` while still holding the guard (fails, silently) | collect the id, drop the guards, then call `delete_page` |
| siblings found with `parent->ValueIndex(page_id) ± 1` | `value_index(..)` returns an `Option`; the `idx > 0` and `idx + 1 < size` checks are explicit |
| redistribution and "coalescing" in the textbook | borrow and merge |

### Learn more
- CMU 15-445 "Tree Indexes" (deletion) · [Wikipedia: B+ tree deletion](https://en.wikipedia.org/wiki/B%2B_tree#Deletion) · [`Vec::drain`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.drain)

## Performance

A remove that leaves its leaf at least half full touches one leaf. One that borrows touches the leaf, one sibling and the parent: three pages written, no allocation, no page freed. Because a borrow always succeeds when either neighbour has a spare entry, removals in a randomly-filled tree rarely need to merge, and the tree stays at roughly the same shape under a mixed workload.

**Measure it.** Insert 100,000 shuffled keys, then remove 50,000 random ones and count how many removals borrowed (instrument `rebalance`) and how many fell through to the merge. Compare with removing in ascending order, which empties leaves from the left and borrows almost never.

## Hints

### Remove, then ask the leaf whether it is short

The size to compare is the one *after* the pair is gone, against `min_size`. The root is exempt: a root leaf may have any number of pairs from 1 up; an empty one means the tree is empty. Do the root check first; it is the only case where `rebalance` must not run.

### Which key in the parent changes when you borrow?

Work one example by hand: `{4 [1,2,3] [4,5]}`, remove 5, the right leaf `[4]` is short. Take 3 from the left leaf: it becomes `[1,2]` and the right one `[3,4]`. The parent's separator must now be 3, the smallest key of the right-hand leaf. Do the mirror case (borrow from the right) on paper too; the separator becomes the right leaf's new first key.

### Take the sibling latch after the parent's, and before you decide

The parent's guard is already on `ctx.write_set` (popped for this step). Take the sibling's write latch while holding it. Do not release the parent until you are done: another thread must not be able to merge your sibling away between your size check and your borrow.
