A challenge: no walkthrough, no hints, no solution. Solve it with what this module and the ones before it taught. It is extra practice and does not count towards the course.

## What to build

`WriteBehind` in `src/buffer/write_behind.rs`: the bookkeeping behind a background flusher. `mark_dirty(page, now)` records that a page became dirty at time `now` (the first time only: re-dirtying an already dirty page does not reset its age). `due(now, max_age)` returns the pages that have been dirty for **at least** `max_age`, oldest first. `flushed(page)` forgets a page.

## Why

A buffer pool that only writes pages when it must evict them makes a checkpoint, a crash and an eviction all slow in different ways. A background flusher that cleans pages that have been dirty too long smooths all three, and its rule is small enough to get exactly right when time is a parameter.

## The contract

- `mark_dirty` keeps the *earliest* dirty time of a page.
- `due(now, max_age)` lists pages with `now - dirty_since >= max_age`, oldest first, ties by page number.
- `flushed(page)` removes the page; true if it was dirty. `dirty_count()` and `oldest()` report the state.
- A `now` earlier than a page's dirty time counts as age 0.

## Invariants

These must hold after every step, whatever the input:

- Every dirty page has exactly one dirty-since time, the earliest it was marked since it was last flushed.
- `due` never lists a page that is not dirty.

## Relations between input and output

How the answer must change when the input changes. The property tests check these on random inputs:

- A larger `max_age` never lists more pages.
- A later `now` never lists fewer pages.
- Flushing the pages `due` returned leaves only the younger ones.

## Examples

Worked cases (the tests include them):

```text
mark 1@0, 2@5, 3@5; due(now 10, age 5) -> [1, 2, 3]; due(10, 6) -> [1]
re-mark 1@8 keeps its dirty time 0
```

## What the tests check

- Ages, ordering and ties.
- Re-dirtying and flushing.
- A property against a model with injected time.

## Done when

All the `s1f_c3` tests pass.
