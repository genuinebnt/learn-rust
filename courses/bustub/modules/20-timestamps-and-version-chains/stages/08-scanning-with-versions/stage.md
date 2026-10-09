Everything so far was preparation: read timestamps, undo logs, `collect` and `reconstruct`. This stage uses them. A **sequential scan inside a transaction** returns, for every tuple of the table, the version that transaction may see (which may be the table's, an older one rebuilt from undo logs, or none at all).

## The task

In `src/execution/executors/seq_scan_executor.rs`, `SeqScanExecutor::next` begins with a region marked `4a-08`, taken when `self.txn` is `Some((txn, txn_mgr))` (the statement runs inside a transaction: `BusTubInstance::execute_sql_txn`). Fill it in. For each tuple of the table iterator, until the batch is full or the table ends:

1. Take its rid and advance the iterator.
2. Read the tuple, its metadata and its undo link **together** with `get_tuple_and_undo_link(txn_mgr, self.table_info, rid)` (given: one page read latch, so the tuple and its link belong to the same moment).
3. `collect_undo_logs(...)` for the transaction; skip the tuple if it returns `None`.
4. `reconstruct_tuple(&self.table_info.schema, ...)`; skip it if that returns `None` (a deleted version).
5. Apply the plan's `filter_predicate` to the **reconstructed** tuple (`passes_filter`, from stage 3e-02), then set its rid and push it with its rid.

Return `true` when the batch is not empty. The non-transactional path below (module 3e) stays as it is for `execute_sql`.

## Tests

- A transaction sees tuples committed before it began and not those committed after.
- An uncommitted tuple is visible to its writer and to nobody else.
- An older version is rebuilt from the undo logs; a delete is visible only to those who began after it.
- The predicate is evaluated on the version the transaction sees, not on the table's.
- Each tuple is judged on its own chain.

## Syntax and methods

```rust
if let Some((txn, txn_mgr)) = &self.txn {
    ...
    let (meta, base_tuple, undo_link) = get_tuple_and_undo_link(txn_mgr, self.table_info, rid)?;
    let Some(logs) = collect_undo_logs(rid, &meta, &base_tuple, undo_link, txn, txn_mgr) else { continue };
    let Some(mut tuple) = reconstruct_tuple(&self.table_info.schema, &base_tuple, &meta, &logs) else { continue };
    tuple.set_rid(rid);
}
```

## Notes

**Filter after reconstruction.** The table's tuple may say `a = 20` while this transaction sees `a = 10`; `WHERE a = 10` must return the tuple, `WHERE a = 20` must not. A scan that filters the table's tuple first gives wrong answers for old snapshots (and the optimizer's merged-filter plans use exactly this scan).

**The rid does not change.** Even though the reconstructed tuple is built from bytes that were never in the table, its rid is the table's: updates and deletes (module 4b) address tuples by it.

**The Halloween guard stays.** `init` still makes an iterator that stops at the table's end when the scan begins, so a statement that inserts into the table it scans does not see its own new tuples.

**Two latches, not one.** `get_tuple_and_undo_link` holds the page's read latch only while reading the tuple and the link. Following the chain afterwards takes no page latch (the logs are in transactions, not on the page); a writer may change the table's version meanwhile, which is fine: the logs you collected describe the version you read.

## In BusTub

`seq_scan_executor.cpp` is a plain scan in Project 3; in Project 4 the scan reads versions instead: for each tuple, `GetTupleAndUndoLink`, `CollectUndoLogs`, `ReconstructTuple`, then the filter. The test `TxnScanTest.ScanTest` builds four tuples with chains across six transactions and checks `SELECT *` in transactions 0 and 1; the test file comments that the hidden cases are the other transactions' results, which the boss below fills in.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto [meta, tuple, link] = GetTupleAndUndoLink(txn_mgr, table_heap, rid);` | `let (meta, base_tuple, undo_link) = get_tuple_and_undo_link(txn_mgr, table_info, rid)?;` |
| `if (!logs.has_value()) continue;` | `let Some(logs) = ... else { continue };` |
| a `Transaction *` stored in the executor via `exec_ctx_->GetTransaction()` | `Option<(Arc<Transaction>, &TransactionManager)>` taken from the context in `new` |

**Port rule:** `if (!opt) continue;` before using the value is `let Some(v) = opt else { continue };`.

## Learn more
- [`let ... else`](https://doc.rust-lang.org/rust-by-example/flow_control/let_else.html) · [PostgreSQL: visibility of rows in MVCC](https://www.postgresql.org/docs/current/mvcc-intro.html)

## Performance

For a reader at the newest snapshot each tuple costs one page-latched read, one hash lookup for the link and one clone; no logs. An old reader additionally pays for the chain walk and the reconstruction per tuple. The page read latch is held for one tuple at a time, so writers are not blocked for long.

**Measure it.** Scan 100 000 tuples as a new reader, then as a reader at an old snapshot after every tuple was updated 10 times; compare the times.

## Hints

### Do not read the tuple and the link separately

`table_info.table.get_tuple(rid)` followed by `get_undo_link(rid)` can see a tuple that has just been updated together with the link from before (or the other way round), and then rebuild a version that never existed.

### The plan's schema is not the table's schema

Reconstruct with the table's schema (`self.table_info.schema`), but evaluate the filter against the tuple under the plan's output schema as stage 3e-02 does; for a plain scan they have the same layout.

### Advance before you can skip

Take the rid and advance the iterator first; every `continue` then moves on. Advancing at the end of the loop body loops forever on the first invisible tuple.
