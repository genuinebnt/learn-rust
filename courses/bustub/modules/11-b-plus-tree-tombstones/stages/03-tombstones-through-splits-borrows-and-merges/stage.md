Tombstones live in leaves, and leaves move pairs around: a split divides a leaf, a borrow moves a pair to a neighbour, a merge combines two leaves. This stage makes each of them keep every tombstone attached to its pair and keep every buffer within its limit. The rules are the ones that BusTub's own tombstone tests pin down, and the stage's scenarios are those tests restated as shapes.

## The task

In `src/storage/index/b_plus_tree.rs`:
- **Split** (in `insert`): the left leaf keeps the tombstones whose keys stayed, the new leaf gets those whose keys moved, **in the same order** (find which half a tombstoned key is in with `lower_bound` before the pairs move).
- **Purge** (`purge_tombstones` in `b_plus_tree_leaf_page.rs`: really remove every tombstoned pair, emptying the buffer) and call it at the start of `rebalance` for a short **leaf**: it is short, so its deleted pairs go first.
- **Borrow** (`borrow_from_left`, `borrow_from_right`): if the pair that moves is tombstoned, its tombstone moves with it; if the receiving leaf's buffer has no room, the deleted pair is simply dropped instead of moved. `rebalance` now **repeats** the borrow while the node is still below `min_size` and a sibling has a spare pair (a purge can leave it short by more than one).
- **Merge** (`merge`, leaf case): the source's tombstones join the destination's; if together they exceed `TOMBS`, the oldest are really removed (the pair goes too).

## Tests

- Splitting a leaf `[0,1,2,3~3,2,0]` with `TOMBS = 3` gives `{3 [0,1,2~2,0] [3,4~3]}`; BusTub's borrow and coalesce scenarios (a short leaf purges its own tombstones, then merges with the tombstoned neighbour: `[2,3,4~2]`; the larger page's tombstones survive a coalesce).
- A leaf that borrows a deleted pair takes its tombstone along (`[2,3,4,5,6~3]` after the walk-through in the test).
- 500 random inserts and removes for three buffer sizes and five node sizes agree with a model after every step and keep the structure checker (buffers within limits, every tombstone a pair in its leaf) satisfied; threads deleting, inserting and reading keep every live key.

## Syntax and methods

```rust
let (stay, go): (Vec<K>, Vec<K>) = leaf.tombstones().into_iter().partition(|t| leaf.lower_bound(t, &self.cmp) < keep);   // Iterator::partition
leaf.set_tombstones(&stay);
right.set_tombstones(&go);
let doomed: Vec<K> = tombs.drain(..tombs.len().saturating_sub(TOMBS)).collect();   // the oldest that do not fit
```

## Notes

**Why purge the short leaf first.** A short leaf is about to lend or borrow; deleted pairs are dead weight in that exchange. Removing them first can only make it shorter (so it may need more help), but a borrowed or merged leaf then holds only live pairs of its own plus whatever the neighbour sends. This is a choice, not a law of nature: the test scenarios pin it down (the tombstone of the leaf that is short does not survive; the neighbour's does).

**Borrowing a deleted pair.** The pair moves because it is the neighbour's first or last, and the borrower needs *entries*; its tombstone moves with it, so the pair stays deleted. If the borrower's buffer is full the deleted pair is dropped instead: nothing is lost (it was deleted) but nothing is gained either, so the loop tries another.

**A merge never overflows a page, but it can overflow a buffer.** Both leaves may hold tombstones; the merged leaf has one buffer. The oldest tombstones that do not fit are really removed.

**The separator key after a borrow** is still the smallest key of the right leaf, tombstoned or not: the physical pair decides the signpost, not whether it is deleted.

## In BusTub

`TombstoneSplitTest` ("each leaf's tombstones are the tombstoned keys it holds, in the order of recency"), `TombstoneBorrowTest` ("EXPECT_GE(size, min_size) ... EXPECT_EQ(tombstones.size(), 1)"), and `TombstoneCoalesceTest` ("The final delete from the smaller page should force a coalesce ... final set of tombstones should either be the last two keys logically deleted from the smaller page or the last two keys logically deleted from the larger page"). BusTub's Project 2 design document asks "Briefly describe how you store tombstones in the leaf and when a tombstone becomes a real removal."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::partition` / manual loops over tombstone indexes, re-adjusting the indexes after each move | `Iterator::partition` over keys: nothing to adjust |
| copying a tombstone list with `std::vector` insert/erase | `Vec::drain`, `extend`, `set_tombstones` |

**Port rule:** tombstones stored as indexes must be rewritten whenever pairs move; tombstones stored as keys survive any shift.

## Learn more
- [`Iterator::partition`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.partition) · [`Vec::drain`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.drain) · [Wikipedia: B+ tree](https://en.wikipedia.org/wiki/B%2B_tree)

## Performance

A split now also partitions a buffer of at most `TOMBS` keys: `O(TOMBS * log capacity)` extra work. A purge removes up to `TOMBS` pairs, each a shift of up to a page, but only when the leaf is short anyway, which already costs a borrow or a merge. A deleted pair that travels with a borrow adds `O(TOMBS)`.

The effect on the tree: fewer physical removals (a pair deleted and inserted again costs no shift at all), at the price of leaves that are up to `TOMBS` pairs fuller than their live contents. A bulk delete leaves the structure intact and does the shifting later (a split, a short leaf), or never, if the keys come back.

**Measure it.** Delete a random 90% of 100,000 keys with `TOMBS` 0 and 4; count page writes, the number of leaves left and the time for a full scan.

## Hints

### Decide which half a tombstone goes to before moving anything

The tombstoned key is still in the leaf, so `lower_bound(key)` is its slot: `< keep` stays. Compute the two lists first, then move the pairs, then write the two buffers. Moving first changes the slots you search in.

### Think of the three exchanges as "who keeps their tombstones"

Split: both halves (each its own). Borrow: the moved pair's tombstone goes with it. Merge: the destination keeps its own and takes the source's. Write each as a sentence before the code, then check each against the shape in a test.

### The structure checker is your friend

After every operation call `check_structure_t::<TOMBS>`: it fails with the leaf and the key if a tombstone has no pair, a buffer is over its limit or a key is buffered twice. Run your random test first with `TOMBS = 1`: the smallest buffer finds the overflow cases fastest.
