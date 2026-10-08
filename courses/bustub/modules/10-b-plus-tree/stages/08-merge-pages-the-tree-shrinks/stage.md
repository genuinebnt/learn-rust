When neither neighbour has an entry to spare, the page and a neighbour together fit in one page, so they **merge**: everything moves into one of them, the other is deleted, and the parent loses a child (and a separator). The parent may now be too empty itself, and the same repair climbs the tree, so a single removal can cascade up to the root. When the cascade empties the root down to **one child**, that child becomes the root and the tree is one level shorter. This is the mirror image of the root split of stage 5, and the only way a B+ tree shrinks.

## The task

Finish `rebalance` and implement `merge` in `src/storage/index/b_plus_tree.rs`.
- If neither sibling could lend, merge with the **left** sibling if there is one (the node's entries are appended to it and the node's page is to be deleted; the parent loses slot `idx`), otherwise with the **right** sibling (its entries are appended to the node, its page is to be deleted; the parent loses slot `idx + 1`).
- `merge(parent, src_idx, dest, src, is_leaf)`: append every entry of `src` to `dest`. **Leaf**: also `dest.next = src.next`. **Internal**: the source's first child comes with the **parent's separator** (the key at `src_idx`) as its key, because the source's own slot-0 key was never stored.
- Then `parent.remove_at(removed_idx)`. If the parent is the root: with one child left that child is the new root (`ctx.set_root(child)`, the old root page is to be deleted); otherwise done. If the parent is not the root and now has fewer than `min_size` children, repeat the whole step with the parent as the short node.

## Tests

- `{3 [1,2] [3,4]}` (leaf max 4) minus 4 merges the short right leaf into the left one and the root collapses to `[1,2,3]`; the old root and the merged-away page leave the pool; minus 1 merges the first leaf with its right sibling (`[2,3,4]`).
- A merge in the middle of a 6-leaf tree keeps the next-leaf chain; removing keys from a 12-key tree keeps a valid structure after every step.
- With `(leaf 3, internal 3)` an internal page that loses a child borrows from or merges with a sibling (exact shapes, step by step); removing 9..1 from a 4-level tree shrinks it one level at a time to empty.
- BusTub's `DeleteTestNoIterator` and `SequentialEdgeMixTest`; 400 random inserts and removes (three seeds, six size pairs) agree with a `BTreeMap` and keep the structure valid after every step; a fully emptied tree gives all its pages back.

## Syntax and methods

```rust
// merge `node` into its left sibling: the node's entries are appended, so the node is the *source*
self.merge(&mut parent_guard, idx, &mut left, &mut node_guard, is_leaf);
to_delete.push(node_page_id);
let mut parent = Internal::<_, K>::new(&mut parent_guard[..]);
parent.remove_at(idx);
if ctx.is_root_page(parent_page_id) {
    if parent.size() == 1 { ctx.set_root(parent.value_at(0)); to_delete.push(parent_page_id); }
    return;
}
if parent.size() >= parent.min_size() { return; }
node_guard = parent_guard;          // the parent is the short node now: loop
```

## Notes

**Why the merged page always fits.** A short page has `min_size - 1` entries and the sibling that cannot lend has exactly `min_size`. For a leaf that is `2 * (max_size / 2) - 1 <= max_size - 1` pairs (a leaf at rest holds at most `max_size - 1`); for an internal page `2 * ceil(max_size / 2) - 1 <= max_size` children. This is what the two different minimum sizes of stage 1 are for.

**Which separator survives.** Merging `right` into `left` removes the parent's key *between* them. Leaf merge: the key is simply dropped (the leaf keys still tell the whole story). Internal merge: the key comes **down** to sit in front of the right page's first child, because it is the only thing that says where the left page's range ends.

**The root.** The root is allowed to have as few as 2 children (or 1 pair if it is a leaf). A root with one child is a lie about the height: promote the child.

**Deletion order.** The merged-away page, and any replaced root, are deleted *after* every latch is released: collect them in `to_delete`.

## In BusTub

`b_plus_tree.cpp` (`Remove`): "Remember to deal with redistribute or merge if necessary." The textbook words are *coalesce* (merge) and *redistribute* (borrow). `DeleteTestNoIterator` ends by removing the last key and asserting `ASSERT_EQ(root_page_id, INVALID_PAGE_ID)`: an emptied tree has no root.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a recursive `CoalesceOrRedistribute(node, txn)` that calls itself for the parent | a `loop` whose state is the short node's guard |
| `if (node->IsRootPage()) return AdjustRoot(node);` | `ctx.is_root_page(id)` then the one-child check |
| `DeletePage` called inside the recursion | pages collected in `to_delete`, deleted at the end |
| copying the parent's key into the moved entry by index arithmetic | read the separator once (`key_at(src_idx)`) and pass it down |

**Port rule:** never delete a page while its guard is alive; return the list of doomed pages to the outermost function.

## Learn more
- CMU 15-445 "Tree Indexes" · [Wikipedia: B+ tree deletion](https://en.wikipedia.org/wiki/B%2B_tree#Deletion) · [Cormen et al., "Introduction to Algorithms", B-trees chapter](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)

## Performance

A merge writes the surviving page, the parent and (for a cascade) each further level, and frees a page: still `O(height)` page writes, with `O(page)` copying. Cascades are rare for the same reason as split cascades. The notable cost is *oscillation*: a workload that alternately inserts and removes one key around a boundary can split and merge the same pair of leaves repeatedly. The standard fixes are hysteresis (a lazy delete that merges only when a page is *empty*, as PostgreSQL does) or the tombstones of module 2d.

Freed pages go back to the buffer pool (and the disk manager's free list), so a tree that shrinks gives its space back for other tables.

**Measure it.** Insert 100,000 keys, remove them all in random order and count merges and borrows; the number of pages freed must equal the number allocated minus one (the header). Then repeat with alternating insert/remove of one key at a leaf boundary and count the split/merge ping-pong.

## Hints

### The node is the source or the destination: which one?

If you merge with the **left** sibling, the left page survives: append the node's entries to it and delete the node. If the node has no left sibling, merge with the **right** one: append *its* entries to the node and delete the right page. Make `merge(dest, src)` take the roles explicitly, and the parent always loses the entry of the *source*.

### What does the parent's separator do in an internal merge?

The source's slot-0 key is unused (that is why it was never stored), so when its first child joins `dest` as a middle child, the key that has to precede it is the parent's separator for the source. Without it the merged page would have a child with no lower bound. Work it through on `{9 {5,7 [4] [5,6] [7,8]} ...}` first.

### Cascading, and the one condition that ends it

The loop ends at a page that has at least `min_size` entries after the removal, or at the root. The root is special: it never *underflows*, but a root internal page with a single child must be replaced by it. Check `size == 1` only for the root, after the parent's `remove_at`.
