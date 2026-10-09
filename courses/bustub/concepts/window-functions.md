---
title: Window functions: aggregates that keep their rows
summary: PARTITION BY, ORDER BY and the default frame: how a window aggregate or rank is computed for each row from its partition, why peers share values, and how it differs from GROUP BY.
minutes: 11
---
`group by` collapses rows: one output row per group. A **window function** computes an aggregate over a group of related rows but **keeps every row**: `select name, salary, avg(salary) over (partition by dept) from emp` lists every employee with the average of *their department* beside them.

```text
 emp:  (ann, eng, 100) (bob, eng, 120) (cat, ops, 80)
 select name, sum(salary) over (partition by dept):
 ann  eng  220      ← the sum of ann's partition
 bob  eng  220
 cat  ops   80
```

## The three parts

`f(x) over (partition by P order by O)`:

- **partition by P**: split the rows into groups with equal `P` (omitted: one partition, the whole input);
- **order by O**: order the rows *inside* each partition; for aggregates this makes the value depend on the row's position;
- **frame**: which rows of the partition count for the current row. BusTub supports only the default, `range between unbounded preceding and current row`.

## The default frame

With **no** `order by` the frame is the whole partition: every row sees the full aggregate (`sum(v) over ()` is the total on every row).

With an `order by`, the frame runs from the start of the partition **to the current row, including its peers** (rows that tie with the current row on the order-by key). So `sum(v) over (order by v)` is a *running* total, except that rows with equal `v` all show the same value: the total up to and including the last of them.

| v | `sum(v) over (order by v)` | `rank() over (order by v)` |
|---|---|---|
| 1 | 2 | 1 |
| 1 | 2 | 1 |
| 2 | 4 | 3 |
| 3 | 7 | 4 |

`rank()` is the position of the row's first peer (1-based): ties share a rank and leave gaps after them (1, 1, 3, 4).

## Computing it

1. Sort the input by `(partition keys, order keys)` so each partition is contiguous and ordered.
2. Walk each partition keeping the running aggregate; for each row emit the value for its frame; rows that are peers get the value after the *last* peer was combined (find the peer group, combine all of it, assign).
3. The output is in the sorted order (a query with a window `order by` returns rows in that order).

Several window functions in one `select` are computed independently (`sum(v) over (partition by a)` and `sum(v) over (order by b)` sort differently); BusTub requires their `order by` clauses to agree, which lets one sort serve all.

## NULLs and empty groups

Aggregates behave as in `group by`: NULL inputs are ignored; `count(*)` counts rows; `sum`/`min`/`max` of only NULLs is NULL. Partitions are never empty.

## C++ comparison

| C / C++ | Rust |
|---|---|
| group rows into `std::map<PartitionKey, std::vector<Tuple>>` | `HashMap<AggregateKey, Vec<(SortKey, Tuple)>>` (reuse the group key) |
| `std::stable_sort` the partition by the window's order | `sort_by` with the shared comparator |
| remember the peer group to assign `rank` | compare the order key with the previous row's |
| the output of the window node in input order | the output is in the sorted order; this port sorts then emits |

## In real code

### Using it: running sums and ranks with peers

```rust test
/// Rows (partition, order value). Returns, for each row in sorted order: (partition, v, running sum including peers, rank).
fn window(rows: &[(i32, i32)]) -> Vec<(i32, i32, i32, usize)> {
    let mut rows = rows.to_vec();
    rows.sort(); // by partition, then by order value
    let mut out = vec![];
    let mut i = 0;
    while i < rows.len() {
        let partition = rows[i].0;
        let mut sum = 0;
        let mut position = 0; // rows of this partition seen so far
        while i < rows.len() && rows[i].0 == partition {
            // the peer group: rows with the same order value
            let v = rows[i].1;
            let mut j = i;
            while j < rows.len() && rows[j].0 == partition && rows[j].1 == v {
                sum += rows[j].1;
                j += 1;
            }
            let rank = position + 1; // the position of the group's first row
            for _ in i..j {
                out.push((partition, v, sum, rank));
            }
            position += j - i;
            i = j;
        }
    }
    out
}

#[test]
fn peers_share_the_running_total_and_the_rank() {
    let out = window(&[(0, 1), (0, 1), (0, 2), (0, 3)]);
    assert_eq!(out, vec![(0, 1, 2, 1), (0, 1, 2, 1), (0, 2, 4, 3), (0, 3, 7, 4)]);
}

#[test]
fn partitions_start_over() {
    let out = window(&[(1, 5), (2, 7), (1, 6), (2, 7)]);
    assert_eq!(out, vec![(1, 5, 5, 1), (1, 6, 11, 2), (2, 7, 14, 1), (2, 7, 14, 1)]);
}

#[test]
fn the_row_count_is_preserved_unlike_group_by() {
    let rows: Vec<(i32, i32)> = (0..20).map(|i| (i % 3, i)).collect();
    assert_eq!(window(&rows).len(), 20);
}
```

### In the exercises

- **3g-05:** window aggregates without `order by`: the whole partition on every row, partitions found by hashing.
- **3g-05:** with `order by`: running aggregates over the default frame (peers included) and `rank()`.

### Where it is used

- **PostgreSQL**: the `WindowAgg` node over a sorted input; the frame options (`rows between`, `range between`, `exclude ...`) generalise the default.
- **Every analytic SQL engine**: DuckDB, ClickHouse, Spark, BigQuery implement `partition by / order by / frame`.
- **pandas**: `groupby(...).transform` and `expanding()` / `rank()`.
- **Time-series analysis**: running totals and moving averages are windows.
