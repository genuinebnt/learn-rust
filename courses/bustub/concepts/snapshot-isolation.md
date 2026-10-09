---
title: Snapshot isolation: what a transaction sees and when it must abort
summary: The visibility rule (read timestamp, own writes), first-updater-wins write-write conflicts, the anomaly snapshot isolation still allows (write skew), and what serializable adds on top.
minutes: 8
---
**Snapshot isolation (SI)** gives every transaction two promises:

1. **A consistent snapshot.** It sees the database exactly as of its **read timestamp**: all transactions that committed at or before it, none that committed after it, and none that are still running. Everything it reads stays the same however long it runs.
2. **Its own writes.** It also sees what it wrote itself.

## Visibility

A version has a timestamp. A transaction `T` with read timestamp `R` and temporary timestamp `T.id` may see a version with timestamp `v` if

```text
v <= R          the version was committed no later than T began, or
v == T.id       T wrote it itself (uncommitted).
```

An uncommitted version of someone else carries *their* id, which is at least 2^62: far above any read timestamp, so the first test fails by itself. No special case for "uncommitted" is needed, which is the point of numbering transactions from 2^62.

## Write-write conflicts: first updater wins

Two transactions that both update the same tuple would, under a snapshot, each overwrite the other's change from a stale starting point (a *lost update*). SI forbids it: when `T` wants to modify a tuple, it first checks that the newest version is one it may modify:

```text
tuple.ts == T.id                    T already changed it: fine (modify again)
tuple.ts <= T.read_ts and not locked   committed before T began: fine
otherwise                           another transaction wrote it (uncommitted),
                                    or committed after T began: CONFLICT
```

On a conflict `T` is **tainted** and can only abort; the error surfaces as an `ExecutionException` so the client knows to retry. The check and the write must be atomic with respect to other writers (BusTub does both under the tuple's page latch).

## What SI does not prevent: write skew

Two doctors are on call; the rule is that at least one must be. Each transaction reads "how many are on call?" (2), sees it is safe to leave, and removes *itself*. They write **different rows**, so there is no write-write conflict, both commit, and nobody is on call. Neither transaction is wrong given its snapshot; the combination is not equal to any serial order.

```svg
caption: Write skew. Both transactions read the same snapshot; each writes a different row, so first-updater-wins sees no conflict. Serializable isolation must catch that T2's read of alice depends on something T1 changed.
<svg viewBox="0 0 760 170" role="img" aria-label="Two transactions reading both rows then each updating one">
<text class="mid fg" x="120" y="30">T1: reads alice, bob (both on call)</text><text class="mid fg" x="120" y="52">writes alice = off</text>
<text class="mid fg" x="500" y="30">T2: reads alice, bob (both on call)</text><text class="mid fg" x="500" y="52">writes bob = off</text>
<rect class="live" x="60" y="80" width="120" height="40" rx="3"/><text class="mid fg" x="120" y="105">alice: on</text>
<rect class="live" x="560" y="80" width="120" height="40" rx="3"/><text class="mid fg" x="620" y="105">bob: on</text>
<text class="mid dim sm" x="380" y="150">after both commit: alice off, bob off. No serial order produces that.</text>
</svg>
```

**Serializable** isolation closes the gap. The approach in this course (module 4b, from the HyPer paper): remember every *predicate* a serializable transaction scanned with; at commit, check that no transaction that committed after it began wrote a tuple matching one of them. If one did, the reader's snapshot was invalidated and it must abort.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `if (meta.ts_ > txn->GetReadTs() && meta.ts_ != txn->GetTransactionTempTs()) { txn->SetTainted(); throw ExecutionException("write-write conflict"); }` | `txn.set_tainted(); return Err(Exception::new(ExceptionType::Execution, "write-write conflict"))` (an `Err`, not an exception: the caller must handle it) |
| a taint flag that the code can forget to check | a `TransactionState` enum: `commit` returns `false` for `Tainted` |

## In real code

### Using it: the visibility and conflict rules

```rust test
const TXN_START_ID: i64 = 1 << 62;

struct Txn {
    id: i64,
    read_ts: i64,
}

fn visible(txn: &Txn, version_ts: i64) -> bool {
    version_ts <= txn.read_ts || version_ts == txn.id
}

/// May `txn` modify a tuple whose newest version has `version_ts`?
fn can_write(txn: &Txn, version_ts: i64) -> bool {
    version_ts <= txn.read_ts || version_ts == txn.id
}

#[test]
fn commit_timestamps_are_visible_only_if_old_enough() {
    let t = Txn { id: TXN_START_ID + 3, read_ts: 5 };
    assert!(visible(&t, 5));
    assert!(!visible(&t, 6));
    assert!(visible(&t, t.id), "my own write");
    assert!(!visible(&t, TXN_START_ID + 4), "somebody else's uncommitted write looks like a huge timestamp");
}

#[test]
fn first_updater_wins() {
    let a = Txn { id: TXN_START_ID, read_ts: 2 };
    let b = Txn { id: TXN_START_ID + 1, read_ts: 2 };
    // a writes first: the tuple now carries a's id
    let tuple_ts = a.id;
    assert!(can_write(&a, tuple_ts));
    assert!(!can_write(&b, tuple_ts), "b conflicts with a's uncommitted write");
    // a commits at 3: b, which began at 2, still conflicts
    assert!(!can_write(&b, 3));
    // a transaction that began after the commit does not
    assert!(can_write(&Txn { id: TXN_START_ID + 2, read_ts: 3 }, 3));
}
```

### Using it: write skew under snapshots

```rust test
use std::collections::HashMap;

#[test]
fn two_snapshots_each_remove_one_doctor_and_nobody_is_left() {
    let committed: HashMap<&str, bool> = [("alice", true), ("bob", true)].into_iter().collect();
    // both transactions read the same snapshot
    let snapshot_1 = committed.clone();
    let snapshot_2 = committed.clone();
    let mut writes_1 = HashMap::new();
    let mut writes_2 = HashMap::new();
    if snapshot_1.values().filter(|&&on| on).count() >= 2 {
        writes_1.insert("alice", false);
    }
    if snapshot_2.values().filter(|&&on| on).count() >= 2 {
        writes_2.insert("bob", false);
    }
    // different rows: no write-write conflict, both commit
    assert!(writes_1.keys().all(|k| !writes_2.contains_key(k)));
    let mut after = committed;
    after.extend(writes_1);
    after.extend(writes_2);
    assert_eq!(after.values().filter(|&&on| on).count(), 0, "the invariant 'at least one on call' is broken");
}

#[test]
fn a_serial_order_would_have_stopped_the_second() {
    let mut on_call = vec!["alice", "bob"];
    for me in ["alice", "bob"] {
        if on_call.len() >= 2 {
            on_call.retain(|d| *d != me);
        }
    }
    assert_eq!(on_call, vec!["bob"]);
}
```

### In the exercises

- **4a-02:** `commit` turns a transaction's temporary timestamps into its commit timestamp; a tainted transaction cannot commit.
- **4a-03 / 4a-05:** `collect_undo_logs` and the scan apply the visibility rule.
- **Module 4b:** the write-write conflict check in update/delete, and serializable validation.

### Where it is used

- **PostgreSQL** `REPEATABLE READ` is snapshot isolation (a conflicting update fails with a serialization error); `SERIALIZABLE` adds predicate tracking (SSI) on top.
- **Oracle**'s `SERIALIZABLE` and **SQL Server**'s `SNAPSHOT` level are snapshot isolation and allow write skew.
- **MySQL InnoDB** `REPEATABLE READ` reads from a snapshot taken at the first read.
