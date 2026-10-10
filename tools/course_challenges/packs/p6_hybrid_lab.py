from _c import C
M4D = "23-the-lock-manager"
CH = []

CH.append(C("4d-c6", M4D, "95-challenge-snapshot-reads-locked-writes", "extend", "Challenge: snapshot reads, locked writes", "hard", "stages_4d::s4d_c6",
  ["combining MVCC-style snapshot reads with the row locks you built","what a writer waiting (instead of aborting) buys, and what `FOR UPDATE` is for"],
  ["lock-modes-and-two-phase-locking","waits-for-graphs-and-deadlock-detection","model-based-testing"],
  "`HybridStore` in `src/concurrency/hybrid_store.rs`: a key-value store that takes the best of both halves of module 4. **Reads** are snapshot reads: a transaction sees the committed state as of the moment it began, plus its own writes, and a read never waits for anyone. **Writes** take an exclusive row lock from **your** `LockManager` and wait if another writer holds it, instead of aborting on conflict. `get_for_update` locks the row first and reads the newest committed value, the way `SELECT ... FOR UPDATE` does.",
  "PostgreSQL and InnoDB are neither pure MVCC nor pure locking: readers use versions so they never block or get blocked, writers use row locks so they queue instead of failing. The two mechanisms answer different questions: versions answer \"what did the world look like when I started\", locks answer \"who may change this row now\". The trap is `FOR UPDATE`: after waiting for a lock, the value your snapshot shows may already be stale, and a read-modify-write on it loses an update.",
  ["`new(locks)` takes the lock manager to use. `begin()` returns a `HybridTxn` (given: its id, its read timestamp, its lock-manager transaction at repeatable read).","`get(txn, key)` returns the value as of `txn.read_ts` with the transaction's own uncommitted writes on top. It never takes a lock and never waits.","`put(txn, key, value)` takes IX on the table and X on the row (waiting if it must) and buffers the write. It returns the lock error if the transaction was chosen as a deadlock victim.","`get_for_update(txn, key)` takes the same locks, then returns the newest committed value (or the transaction's own write), not the snapshot value.","`commit(txn)` installs the writes at a new commit timestamp, then releases every lock, and returns the timestamp. `abort(txn)` discards the writes and releases every lock."],
  ["A transaction never sees another transaction's uncommitted write, and never sees a commit that happened after it began (except through `get_for_update`).","Two writers are never inside the same row at once; versions of a key are installed in commit order.","Locks are held until commit or abort."],
  ["A read-only transaction reads the same values however many others commit meanwhile.","A reader's answer does not depend on whether a writer holds the row.","`get_for_update` then `put` of value + 1, from any number of threads, adds exactly the number of increments.","An aborted transaction leaves no trace."],
  ["x = 0. A begins and reads 0; B writes 5 and commits; A reads 0 (snapshot), `get_for_update` gives 5","two writers on one key: the second `put` returns only after the first commits"],
  ["Snapshots across commits.","A reader while a writer holds the row (watchdog).","A second writer waits, then proceeds.","Abort frees the row.","Counter increments from several threads.","A deadlock is broken and the survivor commits.","A property against a model of sequential transactions."],
  src=("src/concurrency/hybrid_store.rs", '''
//! A key-value store with snapshot reads and locked writes.

use std::collections::HashMap;
use std::sync::{Arc, Mutex};

use crate::catalog::catalog::TableOid;
use crate::common::config::PageId;
use crate::common::rid::Rid;
use crate::concurrency::lock_error::LockError;
use crate::concurrency::lock_manager::LockManager;
use crate::concurrency::lock_mode::LockMode;
use crate::concurrency::lock_txn::{LockIsolation, LockTxn};
use crate::concurrency::transaction::TxnId;

const TABLE: TableOid = 1;

/// A running transaction (given): its id, the commit timestamp it reads as of, and its handle for the lock manager.
pub struct HybridTxn {
    pub id: TxnId,
    pub read_ts: u64,
    pub lock: Arc<LockTxn>,
}

fn rid(key: u32) -> Rid {
    Rid::new(PageId(0), key)
}

// @begin 4d-c6
struct State {
    next_id: TxnId,
    clock: u64,
    /// Committed versions per key, in commit order: `(commit_ts, value)`.
    versions: HashMap<u32, Vec<(u64, i64)>>,
    /// Buffered writes of running transactions.
    pending: HashMap<TxnId, HashMap<u32, i64>>,
}
// @end

pub struct HybridStore {
    // @begin 4d-c6
    locks: Arc<LockManager>,
    state: Mutex<State>,
    //~ _hybrid: (),
    // @end
}

impl HybridStore {
    pub fn new(locks: Arc<LockManager>) -> HybridStore {
        // @begin 4d-c6
        HybridStore { locks, state: Mutex::new(State { next_id: 1, clock: 0, versions: HashMap::new(), pending: HashMap::new() }) }
        //~ let _ = locks;
        //~ todo!("4d-c6: an empty store that uses this lock manager")
        // @end
    }

    pub fn begin(&self) -> HybridTxn {
        // @begin 4d-c6
        let mut st = self.state.lock().unwrap();
        let id = st.next_id;
        st.next_id += 1;
        st.pending.insert(id, HashMap::new());
        HybridTxn { id, read_ts: st.clock, lock: LockTxn::new(id, LockIsolation::RepeatableRead) }
        //~ todo!("4d-c6: a new transaction that reads as of the latest commit")
        // @end
    }

    /// The value `txn` sees: its own write, else the newest version committed at or before its read timestamp.
    pub fn get(&self, txn: &HybridTxn, key: u32) -> Option<i64> {
        // @begin 4d-c6
        let st = self.state.lock().unwrap();
        if let Some(v) = st.pending.get(&txn.id).and_then(|w| w.get(&key)) {
            return Some(*v);
        }
        st.versions.get(&key)?.iter().rev().find(|(ts, _)| *ts <= txn.read_ts).map(|(_, v)| *v)
        //~ todo!("4d-c6: a snapshot read: no lock, no waiting")
        // @end
    }

    /// Takes IX on the table and X on the row; may wait, may be chosen as a deadlock victim.
    fn lock_for_write(&self, txn: &HybridTxn, key: u32) -> Result<(), LockError> {
        // @begin 4d-c6
        self.locks.lock_table(&txn.lock, LockMode::IntentionExclusive, TABLE)?;
        self.locks.lock_row(&txn.lock, LockMode::Exclusive, TABLE, rid(key))
        //~ todo!("4d-c6: the table intention lock, then the row lock")
        // @end
    }

    pub fn put(&self, txn: &HybridTxn, key: u32, value: i64) -> Result<(), LockError> {
        // @begin 4d-c6
        self.lock_for_write(txn, key)?;
        self.state.lock().unwrap().pending.entry(txn.id).or_default().insert(key, value);
        Ok(())
        //~ todo!("4d-c6: lock the row (waiting if needed), then buffer the write")
        // @end
    }

    /// Like `get`, but locks the row first and returns the newest committed value, not the snapshot value.
    pub fn get_for_update(&self, txn: &HybridTxn, key: u32) -> Result<Option<i64>, LockError> {
        // @begin 4d-c6
        self.lock_for_write(txn, key)?;
        let st = self.state.lock().unwrap();
        if let Some(v) = st.pending.get(&txn.id).and_then(|w| w.get(&key)) {
            return Ok(Some(*v));
        }
        Ok(st.versions.get(&key).and_then(|v| v.last()).map(|(_, v)| *v))
        //~ todo!("4d-c6: lock first; then read the newest committed version, whatever the snapshot says")
        // @end
    }

    /// Installs the writes at a new commit timestamp, then lets go of every lock. Returns the timestamp.
    pub fn commit(&self, txn: HybridTxn) -> u64 {
        // @begin 4d-c6
        let ts = {
            let mut st = self.state.lock().unwrap();
            st.clock += 1;
            let ts = st.clock;
            for (key, value) in st.pending.remove(&txn.id).unwrap_or_default() {
                st.versions.entry(key).or_default().push((ts, value));
            }
            ts
        };
        txn.lock.set_state(crate::concurrency::lock_txn::LockState::Committed);
        self.locks.release_all(&txn.lock);
        ts
        //~ todo!("4d-c6: install the buffered writes at a new timestamp, then release the locks")
        // @end
    }

    /// Throws the writes away and lets go of every lock.
    pub fn abort(&self, txn: HybridTxn) {
        // @begin 4d-c6
        self.state.lock().unwrap().pending.remove(&txn.id);
        txn.lock.set_state(crate::concurrency::lock_txn::LockState::Aborted);
        self.locks.release_all(&txn.lock);
        //~ todo!("4d-c6: forget the writes, release the locks")
        // @end
    }
}
'''),
  test=("tests/stages_4d.rs", '''
use bustub::concurrency::deadlock::DeadlockDetector;
use bustub::concurrency::hybrid_store::HybridStore;
use bustub::concurrency::lock_error::LockErrorKind;
use bustub::concurrency::lock_manager::LockManager;
use std::collections::HashMap;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::time::Duration;

fn finish_within<T: Send + 'static>(secs: u64, what: &'static str, f: impl FnOnce() -> T + Send + 'static) -> T {
    let (tx, rx) = std::sync::mpsc::channel();
    std::thread::spawn(move || {
        let _ = tx.send(f());
    });
    rx.recv_timeout(Duration::from_secs(secs)).unwrap_or_else(|_| panic!("{what}: did not finish in {secs}s (a wait that never ends?)"))
}

fn store_with(rows: &[(u32, i64)]) -> Arc<HybridStore> {
    let s = Arc::new(HybridStore::new(Arc::new(LockManager::new())));
    let t = s.begin();
    for &(k, v) in rows {
        s.put(&t, k, v).unwrap();
    }
    s.commit(t);
    s
}

#[test]
fn s4d_c6_a_reader_keeps_its_snapshot_while_others_commit() {
    let s = store_with(&[(1, 10)]);
    let (a, b) = (s.begin(), s.begin());
    s.put(&b, 1, 50).unwrap();
    s.commit(b);
    assert_eq!(s.get(&a, 1), Some(10), "a began before b committed");
    let c = s.begin();
    assert_eq!(s.get(&c, 1), Some(50));
    assert_eq!(s.get(&a, 1), Some(10), "and keeps reading the same value");
    assert_eq!(s.get(&a, 2), None);
}

#[test]
fn s4d_c6_a_read_does_not_wait_for_a_writer_holding_the_row() {
    let s = store_with(&[(1, 10)]);
    let w = s.begin();
    s.put(&w, 1, 99).unwrap();
    let s2 = s.clone();
    let seen = finish_within(5, "a snapshot read", move || {
        let r = s2.begin();
        s2.get(&r, 1)
    });
    assert_eq!(seen, Some(10), "the writer's uncommitted 99 must not be visible");
    assert_eq!(s.get(&w, 1), Some(99), "a writer sees its own write");
    s.abort(w);
}

#[test]
fn s4d_c6_a_second_writer_waits_instead_of_aborting() {
    let s = store_with(&[(1, 0)]);
    let w1 = s.begin();
    s.put(&w1, 1, 1).unwrap();
    let done = Arc::new(AtomicBool::new(false));
    let h = {
        let (s, done) = (s.clone(), done.clone());
        std::thread::spawn(move || {
            let w2 = s.begin();
            s.put(&w2, 1, 2).unwrap();
            done.store(true, Ordering::SeqCst);
            s.commit(w2);
        })
    };
    std::thread::sleep(Duration::from_millis(100));
    assert!(!done.load(Ordering::SeqCst), "the second writer must wait for the row, not run ahead");
    s.commit(w1);
    finish_within(5, "second writer", move || h.join().unwrap());
    let r = s.begin();
    assert_eq!(s.get(&r, 1), Some(2), "the writer that waited committed last");
}

#[test]
fn s4d_c6_abort_discards_the_writes_and_frees_the_row() {
    let s = store_with(&[(1, 10)]);
    let w = s.begin();
    s.put(&w, 1, 77).unwrap();
    s.abort(w);
    let s2 = s.clone();
    finish_within(5, "a writer after an abort", move || {
        let t = s2.begin();
        assert_eq!(s2.get(&t, 1), Some(10));
        s2.put(&t, 1, 11).unwrap();
        s2.commit(t);
    });
    let r = s.begin();
    assert_eq!(s.get(&r, 1), Some(11));
}

#[test]
fn s4d_c6_for_update_reads_the_newest_committed_value_not_the_snapshot() {
    let s = store_with(&[(1, 0)]);
    let a = s.begin();
    assert_eq!(s.get(&a, 1), Some(0));
    let b = s.begin();
    s.put(&b, 1, 5).unwrap();
    s.commit(b);
    assert_eq!(s.get(&a, 1), Some(0), "the snapshot still says 0");
    assert_eq!(s.get_for_update(&a, 1), Ok(Some(5)), "but the locked read must see what is really there");
    s.put(&a, 1, 6).unwrap();
    s.commit(a);
    let r = s.begin();
    assert_eq!(s.get(&r, 1), Some(6), "an increment on top of 5, not on top of the stale 0");
}

#[test]
fn s4d_c6_increments_from_many_threads_are_not_lost() {
    let s = store_with(&[(1, 0)]);
    finish_within(30, "counter", {
        let s = s.clone();
        move || {
            let hs: Vec<_> = (0..4)
                .map(|_| {
                    let s = s.clone();
                    std::thread::spawn(move || {
                        for _ in 0..50 {
                            let t = s.begin();
                            let v = s.get_for_update(&t, 1).unwrap().unwrap_or(0);
                            s.put(&t, 1, v + 1).unwrap();
                            s.commit(t);
                        }
                    })
                })
                .collect();
            for h in hs {
                h.join().unwrap();
            }
        }
    });
    let r = s.begin();
    assert_eq!(s.get(&r, 1), Some(200));
}

#[test]
fn s4d_c6_a_deadlock_is_broken_and_the_survivor_commits() {
    let locks = Arc::new(LockManager::new());
    let _detector = DeadlockDetector::start(locks.clone(), Duration::from_millis(15));
    let s = Arc::new(HybridStore::new(locks));
    let (a, b) = (s.begin(), s.begin());
    s.put(&a, 1, 1).unwrap();
    s.put(&b, 2, 2).unwrap();
    let (s1, s2) = (s.clone(), s.clone());
    let ha = std::thread::spawn(move || {
        let r = s1.put(&a, 2, 10);
        match r {
            Ok(()) => {
                s1.commit(a);
                None
            }
            Err(e) => {
                s1.abort(a);
                Some(e.kind)
            }
        }
    });
    let hb = std::thread::spawn(move || {
        let r = s2.put(&b, 1, 20);
        match r {
            Ok(()) => {
                s2.commit(b);
                None
            }
            Err(e) => {
                s2.abort(b);
                Some(e.kind)
            }
        }
    });
    let (ra, rb) = finish_within(20, "deadlock", move || (ha.join().unwrap(), hb.join().unwrap()));
    let victims: Vec<_> = [ra, rb].into_iter().flatten().collect();
    assert_eq!(victims, vec![LockErrorKind::Deadlock], "exactly one transaction is the victim; the other commits");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 64, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: sequential transactions agree with a map; a reader opened at the start never sees any of them.
    #[test]
    fn s4d_c6_property_sequential_transactions_match_a_map_and_old_snapshots_stay_old(txns in proptest::collection::vec((proptest::collection::vec((0u32..5, -50i64..50), 0..4), any::<bool>()), 0..12)) {
        let s = store_with(&[(0, 100), (1, 101)]);
        let old = s.begin();
        let mut model: HashMap<u32, i64> = HashMap::from([(0, 100), (1, 101)]);
        for (writes, commit) in txns {
            let t = s.begin();
            for &(k, v) in &writes { s.put(&t, k, v).unwrap(); }
            if commit {
                for &(k, v) in &writes { model.insert(k, v); }
                s.commit(t);
            } else {
                s.abort(t);
            }
            prop_assert_eq!(s.get(&old, 0), Some(100));
            prop_assert_eq!(s.get(&old, 1), Some(101));
            prop_assert_eq!(s.get(&old, 4), None);
        }
        let r = s.begin();
        for k in 0..5 { prop_assert_eq!(s.get(&r, k), model.get(&k).copied()); }
    }
}
''')))

