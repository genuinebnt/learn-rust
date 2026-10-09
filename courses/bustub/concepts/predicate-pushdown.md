---
title: Predicate pushdown: filtering as early as possible
summary: Why a filter belongs as close to the data as it can get, what the optimizer rewrites to put it there, and the one rule that matters: only rows for which the predicate is TRUE survive.
minutes: 6
---
`select name from people where age > 30` can run as `Projection(name) ← Filter(age > 30) ← Scan(people)`: the scan produces every row, the filter drops most of them. Or as `Projection(name) ← Scan(people, filter age > 30)`: the scan itself decides, and rows that fail never leave it. The second is **predicate pushdown**, and it matters for three reasons:

- **Fewer tuples travel.** A row that is dropped inside the scan is never copied into a batch, passed to the parent's `next`, or inspected again.
- **Cheaper rejection.** A scan can evaluate the predicate on the page's bytes before building a full tuple (BusTub builds the tuple first; real engines test the raw column).
- **It leads to an index.** A predicate `col = constant` sitting in a scan is exactly what an index lookup needs (module 3h turns it into one).

## Where it happens

The planner (given) builds the simple shape: a `Filter` over a `SeqScan`. The optimizer rule `merge filter into scan` (given) rewrites `Filter(p) ← SeqScan` into `SeqScan(filter p)`. The scan executor then has one more job: apply the predicate to each tuple. `EXPLAIN` shows the difference:

```text
Filter { predicate=(#0.0>2) }           SeqScan { table=t, filter=(#0.0>2) }
  SeqScan { table=t }
```

The same idea reaches further in real optimizers: filters move below joins (to shrink a join's inputs), below projections, and into the storage layer (Parquet's row-group statistics let a scan skip whole chunks).

## The rule that does not change: TRUE only

A predicate answers true, false or NULL (module 3a). A `WHERE` keeps a row only if the answer is **true**; the scan must too. `a != 1` on a NULL `a` is NULL, so the row is dropped, not kept. Code that treats "not false" as "keep" returns rows SQL says it must not.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `if (filter_predicate_ != nullptr && !pred->Evaluate(&tuple, schema).GetAs<bool>()) { continue; }` (a NULL's payload is garbage) | `predicate.evaluate(..)?.as_bool() == Some(true)` (NULL is `None`, never true) |
| the optimizer mutates `SeqScanPlanNode::filter_predicate_` | the optimizer builds a new `PlanKind::SeqScan { filter_predicate: Some(p), .. }` |

## In real code

### Using it: a scan that filters

```rust test
#[derive(Clone, Debug, PartialEq)]
enum V { Int(i32), Null }

/// Rows as a column of nullable ints; the predicate answers Some(true/false) or None (unknown).
fn scan(rows: &[V], predicate: Option<&dyn Fn(&V) -> Option<bool>>) -> Vec<V> {
    rows.iter()
        .filter(|row| match predicate {
            None => true,
            Some(p) => p(row) == Some(true),
        })
        .cloned()
        .collect()
}

fn gt(n: i32) -> impl Fn(&V) -> Option<bool> {
    move |v| match v { V::Int(x) => Some(*x > n), V::Null => None }
}

fn ne(n: i32) -> impl Fn(&V) -> Option<bool> {
    move |v| match v { V::Int(x) => Some(*x != n), V::Null => None }
}

#[test]
fn only_true_passes() {
    let rows = vec![V::Int(1), V::Null, V::Int(5)];
    assert_eq!(scan(&rows, Some(&gt(2))), vec![V::Int(5)]);
    assert_eq!(scan(&rows, Some(&ne(1))), vec![V::Int(5)], "NULL != 1 is unknown, which is dropped");
    assert_eq!(scan(&rows, None), rows, "no predicate keeps everything, NULLs too");
}

#[test]
fn pushing_a_filter_into_the_scan_gives_the_same_rows() {
    let rows: Vec<V> = (0..20).map(|i| if i % 5 == 0 { V::Null } else { V::Int(i) }).collect();
    let separate: Vec<V> = scan(&rows, None).into_iter().filter(|r| gt(10)(r) == Some(true)).collect();
    let pushed = scan(&rows, Some(&gt(10)));
    assert_eq!(separate, pushed);
    assert_eq!(pushed.len(), 8);
}
```

### In the exercises

- **3e-01:** `passes_filter` is the predicate check inside the scan; `explain` shows `SeqScan { table=t, filter=... }` after the optimizer's merge rule.
- **3e-04:** the index scan applies its `filter_predicate` to what the index found.
- **Module 3h:** the rule that turns a pushed predicate `col = constant` into an index scan.

### Where it is used

- **PostgreSQL**: quals attached to scan nodes (`Filter:` lines in `EXPLAIN`), and `Index Cond` for the part the index can answer.
- **SQLite**: the `WHERE` terms are assigned to the loops they can run in (`WhereLoop`) as early as possible.
- **Parquet / Iceberg / DuckDB**: min/max statistics and bloom filters let a scan skip whole row groups.
- **Distributed engines (Spark, Trino)**: pushing a filter all the way to the storage node is often the biggest win.
