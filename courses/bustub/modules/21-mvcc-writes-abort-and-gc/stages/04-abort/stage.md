A transaction that fails, or whose client changes its mind, must leave no trace. Because it wrote the table in place, the traces are in the table: tuples with its temporary timestamp, new tuples, tombstones. In stage 3 you kept an undo log for every tuple it changed; abort is where that log pays off a second time.

## The task

In `src/concurrency/transaction_manager.rs`, `abort(txn)`, the region marked `4b-04` (the state check above and the state change below are given from stage 4a-03): for every `(table oid, rids)` in `txn.write_sets()`, for every rid, under the page's write latch (`table.table.with_page_mut(rid, ..)`):

- if the tuple's head undo link is **this transaction's** (`link.prev_txn == txn.id()`): take that log, rebuild the old version with `reconstruct_tuple(schema, &tuple, &meta, &[log])`. Write it back with `TupleMeta { ts: log.ts, is_deleted: false }`; if the log says the tuple did not exist (the result is `None`) write the tuple as it is, with `is_deleted: true` and `ts: log.ts`. Then set the link to `log.prev_version` (no link if it is invalid) with `update_undo_link`;
- otherwise the transaction created the tuple: nobody saw it. Make it a tombstone with `ts: 0`.

## Tests

- Aborting an insert leaves no visible rows.
- Aborting an update restores values, timestamps (the committed timestamp is back) and the chain (the head link is gone).
- Aborting a delete brings the rows back.
- Several changes (update, update, delete) are undone by the one log; a reader that began before sees the same throughout.
- A tainted transaction is aborted like any other, and a tuple it had locked can be written by others afterwards.

## Syntax and methods

```rust
table.table.with_page_mut(rid, |page| -> Result<()> {
    let (meta, tuple) = page.get_tuple(rid)?;
    ...
    page.update_tuple_in_place_unsafe(&new_meta, &new_tuple, rid)?;
    self.update_undo_link(rid, Some(log.prev_version).filter(|l| l.is_valid()), None);
    Ok(())
})?;
```

## Notes

**Why under the latch.** Another transaction's `get_tuple_and_undo_link` reads the tuple and the link under the page's *read* latch. If abort wrote them one at a time, a reader could see the restored tuple with the old head link (and apply this transaction's log on top of already-restored data). Writing tuple and link inside one `with_page_mut` closure keeps the pair consistent.

**The `None` case is not an error.** A tuple with no log of this transaction's was created by it (a fresh insert). Marking it deleted with timestamp 0 means "it has been dead since forever": every reader's search ends with "did not exist". The slot is not reclaimed; the next insert of the same primary key will reuse it (stage 6).

**A log that says "did not exist".** An insert over a tombstone (stage 6) leaves a log with `is_deleted = true` and the tombstone's timestamp. Restoring it gives back the tombstone with its original timestamp, so that older readers still find the version below.

**Order of the two pieces.** Abort first restores the tuples, then (given code) marks the transaction `Aborted` and releases its read timestamp. A reader that began meanwhile never sees the temporary timestamp as anything but "invisible".

## In BusTub

`transaction_manager.cpp`, `Abort`: "`// TODO(P4): Implement the abort logic!`" between the state check and `txn->state_ = TransactionState::ABORTED`. `TxnAbortTest.SimpleAbortTest` has the four cases A to F above (insert then abort, update then abort, delete then abort, commit with duplicates) and `AbortIndexTest` the index-related ones of stage 6; the tests expect the heap not to grow after aborted inserts that are inserted again.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `table_heap->UpdateTupleInPlaceWithLockAcquired(meta, tuple, rid, page)` inside an acquired page guard | `with_page_mut(rid, \|page\| page.update_tuple_in_place_unsafe(..))` |
| `std::optional<UndoLink>` head link | `Option<UndoLink>`; `filter(\|l\| l.is_valid())` for "has a log" |

**Port rule:** a guard obtained and then used for several calls is a closure given to `with_page_mut`.

## Learn more
- [`std::slice::from_ref`](https://doc.rust-lang.org/std/slice/fn.from_ref.html) (one log as a slice) · [Rollback in HyPer (Neumann et al. 2015, section 3.3)](https://db.in.tum.de/~muehlbau/papers/mvcc.pdf)

## Performance

Abort costs about what the transaction's writes cost: one latched page update per rid of the write set, each a tuple reconstruction from one log. Undoing is on the failure path, so correctness comes first, but a system with many conflicts (stage 2) aborts often: the cost of one abort is proportional to how much the transaction wrote before it failed.

**Measure it.** Update 10 000 rows, abort, and time the abort; then update 10 rows and abort. The ratio should be about 1000.

## Hints

### Check *whose* log the head is

A tuple in the write set can have another transaction's log at its head only if this transaction inserted it over nothing (then there's no link at all) or something is wrong. Test `link.prev_txn == txn.id()` rather than "the link exists".

### Restore the timestamp from the log

`log.ts` is the timestamp of the version being restored. Leaving the temporary timestamp in place would keep the tuple invisible; setting a made-up timestamp (0, say) would make older readers see a version newer than their snapshot.

### Don't forget the link

Restoring the bytes without moving the head link leaves a chain that starts with a log of an aborted transaction: readers would apply it on top of the restored tuple.
