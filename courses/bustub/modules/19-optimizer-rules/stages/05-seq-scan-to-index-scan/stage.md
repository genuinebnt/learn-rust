The last rule: a sequential scan with a filter that is a point lookup on an **indexed column** becomes an index scan that probes the index instead of reading the table. The given rule `merge filter into scan` has already moved `where` into the scan's `filter_predicate`; your rule looks at that predicate, finds an index (`self.match_index(table_name, column)`, given: the index whose key is exactly that column), and builds the `IndexScan` plan whose executor you wrote in module 3e.

## The task

In `src/optimizer/optimizer.rs`, `optimize_seq_scan_as_index_scan(&self, plan: &PlanRef) -> PlanRef`:
- optimize the children first;
- if the node is a `SeqScan` with a filter predicate: take the whole predicate and, if it is an `AND`, each of its conjuncts as candidates (`Optimizer::conjuncts`); for the first candidate for which `extract_point_lookup` succeeds **and** an index exists on that column, return `PlanNode::new(scan's output schema, vec![], PlanKind::IndexScan { table_oid, index_oid, filter_predicate: Some(the whole predicate), pred_keys: keys })`;
- otherwise return the node unchanged.

## Tests

- `where v1 = 2` (and `3 = v1`) shows an `IndexScan`, no `SeqScan`, and returns the right row.
- `4 = v1 or v1 = 5` looks up both keys; missing keys find nothing.
- `v1 > 2`, a column without an index, `v1 = 2 or v2 = 20` (two columns) and no `where` stay sequential scans.
- `v1 = 5 and v3 = 445` uses the index and still applies the other condition (`v1 = 5 and v3 = 1` finds nothing); the indexed conjunct may come second.
- `v1 = null` finds nothing.
- `update ... where v1 = 4` and `delete ... where v1 = 4 or v1 = 5` behave like scans; a deleted key can be inserted again; an empty table with an index works.

## Syntax and methods

```rust
let mut candidates = vec![]; Optimizer::conjuncts(predicate, &mut candidates);
if let Some((col, keys)) = Self::extract_point_lookup(&candidate) {
    if let Some((index_oid, _name)) = self.match_index(table_name, col) { .. }
}
PlanKind::IndexScan { table_oid, index_oid, filter_predicate: Some(predicate.clone()), pred_keys: keys }
```

## Notes

**Keep the whole predicate as the filter.** The index finds rows by key; the executor then re-evaluates `filter_predicate` on each row (module 3e, stage 8). That makes the rule safe: other conjuncts are still checked, a `NULL` key (which no row equals) returns nothing, and a stale index entry cannot produce a wrong row.

**Using a conjunct.** `v1 = 5 and v3 = 445` is two conjuncts; the first is a point lookup on `v1` and gives the index probe; the second is checked by the filter. If you only tried the whole predicate you would miss this common shape. Try the whole predicate first (so `4 = v1 or v1 = 5` works), then each conjunct.

**Which index.** `match_index` returns an index whose key attributes are exactly `[column]`. A composite index on `(v1, v2)` does not serve `v1 = 1` in this port (a prefix scan would be the extension, and BusTub's `p3.22` tests ask for it).

**Order of rules.** This rule must run after `merge filter into scan` (the predicate has to be in the scan) and uses the same pipeline position as in BusTub's `OptimizeCustom`. And the order-by rule (given) runs before: `order by v1` on an indexed column already became an index scan without keys.

## In BusTub

`seqscan_as_indexscan.cpp` (a stub returning the plan), `optimizer.cpp` (with `force_optimizer_starter_rule` the pipeline includes this rule too), and the tests `p3.05-index-scan-btree.slt` and `p3.06-empty-table.slt`, which check `+ensure:index_scan`: the runner calls `explain (o)` and looks for "IndexScan".

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::make_shared<IndexScanPlanNode>(schema, table_oid, index_oid, predicate, pred_keys)` | `PlanNode::new(schema, vec![], PlanKind::IndexScan { .. })` |
| `catalog_.GetTableIndexes(table_name)` scanning for `GetKeyAttrs() == {col}` | `self.match_index(table_name, col)` (given) |
| mutating `seq_scan.filter_predicate_` | building a new node: plans are immutable |
| `+ensure:index_scan` as a string search in the explain output | the same check in `tests/slt/mod.rs` |

**Port rule:** the replacement carries the original predicate; correctness never depends on the index being exact.

## Learn more
- [PostgreSQL: index scans in EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html) · [Bitmap scans](https://www.postgresql.org/docs/current/indexes-bitmap-scans.html) · [Use The Index, Luke](https://use-the-index-luke.com/)

## Performance

A point lookup reads the index path (3 or 4 pages) and the table page of each match; the scan it replaces reads every page. On a million-row table that is microseconds against hundreds of milliseconds, the biggest single factor in the course's optimizer.

**Measure it.** Look up one key in a 100,000-row table with and without the index (`drop` the rule by running with `set force_optimizer_starter_rule=yes`, which has no point-lookup rule, or compare against a column without an index).

## Hints

### Rebuild with the scan's schema

The new node must have the same output schema as the old one: the parent plan's expressions refer to its columns by position.

### Do not drop the filter

Passing `filter_predicate: None` makes `v1 = 5 and v3 = 1` return the `v1 = 5` row. The tests use that case on purpose.

### Try the whole predicate, then the conjuncts

For an `AND`, `extract_point_lookup` of the whole predicate is `None`, so look at each conjunct. For an `OR` of lookups there is only one candidate: the whole predicate.
