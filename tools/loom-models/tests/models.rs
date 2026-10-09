#![cfg(loom)]
//! Loom models of the course's concurrency protocols: every interleaving of the threads is explored.

use loom::sync::atomic::{AtomicI64, Ordering};
use loom::sync::{Arc, Mutex};
use loom::thread;

// ---- Presto HyperLogLog: raising a register is read, compare, write ----------------------------------------------------------------------

/// The buggy shape: read under one lock, write under another.
fn raise_two_locks(reg: &Mutex<u32>, v: u32) {
    let current = *reg.lock().unwrap();
    if v > current {
        *reg.lock().unwrap() = v;
    }
}

/// The shipped shape: the compare is inside the critical section that writes.
fn raise_one_lock(reg: &Mutex<u32>, v: u32) {
    let mut r = reg.lock().unwrap();
    if v > *r {
        *r = v;
    }
}

#[test]
fn hll_register_never_loses_the_larger_run_with_one_lock() {
    loom::model(|| {
        let reg = Arc::new(Mutex::new(0u32));
        let hs: Vec<_> = [5u32, 20].into_iter().map(|v| { let r = reg.clone(); thread::spawn(move || raise_one_lock(&r, v)) }).collect();
        hs.into_iter().for_each(|h| h.join().unwrap());
        assert_eq!(*reg.lock().unwrap(), 20);
    });
}

#[test]
#[should_panic]
fn hll_register_can_lose_the_larger_run_with_two_locks() {
    loom::model(|| {
        let reg = Arc::new(Mutex::new(0u32));
        let hs: Vec<_> = [5u32, 20].into_iter().map(|v| { let r = reg.clone(); thread::spawn(move || raise_two_locks(&r, v)) }).collect();
        hs.into_iter().for_each(|h| h.join().unwrap());
        assert_eq!(*reg.lock().unwrap(), 20);
    });
}

// ---- TrieStore: two writers must take turns -----------------------------------------------------------------------------------------

struct Store {
    root: Mutex<Vec<u32>>,  // the current "version" (a persistent trie in the real code)
    write_lock: Mutex<()>,
}

impl Store {
    fn put_serialised(&self, v: u32) {
        let _w = self.write_lock.lock().unwrap();
        let mut next = self.root.lock().unwrap().clone();
        next.push(v);
        *self.root.lock().unwrap() = next;
    }
    fn put_unserialised(&self, v: u32) {
        let mut next = self.root.lock().unwrap().clone();
        next.push(v);
        *self.root.lock().unwrap() = next;
    }
}

#[test]
fn trie_store_with_a_write_lock_loses_no_update() {
    loom::model(|| {
        let s = Arc::new(Store { root: Mutex::new(vec![]), write_lock: Mutex::new(()) });
        let hs: Vec<_> = [1u32, 2].into_iter().map(|v| { let s = s.clone(); thread::spawn(move || s.put_serialised(v)) }).collect();
        hs.into_iter().for_each(|h| h.join().unwrap());
        assert_eq!(s.root.lock().unwrap().len(), 2);
    });
}

#[test]
#[should_panic]
fn trie_store_without_the_write_lock_loses_an_update() {
    loom::model(|| {
        let s = Arc::new(Store { root: Mutex::new(vec![]), write_lock: Mutex::new(()) });
        let hs: Vec<_> = [1u32, 2].into_iter().map(|v| { let s = s.clone(); thread::spawn(move || s.put_unserialised(v)) }).collect();
        hs.into_iter().for_each(|h| h.join().unwrap());
        assert_eq!(s.root.lock().unwrap().len(), 2);
    });
}

// ---- MVCC: begin and commit -----------------------------------------------------------------------------------------------------

/// The watermark's lock covers (last commit ts, readers). `begin` reads the last commit and registers under it; `commit` stamps the tuple
/// first, then publishes the commit under the same lock.
struct Mgr {
    inner: Mutex<(i64, Vec<i64>)>, // (watermark commit_ts == last_commit_ts, read timestamps of running transactions)
    tuple_ts: AtomicI64,           // the tuple's timestamp: a temp ts (huge) until commit stamps it
}

const TEMP: i64 = 1 << 62;

