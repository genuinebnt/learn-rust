`select * from t where v1 = 2` asks for the rows with one particular value. If `v1` has an index, the engine can find them without reading the table. Before the optimizer can use the index it must **recognise** a point lookup in the predicate: `v1 = 2`, `2 = v1`, or an `OR` of such equalities on the same column (`v1 = 4 or v1 = 7`). This stage writes the recogniser; stage 5 uses it in the rule.

## The task

In `src/optimizer/optimizer.rs`, `extract_point_lookup(predicate: &ExprRef) -> Option<(u32, Vec<ExprRef>)>`:
- an `Equal` comparison between a `ColumnValueExpression` and a `ConstantValueExpression`, in either order, gives `(the column's index, [the constant expression])`;
- an `OR` whose two sides are both point lookups **on the same column** gives that column and the keys of the left side followed by those of the right (so `4 = v1 or v1 = 7` gives `[4, 7]`; nested `OR`s work by recursion);
- anything else is `None`: another operator, column = column, constant = constant, an `OR` over different columns or with a non-lookup side, an `AND` (the rule deals with `AND` conjunct by conjunct).

## Tests

- `col = const` and `const = col`.
- An `OR` of equalities on one column gives all the keys in order, also with three alternatives.
- `>`, `!=`, `column = column`, `constant = constant` are not point lookups.
- An `OR` over different columns, or with a non-equality side, or an `AND`, is not one.
- Negative constants work; a computed key (not a constant node) is refused.

## Syntax and methods

```rust
let (a, b) = (&cmp.children()[0], &cmp.children()[1]);
col.as_any().downcast_ref::<ColumnValueExpression>()?.col_idx()
constant.as_any().downcast_ref::<ConstantValueExpression>()?
predicate.as_any().downcast_ref::<LogicExpression>() -> .logic_type == LogicType::Or
keys.extend(more_keys);
```

## Notes

**Either order.** SQL users write `v1 = 2` and `2 = v1`; both must work. A small closure that takes "the column side" and "the constant side" and returns the result, tried in both orders, avoids duplicating the code.

**Why the same column.** An index covers one column (this port's executor looks up one-column keys). `v1 = 1 or v2 = 2` needs two different indexes or a scan; recognising it as a lookup on `v1` would drop rows that match only the `v2` condition.

**Constants only.** The key goes into the plan as an expression evaluated once without a row. A column on the right (`v1 = v2`) is a join condition or a filter, not a lookup. A constant-folded `1 + 1` would also work, but needs a constant folding rule first; this recogniser takes constant *nodes*.

**NULL.** `v1 = NULL` is a "point lookup" of the NULL value as far as the shape goes. The rule of stage 5 keeps the whole predicate as a filter, which rejects every row because `NULL = x` is never true; so a lookup of the NULL key (where the index stores NULLs under an internal number) cannot return wrong rows.

## In BusTub

`seqscan_as_indexscan.cpp`: "Optimizes seq scan as index scan if there's an index on a table". The plan node `IndexScanPlanNode(output, table_oid, index_oid, filter_predicate = nullptr, pred_keys = {})` has the `pred_keys` this recogniser produces. The tests (`p3.05-index-scan-btree.slt`) use `select * from t1 where v1 = 2;` and `where 4 = v1 or v1 = 7;`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a cascade of `dynamic_cast<ComparisonExpression *>` and `nullptr` checks | `downcast_ref()?` chains inside a closure returning `Option` |
| `if (left_is_column && right_is_const) {...} else if (right_is_column && left_is_const) {...}` | `split(a, b).or_else(\|\| split(b, a))` |
| recursion with a `std::vector<AbstractExpressionRef> &keys` out-parameter | recursion returning `Option<(u32, Vec<ExprRef>)>` |
| `ConstantValueExpression::val_` read directly | keep the expression: the executor evaluates it |

**Port rule:** try both operand orders with one helper and `or_else`.

## Learn more
- [`Option::or_else`](https://doc.rust-lang.org/std/option/enum.Option.html#method.or_else) · [Use The Index, Luke: the equals operator](https://use-the-index-luke.com/sql/where-clause/the-equals-operator) · PostgreSQL [Index Cond in EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)

## Performance

Plan-time only. The payoff comes from the index scan it enables: a handful of page reads instead of a scan.

**Measure it.** See stage 5.

## Hints

### `?` inside the closure

A closure returning `Option` can use `?` on the downcasts; then `split(a, b).or_else(|| split(b, a))` tries the second order only if the first failed.

### Equal only

`v1 != 2` and `v1 > 2` are comparisons too; check `comp_type == Equal` before looking at the children.

### Keep key order

For `4 = v1 or v1 = 7` the keys are `[4, 7]`: the left alternative's keys first. The executor returns rows in key order and `p3.05` expects it.
