Tests that check not just the *answer* but the *plan*. BusTub's `.slt` files can say `query +ensure:hash_join`, and the runner then asks the engine for `explain (o)` of the same query and looks in the optimized plan for `HashJoin`, `TopN`, `IndexScan` or `NestedIndexJoin` (or the absence of a `Filter`, or a `SeqScan` where an index must not be used). A query whose result is right but whose plan is slow fails. This boss runs those files.

## The task

Make `sql_optimizer_test` pass (`cargo test --test sql_optimizer_test`): `p3.05` and `p3.06` (index scans), `p3.14` and `p3.15` (hash joins, many shapes), `p3.16` (now with its `+ensure:hash_join` checks), `p3.17` (top-N, with the heap-size check), and one test running four small files (`hash_join`, `order_by`, `nested_index_join`, `update`) that issue `explain` and the query for each of several shapes.

## Tests

- `sql_optimizer_test.rs`: 7 tests.

## Notes

**The `+ensure:` options.** `index_scan`: the plan has an `IndexScan`. `seq_scan`: no `IndexScan`, and no `Filter` after the `OPTIMIZER` heading (a filter must have been merged into the scan). `hash_join`: exactly one `HashJoin` (or a `Filter` is left: the check tolerates un-merged filters), `hash_join*2`, `hash_join*3` for the number of hash joins, `hash_join_no_filter`: all filters pushed into the join. `topn`, `topn*2`: the plan has that many `TopN` nodes, and the run uses `TopNCheckExecutor`. `index_join`, `nlj_init_check`: for module 3f.

**Reading a failure.** The runner prints the line, the SQL and a message such as `HashJoin not found`. Reproduce in the shell with `explain (o) <query>` and compare with what the test wants. The usual causes: a rule that does not recurse into a subquery or a join's inputs, a predicate shape the extraction does not accept (a condition written `b.q = a.y` instead of `a.y = b.q`), a rule applied before the one it depends on.

**What is not here.** `p3.22` (composite-key index scans, which need prefix matching), the hash and `stl_*` index types (`index.slt`, `index-scan-hash.slt`), the leaderboard queries (`TopNPerGroup`), and column pruning (`OptimizeColumnPruning`): extensions beyond this course's rules.

## In BusTub

`tools/sqllogictest/sqllogictest.cpp`, `ProcessExtraOptions`: "`instance.ExecuteSql("explain (o) " + sql, writer);` ... `if (opt == "ensure:index_scan") { if (!bustub::StringUtil::Contains(result.str(), "IndexScan")) { fmt::print("IndexScan not found\n"); return false; } }`".

## The C/C++ way

| C / C++ | Rust |
|---|---|
| the runner's `ProcessExtraOptions` | `process_extra_options` in `tests/slt/mod.rs` (given) |
| `make sqllogictest && ./bin/bustub-sqllogictest p3.14-hash-join.slt --verbose` | `cargo test --test sql_optimizer_test p3_14 -- --nocapture` |

**Port rule:** a test that asserts a property of the plan inspects the `explain` text, as the runner does.

## Learn more
- [BusTub's sqllogictest runner](https://github.com/cmu-db/bustub/blob/master/tools/sqllogictest/sqllogictest.cpp) · [PostgreSQL EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)

## Performance

These files are where the rules prove their worth: `p3.14` and `p3.15` join tables of hundreds of rows with up to four-way joins; as nested loops they take seconds, as hash joins milliseconds. `p3.17` runs top-N queries over a few hundred rows many times.

**Measure it.** `cargo test --release --test sql_optimizer_test -- --nocapture`; then comment out one rule in `Optimizer::optimize` and watch which tests fail and which just get slower.

## Hints

### `HashJoin not found` on a multi-way join

Each join level must be rewritten: check that your rule recurses (children first) and that the inner join's predicate was merged before your rule ran (the order of the pipeline).

### `IndexScan not found` for a query with an `AND`

The predicate has several conjuncts: look at each one, as in stage 5. And check the index really is on exactly that column.

### The result is right but `topn*2` fails

A second `Limit(Sort(...))` inside a subquery needs the children-first recursion; the outer rule alone only sees the outer pair.
