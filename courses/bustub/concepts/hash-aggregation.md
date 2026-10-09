---
title: Hash aggregation: GROUP BY with a hash table
summary: How count, sum, min and max are computed per group with one pass over the input, the combine step that folds a row into a running value, the NULL rules, and what an empty input must produce.
minutes: 9
---
`select dept, count(*), sum(salary) from emp group by dept` produces one row per department. A **hash aggregation** does it in one pass: keep a hash table from the group's key (`dept`) to its running aggregates (`count`, `sum`); for each input row, find (or create) its group and **combine** the row's values into the running ones; when the input ends, output one row per entry.

```svg
caption: One pass over the input. Each row is hashed on its group-by key; the group's running aggregates are updated in place. After the last row the table is the answer.
<svg viewBox="0 0 760 190" role="img" aria-label="Input rows flowing into a hash table of groups with running counts and sums">
<defs><marker id="ha-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<rect class="live" x="20" y="30" width="170" height="30" rx="2"/><text class="mid fg sm" x="105" y="50">(eng, 100)</text>
<rect class="live" x="20" y="66" width="170" height="30" rx="2"/><text class="mid fg sm" x="105" y="86">(ops, 80)</text>
<rect class="live" x="20" y="102" width="170" height="30" rx="2"/><text class="mid fg sm" x="105" y="122">(eng, 120)</text>
<rect class="live" x="20" y="138" width="170" height="30" rx="2"/><text class="mid fg sm" x="105" y="158">(ops, NULL)</text>
<rect class="blue" x="400" y="40" width="320" height="40" rx="3"/><text class="mid t-b sm" x="560" y="65">eng → count 2, sum 220</text>
<rect class="blue" x="400" y="96" width="320" height="40" rx="3"/><text class="mid t-b sm" x="560" y="121">ops → count 2, sum 80  (NULL adds nothing)</text>
<path class="ln" d="M192 45 C300 45 320 55 398 58" marker-end="url(#ha-a)"/><path class="ln" d="M192 81 C300 90 320 110 398 114" marker-end="url(#ha-a)"/><path class="ln" d="M192 117 C300 100 320 70 398 62" marker-end="url(#ha-a)"/><path class="ln" d="M192 153 C300 150 320 130 398 126" marker-end="url(#ha-a)"/>
<text class="dim sm" x="300" y="22" style="text-anchor:middle">hash(key) picks the group</text>
</svg>
```

## The running value and the combine step

Every aggregate has an **initial value** and a rule to **combine** one input value into the running one:

| aggregate | initial | combine with input `x` |
|---|---|---|
| `count(*)` | 0 | `+ 1` (every row counts, NULLs included) |
| `count(x)` | NULL | if `x` is not NULL: `1` if the running value is NULL, else `+ 1` |
| `sum(x)` | NULL | if `x` is not NULL: `x` if the running value is NULL, else `+ x` |
| `min(x)` / `max(x)` | NULL | if `x` is not NULL: `x` if the running value is NULL, else the smaller / larger |

The rule behind all of them: **NULL inputs are ignored** (except by `count(*)`), and "no non-NULL input seen yet" is itself NULL. That is why `sum` over a column of NULLs is NULL, not 0, and why `count(x)` in BusTub over an empty table is also NULL: its initial value is NULL like the others' (standard SQL says 0; BusTub's tests expect NULL, so this course follows BusTub).

## Without GROUP BY

`select count(*), sum(x) from t` has no group-by key: there is exactly one group. An *empty* input still yields **one row** (the initial values: `0` and NULL), because SQL says an aggregate without grouping always returns a row. With a `GROUP BY` and no input there are no groups and so no rows. Getting this asymmetry right is the most common mistake in an aggregation executor.

## Pipeline breaker

The first `next` call must read the *whole* input before it can emit anything: the last row might change any group. So aggregation is a pipeline breaker (like sort): `init` (or the first `next`) builds the table; later calls hand out its entries in batches.

## Keys and equality

Group keys are lists of values compared as **grouping equality**: two NULLs are in the same group (unlike `NULL = NULL`, which is unknown), two equal numbers or strings are the same key. A hash table keyed on values therefore needs `Hash` and `Eq` implemented for that notion of equality (the concept *Hashing values and keys*).

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::unordered_map<AggregateKey, AggregateValue>` with a custom `std::hash` specialisation | `HashMap<AggregateKey, AggregateValue>` with `Hash`/`Eq` implemented for `AggregateKey` |
| `ht_[agg_key]` inserts a default if missing | `map.entry(key).or_insert_with(initial)` |
| `switch (agg_types_[i])` to combine | `match agg_types[i]` |
| a hash table iterator held across `Next` calls | collect the entries into a `Vec` in `init` and walk it with an index |

## In real code

### Using it: a hash aggregation over `(key, value)` rows

```rust test
use std::collections::HashMap;

