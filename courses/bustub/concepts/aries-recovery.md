---
title: Crash recovery: analysis, redo, undo
summary: The three passes of ARIES-style recovery (who was running, repeat history, roll back the losers), why redo must be idempotent, why undo is logged too, and what a checkpoint buys.
minutes: 14
---
After a crash the database restarts with two things: the **log**, which holds every record that was flushed, and the **data pages**, each of which was either written before the crash or not (any subset of them, in any state of staleness). Recovery has to turn this into the state of exactly the **committed** transactions, no matter which pages made it. The textbook answer is **ARIES** (Mohan et al., 1992), and its idea fits in one sentence: *repeat history, then undo the losers.*

## Three passes

**1. Analysis.** Read the log and decide who was running. A transaction with a `Commit` record is a **winner**; one with an `Abort` record has finished rolling back; every other one that appears in the log is a **loser**: it was active at the crash and must be undone.

**2. Redo: repeat history.** Walk the log from the start (or from the last checkpoint) and re-apply **every** change, in order, whether its transaction committed or not. Why even the losers'? Because the pages may contain any mixture, and "put every change in place in log order" is the one procedure that is correct from every starting point: after it, the pages are exactly as they were at the instant of the crash. That is a clean starting point for the third pass.

Redo must be **idempotent**: applying a record to a page that already has the change must do no harm. In this course that is arranged by describing each change as "put this slot in this state" (the value after the change) rather than "add 5": setting a slot to a value twice is the same as setting it once. ARIES gets the same effect by storing, in each page, the LSN of the last change applied to it and skipping records at or below it.

**3. Undo the losers.** Now roll back every loser, newest change first, by restoring each change's *before* state. Because redo repeated history, the pages hold every loser change, so undoing them is well defined.

## Undo is logged too

When a transaction is rolled back (at run time or in recovery), each undo step is itself a change to a page, and it must be **logged** like any other: as a change with `before` and `after` swapped (ARIES calls it a *compensation log record*). Three reasons:

- If the machine dies *during* recovery, the next recovery repeats history, including the undo steps already done, and only the remaining ones have to be undone: recovery makes progress.
- A transaction that was rolled back at run time and whose rids are then written by another transaction must not be rolled back *again* by recovery on top of the newer work. With the undo logged and an `Abort` record at the end, redo replays both the changes and their undos, and the transaction counts as finished.
- The log stays the single truth: the state of the pages is always "the log applied in order".

## Checkpoints

Redo from the start of the log gets slower as the log grows. A **checkpoint** bounds it: write every dirty page to disk (a *sharp* checkpoint, which this course uses), then log a `Checkpoint` record that lists the transactions active at that moment. Everything before it is already in the pages, so redo starts at the checkpoint. Losers that were active at the checkpoint still have changes before it; to undo them, recovery must read back as far as their first record (or, as ARIES does, follow a chain of previous LSNs per transaction). Real systems use *fuzzy* checkpoints that do not stop the world, recording which pages were dirty instead of forcing them.

## What you can and cannot prove with a test

Recovery is the hardest code in the course to test by example, because the bugs live in the interleaving of three things: when pages were written, how far the log was flushed, and where the crash fell. A **property test** can generate a random run, crash at the end, recover and compare with a model of the committed transactions; a deterministic test can crash at *every* step of a script (the bank-transfer test of the boss stage). Both find bugs that no hand-written scenario does, and both rely on a test double for the disk that can be copied to simulate the crash.

## C++ comparison

| C / C++ | Rust |
|---|---|
| a `LogRecord` class hierarchy with a type tag | an `enum LogRecord` with data, matched exhaustively |
| `LogRecovery::Redo()` loops over `std::unordered_map<txn_id_t, lsn_t>` tables | `HashSet` / `Vec` of transaction ids from `analyse` |
| `memcpy` of record headers | explicit serialization with a length and a checksum |

## In real code

### Using it: analysis, redo and undo on a tiny log

```rust test
use std::collections::{BTreeMap, HashSet};

#[derive(Clone, Debug)]
enum Rec {
    Begin(u32),
    Set { txn: u32, key: char, before: Option<i32>, after: Option<i32> },
    Commit(u32),
    Abort(u32),
}

fn apply(db: &mut BTreeMap<char, i32>, key: char, state: Option<i32>) {
    match state {
        Some(v) => db.insert(key, v),
        None => db.remove(&key),
    };
}

/// Returns the recovered database from whatever the disk had and the durable log.
fn recover(mut disk: BTreeMap<char, i32>, log: &[Rec]) -> BTreeMap<char, i32> {
    // analysis
    let (mut seen, mut finished) = (vec![], HashSet::new());
    for r in log {
        match r {
            Rec::Begin(t) | Rec::Set { txn: t, .. } => if !seen.contains(t) { seen.push(*t) },
            Rec::Commit(t) | Rec::Abort(t) => { finished.insert(*t); }
        }
    }
    let losers: Vec<u32> = seen.into_iter().filter(|t| !finished.contains(t)).collect();
    // redo: repeat history
    for r in log {
        if let Rec::Set { key, after, .. } = r {
            apply(&mut disk, *key, *after);
        }
    }
    // undo the losers, newest first
    for r in log.iter().rev() {
        if let Rec::Set { txn, key, before, .. } = r {
            if losers.contains(txn) {
                apply(&mut disk, *key, *before);
            }
        }
    }
    disk
}

#[test]
fn committed_work_survives_and_the_unfinished_is_rolled_back_whatever_the_disk_held() {
    let log = vec![
        Rec::Begin(1),
        Rec::Set { txn: 1, key: 'a', before: None, after: Some(10) },
        Rec::Begin(2),
        Rec::Set { txn: 2, key: 'b', before: None, after: Some(20) },
        Rec::Commit(1),
    ];
    // any starting state of the disk gives the same result: nothing written, everything written, a stale value
    for disk in [BTreeMap::new(), BTreeMap::from([('a', 10), ('b', 20)]), BTreeMap::from([('a', 99)])] {
        assert_eq!(recover(disk, &log), BTreeMap::from([('a', 10)]));
    }
}

#[test]
fn recovering_twice_is_the_same_as_recovering_once() {
    let log = vec![Rec::Begin(1), Rec::Set { txn: 1, key: 'x', before: None, after: Some(1) }];
    let once = recover(BTreeMap::new(), &log);
    assert_eq!(recover(once.clone(), &log), once);
}
```

### In the exercises

- **4c-05:** `analyse` (winners and losers) and `redo` over the records.
- **4c-06:** `undo`, with each undo logged as a swapped change and `Abort` at the end.
- **4c-07:** the checkpoint and the shorter redo; **4c-08:** a crash at every step of a script and random crashes with a garbage log tail and a crash in the middle of recovery.

### Where it is used

- **PostgreSQL** replays WAL from the last checkpoint after a crash (redo only: its MVCC makes aborted transactions' versions invisible, so there is no undo pass).
- **InnoDB, SQL Server and DB2** use ARIES descendants with all three passes and physiological logging.
- **SQLite** in rollback-journal mode does undo only (it restores the pages from the journal); in WAL mode it does redo only.
- **Filesystems** (ext4's journal, NTFS) apply the same ideas to metadata.
