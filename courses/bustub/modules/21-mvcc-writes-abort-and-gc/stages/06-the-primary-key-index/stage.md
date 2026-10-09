Tables with a primary key have an index that must stay consistent with versions. Entries are **never removed** by a delete: a deleted tuple is a tombstone, and the next insert of its key finds the entry and reuses the rid. The index also arbitrates races: two transactions that insert the same new key at once, one of them must fail. And an index scan must hand each rid to the same version-reading code as the sequential scan.

## The task

In `src/execution/execution_common.rs`, `insert_mvcc`, the region marked `4b-06` (before the `4b-01` fallback): if `indexes` contains a primary-key index (`is_primary_key`):

- the key is `tuple.key_from_tuple(&table.schema, &pk.key_schema, pk.index.metadata().get_key_attrs())`;
- `pk.index.scan_key(&key)`: if an entry exists, look at the tuple at its rid (`get_tuple_and_undo_link`). **Live** (`!is_deleted`): duplicate key, fail with `write_write_conflict(txn)`. **Deleted**: reuse the rid, `modify_tuple(txn, txn_mgr, table, rid, Some(tuple))` (stage 2/3's path);
- no entry: insert the tuple (temporary timestamp), add it to the write set, then `insert_entry(&key, rid)`. If that returns `false` another transaction got the key between your lookup and now: mark your new tuple deleted (`update_tuple_meta`) and fail the same way.

In `src/execution/executors/index_scan_executor.rs`, the region marked `4b-06` at the top of `next`: when `self.txn` is `Some`, for every rid use `read_visible_version(txn, txn_mgr, table, rid)` (given: tuple + link under one latch, `collect_undo_logs`, `reconstruct_tuple`) instead of reading the heap directly; skip `None`; apply the filter predicate as before.

## Tests

- A duplicate key fails and taints; the heap does not grow. A key committed by another transaction is a duplicate too, even if the inserter cannot see it.
- Deleting a key and inserting it again reuses the tuple (the heap does not grow); an older snapshot still sees the old row.
- Point lookups by key see the version of the reader's snapshot: the old rows for a reader that began before a delete.
- Abort of an insert keeps the entry; inserting the key again reuses the tombstone.
- Delete then insert of the same key in one transaction is one tuple with one log.

## Syntax and methods

```rust
let key = tuple.key_from_tuple(&table.schema, &pk.key_schema, pk.index.metadata().get_key_attrs());
pk.index.scan_key(&key)            // Vec<Rid>: the rid(s) under the key
pk.index.insert_entry(&key, rid)   // bool: false if the key is there
read_visible_version(txn, txn_mgr, table, rid)?   // Result<Option<Tuple>>
```

## Notes

**A rid belongs to one key for life.** Entries are never removed and a key's rid is reused, so the tuple at a rid always has (or had) that key. An index scan therefore never needs to re-check the key against the reconstructed tuple.

**Why look before inserting, and still handle the failure.** The lookup tells you whether to reuse; it cannot prevent another transaction from inserting the same new key right after. `insert_entry` is atomic and returns `false` for the loser, which is the real decision. The loser's heap tuple is a harmless buried tuple (deleted, temp timestamp, in the write set so commit or abort cleans up).

**Tombstone reuse is an ordinary in-place change.** `modify_tuple` with a deleted base creates a log with `is_deleted = true` and the tombstone's timestamp (readers between the delete and now see "no tuple"), links it in front of the older chain (readers before the delete see the old row), and checks for conflicts: a tombstone whose delete was committed after your snapshot, or deleted by someone still uncommitted, is a conflict, not a reuse.

**Only the primary key.** This course's transactions maintain the primary-key index only. Other indexes are not touched by transactional writes (BusTub's own tests use primary keys); a secondary index in a transactional table can return stale rids.

## In BusTub

`txn_index_test.cpp`: `IndexInsertTest` ("`WithTxn(txn1, ExecuteTxnTainted(*bustub, _var, _txn, "INSERT INTO maintable VALUES (1, 1)"))`"), `InsertDeleteTest` (via `QueryIndex`, which runs `SELECT ... WHERE col1 = k` and needs `EnsureIndexScan`'s plan to contain `IndexScan`) and `AbortIndexTest`; all end with `TableHeapEntryNoMoreThan`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `index->ScanKey(key, &rids, txn)` | `index.scan_key(&key)` returns a `Vec<Rid>` |
| `index->InsertEntry(key, rid, txn)` returning false on a duplicate | `index.insert_entry(&key, rid)` returns `bool` |
| `GetTupleAndUndoLink` plus `CollectUndoLogs` plus `ReconstructTuple` in each executor | `read_visible_version` (given) for the index scan |

**Port rule:** when two executors need the same visible-version logic, one function serves both.

## Learn more
- [PostgreSQL: unique indexes and concurrent inserts](https://www.postgresql.org/docs/current/index-unique-checks.html) · [`Option::first`/`slice::first`](https://doc.rust-lang.org/std/primitive.slice.html#method.first)

## Performance

A transactional insert into a table with a primary key costs one index lookup (a B+ tree descent) and either one tuple append plus one index insert, or one in-place change of a tombstone. Reuse keeps both table and index from growing under delete/insert churn, which would otherwise make every scan walk dead tuples. An index scan costs one lookup per key plus one version read per rid.

**Measure it.** Delete and re-insert the same 1 000 keys 100 times and watch the heap's tuple count stay at 1 000.

## Hints

### Decide on the tuple's *state*, not on the visible version

A live tuple under the key means "taken", whether or not the inserting transaction could see it. Judging by what *you* can see would let an invisible uncommitted insert be overwritten.

### Add the write-set entry before the index insert

If the index insert fails and you bury the tuple, commit or abort must still find it. Registering after the failure path is a leak.

### The loser must fail the statement

Burying the tuple and returning `Ok` would let the statement report success with nothing inserted. Taint and return the error.