impl Mgr {
    fn begin(&self) -> i64 {
        let mut g = self.inner.lock().unwrap();
        let read_ts = g.0;
        assert!(read_ts >= g.0, "read ts < commit ts");
        g.1.push(read_ts);
        read_ts
    }
    fn commit(&self) {
        let commit_ts = self.inner.lock().unwrap().0 + 1; // (the commit mutex makes this the only committer)
        self.tuple_ts.store(commit_ts, Ordering::SeqCst); // stamp the tuple
        let mut g = self.inner.lock().unwrap();
        g.0 = commit_ts; // publish
    }
}

#[test]
fn a_transaction_that_begins_after_a_commit_sees_the_stamped_tuple() {
    loom::model(|| {
        let m = Arc::new(Mgr { inner: Mutex::new((0, vec![])), tuple_ts: AtomicI64::new(TEMP) });
        let committer = { let m = m.clone(); thread::spawn(move || m.commit()) };
        let reader = {
            let m = m.clone();
            thread::spawn(move || {
                let read_ts = m.begin();
                let ts = m.tuple_ts.load(Ordering::SeqCst);
                // visible iff ts <= read_ts; if the reader began after the commit it must see the tuple, and a temp ts is never visible
                if read_ts >= 1 {
                    assert!(ts <= read_ts, "began after the commit but the tuple is not stamped yet");
                }
                assert!(ts == TEMP || ts == 1);
            })
        };
        committer.join().unwrap();
        reader.join().unwrap();
    });
}

#[test]
#[should_panic]
fn publishing_before_stamping_would_hand_out_an_unstamped_tuple() {
    loom::model(|| {
        let m = Arc::new(Mgr { inner: Mutex::new((0, vec![])), tuple_ts: AtomicI64::new(TEMP) });
        let committer = {
            let m = m.clone();
            thread::spawn(move || {
                let commit_ts = 1;
                m.inner.lock().unwrap().0 = commit_ts; // wrong order: publish first
                m.tuple_ts.store(commit_ts, Ordering::SeqCst); // then stamp
            })
        };
        let reader = {
            let m = m.clone();
            thread::spawn(move || {
                let read_ts = m.begin();
                let ts = m.tuple_ts.load(Ordering::SeqCst);
                if read_ts >= 1 {
                    assert!(ts <= read_ts, "began after the commit but the tuple is not stamped yet");
                }
            })
        };
        committer.join().unwrap();
        reader.join().unwrap();
    });
}

// ---- write-write conflict: the check and the write are one critical section ------------------------------------------------------------------

#[test]
fn of_two_writers_with_the_same_read_ts_exactly_one_writes() {
    loom::model(|| {
        let tuple = Arc::new(Mutex::new(0i64)); // the page latch protects the tuple's ts
        let won = Arc::new(AtomicI64::new(0));
        let hs: Vec<_> = [TEMP + 1, TEMP + 2]
            .into_iter()
            .map(|me| {
                let (tuple, won) = (tuple.clone(), won.clone());
                thread::spawn(move || {
                    let read_ts = 0;
                    let mut ts = tuple.lock().unwrap(); // check and write under the latch
                    let conflict = *ts != me && *ts > read_ts;
                    if !conflict {
                        *ts = me;
                        won.fetch_add(1, Ordering::SeqCst);
                    }
                })
            })
            .collect();
        hs.into_iter().for_each(|h| h.join().unwrap());
        assert_eq!(won.load(Ordering::SeqCst), 1);
    });
}

#[test]
#[should_panic]
fn checking_outside_the_latch_lets_both_writers_in() {
    loom::model(|| {
        let tuple = Arc::new(Mutex::new(0i64));
        let won = Arc::new(AtomicI64::new(0));
        let hs: Vec<_> = [TEMP + 1, TEMP + 2]
            .into_iter()
            .map(|me| {
                let (tuple, won) = (tuple.clone(), won.clone());
                thread::spawn(move || {
                    let seen = *tuple.lock().unwrap(); // read the ts, release the latch
                    if !(seen != me && seen > 0) {
                        *tuple.lock().unwrap() = me; // write later: a second writer got in between
                        won.fetch_add(1, Ordering::SeqCst);
                    }
                })
            })
            .collect();
        hs.into_iter().for_each(|h| h.join().unwrap());
        assert_eq!(won.load(Ordering::SeqCst), 1);
    });
}
