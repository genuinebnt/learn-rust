BusTub's SQL tests for aggregation and joins: `p3.07-simple-agg.slt` through `p3.13-nested-index-join.slt`. Aggregates with NULLs and an empty table, `group by` over an integer and a string with 1,000 and 10,000 mock rows, an inner and a left join (with the nested loop init check), a four-way join, a repeated join, and the nested index join with the starter rules. They run in a fresh database through the sqllogictest runner.

## The task

Make `sql_aggregation_and_joins_test` pass (`cargo test --test sql_aggregation_and_joins_test`): seven tests, one per file. (`p3.14` and `p3.15`, the hash join tests, wait for the optimizer rule of module 3h; your hash join is tested by hand-built plans in stages 6 and 7.)

## Tests

- `sql_aggregation_and_joins_test.rs`: 7 tests (`p3.07` to `p3.13`).

## Notes

**What the files cover.** `p3.07`: `count`, `min`, `max`, `sum` with NULLs and expressions inside aggregates (`min(v1+v2-3)`, `sum(1)`, `max(233)`), and the empty table. `p3.08`/`p3.09`: `group by` and `having` over `__mock_agg_input_small`/`_big`, including grouping on columns with NULLs. `p3.10`: inner and left joins, with `+ensure:nlj_init_check`. `p3.11`: joins of 3 to 4 tables in several shapes, with parentheses and aliases. `p3.12`: the same join twice in one session. `p3.13`: the nested index join, forced with `set force_optimizer_starter_rule=yes`.

**When one fails.** The runner prints the line and a diff. Reproduce in the shell (`cargo run --bin bustub_shell`) with `explain` first: a missing operator or a different join type in the plan tells you whether the optimizer or an executor is responsible. Typical culprits: `count(v)` of a NULL, a left join that pads with the wrong types, a hash that treats NULLs as separate groups (`p3.08`'s comment: "if you see a seg fault here, it is likely because you are not currently supporting group by on columns with nulls").

**Order.** Files without `rowsort` expect an order; aggregation output order is unspecified, so the files `rowsort`. Joins output in left-tuple order.

## In BusTub

`test/sql/p3.07-simple-agg.slt` to `p3.13-nested-index-join.slt`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `bustub-sqllogictest p3.08-group-agg-1.slt` | `cargo test --test sql_aggregation_and_joins_test p3_08` |
| `+ensure:nlj_init_check` toggled through `CheckOptions` | the same options, carried by `ExecutorContext` |

**Port rule:** one test function per file; the plan checks live in the `.slt` comments, not in the test code.

## Learn more
- [sqllogictest](https://www.sqlite.org/sqllogictest/doc/trunk/about.wiki) · [BusTub's SQL tests](https://github.com/cmu-db/bustub/tree/master/test/sql)

## Performance

`p3.08` and `p3.09` push 1,000 and 10,000 rows through an aggregation, `p3.11` joins several tables of up to hundreds of rows with nested loops: milliseconds in a release build. If a file takes seconds, an executor is re-reading something it should keep (a join re-initialising the left side, an aggregation rebuilding its table per call).

**Measure it.** `cargo test --release --test sql_aggregation_and_joins_test -- --nocapture` and look at the time per file.

## Hints

### An aggregation with an unexpected extra row

The empty-input rule applied to a `GROUP BY` query. Only an aggregate query with **no** group-by expressions gets the single initial row.

### A join that is right but slow

Check `explain`: a nested loop where you expected an index join means `set force_optimizer_starter_rule=yes` did not take effect, or the index is on a different column from the join key.

### A join result with duplicated rows

The padded left row was output even though the left tuple matched; the `matched` flag must be per left tuple and reset when the next one is taken.
