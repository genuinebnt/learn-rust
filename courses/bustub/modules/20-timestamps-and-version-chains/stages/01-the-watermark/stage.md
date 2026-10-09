Old versions of tuples are garbage once no transaction can need them. The **watermark** is the line between needed and garbage: the smallest read timestamp among the running transactions, or the last commit's timestamp if none is running. This stage writes the structure that tracks it. It is small, self-contained, and the transaction manager of the next stage depends on it.

## The task

In `src/concurrency/watermark.rs`, `Watermark` has `commit_ts` (the timestamp of the last commit, kept up to date by the given `update_commit_ts`) and `current_reads` (an ordered map from read timestamp to the number of running transactions that have it). Write:

- `add_txn(read_ts)`: a transaction begins. If `read_ts < commit_ts` return an `Execution` error whose message is `read ts < commit ts` (a transaction cannot read before the newest commit it could have seen). Otherwise count one more reader at `read_ts`.
- `remove_txn(read_ts)`: a transaction ends. Count one fewer at `read_ts`; when nobody is left at that timestamp, forget the timestamp.
- `get_watermark()`: the smallest timestamp somebody reads at, or `commit_ts` when nobody does.

## Tests

- No readers: the watermark is the last commit; it follows `update_commit_ts`.
- The smallest of several readers wins; removing it moves the watermark up; removing another leaves it.
- Two readers at one timestamp are counted: one `remove_txn` does not release the timestamp.
- A reader older than the last commit is refused with `read ts < commit ts`.
- A million transactions, added and removed in ascending and in descending order, finish quickly.

## Syntax and methods

```rust
*self.current_reads.entry(ts).or_insert(0) += 1;       // counter in an ordered map
self.current_reads.get_mut(&ts)                         // Option<&mut usize>
self.current_reads.remove(&ts);
self.current_reads.keys().next().copied()               // the smallest key: Option<i64>
Err(Exception::new(ExceptionType::Execution, "read ts < commit ts"))
```

## Notes

**Why a map of counts.** Two transactions that begin between the same two commits read at the same timestamp. A `BTreeSet<Timestamp>` would forget one of them; when the first ended, the timestamp would disappear while the second still reads it, and the watermark would jump too far, letting garbage collection delete a version someone needs. The counts are the whole point.

**Why ordered.** `get_watermark` is called often (every garbage collection, every `begin` in some designs) and must not scan the readers. `BTreeMap` keeps keys sorted, so the smallest is the first key: `O(log n)` to find, add and remove.

**`remove_txn` of an unknown timestamp.** Removing a timestamp that was never added is a bug elsewhere; make it harmless rather than panicking (BusTub's tests never do it).

## In BusTub

`watermark.cpp`: "`if (read_ts < commit_ts_) { throw Exception("read ts < commit ts"); }` ... `// TODO(P4): implement me!`". The header says the watermark is the lowest read timestamp in the system; `transaction_manager.h`: "`/** @brief Get the lowest read timestamp in the system. */`". The starter hints at `std::map`; the performance test `TxnTsTest.WatermarkPerformance` adds and removes a million transactions.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::map<timestamp_t, int> current_reads_;` | `BTreeMap<Timestamp, usize>` |
| `current_reads_[read_ts]++` | `*current_reads.entry(read_ts).or_insert(0) += 1` |
| `current_reads_.begin()->first` (undefined on an empty map) | `current_reads.keys().next()` is an `Option`: use `unwrap_or(commit_ts)` |
| `throw Exception("...")` | `return Err(Exception::new(...))` |

**Port rule:** `std::map<K, int>` used as a counter is a `BTreeMap<K, usize>` and `entry`.

## Learn more
- [`BTreeMap`](https://doc.rust-lang.org/std/collections/struct.BTreeMap.html) · [`entry`](https://doc.rust-lang.org/std/collections/btree_map/enum.Entry.html) · [MVCC garbage collection in Wu et al.](https://www.vldb.org/pvldb/vol10/p781-Wu.pdf)

## Performance

`BTreeMap` operations are `O(log n)`; with `n` distinct read timestamps the million-transaction test does about 2 million of them, well under a second in release mode. A `Vec` that is searched for its minimum on every `get_watermark` costs `O(n)` per call: the same test would do `10^12` steps.

**Measure it.** Run the stage's last test with `cargo test --release s4a_01 -- --nocapture` and time it; then temporarily replace the map by a `Vec<(Timestamp, usize)>` scanned linearly and watch the time grow by orders of magnitude.

## Hints

### Count, don't store

The map value is how many transactions read at that timestamp. `remove_txn` must delete the key only when the count reaches zero, or a later `get_watermark` reports a timestamp nobody reads.

### The first key is the minimum

An ordered map iterates in key order, so `keys().next()` is the smallest. An empty map yields `None`, which is exactly the "nobody runs" case.

### Check the order of the two timestamps

`read_ts < self.commit_ts` is the error; `==` is fine (a transaction that begins right after a commit reads that commit).
