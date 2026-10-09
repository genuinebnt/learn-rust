A challenge: no walkthrough, no hints, no solution. Solve it with what this module and the ones before it taught. It is extra practice and does not count towards the course.

## What to build

`insert_into_leaf` in `src/storage/index/leaf_reclaim.rs`: insert a key into one sorted leaf of at most `capacity` entries, where an entry is a key with a live flag (`false` is a tombstone). If the key is already there it becomes live; if the leaf has room it is inserted; if the leaf is **full**, tombstones are dropped to make room, and only a full leaf with no tombstones splits in two.

## Why

Tombstones make a delete cheap and make a leaf look fuller than it is. A tree that splits a leaf half-full of dead keys grows deeper for nothing and never gets the space back. The rule "reclaim, then split" is the reason a tombstone design does not bloat; the part to be careful about is that reclaiming must never lose a live key or reorder the leaf.

## The contract

- `insert_into_leaf(entries, capacity, key)` takes entries sorted by key and returns `Done(entries)` or `Split(left, right)`; both halves sorted, every key of `left` below every key of `right`.
- Existing key (live or tombstone): it ends up live; the length does not change.
- New key and `len < capacity`: inserted in order, `Done`.
- New key and `len == capacity`: tombstones are removed first; if that leaves room it is `Done`, otherwise the leaf plus the new key (`capacity + 1` entries) is split with `(capacity + 2) / 2` entries on the left.

## Invariants

These must hold after every step, whatever the input:

- Entries are sorted by key with no duplicates, in `Done` and in both halves of `Split`.
- Every live key before the call is live after it (in `Done`, or in one half), plus the new key.
- A `Split` is only returned for a full leaf with no tombstones.

## Relations between input and output

How the answer must change when the input changes. The property tests check these on random inputs:

- The live keys after equal the live keys before plus the key, whatever path was taken.
- A leaf with at least one tombstone never splits.
- `Done` never has more than `capacity` entries.

## Examples

Worked cases (the tests include them):

```text
capacity 3, [(1,live), (2,dead), (3,live)], insert 4 -> Done([(1,live), (3,live), (4,live)])
capacity 3, [(1,live), (2,live), (3,live)], insert 4 -> Split([(1),(2)], [(3),(4)])
```

## What the tests check

- Existing key revived, room available.
- Full leaf with tombstones is cleaned, not split.
- Full clean leaf splits in the middle.
- A property against a model of live keys.

## Done when

All the `s2d_c5` tests pass.
