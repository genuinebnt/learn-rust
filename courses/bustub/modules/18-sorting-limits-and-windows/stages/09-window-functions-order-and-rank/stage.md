Add an `order by` to the window and the aggregate changes meaning: `sum(v) over (order by v)` is a **running total**, and `rank() over (order by v)` numbers the rows. The default frame is *from the start of the partition up to the current row and its peers*. **Peers** are the rows that tie with the current row on the order-by key; they all see the same value, because "up to the current row" includes every row that is not strictly after it.

## The task

In `src/execution/executors/window_function_executor.rs`, `compute_ordered(&self, wf, rows, keys, partitions, cmp) -> Result<Vec<Value>>` (`init` sorts the rows by the common `order by` first, so `rows`, `keys[i]` (the sort key of row `i`) and every partition's indexes are in order):
- walk each partition, one **group of peers** at a time: the rows from `start` while `cmp.compare_keys(&keys[a], &keys[b]) == Equal`;
- for an **aggregate**: fold the whole peer group into the partition's running aggregate (`combine_aggregate_values`), then give **every row of the group** the running value;
- for **rank**: give every row of the group the 1-based index of the group's *first* row in the partition (`start + 1`): ties share a rank and leave gaps (1, 1, 3, 4);
- return one value per row, indexed like `rows`.

## Tests

- Running `count(*)`, `sum`, `min`, `max` over `order by v`; the rows come out in that order.
- Peers share the value of the last peer (`1, 1, 2, 3, 3, 3` gives sums 2, 2, 4, 13, 13, 13).
- `rank()` with ties and gaps (1, 1, 3, 4 ... 8 after two duplicates).
- `partition by` with `order by` restarts in each partition.
- Descending order and NULLs (NULL smallest ascending, last descending).
- Several functions with the same `order by`; `rank` without `order by`, other frames (`rows between ...`) and window functions that order differently are refused by the planner.

## Syntax and methods

```rust
cmp.compare_keys(&keys[i], &keys[j]) == std::cmp::Ordering::Equal       // peers
while end < partition.len() && cmp.compare_keys(&keys[partition[start]], &keys[partition[end]]) == Ordering::Equal { end += 1; }
for &i in &partition[start..end] { out[i] = value.clone(); }
Value::integer(start as i32 + 1)                                        // rank
```

## Notes

**Peers, not rows.** A frame "up to the current row" would give two equal rows different totals depending on which came first, and the order of equal rows is arbitrary. SQL defines the default frame as a `RANGE`: it extends to the last row with the same key. So the unit of work is the peer *group*: fold all of it, then assign.

**Rank counts rows, not groups.** `rank` is the position of the group's first row, so after a group of two at rank 1 the next group has rank 3. (`dense_rank` would be 2; BusTub only has `rank`.)

**Sorting happens once, in `init`.** All window functions of a query have compatible `order by` clauses (the planner checks), so one stable sort serves them; each function then partitions independently (stage 8). A function with no `order by` mixed with ones that have it is refused by the planner: its frame would have to be the whole partition in a sorted stream, which BusTub does not support.

**Output order.** With an `order by` the rows come out sorted, which is what the `.slt` expectations show (no `rowsort` in the first queries of `p3.20`).

## In BusTub

`window_plan.h` (`WindowFunctionType::{CountStarAggregate, CountAggregate, SumAggregate, MinAggregate, MaxAggregate, Rank}`), `plan_window_function.cpp` (`CheckOrderByCompatible`, "BusTub currently only support window function with default window frame settings", "order by clause is mandatory for rank function") and `p3.20-window-function.slt`: "`select v1, rank() over (order by v1) from t1;` ... `# duplicate ranks`".

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::stable_sort` of the rows by the shared comparator, then loops with an index `j` scanning forward over equal keys | the same two-pointer scan over `partition[start..end]` |
| a `std::unordered_map<AggregateKey, AggregateValue>` per window function holding running values | one `SimpleAggregationHashTable` per function, one running value per partition |
| `RANK` implemented with a counter that resets per partition | `start + 1` computed from the group's position |

**Port rule:** peer-aware frames are "extend `end` while keys are equal", then assign to `start..end`.

## Learn more
- [PostgreSQL: window function frames](https://www.postgresql.org/docs/current/sql-expressions.html#SYNTAX-WINDOW-FUNCTIONS) · [SQLite window functions](https://www.sqlite.org/windowfunctions.html) · [Rank vs dense_rank](https://www.postgresql.org/docs/current/functions-window.html)

## Performance

The sort is `O(rows log rows)` (done with the stable `sort_by`, in memory); the walk is `O(rows)`. The materialised input and the keys are `O(rows)` memory: a window over a table bigger than memory would need the external sort of stage 5 underneath, which this port does not wire in.

**Measure it.** `sum(v) over (order by v)` on 100,000 rows with all-distinct and with all-equal `v`: the all-equal case is one giant peer group, one fold and one assignment.

## Hints

### Two loops: groups outside, rows inside

Outer: `while start < partition.len()`. Find `end`. Inner: fold `partition[start..end]`, then assign `partition[start..end]`. Then `start = end`. A running aggregate that you reset by mistake per group gives non-running values.

### Rank uses the group's start, not the running count

`Value::integer(start as i32 + 1)`: after a group of 2 at `start = 0`, the next group's `start` is 2, so its rank is 3 without any extra counter.

### Compare keys, not tuples

`keys[i]` is the sort key of row `i` (sorted along with the rows). Two rows are peers iff their keys compare `Equal`: for `order by v desc` that is still equality of `v`.
