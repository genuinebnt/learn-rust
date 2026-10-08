BusTub's own SQL tests for this part of the system, run by a port of its `sqllogictest` runner. They are the files `p0.01-lower-upper.slt`, `p0.02-function-error.slt`, `p0.03-string-scan.slt`, `baby_arithmetic.slt` and `intro.slt` from `test/sql/`: expressions on constants (`select 1 + 2 + 3 + null;`), `lower`/`upper` with right and wrong arguments, and scans of the built-in `__mock_*` tables with expressions over their columns.

## The task

Make `slt_expressions_test` pass (`cargo test --test slt_expressions_test`): five tests, one per file. Each starts a fresh database (`tests/slt/mod.rs`, given), creates the mock tables and runs the file's records in order.

## Tests

- `slt_expressions_test.rs`: 5 tests (the five `.slt` files).

## Syntax and methods

A `.slt` file is a list of records separated by blank lines:

```text
statement ok                      # must run without an error  ("statement error": must fail)
create table t(a int);

query rowsort                     # must return exactly these rows; rowsort: in any order
select a + 1 from t;
----
2
3
```

Cells are separated by one space; NULLs print as `integer_null`, `varlen_null`, ...; a decimal has six digits (`3.140000`).

## Notes

**Reading a failure.** The runner stops at the first failing record and prints `file:line`, the SQL, and the first rows you produced and expected. Start there: run the same SQL in the shell (`cargo run --bin bustub_shell`), put `explain` in front, and compare the plan with what you expect.

**What the files cover.** `baby_arithmetic.slt` is `+`, `-`, comparisons and `and`/`or` with NULLs (your three-valued logic and your overflow behaviour). The `p0.*` files are `lower`/`upper`: valid calls, the error cases that must fail at plan time, and calls over a mock table's VARCHAR columns. `intro.slt` only checks that the mock tables can be scanned with `where` and expressions.

**The mock tables.** `__mock_table_1` has `colA = 0..99` and `colB = colA * 100`; `__mock_table_3` has NULLs in `colE` on odd rows; `__mock_table_schedule` has the days of the week. They have no storage: the *mock scan* (given) makes row `i` on demand. Real tables arrive with the next module.

## In BusTub

`tools/sqllogictest/sqllogictest.cpp` and `parser.cpp` (the runner: `ResultCompare`, `ProcessExtraOptions`), and `test/sql/*.slt`. BusTub's runner compares output line by line after trimming trailing spaces, with `rowsort` sorting both sides first.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a `bustub-sqllogictest` binary run by a script | a test function per file that calls `run_slt("file.slt", 128)` |
| `exit(1)` on the first mismatch | `panic!` with the diff, which `cargo test` shows |
| `std::stringstream` + `SimpleStreamWriter` | a `String` + `SimpleStreamWriter` |

**Port rule:** a test driver binary becomes a library function plus `#[test]`s that call it.

## Learn more
- [sqllogictest format](https://www.sqlite.org/sqllogictest/doc/trunk/about.wiki) · [BusTub's runner](https://github.com/cmu-db/bustub/blob/master/tools/sqllogictest/sqllogictest.cpp)

## Performance

These files are tiny: the whole boss runs in milliseconds, and a mock table of 100 rows is scanned in microseconds. Larger `.slt` files in the next modules run thousands of rows through the same path, so keep an eye on `cargo test --release` when you get there.

**Measure it.** Time `slt_expressions_test` with `cargo test --release -- --nocapture` and see how much of it is building the 27 mock tables (each creates a table heap page).

## Hints

### If `baby_arithmetic` fails on a NULL line

The expected text `integer_null` is how a NULL INTEGER prints. `select 1 + 2 + 3 + null;` is `((1+2)+3)+NULL`: your arithmetic must produce the INTEGER NULL, not an error and not 0.

### If a `statement error` record fails with "statement should error"

Some errors must happen at **plan time**: `select upper(1);` has no rows to fail on. Check that the `StringExpression` constructor (given) is reached: your factory must call it, not build the node some other way.

### If a mock table query fails with "column not found"

Column names are case-insensitive in SQL but stored as declared: `colA` is the column's real name. The binder (given) matches case-insensitively, then the plan uses the declared name. If you changed names in your expressions, the planner cannot find them again.
