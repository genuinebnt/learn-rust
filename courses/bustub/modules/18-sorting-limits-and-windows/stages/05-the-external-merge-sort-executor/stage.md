All the pieces exist; this stage assembles the executor. `init` runs the algorithm (pass 0, then merge passes until one run remains) and `next` reads the final run back, a page at a time. Because the data lives in the buffer pool and not in a `Vec`, this sort works on tables far larger than the pool: the test sorts 20,000 rows through 16 frames.

## The task

In `src/execution/executors/external_merge_sort_executor.rs` (`new`, the factory wiring and `Drop`, which frees the last run's pages, are given):
- `init`: free the pages of an earlier sort if there was one (`self.sorted.take()`); `generate_initial_runs()`; while there is more than one run, **merge them `K` at a time** into the next pass's runs (a leftover group of a single run is carried over unchanged); keep the last run in `self.sorted`; set `next_page = 0` and empty `buffered`;
- `next`: hand out the next at most `batch_size` tuples of the sorted run: `read_page(next_page)` into `self.buffered` when it is empty, `pop_front` from it; a default rid with each; `true` if the batch is not empty. No run (an empty input) means `false`.

## Tests

- `order by` ascending and descending, `order by b desc` with a different projection.
- Several keys, expressions, NULLs (`nulls first`/`nulls last`).
- 20,000 rows through a 16-frame buffer pool come out sorted.
- Equal keys keep their input order (a stable sort).
- An empty table and a single row; strings (`Apple` before `apple`); the sort can be run twice.
- Output arrives in batches of 20/20/5 for 45 rows.

## Syntax and methods

```rust
let group: Vec<_> = rest.by_ref().take(K).collect();        // up to K runs from an iterator
self.merge_runs(group)?                                      // -> MergeSortRun
self.sorted = runs.pop();                                    // Option<MergeSortRun>
self.buffered = run.read_page(self.next_page).into();        // Vec<Tuple> -> VecDeque<Tuple>
self.buffered.pop_front()
```

## Notes

**Passes.** Start with `r` runs. One pass turns them into `⌈r / K⌉` runs; repeat until one. With the `a < b` rule of stage 4 inside, every pass preserves order among equal keys. The number of passes is `⌈log_K r⌉`.

**Read-back is lazy.** The final run stays in the buffer pool (or on disk) and `next` loads one page at a time. Reading everything into a `Vec` in `init` would make the sort external only on the way in and in-memory on the way out. The executor keeps the run and a page counter instead, no borrows into itself.

**Re-initialisation.** A join may call `init` on a sort repeatedly (the inner side of a nested loop). Freeing the previous run first and rebuilding keeps the executor correct and the pool from filling with dead pages; `Drop` frees the last one when the query ends.

**When nothing needs sorting.** Zero or one run needs no merge at all: pass 0 already is the answer.

## In BusTub

`executor_factory.cpp`: `case PlanType::Sort: ... return std::make_unique<ExternalMergeSortExecutor<2>>(exec_ctx, sort_plan, std::move(child));` and the p3 tests `p3.16-sort-limit.slt` (including `select * from __mock_table_4 order by colH desc, colG asc limit 3;`) and, for scale, `__mock_external_merge_sort_input` with 100,000 rows.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a `std::vector<MergeSortRun>` replaced pass by pass | `runs = next_pass;` in a `while runs.len() > 1` loop |
| `std::optional<MergeSortRun::Iterator>` held across `Next` calls | a page counter and a small buffer of decoded tuples (nothing borrows `self`) |
| the destructor frees pages (if you wrote it) | `impl Drop` frees them |
| `template <size_t K>` | `const K: usize` |

**Port rule:** to read a paged structure back across calls without a self-borrow, keep an index and a small buffer instead of an iterator.

## Learn more
- [`Iterator::take` and `by_ref`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.by_ref) · [`VecDeque`](https://doc.rust-lang.org/std/collections/struct.VecDeque.html) · [`const` generics](https://doc.rust-lang.org/reference/items/generics.html#const-generics)

## Performance

Total I/O is `2N(1 + ⌈log_K N⌉)` page transfers for `N` pages of input. With a pool bigger than the data nothing reaches the disk and the cost is the CPU's: comparisons and tuple copies. With a small pool the cost is the disk's; that is the regime the 16-frame test puts you in.

**Measure it.** Sort 100,000 rows with pool sizes 16 and 4,096 and compare; then try `K = 2` and `K = 8` (change the factory's `::<2>`).

## Hints

### Carry over a lone run

If the number of runs in a pass is odd (with `K = 2`), the last group has one run; merging "one run" would copy it for nothing. Move it to the next pass as it is.

### Start over cleanly

Reset `next_page` and `buffered` in `init`; a stale buffer from a previous run gives a second execution extra tuples at the front.

### Keep `Drop` in mind

The executor owns the final run; if you replace `self.sorted` without deleting the old one, its pages leak for the rest of the session.
