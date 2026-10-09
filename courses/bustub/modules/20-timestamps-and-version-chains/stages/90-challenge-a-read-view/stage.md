A challenge: no walkthrough, no hints, no solution. Solve it with what this module and the ones before it taught. It is extra practice and does not count towards the course.

## What to build

`ReadView` in `src/concurrency/read_view.rs`: the snapshot rule used by InnoDB and others, based on **transaction ids** rather than commit timestamps. When a transaction begins it records the set of transactions that are active and the id the next transaction will get. `visible(writer)` says whether a version written by transaction `writer` is visible to it.

## Why

Commit timestamps need a number assigned at commit; ids are assigned at begin, so a snapshot must remember who had not finished. The rule is three lines, but each line is an easy one to get backwards: a version is visible if its writer committed before the snapshot began. In id terms, that is "older than the snapshot, and not in the active set", plus your own writes.

## The contract

- `ReadView::new(own_id, active_ids, next_id)`: `active_ids` are the ids of transactions that had begun and not finished (they may include `own_id`); `next_id` is the id that will be given to the next transaction.
- `visible(writer)` is true for `writer == own_id`; false for `writer >= next_id` (began after the snapshot) and for any writer in `active_ids`; true otherwise.

## Invariants

These must hold after every step, whatever the input:

- A writer is visible exactly when it is `own_id`, or it began before the snapshot and was not active.
- The answer for a given writer never changes during the life of the view.

## Relations between input and output

How the answer must change when the input changes. The property tests check these on random inputs:

- Adding an id to the active set can only turn a visible writer invisible.
- Raising `next_id` can only turn invisible writers (those that began after) visible, never an active one.
- `own_id` is always visible to itself.

## Examples

Worked cases (the tests include them):

```text
own 5, active [3, 5, 7], next 9: visible(2) yes, visible(3) no, visible(4) yes, visible(5) yes, visible(7) no, visible(9) no
```

## What the tests check

- Each rule on a small view.
- Edge ids: 0, own id, the next id.
- A property against a set model.

## Done when

All the `s4a_c1` tests pass.
