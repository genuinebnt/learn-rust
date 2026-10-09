`reconstruct_tuple` applies the logs it is given. Which logs does a particular transaction need? That depends on its read timestamp: the table's version is right for it, or one of the older versions is, or none is. This stage writes the walk down the version chain.

## The task

In `src/execution/execution_common.rs`:

`collect_undo_logs(rid, base_meta, base_tuple, undo_link, txn, txn_mgr) -> Option<Vec<UndoLog>>`:

- If the table's version is visible to `txn`: `base_meta.ts <= txn.read_ts()`, or `base_meta.ts == txn.temp_ts()` (it wrote it itself), return `Some(vec![])`.
- Otherwise follow the chain starting at `undo_link` (`None` or an invalid link is an empty chain): fetch each log with `txn_mgr.get_undo_log_optional(link)`; add it to the result; if its `ts <= txn.read_ts()` stop and return the logs; else continue with its `prev_version`.
- If the chain ends without finding a visible version, or a log cannot be fetched (its transaction was garbage collected), return `None`: the tuple did not exist for this transaction.

The result is what `reconstruct_tuple` takes. Whether the *reconstructed* tuple is a deleted one is for the caller: `None` from here means "no such version", `Some(logs)` followed by `reconstruct_tuple` returning `None` means "it existed and was deleted".

## Tests

- A tuple committed at or before the read timestamp, or written by the reader itself, needs no logs.
- A newer tuple with no chain, or another transaction's uncommitted tuple, did not exist for the reader.
- The walk stops at the first log with `ts <= read_ts` and returns the logs up to and including it.
- A chain of only newer versions gives `None`.
- A log whose owner has been collected ends the search with `None`.

## Syntax and methods

```rust
let mut link = undo_link;
while let Some(current) = link.filter(|l| l.is_valid()) {
    let log = txn_mgr.get_undo_log_optional(current)?;   // `?` on Option: return None if the log is gone
    link = Some(log.prev_version);
    ...
}
```

## Notes

**Two visibility tests, one reason.** `ts <= read_ts` covers every committed version at or before the snapshot. `ts == temp_ts` covers the reader's own writes, which carry its id. Another transaction's id is at least 2^62 and never `<= read_ts`, so it needs no third case.

**Inclusive stop.** The log whose `ts <= read_ts` is *included*: it is the log that turns the next-newer version into the version the reader may see. Stopping before it returns a version that is too new.

**The meaning of a log's `ts`.** A log's `ts` is the timestamp of the version it *restores*, not of the change that made it. In the picture of the concept article, the log at the head of a tuple written at ts 5 and previously at ts 3 has `ts = 3`.

**Garbage-collected links.** `get_undo_log_optional` returns `None` when the transaction that owned the log has been removed from the map. For a reader whose read timestamp is at or above the watermark that cannot happen (everything it needs is kept); returning `None` is the safe answer anyway.

## In BusTub

`execution_common.cpp`:
```cpp
/**
 * @brief Collects the undo logs sufficient to reconstruct the tuple w.r.t. the txn.
 * ...
 * @return An optional vector of undo logs to pass to ReconstructTuple(). std::nullopt if the tuple did not exist at the
 * time.
 */
auto CollectUndoLogs(RID rid, const TupleMeta &base_meta, const Tuple &base_tuple, std::optional<UndoLink> undo_link,
                     Transaction *txn, TransactionManager *txn_mgr) -> std::optional<std::vector<UndoLog>>
```
and its test `TxnScanTest.CollectUndoLogTest` builds ten tuples with chains of different shapes and checks what the inspecting transaction (read ts 2) gets from each.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `while (undo_link.has_value() && undo_link->IsValid())` | `while let Some(current) = link.filter(\|l\| l.is_valid())` |
| `auto log = txn_mgr->GetUndoLogOptional(*undo_link); if (!log) return std::nullopt;` | `let log = txn_mgr.get_undo_log_optional(current)?;` |
| `std::vector<UndoLog>` | `Vec<UndoLog>` (logs are cloned out of their transactions) |

**Port rule:** `if (!x) return std::nullopt;` in a function returning `optional` is `?` on an `Option` in a function returning `Option`.

## Learn more
- [The `?` operator on `Option`](https://doc.rust-lang.org/std/option/enum.Option.html#the-question-mark-operator) · [`let ... else` and `while let`](https://doc.rust-lang.org/book/ch18-01-all-the-places-for-patterns.html)

## Performance

The walk is linear in the number of versions newer than the reader's snapshot. Each step fetches a log through the manager's map (a read lock and a hash lookup) and clones the log, so a long-running old reader pays a cost proportional to how many commits it missed. Fresh readers stop at the table's version without any lookup.

**Measure it.** Build a chain of 1000 logs and time `collect_undo_logs` for a reader at the newest timestamp (immediate) and at the oldest (the full walk).

## Hints

### Check the table's version before touching the chain

Most reads end at the first test; do not take a single lock for them.

### Distinguish the two ways to return None

The chain ending early (all remaining versions are newer) and a missing log both mean "did not exist for this reader"; do not panic on either.

### A log can be newer than the reader and still be needed

The reader at 2 needs a log with `ts = 1` even though the *change* that wrote it happened at 3. Compare against the log's `ts`, not against anything about the writer.
