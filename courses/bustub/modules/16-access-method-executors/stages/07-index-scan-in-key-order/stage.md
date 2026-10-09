`select * from t order by a` with an index on `a` does not need a sort: the B+ tree already has the keys in order, and its leaves are linked. An **index scan** reads the whole index in key order and, for each entry, fetches the row it points to. The optimizer (given: `order by` over a scan of an indexed column becomes an `IndexScan`) uses this; this stage writes the executor.

Reading a table through an index differs from a sequential scan in two ways: rows come out in **key order**, not storage order; and the executor works from **rids** (what the index returns), so it must fetch each row itself and check that it is still alive.

## The task

In `src/execution/executors/index_scan_executor.rs` (the struct, `new` and `collect_rids` are given; `collect_rids` returns every rid of the index in key order until stage 8):
- `init`: ask `collect_rids()` for the rids to visit, keep them in `self.rids`, and start at `cursor = 0`;
- `next`: fill the batch from `self.rids[self.cursor..]`: fetch each row with `table.get_tuple(rid)?`, skip it if it is deleted or if the plan's `filter_predicate` (when there is one) is not TRUE, push the tuple and its rid; stop at `batch_size` or the end. Return `true` if the batch is not empty.

## Tests

- Rows come back in key order, though they were stored in another order; negative keys sort as numbers, not as bytes.
- Batches are at most `batch_size` long; an empty table gives nothing.
- A row flagged deleted behind the index's back is not returned.
- `explain` on `select * from t order by a` (with `set force_optimizer_starter_rule=yes`) shows an `IndexScan`, and the SQL returns sorted rows, including rows inserted after the index was created; `order by` a column with no index stays a sort.

## Syntax and methods

```rust
let rids: Vec<Rid> = self.index_info.index.scan_all();           // every rid, in key order (module 3c's Index trait)
let (meta, tuple) = self.table_info.table.get_tuple(rid)?;        // fetch a row by rid
if meta.is_deleted { continue; }
```

## Notes

**Rid to row.** The index stores `key → rid`. For each rid in order, ask the heap for the row. Two page reads per row instead of one amortised read: the price of ordered output.

**The table is the truth.** Delete (stage 5) removes index entries, but a concurrent change, a crash in the middle of a statement, or a future version of the engine may leave an entry that names a deleted row. Checking `is_deleted` makes the scan right regardless. The test flags a row *without* touching the index to prove it.

**Rids are collected up front.** `scan_all` returns a vector of rids; `init` stores it and `next` walks it. Collecting at `init` is also what makes the scan a snapshot: entries added by the same statement later are not visited.

**Why key order is not sort order, in general.** The index is ordered by its key columns compared as *values* (module 3c's comparator), so `-7 < -1 < 0`; that is the order a `SELECT ... ORDER BY a ASC` wants, and the optimizer only uses the index for ascending orders.

## In BusTub

`index_scan_executor.cpp` is a stub like the others; `index_scan_plan.h` (`IndexScanPlanNode(SchemaRef output, table_oid_t table_oid, index_oid_t index_oid, AbstractExpressionRef filter_predicate = nullptr, std::vector<AbstractExpressionRef> pred_keys = {})`) and `order_by_index_scan.cpp` (the rule: "optimize order by as index scan if there's an index on a table") are given.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `BPlusTreeIndex::GetBeginIterator()` and `++it` over `(key, rid)` | `scan_all()` returns the rids as a `Vec` |
| `table_heap_->GetTuple(rid)` returning `pair<TupleMeta, Tuple>` | `get_tuple(rid)?` → `(TupleMeta, Tuple)` |
| `dynamic_cast<BPlusTreeIndexForTwoIntegerColumn *>(index_info->index_.get())` to reach the tree | the `Index` trait hides the tree; no cast |
| `continue` in a `while` over an iterator | the same, with an index into the rid vector |

**Port rule:** if a trait offers `scan_all() -> Vec<Rid>`, an index scan is "loop over rids, fetch, skip, push".

## Learn more
- [PostgreSQL: indexes and ORDER BY](https://www.postgresql.org/docs/current/indexes-ordering.html) · [Use The Index, Luke: ORDER BY](https://use-the-index-luke.com/sql/sorting-grouping/indexed-order-by) · [B+ tree leaf chain (module 2c)](https://en.wikipedia.org/wiki/B%2B_tree)

## Performance

The index scan visits every row once, but in index order: consecutive keys are usually on *different* table pages, so each fetch is a random page access. On a table much larger than the buffer pool this is far slower than a sequential scan plus a sort *for the whole table*; for `ORDER BY ... LIMIT 10` it is far faster because it stops after ten fetches. This course's `scan_all` also materialises all rids first, which costs memory proportional to the table (a lazy iterator would not).

**Measure it.** Compare `select * from t order by a` with the index (starter rule on) and without (a sort) on 100,000 rows, then with a `limit 10` (module 3g).

## Hints

### The rid vector is the cursor

`self.cursor` indexes `self.rids`; advance it *before* deciding whether to keep the row, as in the sequential scan.

### Deleted rows and filters both `continue`

Neither is an error. Check the metadata after `get_tuple`, then evaluate the predicate (if any) on the tuple with `self.plan.output_schema`.

### Keep the index's order

Do not sort the tuples yourself and do not collect them in a map: the whole point is that the order comes from the index.
