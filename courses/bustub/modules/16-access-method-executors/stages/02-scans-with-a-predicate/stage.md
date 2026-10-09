A `WHERE` clause rarely wants every row. The planner (given) builds `Filter ← SeqScan`; the optimizer's `merge filter into scan` rule (given) rewrites that into a single `SeqScan` whose plan carries a `filter_predicate`, so a row that fails never leaves the scan. The scan therefore needs one more skill: **evaluate the predicate on each tuple, and keep it only if the answer is TRUE**.

## The task

In `src/execution/executors/seq_scan_executor.rs`, implement the helper `passes_filter(filter, schema, tuple) -> Result<bool>` that `next` (stage 1) already calls:
- no predicate: keep everything;
- a predicate: evaluate it on the tuple with the scan's output `schema`; keep the row only if the result is the BOOLEAN **true**. A false result, and a NULL result (unknown), are both dropped. An error from `evaluate` is passed on.

## Tests

- Only the rows for which the predicate is true come back; a predicate that nothing satisfies gives no batch.
- NULL is not true: `a != 1` drops the row where `a` is NULL.
- Batches are filled with *matching* rows, not with scanned rows (every 10th row matches, batch size 4: 4 + 4 + 2).
- A deleted row that would match is still skipped.
- Through SQL: `select * from t where a > 2` works, `explain` shows `SeqScan { table=t, filter=(#0.0>2) }`, and a `where` inside a subquery works too.

## Syntax and methods

```rust
let answer = predicate.evaluate(tuple, schema)?;     // Value, usually BOOLEAN or the BOOLEAN NULL
answer.as_bool() == Some(true)                       // true only for TRUE; None (NULL) and Some(false) are both "no"
```

## Notes

**TRUE, not "not false".** `Value::as_bool()` is `None` for a NULL. Comparing `== Some(true)` is the whole rule. `!= Some(false)` would keep the NULL rows, which is the classic bug (`WHERE a != 1` returning rows where `a` is NULL).

**The schema is the scan's output schema.** The predicate's column references (`#0.0`, ...) are positions in the scan's output; the tuple has the table's layout, and the output schema (the table's columns with qualified names) has the same offsets.

**The optimizer did the rewriting.** Nothing in the executor asks "is there a Filter above me?". By the time the scan runs, the filter is *in* the plan node; the executor just obeys it. This separation (the optimizer decides, the executor executes) is why the same scan executor can serve a plan with or without a predicate.

## In BusTub

`seq_scan_plan.h` (`SeqScanPlanNode(SchemaRef output, table_oid_t table_oid, std::string table_name, AbstractExpressionRef filter_predicate = nullptr)`) and `merge_filter_scan.cpp` (the rule: "merge filter into filter_predicate of seq scan plan node"). The explain format is `SeqScan { table={}, filter={} }`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `filter_predicate_ == nullptr` | `Option<ExprRef>` and `match` |
| `auto value = predicate->Evaluate(&tuple, schema); if (!value.IsNull() && value.GetAs<bool>())` | `value.as_bool() == Some(true)` |
| the filter executor in BusTub writes `if (filter_expr == nullptr || (!value.IsNull() && value.GetAs<bool>()))` (it dereferences first) | one `match` that cannot dereference a missing predicate |

**Port rule:** a nullable pointer to an expression is an `Option`; "not NULL and true" is `== Some(true)`.

## Learn more
- [`Option`](https://doc.rust-lang.org/std/option/enum.Option.html) · [PostgreSQL: three-valued logic and WHERE](https://www.postgresql.org/docs/current/functions-logical.html) · [Use The Index, Luke](https://use-the-index-luke.com/)

## Performance

Evaluating a predicate per row is the dominant cost of a scan of a big table: an expression tree walk and `Value` allocations. That is why real engines evaluate predicates on column vectors, and why an *index* (stage 8) that finds the few matching rows beats any amount of cleverness here.

**Measure it.** Scan 100,000 rows with `where a > 99990` (10 matches) and without a `where`: the difference between the two is the predicate's cost per row.

## Hints

### The predicate only decides; it does not change the tuple

Push the original tuple. A projection above the scan computes new values; the scan never does.

### Propagate evaluation errors

`predicate.evaluate(..)?`: an arithmetic overflow in a `WHERE` is a query error, not a row to skip.

### `explain` first

If rows are wrong, `explain (o) select ...` shows whether the filter reached the scan. If you see a separate `Filter` node the rule did not fire (a join, a projection in between), and `passes_filter` is not the problem.
