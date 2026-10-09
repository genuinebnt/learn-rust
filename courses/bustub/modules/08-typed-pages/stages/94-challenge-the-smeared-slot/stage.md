A challenge: no walkthrough, no hints, no solution. It is extra practice and does not count towards the course.

## What to fix

`src/storage/page/shift_array.rs` inserts into and removes from the middle of a fixed array by shifting the entries after the position. It looks right, and after an insert in the middle several slots hold the same value. Find the bug and fix it.

## Why

Every sorted page does this shift, and the bug is as old as `memcpy`: copying a range onto an overlapping range of itself from the front smears the first element over the rest. In C the cure is `memmove`; in Rust it is `copy_within`, or a loop that goes the other way.

## The contract

- `insert_at(arr, len, at, value)` puts `value` at index `at`, shifting `arr[at..len]` one place right; requires `len < arr.len()` and `at <= len`; returns the new length.
- `remove_at(arr, len, at)` removes `arr[at]`, shifting the later entries one place left, and returns the new length.

## Invariants

These must hold after every step, whatever the input:

- After `insert_at`, `arr[..len + 1]` is the old `arr[..len]` with `value` inserted at `at`.
- After `remove_at`, `arr[..len - 1]` is the old `arr[..len]` without index `at`.
- Entries beyond the length are not read.

## Relations between input and output

How the answer must change when the input changes. The property tests check these on random inputs:

- `remove_at(insert_at(x))` restores the original prefix.
- Inserting at the end and at the front both work.
- The result equals `Vec::insert` / `Vec::remove` on the same prefix.

## Examples

Worked cases (the tests include them):

```text
[1,2,3,_], len 3: insert_at(1, 9) -> [1,9,2,3], len 4
[1,9,2,3], len 4: remove_at(1) -> [1,2,3], len 3
```

## What the tests check

- Insert at the front, middle and end.
- Remove from the front, middle and end.
- A property against `Vec::insert` and `Vec::remove`.

## Done when

All the `s2a_c5` tests pass, and you can say in one sentence what the bug was.
