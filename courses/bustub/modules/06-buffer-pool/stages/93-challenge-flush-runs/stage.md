A challenge: no walkthrough, no hints, no solution. Solve it with what this module and the ones before it taught. It is extra practice and does not count towards the course.

## What to build

`flush_runs` in `src/buffer/flush_runs.rs`: given the page numbers of the dirty pages (in any order, maybe with repeats), return the writes to issue as **runs** `(first_page, length)` of consecutive pages in increasing order, with no run longer than `max_run`.

## Why

A disk writes a run of neighbouring pages almost as fast as one page. A buffer pool that flushes dirty pages one by one in the order it found them does the most seeks; sorting and merging neighbours is the cheapest big win in write-back, and a cap keeps one run from monopolising the disk.

## The contract

- Pages are deduplicated and sorted; neighbours (p, p + 1) join a run.
- No run is longer than `max_run` (at least 1); a longer stretch is split into runs of exactly `max_run` and a shorter last run.
- The result is in increasing page order.

## Invariants

These must hold after every step, whatever the input:

- The runs cover exactly the set of input pages: every page once, no page that was not given.
- Runs are disjoint and in increasing order.
- Every run has length between 1 and `max_run`.

## Relations between input and output

How the answer must change when the input changes. The property tests check these on random inputs:

- The number of runs is the minimum possible for the cap.
- Permuting or repeating the input does not change the output.
- With `max_run` at least the number of pages, the number of runs is the number of maximal consecutive stretches.

## Examples

Worked cases (the tests include them):

```text
[5,3,4,10,3] max 8 -> [(3,3), (10,1)]
[1,2,3,4,5] max 2 -> [(1,2), (3,2), (5,1)]
```

## What the tests check

- Sorting, deduplicating and merging.
- The cap, including a cap of 1.
- A property: coverage, disjointness, minimality, order independence.

## Done when

All the `s1f_c2` tests pass.
