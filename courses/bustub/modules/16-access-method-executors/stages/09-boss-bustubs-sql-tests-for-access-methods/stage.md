BusTub's own SQL tests for project 3's first task: `p3.00-primer.slt` through `p3.04-delete.slt`. They create tables, insert 🥰-filled rows through `values` lists and `insert ... select`, scan with and without `where`, update (including `set v3 = v3 + v1`), and delete (everything, a condition, nothing). Each file runs in a fresh database through the sqllogictest runner of module 3d.

## The task

Make `sql_access_methods_test` pass (`cargo test --test sql_access_methods_test`): five tests, one per file. (`p3.05` and `p3.06` exercise index scans through optimizer rules you write in module 3h, so they come later.)

## Tests

- `sql_access_methods_test.rs`: 5 tests (`p3.00-primer`, `p3.01-seqscan`, `p3.02-insert`, `p3.03-update`, `p3.04-delete`).

## Notes

**What the files check.** `p3.00` is a scan of a built-in mock table with `rowsort`. `p3.01` scans `test_simple_seq_1` and `_2` (real tables made by the table generator) with column reorderings and expressions. `p3.02` inserts literal rows, copies tables with `insert ... select`, inserts nothing, and checks the counts. `p3.03` and `p3.04` update and delete with conditions that match some, all, or no rows, and look at the table after each.

**When one fails.** The runner prints the file, line, SQL and the first rows you got and expected. Reproduce in the shell (`cargo run --bin bustub_shell`): create the same table, run the statements up to the failing one, and `explain` the failing query. Typical culprits: a scan that returns deleted rows, an update that counts rows twice, an insert that reports batches instead of rows.

**Order matters in some files.** Queries without `rowsort` expect rows in storage order. After an `update` that stores new rows at the end, a non-`rowsort` query would see them last; the files use `rowsort` where that matters.

## In BusTub

`test/sql/p3.0*.slt`, run by `bustub-sqllogictest`. The point values in the comments (`# 4 pts`) are the Gradescope weights of the C++ course.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `make -j sqllogictest; ./bin/bustub-sqllogictest ../test/sql/p3.02-insert.slt --verbose` | `cargo test --test sql_access_methods_test p3_02_insert -- --nocapture` |
| a separate runner binary | `tests/slt/mod.rs` (given) |

**Port rule:** one test function per test file; the runner panics with the diff.

## Learn more
- [sqllogictest](https://www.sqlite.org/sqllogictest/doc/trunk/about.wiki) · [BusTub's SQL tests](https://github.com/cmu-db/bustub/tree/master/test/sql)

## Performance

The files are small; the whole boss runs in well under a second. The point of this stage is correctness; the cost of these operators shows when the tables have 100,000 rows (module 3f's tests).

**Measure it.** `cargo test --release --test sql_access_methods_test -- --nocapture` and see how long the five files take with the buffer pool at 128 frames.

## Hints

### A count that is off by a batch

If `insert` returns 20 for 25 rows, you counted calls or stopped after one batch. If an `update` count is double, it visited its own output (the scan was created with the eager iterator).

### Rows that reappear after a delete

The scan is not skipping deleted tuples (stage 1), or the delete flagged a different rid than the one the child produced.

### Everything fails at once

Run `p3_00_primer` first: if a plain scan of a mock table fails, the problem is not an access method. Then `p3_01_seqscan`, the first to read a real table.
