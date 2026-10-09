BusTub's SQL tests for sorting, limits, integration queries and window functions: `p3.16-sort-limit.slt`, `p3.18-integration-1.slt`, `p3.19-integration-2.slt` and `p3.20-window-function.slt`. They sort mock tables with NULLs and strings (`__mock_table_4`), run `order by ... limit` on tables of 300 rows, compute shortest paths over a small graph with nested subqueries, joins, `group by` and `min`, and run every window function with partitions and orders. They exercise everything built so far, together.

## The task

Make `sql_sort_and_window_test` pass (`cargo test --test sql_sort_and_window_test`): four tests, one per file. (`p3.17-topn.slt`, and the `+ensure:hash_join` checks inside `p3.16`, need optimizer rules of module 3h; here they are skipped. `p3.16` still runs every query and checks its result.)

## Tests

- `sql_sort_and_window_test.rs`: 4 tests (`p3.16`, `p3.18`, `p3.19`, `p3.20`).

## Notes

**What the files cover.** `p3.16`: `order by` on a mock table with NULLs and emoji strings, `desc`/`asc`/`nulls first`/`nulls last` combinations, `order by ... limit` over tables of 300 rows with eight columns, and the sort of joined results. `p3.18`: "shortest path" queries over `__mock_graph` (self-joins of a 100-row table, `group by`, `min`). `p3.19`: the same idea iterated, using `insert into ... select`, temp tables and `order by` inside subqueries. `p3.20`: every window function, with `partition by`, `order by` and rank with ties.

**Integration, not unit.** If one of these fails and your stage tests pass, the bug is usually an interaction: a sort that is re-initialised by a join and keeps stale tuples, a limit that stops a child other operators share, a window function above a join whose output schema differs from what the expressions expect. Reproduce the failing query in the shell with `explain` first.

**Performance matters a little.** `p3.19` iterates a join and an aggregation several times over a graph of 100 edges; a nested loop with a leak (each `init` allocating pages that are never freed) turns a second into a minute.

## In BusTub

`test/sql/p3.16-sort-limit.slt`, `p3.18-integration-1.slt`, `p3.19-integration-2.slt`, `p3.20-window-function.slt`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `bustub-sqllogictest p3.20-window-function.slt` | `cargo test --test sql_sort_and_window_test p3_20` |
| `+ensure:hash_join` checked by the runner | skipped here by `run_slt_skipping(.., &["hash_join"])` |

**Port rule:** a check that depends on a later module is disabled with a named exception, not deleted.

## Learn more
- [BusTub's SQL tests](https://github.com/cmu-db/bustub/tree/master/test/sql) · [sqllogictest](https://www.sqlite.org/sqllogictest/doc/trunk/about.wiki)

## Performance

In a release build the four files run in a fraction of a second. `p3.16` sorts 300-row tables with up to eight order keys many times; each sort allocates run pages, so a missing `delete_pages` shows up as a slow, memory-hungry test rather than a wrong answer.

**Measure it.** `cargo test --release --test sql_sort_and_window_test -- --nocapture` and time each file; then try with a 16-frame buffer pool (`run_slt(file, 16)`) to see the external sort spill.

## Hints

### A sort result that differs only in ties

The expected output of an `order by` with equal keys follows BusTub's algorithm: the input order of the ties, which a stable sort with a stable merge gives. If your ties are shuffled, check the merge's tie rule and the use of `sort_by` (not `sort_unstable_by`).

### A window query that has the right numbers in the wrong order

With an `order by` the rows are output in that order; without one in input order. If the numbers are right and the order is not, the sort or the output loop is at fault, not the arithmetic.

### One file passes alone and fails after another

Each test uses a fresh database. A failure only in a sequence means state inside the file: a table you modified earlier in the same file (look at the statements above the failing line).
