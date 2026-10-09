A challenge: no walkthrough, no hints, no solution. It is extra practice and does not count towards the course.

## What to fix

`src/execution/ranks.rs` computes `ROW_NUMBER`, `RANK` and `DENSE_RANK` for a list of keys already sorted. `row_number` and `dense_rank` are right; `rank` is wrong whenever there are ties. Find the bug and fix it.

## Why

The three ranking functions differ only in what ties do: `ROW_NUMBER` ignores them (1,2,3,4), `RANK` gives ties the same number and **skips** (1,1,3,4), `DENSE_RANK` gives ties the same number and **does not skip** (1,1,2,3). Confusing the last two is the standard mistake, and it only shows when the data has ties.

## The contract

- Input keys are non-decreasing. `row_number[i] = i + 1`.
- `rank[i]` is `1 +` the number of rows with a strictly smaller key. `dense_rank[i]` is `1 +` the number of distinct smaller keys.

## Invariants

These must hold after every step, whatever the input:

- `rank[i] <= row_number[i]` and `dense_rank[i] <= rank[i]`.
- Equal keys have equal rank and equal dense rank.

## Relations between input and output

How the answer must change when the input changes. The property tests check these on random inputs:

- Without ties all three are equal.
- `rank` jumps by the size of the tie group; `dense_rank` always by one.
- The last `dense_rank` is the number of distinct keys.

## Examples

Worked cases (the tests include them):

```text
keys [10,20,20,30]: row_number [1,2,3,4]; rank [1,2,2,4]; dense_rank [1,2,2,3]
```

## What the tests check

- The three on data with and without ties.
- A property against the definitions.

## Done when

All the `s3g_c4` tests pass, and you can say in one sentence what the bug was.
