---
title: Write-ahead logging
summary: Why a database writes down what it is about to do before it does it, the one rule (log before data) that makes crashes survivable, what a commit really waits for, and the cost model that makes the log the fast path.
minutes: 12
---
A transfer moves 30 from account A to account B: two records change. The machine loses power between the two writes. When it restarts, A has lost 30 and B has not gained it, and nothing on disk says that a transfer was ever under way. The database has been corrupted by a perfectly normal event.

The fix is old and simple. Before changing anything, **write down what you are about to do** in a separate file that only ever grows, the **log**, and make sure that note is on disk. If the machine dies, the restart reads the log and finishes or undoes whatever was in flight. That is **write-ahead logging** (WAL), and almost every serious database does it: PostgreSQL, MySQL's InnoDB, SQLite in WAL mode, Oracle, SQL Server.

## The one rule

> A change to a data page may reach the disk only after the log record that describes it has reached the disk.

That is the whole protocol; everything else follows. Say a page with a half-finished transaction's change is written and the machine dies. On restart the log record is there, so the change can be recognised as belonging to a transaction that never committed and be undone. If the page could be written *before* its record, a crash would leave a change on disk that nobody knows about: nothing can undo it.

The second half is about commits. A transaction is **committed** when its `Commit` record is durable in the log. Not when its pages are written: they may be written minutes later, or lost, and the log can rebuild them. So a commit costs one sequential write and one sync of the log, not a write of every page it touched.

## Why the log is the fast path

Data pages are scattered: updating a hundred records may touch a hundred pages, each a random write. The log is **sequential**: appending is the cheapest disk operation there is. A database that wrote every changed page at commit would spend its time seeking; with a log it appends a few hundred bytes, syncs once, tells the client "done", and writes the pages later, in whatever order is convenient, in the background. Many commits can share one sync (**group commit**): the throughput of a database is largely the number of commits per log sync.

## What a record holds

To go forward (**redo**) a record needs the new value; to go backward (**undo**) it needs the old one. A record that holds both, `before` and `after`, can do either. It also needs enough to find the place it applies to (a page and a slot), and the transaction it belongs to, so that recovery can tell which changes to keep.

A log record gets its position, the **LSN** (log sequence number), when it is appended. LSNs only grow. Every page remembers the LSN of the last change it holds (its *page LSN*), and that is how the rule is enforced in practice: before writing a page, flush the log up to that page's LSN.

## What can go wrong

- **A torn record.** The machine can die in the middle of writing a log record. The log must be readable up to the last whole record; a record carries a length and a checksum so that a half-written or damaged one is recognised as the end.
- **A lie by the disk.** A write that "succeeded" may only have reached the drive's cache. Real systems call `fsync` (or write with `O_DSYNC`) and check that the drive honours it; see the durability concept.
- **Forgetting the rule under pressure.** A buffer pool that evicts a dirty page to make room is writing a page behind the log's back. It must flush the log first, or ask the log manager to. A WAL bug of this kind shows only after a crash at exactly the wrong moment, which is why you test it by crashing at every moment.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `fsync(fd)` / `fdatasync(fd)` | `File::sync_all()` / `sync_data()` |
| a `LogManager` with a mutex and a condition variable for the flush thread | a `Mutex<State>` and, if you want group commit, a `Condvar` |
| `memcpy` of a struct into the log buffer | an explicit `serialize` to bytes (a struct's layout is not a format) |
| `reinterpret_cast` of bytes read back | `deserialize` that checks length and checksum first |

## In real code

### Using it: the rule on a tiny key-value store

```rust test
use std::collections::BTreeMap;

/// A log (durable once flushed), a buffer of records not yet flushed, and "disk pages" (the data, written only on `write_page`).
#[derive(Default, Clone)]
struct Disk {
    log: Vec<(u64, String, i32)>, // (lsn, key, new value)
    pages: BTreeMap<String, i32>,
}

#[derive(Default)]
struct Db {
    disk: Disk,
    buffer: Vec<(u64, String, i32)>,
    memory: BTreeMap<String, i32>,
    page_lsn: BTreeMap<String, u64>,
    next_lsn: u64,
}

impl Db {
    fn set(&mut self, key: &str, value: i32) {
        let lsn = self.next_lsn;
        self.next_lsn += 1;
        self.buffer.push((lsn, key.into(), value)); // 1. say what you are about to do
        self.memory.insert(key.into(), value); // 2. then do it (in memory)
        self.page_lsn.insert(key.into(), lsn);
    }
    fn flush_log(&mut self) {
        self.disk.log.append(&mut self.buffer);
    }
    /// Writing a page: the log must be durable up to this page's last change first.
    fn write_page(&mut self, key: &str) {
        let lsn = self.page_lsn[key];
        if self.disk.log.last().map_or(true, |(l, _, _)| *l < lsn) {
            self.flush_log();
        }
        self.disk.pages.insert(key.into(), self.memory[key]);
    }
    /// What a crash leaves: only the disk.
    fn crash(&self) -> Disk {
        self.disk.clone()
    }
}

#[test]
fn a_page_on_disk_is_always_explained_by_the_durable_log() {
    let mut db = Db::default();
    db.set("a", 1);
    db.set("b", 2);
    db.write_page("a"); // flushes the log first
    let after_crash = db.crash();
    for (k, v) in &after_crash.pages {
        assert!(after_crash.log.iter().any(|(_, lk, lv)| lk == k && lv == v), "{k}={v} is on disk but not in the log");
    }
    // the record of b was flushed too: flushing flushes everything buffered, never less
    assert_eq!(after_crash.log.len(), 2);
}

#[test]
fn what_was_not_flushed_is_lost_and_nobody_was_told_it_was_safe() {
    let mut db = Db::default();
    db.set("a", 1);
    let after_crash = db.crash();
    assert!(after_crash.log.is_empty() && after_crash.pages.is_empty());
}
```

### In the exercises

- **4c-01 and 4c-02:** the record format (length, checksum, body) and the log manager with its buffer, LSNs and `flush`.
- **4c-04:** `Store::change` appends the record, then changes the page; `flush_page` flushes the log up to the page's LSN first; `commit` waits for its `Commit` record to be durable.

### Where it is used

- **PostgreSQL's WAL** (`pg_wal/`) is exactly this, with full-page images after a checkpoint to survive torn pages; `synchronous_commit` decides whether a commit waits for the sync.
- **SQLite's WAL mode** appends changed pages to a `-wal` file and merges them into the database at checkpoints; readers see the log and the file together.
- **InnoDB** has a redo log (`ib_logfile`) and a separate undo log; `innodb_flush_log_at_trx_commit` is the durability knob.
- **LSM-tree stores** (RocksDB, LevelDB) write each update to a WAL and to an in-memory table; a restart rebuilds the table from the WAL.
