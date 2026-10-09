Now the executor around the hash table. An aggregation reads **all** of its child, groups the rows, and only then produces output: the first `next` cannot answer before the last input row is seen. (This is why aggregation is a *pipeline breaker*.) It also has the rule that surprises everyone once: `select count(*) from empty_table` returns **one row** (`0`), while `select g, count(*) from empty_table group by g` returns none.

## The task

In `src/execution/executors/aggregation_executor.rs`:
- `make_aggregate_key(tuple)`: evaluate every group-by expression on the child's tuple (with the child's output schema) into an `AggregateKey`;
- `make_aggregate_value(tuple)`: evaluate every aggregate's input expression into an `AggregateValue`;
- `init`: initialise the child; empty the table; for every tuple of the child, `insert_combine` its key and value; if the table is still empty and there is **no** `GROUP BY`, add the group of the empty key with `insert_initial`; then build one **output tuple per group**, the group-by values followed by the aggregate values, with the plan's output schema, into `self.results`; reset `cursor`;
- `next`: hand out the next at-most-`batch_size` of those tuples (each with a default rid); `true` if the batch is not empty.

## Tests

- `group by` one column (with a NULL group), several columns and expressions.
- Aggregates without `group by` give one row; an empty input gives one row of initial values (`0` and NULLs) without `group by`, and no rows with it.
- `having` filters groups; 100 groups come out in more than one batch.
- `select distinct` is a `group by` with no aggregates.
- The statement can be repeated and an aggregation can feed another operator.

## Syntax and methods

```rust
self.table.insert_combine(key, &value)?;           // Result<()>
self.table.insert_initial(AggregateKey { group_bys: vec![] });
let values: Vec<Value> = key.group_bys.iter().chain(&value.aggregates).cloned().collect();
Tuple::new(&values, &self.plan.output_schema)
self.table.entries()                               // iterator of (&AggregateKey, &AggregateValue), in no particular order
```

## Notes

**Build in `init`.** BusTub builds the table in `Init` and lets `Next` walk it; so does this port. It keeps `next` a plain batch dispenser, and a second `init` rebuilds from a fresh run of the child (the child must restart, as in every operator).

**Group-by values come first.** The planner's output schema for an aggregation is "the group-by columns, then the aggregates" (`group_by`, then `agg#0`, `agg#1`, ...), and the `Projection` above reorders them for the select list. Build tuples in that order.

**The empty-input rule.** An aggregate query without `GROUP BY` always has exactly one group, even if no row arrived: SQL defines `count(*)` of nothing as 0 and `sum` of nothing as NULL. The one-group case is detected by `group_bys.is_empty()`, *not* by "the table is empty", which is also true for `GROUP BY` on empty input (no groups).

**`DISTINCT`.** The planner (given) turns `select distinct a, b` into an aggregation with group-bys `a, b` and no aggregates; your executor already does it: the output is one tuple per distinct key.

## In BusTub

`aggregation_executor.h` (`MakeAggregateKey`, `MakeAggregateValue`, the iterator over the hash table that `Next` advances), and the p3 tests: `p3.07-simple-agg.slt` ("Simple aggregation over an empty table": `select count(*) from t1;` gives `0`, `select min(v1) from t1;` gives `integer_null`).

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `SimpleAggregationHashTable::Iterator aht_iterator_` stored in the executor | collect the output tuples in `init`, walk them with a cursor (no iterator held across calls, no self-reference) |
| `std::vector<Value> values; values.insert(end, key.group_bys_...)` | `key.group_bys.iter().chain(&value.aggregates).cloned().collect()` |
| `plan_->GetGroupBys().empty()` | `self.group_bys.is_empty()` |
| `aht_.Clear()` in `Init` | `self.table.clear()` |

**Port rule:** an iterator over your own container held across calls becomes a materialised `Vec` plus an index when the borrow checker (rightly) objects.

## Learn more
- [`Iterator::chain`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.chain) · PostgreSQL [aggregate functions](https://www.postgresql.org/docs/current/functions-aggregate.html) · [`HashMap`](https://doc.rust-lang.org/std/collections/struct.HashMap.html)

## Performance

One pass over the child and a hash table with one entry per group: memory is proportional to the number of *groups*, not rows. A query with a billion distinct groups does not fit in memory; real engines then partition the input to disk (hybrid hash aggregation) or sort and stream (module 3g's sort makes the alternative possible).

**Measure it.** `select a, count(*) from t group by a` with 1,000,000 rows and 10 versus 1,000,000 distinct values of `a`, and watch the time and memory.

## Hints

### Build tuples in plan order

`key.group_bys` then `value.aggregates`. The output schema's column names are the planner's; the types decide how the tuple is laid out, so a swapped order would put a count where a string belongs.

### Do not confuse "no groups" with "no GROUP BY"

`if self.table.is_empty() && self.group_bys.is_empty()` adds the single empty-key group. With a `GROUP BY` and an empty input, leave the table empty and return `false` at once.

### The batch is a slice of the results

`results[cursor..]`, up to `batch_size`; advance the cursor; `true` if you gave out anything. The last call that finds nothing returns `false`.
