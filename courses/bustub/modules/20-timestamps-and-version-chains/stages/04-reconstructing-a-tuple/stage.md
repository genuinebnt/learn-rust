The table holds the newest version of a tuple. Older versions exist only as **undo logs**: each says how to turn a version into the previous one. This stage writes the function that does the turning: given the tuple in the table and a list of undo logs, produce the version they lead to.

## The task

In `src/execution/execution_common.rs`:

`reconstruct_tuple(schema, base_tuple, base_meta, undo_logs) -> Option<Tuple>`:

- start from the values of `base_tuple`; the tuple does not exist if `base_meta.is_deleted`;
- apply **every** log in `undo_logs`, front first (newest first), whatever its timestamp;
- a log with `is_deleted` makes the tuple not exist;
- any other log writes its old values into the columns where `modified_fields[i]` is true. The log's tuple holds *only* those columns, in table order, under `get_undo_log_schema(schema, &log.modified_fields)` (given): the value of table column `i` is at partial position "number of true flags before `i`";
- if the tuple does not exist when a restoring log comes (a deleted base, or after a deleting log), start from all NULLs (`null_values(schema)`, given) and then apply it: a log that brings back a tuple restores every column;
- return `None` if the tuple does not exist at the end, else `Some` of the tuple built from the values (`Tuple::new`).

## Tests

- No logs: the base tuple; a deleted base with no logs: `None`.
- A full log over a deleted base brings the tuple back.
- Partial logs, including one with no modified columns and one with non-adjacent columns, change only their columns.
- Several full logs: the last one wins.
- Delete, restore, delete, restore sequences, as in BusTub's case D.

## Syntax and methods

```rust
let mut values: Vec<Value> = (0..schema.column_count()).map(|i| base_tuple.get_value(schema, i)).collect();
let partial = get_undo_log_schema(schema, &log.modified_fields);
log.tuple.get_value(&partial, next)        // the next modified column's old value
Tuple::new(&values, schema)
```

## Notes

**Think of two moving parts.** `deleted: bool` and `values: Vec<Value>`. A deleting log sets `deleted`; a restoring log first clears it (resetting `values` to NULLs if it was set), then copies columns. At the end `deleted` decides `None` or `Some`.

**The partial index.** Walk the columns once with a counter `next` that advances only for modified columns. Looking up "position of column i in the partial schema" separately for each column costs a scan each time and is easy to get off by one.

**Why start from NULLs.** After a delete, the table's old bytes are meaningless for the next older version: a log that says "version before this was (1, 2.0, false)" is always a full log (a deletion's log restores every column), so the starting values are overwritten anyway. Starting from NULLs makes the function correct even if a test gives a partial log after a delete, instead of leaking the deleted tuple's data.

## In BusTub

`execution_common.cpp`:
```cpp
/**
 * @brief Reconstruct a tuple by applying the provided undo logs from the base tuple. All logs in the undo_logs are
 * applied regardless of the timestamp
 *
 * @param base_tuple The base tuple to start the reconstruction from.
 * @param undo_logs The list of undo logs to apply during the reconstruction, the front is applied first.
 * @return An optional tuple that represents the reconstructed tuple. If the tuple is deleted as the result, returns
 * std::nullopt.
 */
```
Its test is `TxnScanTest.TupleReconstructTest`, four scenarios A to D.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::optional<Tuple>` | `Option<Tuple>` |
| `Schema::CopySchema(schema, attrs)` for the partial schema | `get_undo_log_schema` (given) calls `Schema::copy_schema` |
| `std::vector<Value> values; ... values.emplace_back(...)` | `Vec<Value>` and `Tuple::new(&values, schema)` |

**Port rule:** a function that may produce "no tuple" returns `Option<Tuple>`, never an empty `Tuple`.

## Learn more
- [`Option`](https://doc.rust-lang.org/std/option/enum.Option.html) · [Delta storage in Wu et al.](https://www.vldb.org/pvldb/vol10/p781-Wu.pdf)

## Performance

Reconstruction is linear in (number of logs) x (columns), plus one tuple allocation at the end. It runs for every tuple of a scan, so a chain of length `k` makes the scan `k` times slower for old readers; the newest version (no logs) costs one tuple copy.

**Measure it.** Scan 20 000 rows after ten updates of every row: a reader at the newest snapshot takes about 5 ms, a reader that began before the updates takes about 37 ms, seven times as long (release mode, same laptop). A flamegraph of the old reader (see the *performance tests and measuring* article for the commands) shows where it goes: about half the samples are `malloc`/`free`, and `Schema::new` inside `get_undo_log_schema` (the partial schema built for every log of every tuple) is the largest piece of your own code after `collect_undo_logs`. Caching the partial schema per modified-fields pattern would cut it; the exercise leaves that as an optimisation.

## Hints

### Do not build a tuple after every log

Keep a `Vec<Value>` and build the `Tuple` once, at the end. Building after each log allocates and re-serialises for nothing.

### A deleting log changes the next restoring log's starting point

Handle `deleted` as part of the loop state, not as a special case after it: "delete, restore, delete, restore" is a sequence the tests walk through.

### Unmodified columns of a restore keep their value

Only the columns flagged in `modified_fields` change. A log with all flags false is legal and is a no-op.