#[derive(Clone, Copy, Debug, PartialEq)]
enum Agg { CountStar, Count, Sum, Min, Max }

type Row = (Option<i32>, Option<i32>); // (group key, value); None is NULL

fn initial(a: Agg) -> Option<i64> {
    match a { Agg::CountStar => Some(0), _ => None }
}

fn combine(a: Agg, running: Option<i64>, input: Option<i32>) -> Option<i64> {
    match (a, input) {
        (Agg::CountStar, _) => Some(running.unwrap_or(0) + 1),
        (_, None) => running, // NULL inputs are ignored
        (Agg::Count, Some(_)) => Some(running.unwrap_or(0) + 1),
        (Agg::Sum, Some(x)) => Some(running.unwrap_or(0) + x as i64),
        (Agg::Min, Some(x)) => Some(running.map_or(x as i64, |r| r.min(x as i64))),
        (Agg::Max, Some(x)) => Some(running.map_or(x as i64, |r| r.max(x as i64))),
    }
}

fn aggregate(rows: &[Row], aggs: &[Agg], group_by: bool) -> Vec<(Option<i32>, Vec<Option<i64>>)> {
    let mut table: HashMap<Option<i32>, Vec<Option<i64>>> = HashMap::new();
    for (key, value) in rows {
        let key = if group_by { *key } else { None };
        let running = table.entry(key).or_insert_with(|| aggs.iter().map(|a| initial(*a)).collect());
        for (slot, a) in running.iter_mut().zip(aggs) {
            *slot = combine(*a, *slot, *value);
        }
    }
    if table.is_empty() && !group_by {
        table.insert(None, aggs.iter().map(|a| initial(*a)).collect()); // an empty input still has one group
    }
    let mut out: Vec<_> = table.into_iter().collect();
    out.sort_by_key(|(k, _)| *k);
    out
}

const ALL: [Agg; 5] = [Agg::CountStar, Agg::Count, Agg::Sum, Agg::Min, Agg::Max];

#[test]
fn groups_are_folded_in_one_pass_and_nulls_are_ignored() {
    let rows = [(Some(1), Some(100)), (Some(2), Some(80)), (Some(1), Some(120)), (Some(2), None)];
    let out = aggregate(&rows, &ALL, true);
    assert_eq!(out[0], (Some(1), vec![Some(2), Some(2), Some(220), Some(100), Some(120)]));
    assert_eq!(out[1], (Some(2), vec![Some(2), Some(1), Some(80), Some(80), Some(80)]), "count(*) counts the NULL row, count(x) does not");
}

#[test]
fn a_group_of_only_nulls_has_null_aggregates() {
    let out = aggregate(&[(Some(1), None), (Some(1), None)], &ALL, true);
    assert_eq!(out, vec![(Some(1), vec![Some(2), None, None, None, None])]);
}

#[test]
fn null_keys_form_a_group_of_their_own() {
    let out = aggregate(&[(None, Some(1)), (None, Some(2)), (Some(7), Some(3))], &[Agg::Sum], true);
    assert_eq!(out, vec![(None, vec![Some(3)]), (Some(7), vec![Some(3)])]);
}

#[test]
fn an_empty_input_without_group_by_still_has_one_row_with_group_by_none() {
    assert_eq!(aggregate(&[], &ALL, false), vec![(None, vec![Some(0), None, None, None, None])]);
    assert!(aggregate(&[], &ALL, true).is_empty());
}
```

### In the exercises

- **3f-01:** `combine_aggregate_values` is `combine` above, for BusTub's five aggregate types.
- **3f-02:** the aggregation executor builds the table in `init`, handles the empty-input rule, and hands out groups in batches.

### Where it is used

- **PostgreSQL**: `HashAgg` nodes (and `GroupAggregate` over sorted input); the transition function per aggregate is the `combine` step.
- **DuckDB**: partitioned hash tables with vectorised updates.
- **Pandas / DataFrames**: `groupby(...).agg(...)` is the same algorithm.
- **MapReduce**: map emits (key, value), reduce combines per key.
