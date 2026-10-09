`select * from t where a = 4 or a = 7` can be answered by looking up two keys instead of reading the table. A plan can say so: an `IndexScan` with **`pred_keys`**, a list of constant expressions, one per lookup. (A BusTub optimizer rule that you write in module 3h creates such plans from `WHERE col = constant`; here you make the executor handle them.)

## The task

In `src/execution/executors/index_scan_executor.rs`, `collect_rids()` (called by `init`):
- no `pred_keys`: every rid of the index in key order (already written);
- with `pred_keys`: for each key expression **in order**: evaluate it (it is a constant: use an empty tuple and an empty schema), make a one-column **key tuple** with the index's key schema (`Tuple::new(&[value], &self.index_info.key_schema)`), look it up with `index.scan_key(&key)`, and append the rids found.

`next` (stage 7) then fetches each row, skips deleted ones and applies the plan's `filter_predicate`, so a probe can be combined with further conditions.

## Tests

- A key finds its row; a missing key finds nothing.
- Several keys are looked up in the order given, not in index order (`[4, 1, 9, 3]` returns rows 4, 1, 3).
- A row deleted through SQL is not found (the delete removed its index entry).
- The filter predicate applies to what the index found (key 2 is found but fails `b > 25`); a filter on a full ordered scan keeps the order.
- An update made earlier is visible to the lookup; 50 keys against batches of 20 give 20 + 20 + 10.

## Syntax and methods

```rust
let value = key_expr.evaluate(&Tuple::empty(), &Schema::new(vec![]))?;       // a constant needs no row
let key = Tuple::new(&[value], &self.index_info.key_schema);                  // the index's one-column key layout
rids.extend(self.index_info.index.scan_key(&key));                            // Vec<Rid>: none or one
```

## Notes

**Keys are expressions.** `pred_keys` are `AbstractExpression`s so the plan can say `a = 4` (a `ConstantValueExpression`) or, for a join (module 3f), `a = outer.x` (a column of the outer row). For a scan they must be constants; evaluating them against an empty tuple works because a constant ignores its tuple.

**One column only.** The key tuple has one value, so this executor handles single-column indexes. A composite index would need a key per column, and a prefix match for `where v1 = 1` on an index over `(v1, v2)`: a natural extension, left for the reader.

**Order of results.** Point lookups return rows in the order of the *keys*, not of the index: the caller asked for `4` before `1`. Duplicate keys are looked up twice and return the row twice; deduplicating `a = 4 or a = 4` is the optimizer's business.

**The probe is a hint, not a proof.** Row found by the index? Still check `is_deleted` and the filter. For `where a = 2 and b > 25` the plan has `pred_keys = [2]` and a filter on `b`; the executor does both.

## In BusTub

`index_scan_plan.h`: `pred_keys_` "the pre-evaluated predicate keys; if empty, this is a full index scan (for ORDER BY)". The explain format `IndexScan { index_oid={}, filter={} }` is what the test runner's `+ensure:index_scan` looks for in `explain (o) ...`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `Tuple key(std::vector<Value>{val}, index_info->index_->GetKeySchema()); index->ScanKey(key, &result, txn);` | `Tuple::new(&[value], &index_info.key_schema)`; `index.scan_key(&key)` returns the rids |
| `dynamic_cast<ConstantValueExpression *>(key.get())->val_` | `key_expr.evaluate(&empty, &no_schema)?` works for any expression |
| a vector filled by an out-parameter | `extend` with a returned `Vec` |

**Port rule:** evaluate an expression with the generic `evaluate` rather than downcasting to the constant it happens to be; it keeps working when the key becomes a column.

## Learn more
- [PostgreSQL: index scans in EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html) · [SQLite: SEARCH ... USING INDEX](https://www.sqlite.org/queryplanner.html) · [`Vec::extend`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.extend)

## Performance

A point lookup costs the tree's height in page reads (3 or 4 for millions of rows) plus one table page: microseconds, against milliseconds or seconds for a scan. This is the difference between an application that scales and one that does not. A lookup per key is still a lookup per key: a thousand keys is a thousand probes; at some point a scan is cheaper.

**Measure it.** Build an index on a 100,000-row table and time 1,000 lookups through `where a = k` with the index (starter rule on) and without.

## Hints

### Evaluate every key, in order

Do not sort or deduplicate `pred_keys`: the tests pin the order. Evaluate each, look it up, append.

### An empty `pred_keys` is not "no keys found"

Empty means *full ordered scan* (stage 7); a plan with keys that all miss returns nothing. Branch on `pred_keys.is_empty()`, not on the lookups' results.

### The key tuple must use the key schema

`Tuple::new(&[value], &self.index_info.key_schema)`, not the table's schema: the comparator reads the key at the key schema's offsets.
