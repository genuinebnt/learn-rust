Now the tree uses the buffer. **Remove** no longer shifts anything: the pair stays in its leaf and its key is written to the buffer as the newest tombstone. When the buffer is already full, the **oldest** tombstoned pair is removed for real (that is the only time a delete costs a shift), and the new tombstone takes its place. **Insert** of a key that is tombstoned brings it back to life with the new value and no new slot. **Search** and **scan** treat tombstoned pairs as if they were gone.

The size of a leaf (the number of pairs in its page, deleted or not) is what splits and underflow look at, so a delete that only buffers a tombstone never changes the shape of the tree. That is the point: a burst of deletes into a leaf costs one buffer write each, and the real removal happens in batches or never.

## The task

The tree and its views are generic over `TOMBS` (`BPlusTree<'a, K, V, C, const TOMBS: usize = 0>`, `IndexIterator<'a, K, V, TOMBS>`): make sure every `Leaf::<_, K, V>` in your code from module 2c says `Leaf::<_, K, V, TOMBS>`, so the tombstone-aware version is used.

In `b_plus_tree_leaf_page.rs`:
- `lookup(key)`: a tombstoned pair is **not found** (`find(key)` still sees it: the physical slot);
- `insert(key, value)`: a key that is present and *tombstoned* gets the new value and loses its tombstone (return `true`, no new slot); a live duplicate is still `false`;
- `remove_at(index)` also drops the removed pair's tombstone (a pair that is gone cannot stay in the buffer);
- `remove_logically(key, cmp) -> bool` (only for `TOMBS > 0`): `false` if the key is missing or already tombstoned; if the buffer is full, really `remove` the oldest tombstoned pair; then `add_tombstone(key)`.

In `b_plus_tree.rs`: `remove` calls `remove_logically` when `TOMBS > 0` (and the old physical `remove` otherwise); `remove_optimistic` handles a logical delete too (it only gives up if the leaf would lose a pair for real and fall below `min_size`).

In `index_iterator.rs`: when normalising a position, step over slots with `is_deleted_at`.

## Tests

- A leaf deletes logically (the pairs stay, the oldest tombstoned pair goes when the buffer is full), refuses to delete twice, and an insert of a tombstoned key brings the pair back.
- A tree shows `[2,3~2,3]` after deleting 2 and 3 from a leaf holding 2 and 3, a full buffer makes room by really removing the oldest (`[0,2,3,4~2,3]`), and removing a deleted or missing key changes nothing.
- Deleted pairs are not found and not scanned (a scan starting at a deleted key starts at the next live one); a tree with every pair deleted scans as empty but keeps its pages; and a delete that fits still write-latches only the leaf.

## Syntax and methods

```rust
let removed = if TOMBS > 0 { leaf.remove_logically(key, &self.cmp) } else { leaf.remove(key, &self.cmp) };   // the branch is decided at compile time
// in the leaf:
if self.tombstones().len() >= TOMBS {
    let oldest = self.tombstones()[0].clone();
    self.remove(&oldest, cmp);                  // a real removal; remove_at drops the tombstone with the pair
}
self.add_tombstone(key);
```

## Notes

**Two sizes.** The leaf's `size()` counts every pair in the page; the *live* pairs are `size() - num_tombstones()`. Every structural rule (a leaf splits at `max_size`, is short below `min_size`) is about `size()`, because that is what occupies the page. A leaf full of tombstones is full, and splitting it moves tombstones around (stage 3).

**Resurrection is not an insert.** Inserting a key that is tombstoned must not use a new slot: the pair is still there. Overwrite its value, drop the tombstone, report `true`. This also means the leaf never grows from it, so it is safe even in a leaf that is one pair from splitting.

**The oldest goes first.** The buffer is a queue: when it is full, the delete that arrives pays for the one that has waited longest. Which pair is "oldest" is the first in the buffer, because `add_tombstone` appends.

**Why the iterator needs a leaf method and not a comparator.** The iterator holds no comparator; a tombstone is a copy of the key's bytes, so `is_deleted_at(slot)` compares bytes. (Stage 1 built it for this.)

## In BusTub

`GetTombstones`'s doc comment in `b_plus_tree_leaf_page.h` and the tests `TombstoneBasicTest` (the tombstones of 1, 5 and 9 appear in leaf order, an insert of the same keys leaves no tombstones, "Test tombstones are processed in the correct order": the third delete from a leaf with a buffer of 2 removes the first one for real) and the final part ("Test index iterator stays valid for 'empty' tree (and that tree isn't fully physically deleted)").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `if constexpr (NumTombs > 0)` (or a runtime check of a template constant) | `if TOMBS > 0 { ... }`: a constant condition the compiler removes |
| tombstone stored as an index into the key array | the key itself, which also works for the iterator without any index arithmetic |
| `std::erase_if` over a vector of tombstones | `Vec::remove(position)` on the decoded list, then `set_tombstones` |

**Port rule:** a generic constant used in an `if` replaces `if constexpr`; the dead branch still has to type-check.

## Learn more
- Wikipedia: [Tombstone (data store)](https://en.wikipedia.org/wiki/Tombstone_(data_store)) · [`Vec::remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.remove) · PostgreSQL's [nbtree README](https://github.com/postgres/postgres/blob/master/src/backend/access/nbtree/README) (lazy deletion of dead index entries)

## Performance

A logical delete is a lookup (`O(log n)` page reads) plus a write of at most `4 + TOMBS * K::SIZE` bytes into one leaf: no shifting of up to 500 pairs and, because the leaf's size does not change, no rebalancing. Only the delete that finds the buffer full pays for a shift, so a leaf absorbs `TOMBS` deletes for the price of one real removal each time around.

The costs move elsewhere: scans test every slot against the buffer (`TOMBS` comparisons), and leaves stay fuller than their live contents (up to `TOMBS` dead pairs each), which a later insert has to split around. Systems that use tombstones (LSM-trees, Cassandra, PostgreSQL's dead index entries) all trade the same way: cheaper deletes now, cleanup later.

**Measure it.** Delete 100,000 keys from 200,000 with `TOMBS` 0 and with 4 and compare the time; then scan the tree and compare the scan time. Count `get_writes()` per delete.

## Hints

### Look at what each operation changes

A logical delete changes one leaf's buffer (and, when full, one pair). It must not change the tree's shape, so it never splits, merges or borrows: the *physical* size stays above `min_size` unless the full-buffer removal takes the leaf below it, in which case the usual rebalance runs (stage 3).

### Do the real removal before adding the tombstone

When the buffer is full: first remove the oldest pair for real (this frees a buffer slot, because `remove_at` drops its tombstone), then `add_tombstone`. If you add first you hit the "buffer is full" panic from stage 1.

### Resurrect before you refuse

`insert` finds the key physically present. Ask whether it is tombstoned *first*: tombstoned means bring it back, live means refuse. The optimistic insert must do the same, and must not insist that the leaf has room: bringing a pair back needs none.