CH.append(C("4d-c7", M4D, "96-challenge-the-anomaly-lab", "build", "Challenge: the anomaly lab", "medium", "stages_4d::s4d_c7",
  ["telling the classic anomalies apart by building each one","which isolation level prevents which anomaly, and by what mechanism"],
  ["lock-modes-and-two-phase-locking","model-based-testing","property-testing-and-fuzzing"],
  "A small database `LabDb` (given, in `src/concurrency/lab_db.rs`) that runs at one of five isolation levels and is driven one step at a time, so a transaction that would have to wait says `Blocked` instead of waiting. In `src/concurrency/anomaly_lab.rs` you write five **scenarios**, one per anomaly: dirty read, non-repeatable read, lost update, write skew and phantom. Each plays a few transactions against the database and returns whether the anomaly **actually happened**, whatever the level. Then you write `possible(level, anomaly)`: your prediction of the table, which the tests compare with what the scenarios observe.",
  "Isolation levels are easy to recite and hard to apply: \"repeatable read prevents non-repeatable reads\" is a tautology until you can name the interleaving, and the surprising entries (a locking repeatable read stops write skew, a snapshot does not; a snapshot stops phantoms, row locks do not) are exactly the ones the names hide. Building each anomaly as an interleaving is how the mechanisms stick: every \"no\" in the table is a lock that blocks or a version that is not visible.",
  ["The levels, mechanically: **read uncommitted** reads other transactions' uncommitted writes and takes no read locks; **read committed** reads the newest committed value; **repeatable read** takes a shared row lock on every row it reads and holds it to the end; **snapshot** reads as of its start and aborts a writer whose row was committed over since it began (first committer wins); **serializable** is repeatable read plus a lock on the whole scanned range, so inserts into a scanned range are blocked.","Writes take an exclusive row lock at every level. A step that conflicts returns `Blocked` and changes nothing; a transaction that is aborted (by snapshot's rule) returns `Aborted` and is finished.","Starting data (the tests load it): dirty read and non-repeatable read: `{1: 100}`; lost update: `{1: 0}`; write skew: `{1: 1, 2: 1}` (two doctors on call; at least one must stay); phantom: `{1: 10, 2: 20}`.","Each scenario must finish every transaction it starts (commit or abort) and must cope with `Blocked` and `Aborted`: a step that was prevented means the anomaly did not happen, not that the scenario failed.","`possible(level, anomaly)` is true when that level lets the anomaly happen."],
  ["A scenario returns `true` only if the interleaving really produced the anomaly (the two reads differ, the update is gone, the constraint is broken).","No transaction is left open when a scenario returns."],
  ["At read uncommitted every anomaly is possible; each level above prevents at least one more.","If `possible(level, a)` is false then the scenario for `a` returns false at `level`, and the other way round.","Lock-based repeatable read and snapshot differ in exactly two anomalies, in opposite directions."],
  ["dirty read at read committed: the reader sees 100, not the 999 that was written and rolled back -> false","phantom at snapshot: both scans return the same two rows, the inserted row 50 is not in the snapshot -> false"],
  ["Each anomaly at each of the five levels (25 observations).","Your table against what the scenarios saw.","Every transaction finished."],
  src=("src/concurrency/anomaly_lab.rs", '''
//! The anomaly lab: five scenarios and a table.

use crate::concurrency::lab_db::{LabDb, Level};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Anomaly {
    DirtyRead,
    NonRepeatableRead,
    LostUpdate,
    WriteSkew,
    Phantom,
}

/// Rows `{1: 100}`. True when a transaction read a value another one wrote and never committed.
pub fn dirty_read(db: &mut LabDb) -> bool {
    // @begin 4d-c7
    let (writer, reader) = (db.begin(), db.begin());
    let mut saw_uncommitted = false;
    if db.write(writer, 1, 999).is_ok() {
        if let Ok(Some(v)) = db.read(reader, 1) {
            saw_uncommitted = v == 999;
        }
    }
    db.abort(writer);
    db.abort(reader);
    saw_uncommitted
    //~ let _ = db;
    //~ todo!("4d-c7: one transaction writes and does not commit; another reads; did it see the write?")
    // @end
}

/// Rows `{1: 100}`. True when one transaction read the same row twice and got two different answers.
pub fn non_repeatable_read(db: &mut LabDb) -> bool {
    // @begin 4d-c7
    let (a, b) = (db.begin(), db.begin());
    let first = db.read(a, 1);
    if db.write(b, 1, 200).is_ok() {
        let _ = db.commit(b);
    }
    let second = db.read(a, 1);
    db.abort(a);
    db.abort(b);
    matches!((first, second), (Ok(x), Ok(y)) if x != y)
    //~ let _ = db;
    //~ todo!("4d-c7: read, let another transaction change the row and commit, read again")
    // @end
}

/// Rows `{1: 0}`. Two transactions each read the row and write it back plus one. True when both commit and the row ended at 1, not 2.
pub fn lost_update(db: &mut LabDb) -> bool {
    // @begin 4d-c7
    let (a, b) = (db.begin(), db.begin());
    let (Ok(x), Ok(y)) = (db.read(a, 1), db.read(b, 1)) else {
        db.abort(a);
        db.abort(b);
        return false;
    };
    let (x, y) = (x.unwrap_or(0), y.unwrap_or(0));
    let a_done = db.write(a, 1, x + 1).is_ok() && db.commit(a).is_ok();
    if !a_done {
        db.abort(a);
    }
    let b_done = db.write(b, 1, y + 1).is_ok() && db.commit(b).is_ok();
    if !b_done {
        db.abort(b);
    }
    a_done && b_done && db.committed(1) == Some(1)
    //~ let _ = db;
    //~ todo!("4d-c7: both read, both write the value plus one, both commit; what is the row now?")
    // @end
}

/// Rows `{1: 1, 2: 1}` (two doctors on call; at least one must stay). Each transaction reads both rows and, seeing two on call, takes one
/// itself off. True when both commit and nobody is on call.
pub fn write_skew(db: &mut LabDb) -> bool {
    // @begin 4d-c7
    fn on_call(db: &mut LabDb, t: usize) -> Option<i64> {
        Some(db.read(t, 1).ok()?.unwrap_or(0) + db.read(t, 2).ok()?.unwrap_or(0))
    }
    let (a, b) = (db.begin(), db.begin());
    let (sa, sb) = (on_call(db, a), on_call(db, b));
    let a_done = sa >= Some(2) && db.write(a, 1, 0).is_ok() && db.commit(a).is_ok();
    if !a_done {
        db.abort(a);
    }
    let b_done = sb >= Some(2) && db.write(b, 2, 0).is_ok() && db.commit(b).is_ok();
    if !b_done {
        db.abort(b);
    }
    a_done && b_done && db.committed(1).unwrap_or(0) + db.committed(2).unwrap_or(0) == 0
    //~ let _ = db;
    //~ todo!("4d-c7: both check the constraint, each writes a different row, both commit")
    // @end
}

/// Rows `{1: 10, 2: 20}`. One transaction scans keys 0 to 100 twice; between the scans another inserts key 50 and commits. True when the
/// two scans differ.
pub fn phantom(db: &mut LabDb) -> bool {
    // @begin 4d-c7
    let (a, b) = (db.begin(), db.begin());
    let first = db.scan(a, 0, 100);
    if db.write(b, 50, 30).is_ok() {
        let _ = db.commit(b);
    }
    let second = db.scan(a, 0, 100);
    db.abort(a);
    db.abort(b);
    matches!((first, second), (Ok(x), Ok(y)) if x != y)
    //~ let _ = db;
    //~ todo!("4d-c7: scan a range, let another transaction insert into it and commit, scan again")
    // @end
}

/// Your prediction: can `anomaly` happen at `level`? The tests compare it with what the scenarios observed.
pub fn possible(level: Level, anomaly: Anomaly) -> bool {
    // @begin 4d-c7
    use Anomaly::*;
    use Level::*;
    match (level, anomaly) {
        (ReadUncommitted, _) => true,
        (_, DirtyRead) => false,
        (ReadCommitted, _) => true,
        (_, NonRepeatableRead | LostUpdate) => false,
        (Snapshot, WriteSkew) => true,
        (RepeatableRead, Phantom) => true,
        _ => false,
    }
    //~ let _ = (level, anomaly);
    //~ todo!("4d-c7: from the mechanism of each level, not from memory of a table")
    // @end
}
'''),
  extra=[("src/concurrency/lab_db.rs", '''
//! A tiny database that runs at one of five isolation levels, one step at a time. Given code: the apparatus of the anomaly lab.
//!
//! There are no threads. A scenario plays several transactions by calling them in the order it likes. A step that would have to wait
//! returns `Blocked` instead of waiting, and changes nothing.

use std::collections::{BTreeMap, BTreeSet};

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
pub enum Level {
    ReadUncommitted,
    ReadCommitted,
    /// Shared row locks on everything read, held to the end (strict two-phase locking on rows).
    RepeatableRead,
    /// Reads as of the start; first committer wins.
    Snapshot,
    /// Repeatable read plus a lock on the whole range a scan covered.
    Serializable,
}

impl Level {
    pub const ALL: [Level; 5] = [Level::ReadUncommitted, Level::ReadCommitted, Level::RepeatableRead, Level::Snapshot, Level::Serializable];
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum LabError {
    /// The step would have to wait for another transaction. Nothing changed; the transaction is still open.
    Blocked,
    /// The transaction is finished (aborted by the database, or already ended).
    Aborted,
}

/// A transaction handle.
pub type Tx = usize;

#[derive(Default)]
struct Txn {
    read_ts: u64,
    writes: BTreeMap<i64, i64>,
    read_locks: BTreeSet<i64>,
    scanned: bool,
    open: bool,
}

pub struct LabDb {
    level: Level,
    clock: u64,
    versions: BTreeMap<i64, Vec<(u64, i64)>>,
    txns: Vec<Txn>,
}

impl LabDb {
    /// A database at `level` holding `rows`, all committed before any transaction begins.
    pub fn new(level: Level, rows: &[(i64, i64)]) -> LabDb {
        let versions = rows.iter().map(|&(k, v)| (k, vec![(0, v)])).collect();
        LabDb { level, clock: 0, versions, txns: Vec::new() }
    }

    pub fn begin(&mut self) -> Tx {
        self.txns.push(Txn { read_ts: self.clock, open: true, ..Txn::default() });
        self.txns.len() - 1
    }

    fn check(&self, tx: Tx) -> Result<(), LabError> {
        match self.txns.get(tx) {
            Some(t) if t.open => Ok(()),
            _ => Err(LabError::Aborted),
        }
    }

    fn latest(&self, key: i64) -> Option<i64> {
        self.versions.get(&key).and_then(|v| v.last()).map(|x| x.1)
    }

    fn latest_ts(&self, key: i64) -> u64 {
        self.versions.get(&key).and_then(|v| v.last()).map_or(0, |x| x.0)
    }

    fn as_of(&self, key: i64, ts: u64) -> Option<i64> {
        self.versions.get(&key).and_then(|v| v.iter().rev().find(|(t, _)| *t <= ts)).map(|x| x.1)
    }

    fn others(&self, tx: Tx) -> impl Iterator<Item = &Txn> {
        self.txns.iter().enumerate().filter(move |(i, t)| *i != tx && t.open).map(|(_, t)| t)
    }

    fn locks_reads(&self) -> bool {
        matches!(self.level, Level::RepeatableRead | Level::Serializable)
    }

    /// The value of `key` as `tx` sees it.
    pub fn read(&mut self, tx: Tx, key: i64) -> Result<Option<i64>, LabError> {
        self.check(tx)?;
        if let Some(&v) = self.txns[tx].writes.get(&key) {
            return Ok(Some(v));
        }
        match self.level {
            Level::ReadUncommitted => {
                if let Some(v) = self.others(tx).find_map(|t| t.writes.get(&key).copied()) {
                    return Ok(Some(v));
                }
                Ok(self.latest(key))
            }
            Level::ReadCommitted => Ok(self.latest(key)),
            Level::RepeatableRead | Level::Serializable => {
                if self.others(tx).any(|t| t.writes.contains_key(&key)) {
                    return Err(LabError::Blocked);
                }
                self.txns[tx].read_locks.insert(key);
                Ok(self.latest(key))
            }
            Level::Snapshot => Ok(self.as_of(key, self.txns[tx].read_ts)),
        }
    }

    /// Sets `key` (an insert when it does not exist yet).
    pub fn write(&mut self, tx: Tx, key: i64, value: i64) -> Result<(), LabError> {
        self.check(tx)?;
        if self.others(tx).any(|t| t.writes.contains_key(&key)) {
            return Err(LabError::Blocked);
        }
        if self.locks_reads() && self.others(tx).any(|t| t.read_locks.contains(&key)) {
            return Err(LabError::Blocked);
        }
        if self.level == Level::Serializable && self.latest(key).is_none() && self.others(tx).any(|t| t.scanned) {
            return Err(LabError::Blocked);
        }
        if self.level == Level::Snapshot && self.latest_ts(key) > self.txns[tx].read_ts {
            self.finish(tx);
            return Err(LabError::Aborted);
        }
        self.txns[tx].writes.insert(key, value);
        Ok(())
    }

    /// All rows with `lo <= key <= hi`, in key order, as `tx` sees them.
    pub fn scan(&mut self, tx: Tx, lo: i64, hi: i64) -> Result<Vec<(i64, i64)>, LabError> {
        self.check(tx)?;
        let mut rows: BTreeMap<i64, i64> = BTreeMap::new();
        for &k in self.versions.keys().filter(|k| (lo..=hi).contains(*k)) {
            let v = if self.level == Level::Snapshot { self.as_of(k, self.txns[tx].read_ts) } else { self.latest(k) };
            if let Some(v) = v {
                rows.insert(k, v);
            }
        }
        match self.level {
            Level::ReadUncommitted => {
                for t in self.others(tx) {
                    for (&k, &v) in t.writes.range(lo..=hi) {
                        rows.insert(k, v);
                    }
                }
            }
            Level::RepeatableRead | Level::Serializable => {
                if self.others(tx).any(|t| t.writes.range(lo..=hi).next().is_some()) {
                    return Err(LabError::Blocked);
                }
                let keys: Vec<i64> = rows.keys().copied().collect();
                self.txns[tx].read_locks.extend(keys);
                if self.level == Level::Serializable {
                    self.txns[tx].scanned = true;
                }
            }
            _ => {}
        }
        for (&k, &v) in self.txns[tx].writes.range(lo..=hi) {
            rows.insert(k, v);
        }
        Ok(rows.into_iter().collect())
    }

    fn finish(&mut self, tx: Tx) {
        let t = &mut self.txns[tx];
        t.open = false;
        t.writes.clear();
        t.read_locks.clear();
        t.scanned = false;
    }

    /// Makes the writes visible and ends the transaction. At snapshot a row committed over since the start aborts it instead.
    pub fn commit(&mut self, tx: Tx) -> Result<(), LabError> {
        self.check(tx)?;
        if self.level == Level::Snapshot {
            let read_ts = self.txns[tx].read_ts;
            if self.txns[tx].writes.keys().any(|&k| self.latest_ts(k) > read_ts) {
                self.finish(tx);
                return Err(LabError::Aborted);
            }
        }
        self.clock += 1;
        let writes = std::mem::take(&mut self.txns[tx].writes);
        for (k, v) in writes {
            self.versions.entry(k).or_default().push((self.clock, v));
        }
        self.finish(tx);
        Ok(())
    }

    /// Ends the transaction and throws its writes away. Does nothing for a transaction that is already finished.
    pub fn abort(&mut self, tx: Tx) {
        if self.txns.get(tx).is_some_and(|t| t.open) {
            self.finish(tx);
        }
    }

    /// The newest committed value of `key`, for checking the outcome.
    pub fn committed(&self, key: i64) -> Option<i64> {
        self.latest(key)
    }

    /// How many transactions are still open.
    pub fn open_count(&self) -> usize {
        self.txns.iter().filter(|t| t.open).count()
    }
}
''')],
  test=("tests/stages_4d.rs", '''
use bustub::concurrency::anomaly_lab::{dirty_read, lost_update, non_repeatable_read, phantom, possible, write_skew, Anomaly};
use bustub::concurrency::lab_db::{LabDb, Level, Level::*};

/// The textbook table for the five levels of the lab database: `true` where the anomaly can happen.
fn truth(level: Level, a: Anomaly) -> bool {
    use Anomaly::*;
    match (level, a) {
        (ReadUncommitted, _) => true,
        (_, DirtyRead) => false,
        (ReadCommitted, _) => true,
        (_, NonRepeatableRead | LostUpdate) => false,
        (Snapshot, WriteSkew) => true,
        (RepeatableRead, Phantom) => true,
        _ => false,
    }
}

fn observe(level: Level, rows: &[(i64, i64)], scenario: fn(&mut LabDb) -> bool) -> bool {
    let mut db = LabDb::new(level, rows);
    let happened = scenario(&mut db);
    assert_eq!(db.open_count(), 0, "{level:?}: the scenario left a transaction open");
    happened
}

fn check(a: Anomaly, rows: &[(i64, i64)], scenario: fn(&mut LabDb) -> bool) {
    for level in Level::ALL {
        assert_eq!(observe(level, rows, scenario), truth(level, a), "{a:?} at {level:?}");
    }
}

#[test]
fn s4d_c7_a_dirty_read_is_reading_a_write_that_never_committed() {
    check(Anomaly::DirtyRead, &[(1, 100)], dirty_read);
}

#[test]
fn s4d_c7_a_non_repeatable_read_is_two_reads_of_one_row_that_differ() {
    check(Anomaly::NonRepeatableRead, &[(1, 100)], non_repeatable_read);
}

#[test]
fn s4d_c7_a_lost_update_is_two_increments_that_add_up_to_one() {
    check(Anomaly::LostUpdate, &[(1, 0)], lost_update);
}

#[test]
fn s4d_c7_write_skew_breaks_a_constraint_that_each_transaction_kept() {
    check(Anomaly::WriteSkew, &[(1, 1), (2, 1)], write_skew);
}

#[test]
fn s4d_c7_a_phantom_is_a_row_that_appears_in_a_range_you_already_read() {
    check(Anomaly::Phantom, &[(1, 10), (2, 20)], phantom);
}

#[test]
fn s4d_c7_your_table_agrees_with_what_the_scenarios_saw() {
    use Anomaly::*;
    for level in Level::ALL {
        for a in [DirtyRead, NonRepeatableRead, LostUpdate, WriteSkew, Phantom] {
            assert_eq!(possible(level, a), truth(level, a), "possible({level:?}, {a:?})");
        }
    }
}
''')))
