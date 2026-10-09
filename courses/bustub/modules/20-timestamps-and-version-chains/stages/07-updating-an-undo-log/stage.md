A transaction that changes the same tuple twice must not leave two logs. Other transactions can only ever want the version **from before the transaction began**, and one log can represent that: it has to grow to cover every column the transaction has changed. This stage writes the merge.

## The task

In `src/execution/execution_common.rs`:

`generate_updated_undo_log(schema, base_tuple: Option<&Tuple>, target_tuple: Option<&Tuple>, log: &UndoLog) -> UndoLog`:

- `base_tuple` is the tuple before *this* change (the transaction's own earlier version), `target_tuple` after it (`None` for a delete); `log` is the log the transaction already has for this tuple.
- If `log.is_deleted` ("the tuple did not exist before this transaction"), or `base_tuple` is `None` (the transaction deleted the tuple earlier, so its log already covers every column), return the log unchanged.
- Otherwise the new log restores every column the old log restores, **with the old log's values** (the version before the transaction), and also every column this change modifies that the old log did not cover (for a delete: all of them), with `base_tuple`'s values (these columns were unmodified until now, so base equals the version before the transaction).
- `ts` and `prev_version` stay as in `log`.

## Tests

- A second change to another column adds that column and keeps the first column's original value.
- A second change to a column already logged keeps its first (oldest) value.
- `ts` and `prev_version` do not change.
- A delete after a partial change makes the log cover every column.
- A "did not exist" log stays; so does a full log when the base is `None`.

## Syntax and methods

```rust
let old_partial = get_undo_log_schema(schema, &log.modified_fields);
let mut next = 0;
for i in 0..n {
    if log.modified_fields[i as usize] {
        values.push(log.tuple.get_value(&old_partial, next));   // keep the oldest value
        next += 1;
    } else if changes(i) {
        modified_fields[i as usize] = true;
        values.push(base.get_value(schema, i));                   // add: unmodified until now
    }
}
```

## Notes

**Oldest value wins.** The log answers "what was the tuple before the transaction touched it?" For a column already in the log, the value is already the oldest; the base tuple now holds the transaction's own earlier write. Overwriting the logged value with the base's would make older readers see the transaction's uncommitted data.

**Why one log suffices.** Undoing the transaction is one step for any reader: apply the single log to the table's version. Two logs from the same transaction would also be a bug in the next module's garbage collection and abort, which assume one log per tuple per transaction. BusTub's helper `CheckUndoLogNum` fails a test that creates two.

**Order of the columns.** The values must be pushed in column order, merged from the old partial tuple and the new additions in one pass, because the partial schema lists columns in table order.

**The two shortcut cases.** A log for a tuple the transaction inserted over a deleted slot says `is_deleted`; it is complete as it stands. A transaction that deleted a tuple earlier already holds a full log; changing the (re-inserted) tuple afterwards cannot add anything.

## In BusTub

`execution_common.h`/`.cpp`:
```cpp
/**
 * @brief Generate the updated undo log to replace the old one, whereas the tuple is already modified by this txn once.
 * @param base_tuple The base tuple before the update, the one retrieved from the table heap. nullptr if the tuple is
 * deleted.
 * @param target_tuple The target tuple after the update. nullptr if this is a deletion.
 * @param log The original undo log.
 * @return The updated undo log.
 */
```
Its use is checked end to end by `TxnExecutorTest.GenerateUndoLogTest` ("Update twice in a txn", "Update then delete in a txn", ...), which module 4b runs.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| copy `log.modified_fields_` into a new vector and merge by hand | `let mut modified_fields = log.modified_fields.clone();` and a single pass |
| `UndoLog{is_deleted, modified, tuple, ts, prev}` aggregate | the struct literal `UndoLog { is_deleted: false, modified_fields, tuple, ts: log.ts, prev_version: log.prev_version }` |

**Port rule:** "return the input unchanged" for a borrowed log is `log.clone()`; the caller then stores the clone back with `modify_undo_log`.

## Learn more
- [`Clone`](https://doc.rust-lang.org/std/clone/trait.Clone.html) · [Undo buffers in Neumann et al. 2015, section 3](https://db.in.tum.de/~muehlbau/papers/mvcc.pdf)

## Performance

Linear in the number of columns, one allocation for the merged tuple. It runs on every second and later write of a transaction to a tuple, so a transaction that updates the same row 1000 times pays 1000 small merges but still keeps one log.

**Measure it.** Update one row 10 000 times in a loop (generate, then update the log each time) and check the log's size stays constant after all columns have been touched.

## Hints

### Walk the columns once

You need old-log values for flagged columns and base values for newly flagged ones, in table order. A single loop with the `next` counter into the old partial tuple does both.

### Decide whether a column is *newly* modified before looking at the target

Only columns the log does not yet cover can be added. A column that is already covered keeps its logged value whatever the target says.

### Test the two shortcut cases first

`log.is_deleted` and `base_tuple == None` return early; the merge loop never has to think about them.
