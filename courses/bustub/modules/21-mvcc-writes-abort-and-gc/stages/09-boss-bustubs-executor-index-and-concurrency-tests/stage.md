BusTub's remaining Project 4 tests, ported: the multi-transaction insert/delete scenario, the two garbage collection walks (with and without tainted transactions), the index conflict test, the three concurrent index tests (inserts racing for keys, updates racing on rows, updates and aborts racing on pairs of rows), and the abort test with ordered queries.

## The task

Make the stage's tests pass: `cargo test --test stages_4b s4b_09`.

## Tests

- `s4b_09_insert_delete_conflict_test`, `s4b_09_index_update_conflict_test`: the scenarios from BusTub's executor and index tests, statement by statement.
- `s4b_09_garbage_collection` and `s4b_09_garbage_collection_with_tainted_transactions`: BusTub's seven-step walks with `EnsureTxnGCed` / `EnsureTxnExists` after every collection.
- `s4b_09_index_concurrent_insert_test`: eight threads race to insert the same keys; each key has exactly one winner, and the table shows each winner's value.
- `s4b_09_index_concurrent_update_test` and `s4b_09_index_concurrent_update_abort_test`: racing updaters (also with a delete and re-insert in the same transaction, and with aborts); the final table must equal what the committed transactions did, and the heap must not grow.
- `s4b_09_simple_abort_with_ordered_queries_and_a_duplicate_heavy_commit`.

## Notes

**Concurrency tests find races, not only bugs in the algorithm.** If one fails, run it several times (`cargo test --test stages_4b s4b_09_index_concurrent -- --test-threads=1 --nocapture`) and read the first difference: "exactly one winner" failing with 0 winners means a transaction failed that should not have (a spurious conflict, often from checking a timestamp against the wrong transaction); with 2 winners means the index let two inserters through (the `insert_entry` result was ignored). A wrong final value means a lost update: a conflict check that ran against a stale copy instead of under the page latch.

**Aborted transactions' leftovers.** The abort test deliberately leaves aborted transactions in the map; the final scan must show only committed increments. If a count is too high, an abort did not restore a tuple; if too low, a commit was lost.

**Time.** Each concurrent test runs a few seconds in debug mode. `--release` is faster and also more racy, which is the point.

## In BusTub

`test/txn/txn_executor_test.cpp`, `txn_index_test.cpp`, `txn_index_concurrent_test.cpp`, `txn_abort_serializable_test.cpp`. The original concurrent tests use 8 threads and 50 trials; the ports use fewer trials so that a debug run finishes in seconds. Some of BusTub's cases continue on the autograder ("`// test continues on Gradescope...`"); the visible part is what is ported.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::thread` and a mutex-protected result map | `std::thread::spawn` and the join handle's return value |
| `BUSTUB_ENSURE(cond, "cannot commit??")` | `assert!(cond, "cannot commit??")` |

**Port rule:** threads that return their results through `JoinHandle` need no shared result map.

## Learn more
- [`std::thread`](https://doc.rust-lang.org/std/thread/) · [BusTub's txn tests](https://github.com/cmu-db/bustub/tree/master/test/txn)

## Performance

The concurrent tests do a few thousand tiny transactions; they measure correctness, not speed. If one is slow, look at lock hold times: the page latch must be held for one tuple update, never across an index lookup or a log allocation.

**Measure it.** `cargo test --release --test stages_4b s4b_09_index_concurrent -- --nocapture` and compare with debug.

## Hints

### A spurious conflict is a bug

A transaction that conflicts with nobody must never fail. Use the single-threaded tests to find the case, then think about what changes under threads.

### Look at the heap size

`heap_entries` too large means an update or insert created a tuple where it should have reused one; too small cannot happen.

### Reproduce with fewer threads

Two threads and one key give the same failure with a message you can read.
