**Pass 0** of the external merge sort turns the unsorted input into the first sorted runs. The textbook version fills the whole sort memory, sorts it and writes one long run; BusTub's is the smallest version of the same idea: collect tuples until a **page** is full, sort them in memory, write them as a run of one page, and repeat. Everything after this stage merges runs; this one makes them.

## The task

In `src/execution/executors/external_merge_sort_executor.rs`, `generate_initial_runs(&mut self) -> Result<Vec<MergeSortRun>>` (`write_sorted_run(entries)`, which sorts the entries stably and writes them as a run, is given):
- initialise the child (`self.child.init()?`) and read all its batches;
- keep `(sort key, tuple)` entries (`generate_sort_key` with `self.order_bys` and the child's schema) in a buffer for as long as their serialized sizes plus the 4-byte count fit in **one page** (`serialized_size(&tuple)`, `BUSTUB_PAGE_SIZE`);
- when the next tuple would not fit (and the buffer is not empty), write the buffer as a run (`write_sorted_run`) and start a new buffer with that tuple;
- write what is left at the end; return the runs in order.

## Tests

- An empty input makes no runs; five tuples make one sorted run of one page.
- 4,000 rows make several runs; **every run is exactly one page** and sorted inside, and together they hold every row exactly once.
- A page is filled before a new run starts: 3,000 rows of 12 serialized bytes give runs of 682, 682, 682, 682 and 272 tuples (`(8192 - 4) / 12 = 682`).
- Descending order is respected and equal keys keep their input order inside a run (stability).
- The function can be called again and gives the same runs.

## Syntax and methods

```rust
let key = generate_sort_key(&tuple, &self.order_bys, &child_schema)?;     // SortKey
buffer.push((key, tuple));                                                // SortEntry = (SortKey, Tuple)
let mut used = COUNT_BYTES;  used + serialized_size(&tuple) > BUSTUB_PAGE_SIZE
runs.push(self.write_sorted_run(&mut buffer)?);                           // sorts (stable) and writes, emptying the buffer
```

## Notes

**Why one page.** A run only needs to be sorted, and the cheapest sorted unit is what fits in a page. It also means the sort needs almost no memory (one page of entries at a time) and the merge passes do all the work; a version with a bigger buffer produces fewer, longer runs and needs fewer merge passes. That is the trade-off real systems tune (`work_mem`).

**Sort entries, not tuples.** The key is computed once per tuple (stage 1). The buffer holds `(key, tuple)` so the sort can compare keys; after sorting only the tuples are written, so the run pages contain no keys.

**Stable.** `write_sorted_run` uses `sort_by`, which is stable: tuples with equal keys stay in their input order within a run. Together with the merge's tie rule (stage 4) the whole sort is stable, so `ORDER BY` returns ties in the order the child produced them: deterministic and testable.

**Counting bytes.** Use the same arithmetic as the run builder: each tuple costs `4 + data.len()` bytes and the page has `8192 - 4` bytes for tuples. If your estimate is smaller than the builder's, a "one page" run would spill onto a second page; the test `every run is one page` catches it.

## In BusTub

`external_merge_sort_executor.h`: `ExternalMergeSortExecutor<K>` with `TupleComparator cmp_`. The factory builds `ExternalMergeSortExecutor<2>` for every `Sort` plan (`executor_factory.cpp`), and `fmt_impl.cpp` notes: "A sort plan node will be converted to an external merge sort executor in Fall 2024. So `ExternalMergeSort` is returned instead of `Sort`." (that is the name `explain` prints).

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::sort(entries.begin(), entries.end(), cmp_)` with a `bool` comparator | `entries.sort_by(|a, b| cmp.compare(a, b))` |
| `std::vector<SortEntry>` of pairs | `Vec<(SortKey, Tuple)>` |
| remembering the page capacity as a constant in a comment | `BUSTUB_PAGE_SIZE` and one shared `serialized_size` |

**Port rule:** compute the sort key once and sort the pairs; the data to keep is the tuple, the key is a means.

## Learn more
- [`sort_by` is stable](https://doc.rust-lang.org/std/primitive.slice.html#method.sort_by) · [External sorting: run formation](https://en.wikipedia.org/wiki/External_sorting) · PostgreSQL [EXPLAIN ANALYZE `Sort Method`](https://www.postgresql.org/docs/current/using-explain.html)

## Performance

Pass 0 reads the input once and writes it once. The sorts are tiny (hundreds of entries), so they fit in the CPU cache and cost `n log(page size)`, not `n log n`. The number of runs is the number of pages of data, `N`, so the merge needs `⌈log_K N⌉` passes: with `K = 2` a 1,000-page sort merges ten times. A larger initial run would save several passes, which is why real systems use as much memory as they are given.

**Measure it.** Count the runs and passes for tables of 1,000 and 100,000 rows.

## Hints

### Start the new buffer with the tuple that did not fit

When the next tuple would overflow the page, write the buffer first; then the tuple goes into the new, empty buffer. Dropping it, or pushing it before the write, loses or misplaces a row.

### An oversized buffer element

A single tuple always fits an empty page unless it is larger than a page, which the table heap would not have stored; `write_sorted_run` reports it as an error through `RunBuilder`.

### The leftover run

After the loop the buffer usually holds a partial page; write it. An input that exactly fills pages leaves nothing to write.
