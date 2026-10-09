`delete from t where a >= 3` runs as `Delete ← Filter ← SeqScan`: the scan and filter find the rows, and the delete executor removes each one. In BusTub deleting a row does not erase its bytes: it sets a flag in the tuple's metadata (module 3b: `is_deleted`), and every reader skips flagged rows. The delete executor also has to remove the row's entries from the table's indexes, or an index would keep pointing at a row that is gone.

## The task

In `src/execution/executors/delete_executor.rs` (the struct, `new` given):
- `delete_from_indexes(tuple)`: for each index of the table, build the key from the **deleted tuple's values** (`key_from_tuple`, as in stage 4) and `delete_entry(&key)`;
- `init`: forget that the count was produced and initialise the child;
- `next`: once, for every `(tuple, rid)` the child produces: mark the heap tuple deleted with `table.update_tuple_meta(&TupleMeta { ts: 0, is_deleted: true }, rid)?`, remove its index entries, count it; then answer with one tuple holding the count; every later call returns `false`.

## Tests

- `delete ... where` returns the count, the rows disappear from `select`, `delete from t` deletes everything, and deleting from an empty table or deleting nothing returns `0`.
- A deleted row's slot is still in the heap, flagged `is_deleted`.
- The index entries of deleted rows are gone (single-column indexes; others are left alone).
- A big table (3,000 rows) can be deleted completely.
- A key can be inserted again after its row was deleted.

## Syntax and methods

```rust
for (tuple, rid) in child_tuples.iter().zip(&child_rids) {            // the child sends both
    self.table_info.table.update_tuple_meta(&TupleMeta { ts: 0, is_deleted: true }, *rid)?;
    self.delete_from_indexes(tuple);
}
index.index.delete_entry(&key);                                       // removes the entry for the key, if any
```

## Notes

**Why `rid_batch` matters here.** The scan's tuples carry their rids in the second out-vector: the delete needs both, the *tuple* (to rebuild the index keys) and the *rid* (to flag the row). A child that dropped the rids (a projection that did not forward them) would make delete impossible; the planner keeps a filter directly over the scan so they arrive intact.

**Marking, not erasing.** Space is not reclaimed (no compaction in BusTub); a deleted tuple is a tombstone in the heap, the same idea as module 2d's tombstones in the B+ tree. The scan stage skips flagged rows, the index stage has to remove their entries.

**Order.** Flag the row and remove the index entries from the *old* values; both must happen for each row before you count it. If a failure stops you in the middle, the table and the indexes disagree: real systems fix that with a transaction and a log (modules 4 and 5).

**A scan that deletes.** The delete reads from a scan of the same table while it flags rows in it; the scan skips what you already flagged, so no row is deleted twice, and no insert happens, so the Halloween problem does not arise.

## In BusTub

`delete_executor.cpp`: "Yield the number of rows deleted from the table. @param[out] tuple_batch The tuple batch with one integer indicating the number of rows deleted from the table ... NOTE: DeleteExecutor::Next() returns true with the number of deleted rows produced only once." and `delete_plan.h` (the plan always has a child: `Delete ← Filter ← SeqScan`; "delete from t" gets a `Filter` with the constant TRUE).

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `table_info->table_->UpdateTupleMeta(TupleMeta{0, true}, rid)` | `table.update_tuple_meta(&TupleMeta { ts: 0, is_deleted: true }, rid)?` |
| `std::vector<RID> *rid_batch` out-parameter filled by the child | the same, as `&mut Vec<Rid>` |
| `index_info->index_->DeleteEntry(key, rid, txn)` | `index.index.delete_entry(&key)` |

**Port rule:** a metadata flag write stays a flag write; ignore nothing that returns `Result` (`?`).

## Learn more
- [`Iterator::zip`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.zip) · [Tombstones (module 2d)](https://en.wikipedia.org/wiki/Tombstone_(data_store)) · PostgreSQL [VACUUM and dead tuples](https://www.postgresql.org/docs/current/routine-vacuuming.html)

## Performance

Marking a tuple deleted is one page write; the index entry removal is a B+ tree delete. The table never shrinks: `delete from t` on a million rows leaves a million flagged slots that every later scan still walks past. Real systems reclaim the space with vacuum or compaction.

**Measure it.** Delete 99% of a 100,000-row table, then time `select * from t`: it is almost as slow as before the delete.

## Hints

### Flag first or index first?

Either order gives the same end state; just do both for every row. What you must not do is flag the row and forget the index: the `delete_removes_the_index_entries` test looks up the deleted key.

### Use the tuple you were given

The child's tuple has the row's values; build the key from it. Fetching the row again from the heap after flagging it works but doubles the page reads.

### A count of zero is still an answer

`delete from t where a != a` deletes nothing and must answer `0`, not nothing. Same shape as stage 3.
