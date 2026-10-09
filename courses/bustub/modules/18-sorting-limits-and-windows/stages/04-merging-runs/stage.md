Pass 0 left many short sorted runs. A **merge** combines `K` sorted runs into one sorted run by repeatedly taking the smallest of the runs' current heads: one pass over all the data, `O(n)` tuple moves, with only `K` tuples (plus one output page) in memory at a time. Repeating the merge turns many runs into one: the sorted output.

## The task

In `src/execution/executors/external_merge_sort_executor.rs`, `merge_runs(&self, runs: Vec<MergeSortRun>) -> Result<MergeSortRun>`:
- keep, for every run, an iterator over it (`run.iter()`) and its current **head**: the next `(sort key, tuple)` entry (`generate_sort_key`; `None` once the run is exhausted);
- repeatedly choose the head that comes first by `self.cmp.compare(..)`; **when heads compare equal, the one from the earlier run wins**; push its tuple into a `RunBuilder` and refill that run's head;
- when no heads are left, `finish()` the builder, **free the input runs' pages** (`run.delete_pages()`, after the iterators are dropped) and return the merged run.

## Tests

- Two runs merge into one sorted run; five runs of different lengths, including an empty one, merge too.
- Equal keys come out in run order (`(1,10) (1,20) (1,30)` from three runs), which keeps the whole sort stable.
- Descending order and `NULLS FIRST` are respected.
- A merged run can be merged again (merge two merges).
- 6,000 tuples merged through a small buffer pool come out complete and ordered.

## Syntax and methods

```rust
let mut iters: Vec<_> = runs.iter().map(|r| r.iter()).collect();      // one RunIterator per run
let mut heads: Vec<Option<SortEntry>> = ...;                           // the current entry of each run, if any
best.is_none_or(|b| self.cmp.compare(h, heads[b].as_ref().unwrap()) == Ordering::Less)   // strictly smaller: ties keep the earlier run
out.push(&tuple)?;                                                      // RunBuilder
drop(iters); for run in runs { run.delete_pages(); }
```

## Notes

**The tie rule is the stability of the sort.** If two entries compare equal, whichever you output first stays first forever. Preferring the earlier run (and runs are made in input order) means equal keys come out in input order after all passes. Use a *strict* `Less` when scanning for the minimum from run 0 upward; `LessOrEqual` would prefer the later run.

**A scan of `K` heads, or a heap.** With `K = 2` (as in the factory) a linear scan of the heads is simplest; with a large `K` a `BinaryHeap` of heads brings the cost per tuple from `O(K)` to `O(log K)`. The tie rule must then include the run index as the last comparison key.

**Memory.** Each iterator holds one decoded page of its run, the builder holds one output page: `K + 1` pages, however big the runs. That is the whole point of an external sort.

**Free what you consumed.** After the merge the input runs are garbage, and their pages are still in the buffer pool or on disk. `delete_pages` hands them back; without it, a big sort leaks pages for every pass. Drop the iterators first: they borrow the runs.

## In BusTub

`external_merge_sort_executor.h`: `template <size_t K> class ExternalMergeSortExecutor`, with `K` the merge fan-in ("K-way merge"). The factory instantiates `K = 2`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::priority_queue<std::pair<SortEntry, size_t>, ..., Greater>` | a linear scan of `heads`, or `BinaryHeap<Reverse<..>>` with a wrapper that implements `Ord` |
| iterators `run.Begin()` / `run.End()` compared with `!=` | `Iterator::next` returning `Option` |
| pages freed by hand (`bpm->DeletePage`) and easy to forget | `delete_pages(self)` takes the run by value |
| a loop with several mutable iterators in a `vector` | the same: `Vec<RunIterator>` with `iters[i].next()` |

**Port rule:** a K-way merge is "peek all heads, pick the minimum, advance one"; make ties deterministic.

## Learn more
- [`Option::is_none_or`](https://doc.rust-lang.org/std/option/enum.Option.html#method.is_none_or) · [`BinaryHeap`](https://doc.rust-lang.org/std/collections/struct.BinaryHeap.html) · [External merge sort](https://en.wikipedia.org/wiki/External_sorting)

## Performance

One merge pass reads and writes every page once. With `K = 2` and `N` pages the sort takes `⌈log₂ N⌉` passes: about `2N · log₂ N` page I/Os in total. Raising `K` cuts passes: `K = 8` makes it `log₈ N`, a third. That needs `K + 1` buffer pages, which the pool must be able to pin at once.

**Measure it.** Merge two runs of 100,000 tuples and time it; then eight runs of 25,000 with a hand-written 8-way version.

## Hints

### Refill the head you took

Only the run whose head you output moves forward. Advancing every iterator is a classic bug that drops tuples.

### Compare entries, not tuples

The heads hold `(key, tuple)`: compare with `self.cmp.compare`. Computing the key again for every comparison would multiply the work by `K`.

### `delete_pages` consumes the run

It takes the run by value, so call it after you no longer need the iterators (drop them, or let them go out of scope) and only on runs that are fully merged.
