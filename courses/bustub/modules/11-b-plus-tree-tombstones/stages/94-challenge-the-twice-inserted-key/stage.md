A challenge: no walkthrough, no hints, no solution. It is extra practice and does not count towards the course.

## What to fix

`src/storage/index/dead_slots.rs` is a sorted list of keys in which `remove` leaves a dead slot behind. It looks right, and after a key is removed and inserted again it is sometimes reported missing and sometimes twice. Find the bug and fix it.

## Why

Tombstones keep the key in place, so a later insert of the same key has to find that slot, not add another one beside it. The bug is invisible in a test that only inserts and removes different keys, and it shows up in the counts: `len` says one thing and a scan says another.

## The contract

- `insert(key)` returns true if the key was not live; a dead slot of the same key is revived, not duplicated.
- `remove(key)` marks the slot dead; false if the key was not live.
- `contains(key)`, `len()` (live keys) and `keys()` (live keys in order).

## Invariants

These must hold after every step, whatever the input:

- The slots hold strictly increasing keys: a key has at most one slot.
- `len()` equals the number of live slots and the length of `keys()`.

## Relations between input and output

How the answer must change when the input changes. The property tests check these on random inputs:

- `insert(k)` then `remove(k)` then `insert(k)` leaves one live `k`.
- `keys()` is always sorted and duplicate-free.

## Examples

Worked cases (the tests include them):

```text
insert 5; remove 5; insert 5 -> contains 5, len 1, keys [5]
```

## What the tests check

- Revive after remove, repeatedly.
- Ordering and counts.
- A property against a `BTreeSet`.

## Done when

All the `s2d_c4` tests pass, and you can say in one sentence what the bug was.
