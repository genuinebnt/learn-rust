A transaction needs three things before it can run: a unique id, a **read timestamp** (what it is allowed to see), and a place in the transaction manager's tables. The id and the table entry are given; this stage chooses the read timestamp and registers it with the watermark. It looks like two lines. The interesting part is doing them **atomically**.

## The task

In `src/concurrency/transaction_manager.rs`, `TransactionManager::begin(isolation_level)`: the first lines (given) take the next id (starting at 2^62, `TXN_START_ID`), create the `Transaction`, and put it in `txn_map`. Write the part marked `4a-02`:

- read the last commit timestamp (`last_commit_ts`);
- set it as the transaction's read timestamp (`txn.set_read_ts(..)`);
- register it with `running_txns` (the watermark), propagating its error.

The two steps (reading `last_commit_ts` and adding it to the watermark) must happen while holding the watermark's lock, for the reason in *Notes*.

## Tests

- The first transactions of a database get ids `2^62`, `2^62 + 1`, ... and human-readable ids 0, 1, 2.
- A new transaction is `Running`, has no commit timestamp, keeps its isolation level, and its temporary timestamp is its id.
- In a database with no commits every transaction reads at 0.
- `begin` leaves the transaction findable in the manager's map.
- Running transactions are registered with the watermark.

## Syntax and methods

```rust
let mut running = self.running_txns.lock().unwrap();     // MutexGuard<Watermark>
let read_ts = self.last_commit_ts.load(Ordering::SeqCst);
txn.set_read_ts(read_ts);
running.add_txn(read_ts)?;                                // Result<(), Exception>
```

## Notes

**Why temporary timestamps are ids, and why ids start at 2^62.** Until a transaction commits, the tuples it writes carry its **temporary timestamp**, which is its id. Commit timestamps count up from 1; ids count up from 2^62. The two ranges can never meet, so a reader comparing a tuple's timestamp with its read timestamp never mistakes somebody's uncommitted write for an old commit: `2^62 + k > read_ts` always. `human_readable_id` is `id ^ TXN_START_ID`, which is just `id - 2^62`; tests and `EXPLAIN` output use it.

**Why the lock covers both steps.** Suppose `begin` reads `last_commit_ts = 5`, then another thread commits at 6 and tells the watermark (`commit_ts = 6`), then `begin` calls `add_txn(5)`. The watermark now sees a reader older than the last commit and returns the error from stage 1; worse, in a design without that check the watermark could be 6 while a reader at 5 runs. Commit (next stage) updates `last_commit_ts` and the watermark's `commit_ts` under the same lock. Holding it here makes "read the newest commit and register as a reader" one indivisible step.

**Lock order.** `begin` already took and released `txn_map`'s lock. It must not hold `txn_map` while taking the watermark's, and `commit` takes them in a fixed order too (see *deadlock and lock ordering*): any code that needs both takes `commit_mutex` first, then the watermark's lock, and never the other way round.

## In BusTub

`transaction_manager.cpp`:
```cpp
  auto txn_id = next_txn_id_++;
  ...
  // TODO(P4): set the timestamps here. Watermark updated below.
  running_txns_.AddTxn(txn_ref->read_ts_);
```
and `transaction.h`: "`GetTransactionIdHumanReadable() const -> txn_id_t { return txn_id_ ^ TXN_START_ID; }`", "`/** @return the temporary timestamp of this transaction */`".

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::atomic<timestamp_t> last_commit_ts_` read with `.load()` | `AtomicI64::load(Ordering::SeqCst)` |
| `std::unique_lock<std::mutex>` that unlocks at scope end | `MutexGuard`, released when it goes out of scope (`drop(guard)` to release earlier) |
| `Transaction *` owned by `txn_map_` (a `unique_ptr`) | `Arc<Transaction>` shared by the map and the caller |

**Port rule:** a lock that must cover two statements is a `let guard = m.lock().unwrap();` that lives until after the second.

## Learn more
- [`std::sync::atomic`](https://doc.rust-lang.org/std/sync/atomic/index.html) · [`Mutex`](https://doc.rust-lang.org/std/sync/struct.Mutex.html) · [Snapshot isolation (Wikipedia)](https://en.wikipedia.org/wiki/Snapshot_isolation)

## Performance

`begin` is on every transaction's path and takes two short locks: the map's write lock to insert and the watermark's lock for a few instructions. Both are held for constant time, so `begin` scales to many threads until the map's write lock becomes the bottleneck (a real system shards the map).

**Measure it.** Begin 100 000 transactions on 1 and on 8 threads and compare the wall time; if 8 threads are not faster, the write lock on `txn_map` is the limit.

## Hints

### Do not read the commit counter before taking the lock

A thread that reads `last_commit_ts` first and locks afterwards can be overtaken by a commit and register a stale timestamp. Lock, then read.

### The error cannot happen if the lock is right

With the lock held, `read_ts` equals the watermark's `commit_ts`, never below. If the stage-1 error shows up in a test, the read and the registration are not atomic.

### The id is not the timestamp

The read timestamp is the *last commit*; the id is only a name. Do not set `read_ts` from the id.
