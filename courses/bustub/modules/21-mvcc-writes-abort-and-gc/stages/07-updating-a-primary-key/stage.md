Changing a primary key in place would break the rule from stage 6: a rid belongs to one key for life. So an update that changes the key columns is executed as **a delete of the old tuple and an insert of the new one**. The order matters: `UPDATE t SET k = k + 1` over keys 1 to 4 deletes 1, 2, 3, 4 and inserts 2, 3, 4, 5. If each tuple were deleted and inserted in turn, inserting 2 would hit the live tuple with key 2 and fail. Do all the deletes first.

## The task

In `src/execution/executors/update_executor.rs`, `update_by_delete_and_insert(txn, txn_mgr, changes)` (region `4b-07`; `changes` is the list of `(rid, new tuple)` from stage 3, and `changes_primary_key` already decided this path is needed):

1. for every change, `modify_tuple(txn, txn_mgr, table, rid, None)`: delete the old tuple (its index entry stays);
2. for every change, `insert_mvcc(txn, txn_mgr, table, &self.indexes, new)`: insert the new tuple. A new key that equals a key just deleted finds the tombstone and reuses its rid; a key nobody had gets a new tuple and entry.

## Tests

- After `SET col1 = col1 + 1` the rows are under their new keys: scans and point lookups agree, and the old first key is gone.
- Shifting keys twice (`+ 1`, then `- 2`) reuses the tombstones: the heap holds the original rows plus one.
- Snapshots that began before the update still see the old keys, by scan and by lookup, and not the new one.
- An update that does not touch the key stays in place with one log per tuple.
- Updating a key to one that is live fails with a conflict and taints.

## Syntax and methods

```rust
for (rid, _) in changes { modify_tuple(txn, txn_mgr, self.table_info, *rid, None)?; }
for (_, new) in changes { insert_mvcc(txn, txn_mgr, self.table_info, &self.indexes, new)?; }
```

## Notes

**Why two loops.** Everything about the order follows from stage 6's rule: an insert onto a key whose tuple is *live* is a duplicate, and onto a key whose tuple is a tombstone is a reuse. The first loop turns all old keys into tombstones (owned by this transaction, with logs), so the second loop's inserts find tombstones for the keys that are being vacated and shifted into.

**What the logs say.** The rid under key 2 is deleted by the first loop (its log keeps the whole old row) and written again by the second loop, in the same transaction. The log is kept as the delete made it, so a reader from before the update who asks for key 2 is given the old row for key 2, which is right for that reader; a reader from after it gets the new row now stored there (the one that came from old key 1). The rid under key 1 stays a tombstone: new readers find nothing there, old readers find the old row.

**Detecting a key change.** `changes_primary_key` (given) compares the primary-key bytes of the old and the new tuple of each change. Comparing the *bytes* of the key tuples is enough because key tuples are built the same way for equal values.

**Failure half-way.** If an insert fails (a live key), the statement errors, the transaction is tainted, and abort undoes the deletes and the inserts so far through the write set.

## In BusTub

`txn_index_test.cpp`, `UpdatePrimaryKeyTest`: "`UPDATE maintable SET col1 = col1 + 1`" over keys 1 to 4, then `QueryIndex(..., std::vector<int>{1, 2, 3, 4, 5}, IntResult{{}, {2, 0}, {3, 0}, {4, 0}, {5, 0}})` (an empty row for key 1), then "`UPDATE maintable SET col1 = col1 - 2`" and keys 0 to 5. The writeup suggests handling primary-key updates as delete + insert in two passes.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a `std::vector<std::pair<RID, Tuple>>` filled by draining the child, then two `for` loops | `Vec<(Rid, Tuple)>` and two `for` loops |
| comparing `IndexKey`s with `CompareExactlyEquals` | comparing the key tuples' `data()` bytes |

**Port rule:** an operation whose steps must not interleave per row (delete all, insert all) is two loops over a collected list.

## Learn more
- [PostgreSQL: how UPDATE creates a new row version](https://www.postgresql.org/docs/current/mvcc-intro.html) (a key change there is a new tuple and new index entries) · [Halloween problem](https://en.wikipedia.org/wiki/Halloween_Problem)

## Performance

A key update does two tuple writes and an index lookup per row, instead of one tuple write; reuse of tombstones keeps heap and index from growing with each shift. For a table-wide key shift the cost is linear in the table size and the transaction's write set holds every row.

**Measure it.** Shift 10 000 keys by one twice and print the heap size: it stays at 10 001, not 20 000.

## Hints

### Do not delete and insert row by row

The second row's insert would run against a table in which the first row's delete has already happened but the second's has not. For a shift this makes the insert collide with a live tuple.

### An insert after your own delete reuses your own tombstone

`modify_tuple` sees `meta.ts == txn.temp_ts()` and a log of its own, so the log is kept as the delete made it. Check `undo_log_columns` in a test: one log, all columns.

### Read the old key from the table, not from the new tuple

`changes_primary_key` needs both keys. The old one is the table's tuple at the rid (the child's visible tuple equals it when there is no conflict).
