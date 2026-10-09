Commit is where a transaction's writes become visible to everyone, **all at once**. Until now its tuples carry its temporary timestamp (its id), which only it can see. Commit picks the next commit timestamp, writes it over the temporary one in every tuple the transaction wrote, and moves the transaction from `Running` to `Committed`. Abort is the simple half: end the transaction and release its read timestamp (module 4b adds undoing its writes).

## The task

In `src/concurrency/transaction_manager.rs`:

`commit(txn)` (the checks are given: one commit at a time via `commit_mutex`, a tainted transaction returns `Ok(false)` and stays tainted, any other state but `Running` is an error). Write the region marked `4a-03`:

1. `commit_ts = last_commit_ts + 1`.
2. For every `(table oid, rids)` in `txn.write_sets()`: look the table up in the catalog and, with `table.table.with_page_mut(rid, ..)` (the page's write latch), set the tuple's metadata to `ts = commit_ts` and the **same** `is_deleted`.
3. `txn.set_commit_ts(commit_ts)` and `txn.set_state(Committed)`.
4. Under the watermark's lock, in this order: `update_commit_ts(commit_ts)`, store `last_commit_ts`, `remove_txn(txn.read_ts())`.

`abort(txn)`: a `Running` or `Tainted` transaction becomes `Aborted` and its read timestamp is removed from the watermark. (Given: any other state is an error.)

## Tests

- Commit timestamps are 1, 2, 3, ...; a transaction that begins later reads the latest.
- The tuples in the write set carry the commit timestamp afterwards; a deleted tuple stays deleted; tuples outside the set are untouched.
- A tainted transaction's commit returns `false` and changes nothing; committing twice is an error.
- Commit and abort move the watermark exactly as BusTub's `TimestampTracking` test expects.
- A tainted transaction can be aborted; a finished one cannot.

## Syntax and methods

```rust
let catalog = self.catalog.read().unwrap();
let table = catalog.table_info(table_oid).ok_or_else(|| Exception::new(ExceptionType::Execution, "..."))?;
table.table.with_page_mut(rid, |page| -> Result<()> {
    let meta = page.get_tuple_meta(rid)?;
    page.update_tuple_meta(&TupleMeta { ts: commit_ts, is_deleted: meta.is_deleted }, rid)
})?;
```

## Notes

**Why this order.** The commit publishes in three steps, and a concurrent `begin` must see a consistent picture whenever it looks:

1. Stamp the tuples. A reader that started earlier has a read timestamp below `commit_ts`, so it does not see them as visible; no harm. A reader that has not started yet cannot see them either, because `last_commit_ts` still has the old value.
2. Tell the watermark about the commit, then raise `last_commit_ts`, under the watermark's lock. A `begin` that holds that lock sees either the old state or the new, never a half.
3. Only then remove this transaction's read timestamp.

If `last_commit_ts` were raised first, a new transaction could read at `commit_ts` before the tuples carry it, and see the old temporary timestamps (`> read_ts`): it would miss the commit it was promised.

**Keeping `is_deleted`.** A delete is a tuple with `is_deleted = true` and the transaction's temporary timestamp. Stamping must not undelete it.

**Why tainted returns `false`, not an error.** A tainted transaction hit a write-write conflict earlier; asking it to commit is a normal outcome the client handles ("retry"). BusTub's `CommitTaintedTxn` test helper expects `false` and the state to stay `TAINTED`.

**The write set.** Executors (module 4b) call `txn.append_write_set(table_oid, rid)` for every tuple they insert, delete or update. Here the tests call it by hand.

## In BusTub

`transaction_manager.cpp`, `Commit`: "`// TODO(P4): acquire commit ts!`" ... "`if (txn->state_ != TransactionState::RUNNING) { throw Exception("txn not in running state"); }`" ... "`// TODO(P4): set commit timestamp + update last committed timestamp here.`" followed by "`txn->state_ = TransactionState::COMMITTED; running_txns_.UpdateCommitTs(txn->commit_ts_); running_txns_.RemoveTxn(txn->read_ts_);`". The write set is `txn->GetWriteSets()`, a map from table oid to a set of rids.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::unique_lock<std::mutex> commit_lck(commit_mutex_);` | `let _commit = self.commit_mutex.lock().unwrap();` |
| `table_info->table_->UpdateTupleMeta(meta, rid)` (takes the page latch itself) | `table.table.with_page_mut(rid, \|page\| ...)` so that read and write share one latch |
| `for (auto &[oid, rids] : txn->GetWriteSets())` | `for (oid, rids) in txn.write_sets()` |

**Port rule:** "read, modify, write under one latch" is one closure given to `with_page_mut`, not a `get_...` followed by an `update_...`.

## Learn more
- [`Mutex`](https://doc.rust-lang.org/std/sync/struct.Mutex.html) · [Commit ordering in Neumann et al. 2015, section 3](https://db.in.tum.de/~muehlbau/papers/mvcc.pdf)

## Performance

Commits are serialised by `commit_mutex`, so the time spent holding it bounds commit throughput: it is roughly the number of tuples in the write set times the cost of a latched page update. Stamping the tuples is the dominant part for a large transaction; the watermark update is constant.

**Measure it.** Commit a transaction that wrote 1, 100 and 10 000 tuples and time each: the cost should grow linearly with the write set, and the commit mutex is the reason two such commits never overlap.

## Hints

### The order of the three publications is a correctness property

`update_commit_ts` on the watermark, then `last_commit_ts`, then `remove_txn`, all while holding the watermark's lock. Moving `last_commit_ts` before the stamping loop passes simple tests and breaks under concurrency.

### Read the old `is_deleted` under the same latch

Fetch the meta and write the new one in the same `with_page_mut` call; two separate latch acquisitions leave a window in which another thread could change the tuple.

### Do not stamp a tainted transaction

The tainted early return comes first. If it ran after stamping, a failed commit would leave tuples with a commit timestamp that never officially happened.
