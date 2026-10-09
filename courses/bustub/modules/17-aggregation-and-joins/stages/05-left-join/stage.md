`select * from a left join b on a.x = b.y` keeps **every row of `a`**. A row with matches appears once per match, as in an inner join. A row with **no** match appears once, with NULLs where `b`'s columns would be: "this department has no employees", "this customer has no orders". Left joins answer the "which ones are missing?" questions, and they are where NULL padding has to get its types right.

## The task

In `src/execution/executors/nested_loop_join_executor.rs`, `unmatched_output(&self, left: &Tuple) -> Option<Tuple>` (called by `next` when the right side is exhausted for a left tuple):
- for a **LEFT** join (`self.join_type == JoinType::Left`) and a left tuple for which `self.matched` is false: `Some` tuple of the left tuple's values (`values_of(left, self.left.output_schema())`) followed by a NULL for every column of the right side (`nulls_for(self.right.output_schema())`), laid out with the plan's output schema;
- otherwise `None`.

## Tests

- Unmatched left rows are kept with NULLs on the right; a row with a NULL key is unmatched but still output.
- The padding has the *types* of the right columns (`integer_null`, `varlen_null`).
- A left row is unmatched if no pair makes the predicate **true**, even if some answers were NULL.
- With an empty right side every left row is output once; an empty left side gives nothing.
- A left row that matches several right rows appears for each match and not as unmatched.
- Chained left joins, and the left join passes the right-side re-initialisation check too.

## Syntax and methods

```rust
let mut values = values_of(left, self.left.output_schema());       // Vec<Value>
values.extend(nulls_for(self.right.output_schema()));              // one typed NULL per right column
Some(Tuple::new(&values, &self.plan.output_schema))
```

## Notes

**"Matched" means a TRUE pair.** The flag is set only when the predicate answers true. A predicate that is NULL (a NULL join key) or false for every right tuple leaves the left row unmatched, and the left join outputs it padded. That is how `a.x = NULL` still yields the row `x = NULL` with NULLs on the right.

**Typed NULLs.** A NULL is not just "nothing": the INTEGER NULL and the VARCHAR NULL are different values (`integer_null`, `varlen_null`). `nulls_for` makes one of the right type for each column of the right child's schema; building NULLs of the wrong type corrupts the tuple.

**Where the padded row appears.** Right after the left tuple's last (non-)match, so the left join's output is grouped by left tuple. Tests use `rowsort` where order does not matter.

**WHERE vs ON.** `... left join b on a.x = b.y where b.y = 1` filters the *padded* rows away (the NULL `b.y` is not equal to 1), turning the left join into an inner join; the same condition in the `on` keeps the left rows. Joins are about `on`; the planner/optimizer (given) keeps them straight.

## In BusTub

`p3.10-simple-join.slt`: `select * from test_simple_seq_1 s1 left join test_simple_seq_2 s2 on s1.col1 + 5 = s2.col1;` expects rows `5 integer_null integer_null` ... for the left rows with no partner; and `select * from test_simple_seq_2 t2 left join t1 on t1.v1 = t2.col1;`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `ValueFactory::GetNullValueByType(col.GetType())` per right column | `Value::null(column.type_id())` via `nulls_for` |
| a `bool left_matched_` member | `matched: bool`, reset per left tuple |
| `if (plan_->GetJoinType() == JoinType::LEFT && !matched)` inside the loop | a small function returning `Option<Tuple>`, called once |

**Port rule:** a "maybe emit one more row" step becomes a function returning `Option`.

## Learn more
- [PostgreSQL: outer joins](https://www.postgresql.org/docs/current/queries-table-expressions.html#QUERIES-FROM) · [`Option`](https://doc.rust-lang.org/std/option/enum.Option.html)

## Performance

A left join costs the same as the inner join plus one extra tuple per unmatched left row; the flag is a bool. The reason left joins are slower in practice is that they cannot be reordered with other joins freely, which limits the optimizer.

**Measure it.** Compare an inner and a left join on tables where 0%, 50% and 100% of left rows match.

## Hints

### Reset `matched` with the left tuple

It belongs to the current left tuple. The `next` of stage 4 does that when it takes a new one; read the flag *before* the left tuple is dropped, which is where `unmatched_output` is called.

### NULL padding is per column

`nulls_for` returns one value per right column; do not build a single NULL or pad with `0`/empty strings.

### Do not output twice

A left tuple that matched at least once must not also appear padded. The flag, not the number of right tuples examined, decides.
