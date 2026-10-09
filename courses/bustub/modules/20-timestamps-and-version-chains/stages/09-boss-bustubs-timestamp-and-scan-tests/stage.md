BusTub's own tests for this part of Project 4, ported: the transaction timestamp walk-through (`TxnTsTest.TimestampTracking`), the tuple-reconstruction cases (`TxnScanTest.TupleReconstructTest`), the ten-tuple undo-log collection (`TxnScanTest.CollectUndoLogTest`), the scan over four tuples with chains across six transactions (`TxnScanTest.ScanTest`) and the eight undo-log generation cases (`TxnExecutorTest.GenerateUndoLogTest`: update, delete, insert, update twice, update then delete, insert then update, insert then delete, delete then insert). All but the scan test are built from the pieces you have written; the scan test needs them all working together.

## The task

Make the stage's tests pass: `cargo test --test stages_4a s4a_09`.

## Tests

- `s4a_09_timestamp_tracking`: begins, commits and aborts in the order of BusTub's test, checking read timestamps, commit timestamps, states and the watermark after every step.
- `s4a_09_tuple_reconstruct`: the four reconstruction scenarios.
- `s4a_09_collect_undo_log_test`: ten tuples with different chains; the transaction with read timestamp 2 is shown the right version of each, or none.
- `s4a_09_scan_test`: `SELECT` inside transactions 0 to 5.
- `s4a_09_generate_undo_log_test`: each generated log applied back with `reconstruct_tuple` gives the tuple it was made from, in all eight cases.

## Notes

**Reading the scan test.** In BusTub's test, only transactions 0 and 1 have their answers filled in; the file says the rest are hidden and suggests drawing the chains out. The ported test fills them in; to check any, draw the chain of each tuple and ask, for each transaction, which version has a timestamp at or before its read timestamp (or is its own):

```text
record1  txn4 (a=1)           -> log ts=1 (a=2)
record2  ts=3 (a=3)           -> log ts=2 (deleted) -> log ts=1 (a=4,2.0,true)
record3  ts=4 deleted         -> log ts=3 (a=5,..)
record4  txn3 deleted         -> log ts=2 (a=6) -> log ts=1 (a=7)
```
Transaction 1 (read ts 1) sees `2`, `4` and `7`; transaction 2 sees `2` and `6`; and so on.

**A failure tells you where.** The timestamp test fails with the first assertion that differs, so its line number is the step in the sequence: usually an `abort` that did not release the read timestamp or a `commit` that raised `last_commit_ts` too early.

**`TxnMgrDbg`.** BusTub asks you to implement a function that prints every tuple with its version chain, because the later tests are impossible to debug without it. This port gives you one: `txn_mgr_dbg("before the scan", &db.txn_manager, &table)` in `execution_common.rs` prints each rid, its timestamp (`txn<id>` for a temporary one), the tuple, and the chain below it.

## In BusTub

`test/txn/txn_timestamp_test.cpp`, `test/txn/txn_scan_test.cpp` and `GenerateUndoLogTest` in `test/txn/txn_executor_test.cpp`: "`// hidden tests... this is the only hidden test case among task 1, 2, 3. We recommend you to implement `TxnMgrDbg` function, draw the version chain out, and think of what should be read by each txn.`"

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `ASSERT_EQ(txn->GetReadTs(), 1)` | `assert_eq!(txn.read_ts(), 1)` |
| `WithTxn(txn1, QueryShowResult(...))` | `query(&db, &txn1, "SELECT ...")` and an `assert_eq!` on the sorted rows |
| `bustub->txn_manager_->UpdateUndoLink(rid, link, nullptr)` | `db.txn_manager.update_undo_link(rid, Some(link), None)` |

**Port rule:** BusTub's `AnyResult`/`IntResult` row-set comparisons are sorted `Vec<String>` equality.

## Learn more
- [BusTub's txn tests](https://github.com/cmu-db/bustub/tree/master/test/txn) · [Neumann et al. 2015](https://db.in.tum.de/~muehlbau/papers/mvcc.pdf)

## Performance

These tests are small; the cost is in the million-transaction watermark test of stage 1 (a second in release mode) and in nothing else. A scan over the four tuples of `ScanTest` walks chains of at most three logs.

**Measure it.** `cargo test --release --test stages_4a s4a_09 -- --nocapture` prints each test's time.

## Hints

### Start from the failing assertion

The first difference names the stage whose function is wrong: a read timestamp is stage 2, a commit timestamp stage 3, a reconstructed value stage 4, a missing or extra tuple stage 5 or 8.

### Draw the chain

For the scan test, write each tuple's versions as a list of `(ts, value)` and mark the version a reader with read ts `R` takes: the first one from the left with `ts <= R`.

### Own writes beat the timestamp rule

In the collect and scan tests, a tuple carrying the reader's temporary timestamp is visible to that reader even though its "timestamp" is huge.
