A challenge: no walkthrough, no hints, no solution. It is extra practice and does not count towards the course.

## What to fix

`LiveKeys` in `src/storage/index/live_iter.rs` walks a chain of leaves in which deleted keys are left as tombstones and yields the live keys in order. It looks right, and it has one bug. Find it and fix it.

## Why

With tombstones, a leaf may be entirely dead, and an iterator that handles tombstones inside a leaf can still mishandle a whole leaf of them. Scans that end early do not fail: they return fewer rows.

## The contract

- Yield every live key, in order, skipping tombstones, across all leaves.
- The iterator stays finished once it is finished.

## Invariants

These must hold after every step, whatever the input:

- Keys are yielded in the order they appear.
- No tombstone is ever yielded; no live key is skipped.

## Relations between input and output

How the answer must change when the input changes. The property tests check these on random inputs:

- The output equals flattening all leaves and filtering the live slots.
- Adding a leaf of only tombstones anywhere does not change the output.

## Examples

Worked cases (the tests include them):

```text
[[1, x, 3], [4, 5, x]] -> 1, 3, 4, 5
[[1], [x, x, x], [9]] -> 1, 9
```

## What the tests check

- Tombstones inside a leaf.
- A dead leaf in the middle, at the ends, several in a row.
- Empty input and empty leaves.
- A property against a flat filter.

## Done when

All the `s2d_c1` tests pass, and you can say in one sentence what the bug was.
