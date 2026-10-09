`select v, sum(v) over (partition by g) from t` returns every row of `t` and, next to it, the sum over *its group*. Unlike `group by` nothing is collapsed. The executor reads the whole input (it needs a group's total before it can emit any of its rows), splits the rows into **partitions**, computes the aggregate per partition and writes it into each row. This stage does the case without `order by`: the frame is the whole partition.

You can reuse stage 2 of module 3f: `SimpleAggregationHashTable::combine_aggregate_values` is exactly the "fold a value into a running aggregate" that a window aggregate needs.

## The task

In `src/execution/executors/window_function_executor.rs` (`init`, which reads the child, sorts if some function has an `order by`, calls the two functions below for each window function and builds the output tuples, is given; so are `aggregation_of` and the planner's rules):
- `partition_rows(&self, wf, rows) -> Result<Vec<Vec<usize>>>`: evaluate the window function's `partition_by` expressions on each row into an `AggregateKey` and group the **indexes** of the rows by key: one `Vec<usize>` per distinct key, in order of first appearance, indexes in row order. No `partition by` means one partition with every row;
- `compute_whole_partitions(&self, wf, rows, partitions) -> Result<Vec<Value>>`: for each partition fold the function's value on each row (`wf.function.evaluate(row, child_schema)`) into one running aggregate (`SimpleAggregationHashTable::new(vec![aggregation_of(wf.func_type).unwrap()])`, `generate_initial_aggregate_value`, `combine_aggregate_values`), and give **every row** of the partition the final value. Return one value per row, indexed like `rows`.

## Tests

- `count(*)`, `sum`, `min`, `max`, `count(v)` over an empty window: the same value on every row, and every row is kept.
- `partition by g`: each group gets its own aggregate; NULLs in the argument are ignored and an all-NULL group has NULL aggregates; a NULL partition key is a partition.
- Several window functions in one select are independent (`sum(v) over (partition by g)` next to `sum(v) over ()`).
- Without an `order by` the rows stay in input order.
- An empty table gives no rows; expressions in the select list work.
- The planner refuses `group by` or a plain aggregate next to a window function.

## Syntax and methods

```rust
let mut index_of: HashMap<AggregateKey, usize> = HashMap::new();       // key -> partition number
*index_of.entry(key).or_insert_with(|| { partitions.push(vec![]); partitions.len() - 1 })
partitions[slot].push(row_index);
let table = SimpleAggregationHashTable::new(vec![agg_type]);
let mut running = table.generate_initial_aggregate_value();
table.combine_aggregate_values(&mut running, &AggregateValue { aggregates: vec![value] })?;
```

## Notes

**Partitions are lists of indexes.** Computing values partition by partition and writing them back to the rows' positions is easiest when a partition is "which rows" (indexes), not a copy of them. `compute_*` returns a `Vec<Value>` with one entry per row, in row order, which `init` places in the right output column.

**Reuse, don't repeat.** A window `sum` and a group-by `sum` are the same fold: the same initial value, the same NULL rules, the same overflow error. The window executor builds a one-aggregate table just to call `combine_aggregate_values`.

**Different functions, different partitions.** Each window function has its own `partition by`, so `partition_rows` runs once per function; the rows are shared, the partitions are not.

**Keys.** The partition key is the `AggregateKey` of module 3f: NULLs form one partition, equal numbers of any width are one key.

## In BusTub

`window_plan.h` (`WindowFunctionPlanNode`: `columns_`, `window_functions_` keyed by output index; `WindowFunction { function_, type_, partition_by_, order_by_ }`), `plan_window_function.cpp` (the planner: "For window function we don't do two passes rewrites like planning normal aggregations") and `p3.20-window-function.slt` (`partition by` cases).

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::unordered_map<AggregateKey, std::vector<size_t>>` | `HashMap<AggregateKey, usize>` + `Vec<Vec<usize>>` (keeps first-appearance order) |
| a copy of the combine logic for windows | reuse `SimpleAggregationHashTable` |
| `std::map<uint32_t, WindowFunction>` ordered by output index | `BTreeMap<u32, WindowFunction>` |
| writing results into a pre-sized `std::vector<Value>` by index | `vec![Value::null(..); rows.len()]` and `out[i] = ..` |

**Port rule:** group by index, compute per group, scatter results back by index.

## Learn more
- [PostgreSQL: window function tutorial](https://www.postgresql.org/docs/current/tutorial-window.html) · [SQLite window functions](https://www.sqlite.org/windowfunctions.html) · [`HashMap::entry`](https://doc.rust-lang.org/std/collections/hash_map/struct.HashMap.html#method.entry)

## Performance

One pass to partition and one to fold: `O(rows)` per window function, `O(rows)` memory for the materialised input. Several window functions with different partitions each partition the rows again, which is why engines try to share a sort or hash among compatible windows.

**Measure it.** `sum(v) over (partition by g)` on 1,000,000 rows with 10 and with 1,000,000 distinct groups.

## Hints

### Indexes, not rows

`partitions[k]` holds row numbers. Clone nothing: the rows stay in one `Vec<Tuple>` and everything refers to positions in it.

### One value per row, in row order

`compute_whole_partitions` returns a vector as long as `rows`; `init` takes `col[r]` for row `r`. Filling it partition by partition leaves no hole because the partitions cover every index.

### count(*) over () counts NULL rows too

The function's value for `count(*)` is the constant `1` (the planner's choice); the fold handles NULLs for the other aggregates. Do not skip rows whose columns are NULL yourself.
