//! Tests for module 4d, the lock manager. A test name starts with its stage: `s4d_03_…` belongs to stage 4d-03.
//!
//! Stages 1 and 2 are exact tables and a model; stages 3 and 4 start threads and look at who waits and who goes first (a thread that waits
//! forever fails the test after ten seconds instead of hanging it); stage 5 checks the rules of each isolation level; stage 6 builds the
//! waits-for graph and breaks real deadlocks; the last stage runs workloads of many threads and checks the history they leave.

use std::collections::{BTreeSet, HashMap, HashSet};
use std::sync::atomic::{AtomicBool, AtomicI64, AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use proptest::prelude::*;

use bustub::common::config::PageId;
use bustub::common::rid::Rid;
use bustub::concurrency::deadlock::{DeadlockDetector, WaitsForGraph};
use bustub::concurrency::lock_error::{LockError, LockErrorKind};
use bustub::concurrency::lock_manager::{LockManager, Resource};
use bustub::concurrency::lock_mode::{can_upgrade, compatible, LockMode};
use bustub::concurrency::lock_queue::LockQueue;
use bustub::concurrency::lock_txn::{LockIsolation, LockState, LockTxn};
use bustub::concurrency::transaction::TxnId;

use LockMode::*;

const ALL: [LockMode; 5] = [IntentionShared, IntentionExclusive, Shared, SharedIntentionExclusive, Exclusive];

fn config() -> ProptestConfig {
    ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() }
}

fn any_mode() -> impl Strategy<Value = LockMode> {
    prop::sample::select(ALL.to_vec())
}

/// The textbook compatibility table, written out independently of the code under test. Rows and columns: IS, IX, S, SIX, X.
fn truth(a: LockMode, b: LockMode) -> bool {
    const T: [[bool; 5]; 5] = [
        [true, true, true, true, false],
        [true, true, false, false, false],
        [true, false, true, false, false],
        [true, false, false, false, false],
        [false, false, false, false, false],
    ];
    let ix = |m: LockMode| ALL.iter().position(|&x| x == m).unwrap();
    T[ix(a)][ix(b)]
}

/// Runs `f` on its own thread and fails the test, instead of hanging, if it does not finish: a thread that waits for a lock that is never
/// granted or a wake-up that never comes.
fn finish_within<T: Send + 'static>(what: &str, f: impl FnOnce() -> T + Send + 'static) -> T {
    let (tx, rx) = std::sync::mpsc::channel();
    thread::spawn(move || {
        let _ = tx.send(std::panic::catch_unwind(std::panic::AssertUnwindSafe(f)));
    });
    match rx.recv_timeout(Duration::from_secs(20)) {
        Ok(Ok(value)) => value,
        Ok(Err(panic)) => std::panic::resume_unwind(panic),
        Err(_) => panic!("{what}: still going after 20 seconds. A lock request is waiting for a grant that never comes, or a thread was never woken."),
    }
}

fn pause() {
    thread::sleep(Duration::from_millis(80));
}

fn table(n: u32) -> Resource {
    Resource::Table(n)
}

fn rid(n: u32) -> Rid {
    Rid::new(PageId(0), n)
}

fn row(t: u32, n: u32) -> Resource {
    Resource::Row(t, rid(n))
}

fn kind<T: std::fmt::Debug>(r: Result<T, LockError>) -> LockErrorKind {
    r.expect_err("expected an error").kind
}

/// Starts `f` on a thread and returns a flag that says whether it has finished, and the handle.
fn spawn_flag<T: Send + 'static>(f: impl FnOnce() -> T + Send + 'static) -> (Arc<AtomicBool>, thread::JoinHandle<T>) {
    let done = Arc::new(AtomicBool::new(false));
    let d = Arc::clone(&done);
    let h = thread::spawn(move || {
        let r = f();
        d.store(true, Ordering::SeqCst);
        r
    });
    (done, h)
}

fn finished(flag: &AtomicBool) -> bool {
    flag.load(Ordering::SeqCst)
}

// ---- 4d-01: lock modes -------------------------------------------------------------------------------------------------------------------

#[test]
fn s4d_01_the_compatibility_table_is_the_textbook_one() {
    for &a in &ALL {
        for &b in &ALL {
            assert_eq!(compatible(a, b), truth(a, b), "compatible({a:?}, {b:?})");
        }
    }
}

#[test]
fn s4d_01_an_exclusive_lock_is_compatible_with_nothing() {
    for &m in &ALL {
        assert!(!compatible(Exclusive, m), "X with {m:?}");
        assert!(!compatible(m, Exclusive), "{m:?} with X");
    }
}

#[test]
fn s4d_01_intention_shared_only_conflicts_with_exclusive() {
    for &m in &ALL {
        assert_eq!(compatible(IntentionShared, m), m != Exclusive, "IS with {m:?}");
    }
}

#[test]
fn s4d_01_readers_and_intending_writers_do_not_mix() {
    assert!(compatible(Shared, Shared));
    assert!(compatible(IntentionExclusive, IntentionExclusive), "two writers of different rows can share a table");
    assert!(!compatible(Shared, IntentionExclusive), "a reader of the whole table and a writer of one row of it conflict");
    assert!(!compatible(SharedIntentionExclusive, SharedIntentionExclusive));
    assert!(!compatible(SharedIntentionExclusive, Shared));
}

#[test]
fn s4d_01_only_a_stronger_mode_is_an_upgrade() {
    let expected: [(LockMode, Vec<LockMode>); 5] = [
        (IntentionShared, vec![Shared, IntentionExclusive, SharedIntentionExclusive, Exclusive]),
        (IntentionExclusive, vec![SharedIntentionExclusive, Exclusive]),
        (Shared, vec![SharedIntentionExclusive, Exclusive]),
        (SharedIntentionExclusive, vec![Exclusive]),
        (Exclusive, vec![]),
    ];
    for (from, tos) in expected {
        for &to in &ALL {
            assert_eq!(can_upgrade(from, to), tos.contains(&to), "can_upgrade({from:?}, {to:?})");
        }
    }
}

proptest! {
    #![proptest_config(config())]

    /// Property: compatibility is symmetric (it describes two holders, not an order).
    #[test]
    fn s4d_01_property_compatibility_is_symmetric(a in any_mode(), b in any_mode()) {
        prop_assert_eq!(compatible(a, b), compatible(b, a));
    }

    /// Property: an upgrade only strengthens: whatever is compatible with the new mode was compatible with the old one, and there is no way back.
    #[test]
    fn s4d_01_property_an_upgrade_only_strengthens(a in any_mode(), b in any_mode(), c in any_mode()) {
        prop_assert!(!can_upgrade(a, a), "the same mode is not an upgrade");
        if can_upgrade(a, b) {
            prop_assert!(!can_upgrade(b, a));
            if compatible(b, c) {
                prop_assert!(compatible(a, c), "{:?} -> {:?}: {:?} fits the new mode but not the old", a, b, c);
            }
        }
    }
}

// ---- 4d-02: one lock, no waiting ---------------------------------------------------------------------------------------------------------

#[test]
fn s4d_02_a_new_lock_has_no_holders() {
    let q = LockQueue::new();
    assert!(q.holders().is_empty());
    assert!(q.is_empty());
    assert_eq!(q.mode_of(1), None);
}

#[test]
fn s4d_02_compatible_requests_share_the_lock() {
    let mut q = LockQueue::new();
    assert_eq!(q.try_acquire(2, Shared), Ok(true));
    assert_eq!(q.try_acquire(1, Shared), Ok(true));
    assert_eq!(q.try_acquire(3, IntentionShared), Ok(true));
    assert_eq!(q.holders(), vec![(1, Shared), (2, Shared), (3, IntentionShared)], "holders come back ordered by transaction id");
    assert_eq!(q.mode_of(2), Some(Shared));
}

#[test]
fn s4d_02_an_incompatible_request_is_refused_and_changes_nothing() {
    let mut q = LockQueue::new();
    assert_eq!(q.try_acquire(1, Exclusive), Ok(true));
    assert_eq!(q.try_acquire(2, Shared), Ok(false));
    assert_eq!(q.try_acquire(2, IntentionShared), Ok(false));
    assert_eq!(q.holders(), vec![(1, Exclusive)]);
    assert_eq!(q.mode_of(2), None);
}

#[test]
fn s4d_02_asking_again_for_the_mode_you_hold_is_fine() {
    let mut q = LockQueue::new();
    assert_eq!(q.try_acquire(1, Shared), Ok(true));
    assert_eq!(q.try_acquire(1, Shared), Ok(true));
    assert_eq!(q.holders(), vec![(1, Shared)], "still one entry");
}

#[test]
fn s4d_02_an_upgrade_replaces_the_mode_when_nobody_is_in_the_way() {
    let mut q = LockQueue::new();
    q.try_acquire(1, Shared).unwrap();
    assert_eq!(q.try_acquire(1, Exclusive), Ok(true));
    assert_eq!(q.holders(), vec![(1, Exclusive)], "the old mode is replaced, not added");
    let mut q = LockQueue::new();
    q.try_acquire(1, Shared).unwrap();
    q.try_acquire(2, Shared).unwrap();
    assert_eq!(q.try_acquire(1, Exclusive), Ok(false), "another holder is in the way");
    assert_eq!(q.mode_of(1), Some(Shared), "a refused upgrade leaves the old lock alone");
    assert!(q.release(2));
    assert_eq!(q.try_acquire(1, Exclusive), Ok(true));
}

#[test]
fn s4d_02_asking_for_a_weaker_mode_is_an_error() {
    let mut q = LockQueue::new();
    q.try_acquire(1, Exclusive).unwrap();
    assert_eq!(q.try_acquire(1, Shared), Err(LockErrorKind::IncompatibleUpgrade));
    q.release(1);
    q.try_acquire(1, IntentionExclusive).unwrap();
    assert_eq!(q.try_acquire(1, Shared), Err(LockErrorKind::IncompatibleUpgrade), "IX to S is not an upgrade either");
    assert_eq!(q.mode_of(1), Some(IntentionExclusive));
}

#[test]
fn s4d_02_releasing_frees_the_lock_for_others() {
    let mut q = LockQueue::new();
    q.try_acquire(1, Exclusive).unwrap();
    assert!(!q.release(2), "2 held nothing");
    assert!(q.release(1));
    assert!(!q.release(1), "already released");
    assert_eq!(q.try_acquire(2, Exclusive), Ok(true));
}

#[derive(Clone, Debug)]
enum QOp {
    Acquire(TxnId, LockMode),
    Release(TxnId),
}

proptest! {
    #![proptest_config(config())]

    /// Property: against a model written from the textbook table, every answer agrees, and the holders are always compatible with each other.
    #[test]
    fn s4d_02_property_a_lock_queue_matches_a_model(ops in proptest::collection::vec(
        prop_oneof![
            3 => (1..5i64, any_mode()).prop_map(|(t, m)| QOp::Acquire(t, m)),
            2 => (1..5i64).prop_map(QOp::Release),
        ], 1..80)) {
        let mut q = LockQueue::new();
        let mut model: HashMap<TxnId, LockMode> = HashMap::new();
        let up = |from: LockMode, to: LockMode| -> bool {
            let rank = |m: LockMode| ALL.iter().position(|&x| x == m).unwrap();
            matches!((rank(from), rank(to)), (0, 1..=4) | (1, 3 | 4) | (2, 3 | 4) | (3, 4))
        };
        for op in ops {
            match op {
                QOp::Acquire(t, m) => {
                    let held = model.get(&t).copied();
                    let want: Result<bool, LockErrorKind> = match held {
                        Some(h) if h == m => Ok(true),
                        Some(h) if !up(h, m) => Err(LockErrorKind::IncompatibleUpgrade),
                        _ => {
                            if model.iter().any(|(&o, &om)| o != t && !truth(om, m)) { Ok(false) } else { model.insert(t, m); Ok(true) }
                        }
                    };
                    prop_assert_eq!(q.try_acquire(t, m), want, "acquire({}, {:?})", t, m);
                }
                QOp::Release(t) => {
                    prop_assert_eq!(q.release(t), model.remove(&t).is_some(), "release({})", t);
                }
            }
            let mut want: Vec<_> = model.iter().map(|(&t, &m)| (t, m)).collect();
            want.sort();
            prop_assert_eq!(q.holders(), want.clone());
            for (i, &(_, a)) in want.iter().enumerate() {
                for &(_, b) in &want[i + 1..] {
                    prop_assert!(truth(a, b), "two holders that cannot share: {:?} and {:?}", a, b);
                }
            }
        }
    }
}

// ---- 4d-03: waiting for a lock -----------------------------------------------------------------------------------------------------------

#[test]
fn s4d_03_a_free_lock_is_granted_at_once_and_shows_its_holder() {
    let m = LockManager::new();
    assert_eq!(m.lock(1, table(1), Shared), Ok(()));
    assert_eq!(m.holders(table(1)), vec![(1, Shared)]);
    assert_eq!(m.waiting(table(1)), 0);
    assert!(m.holders(table(2)).is_empty(), "another table is untouched");
}

#[test]
fn s4d_03_shared_locks_are_granted_together() {
    finish_within("shared locks", || {
        let m = Arc::new(LockManager::new());
        let hs: Vec<_> = (1..=4)
            .map(|t| {
                let m = Arc::clone(&m);
                thread::spawn(move || m.lock(t, table(1), Shared).unwrap())
            })
            .collect();
        for h in hs {
            h.join().unwrap();
        }
        assert_eq!(m.holders(table(1)).len(), 4);
    });
}

#[test]
fn s4d_03_an_exclusive_request_waits_until_the_holder_lets_go() {
    finish_within("exclusive waits", || {
        let m = Arc::new(LockManager::new());
        m.lock(1, table(1), Exclusive).unwrap();
        let (done, h) = spawn_flag({
            let m = Arc::clone(&m);
            move || m.lock(2, table(1), Exclusive).unwrap()
        });
        pause();
        assert!(!finished(&done), "the second exclusive request must wait");
        assert_eq!(m.waiting(table(1)), 1);
        assert_eq!(m.holders(table(1)), vec![(1, Exclusive)]);
        m.unlock(1, table(1)).unwrap();
        h.join().unwrap();
        assert_eq!(m.holders(table(1)), vec![(2, Exclusive)]);
        assert_eq!(m.waiting(table(1)), 0);
    });
}

#[test]
fn s4d_03_a_reader_does_not_jump_a_waiting_writer() {
    finish_within("fair queue", || {
        let m = Arc::new(LockManager::new());
        let order = Arc::new(Mutex::new(Vec::new()));
        m.lock(1, table(1), Shared).unwrap();
        let writer = {
            let (m, order) = (Arc::clone(&m), Arc::clone(&order));
            thread::spawn(move || {
                m.lock(2, table(1), Exclusive).unwrap();
                order.lock().unwrap().push(2);
                m.unlock(2, table(1)).unwrap();
            })
        };
        pause();
        // transaction 3 would be compatible with the holder, but a writer is ahead of it
        let reader = {
            let (m, order) = (Arc::clone(&m), Arc::clone(&order));
            thread::spawn(move || {
                m.lock(3, table(1), Shared).unwrap();
                order.lock().unwrap().push(3);
                m.unlock(3, table(1)).unwrap();
            })
        };
        pause();
        assert_eq!(m.waiting(table(1)), 2, "both wait: the reader is behind the writer");
        assert_eq!(m.holders(table(1)), vec![(1, Shared)]);
        m.unlock(1, table(1)).unwrap();
        writer.join().unwrap();
        reader.join().unwrap();
        assert_eq!(*order.lock().unwrap(), vec![2, 3], "the writer was first in line");
    });
}

#[test]
fn s4d_03_waiting_requests_are_granted_in_the_order_they_arrived() {
    finish_within("fifo", || {
        let m = Arc::new(LockManager::new());
        let order = Arc::new(Mutex::new(Vec::new()));
        m.lock(0, table(1), Exclusive).unwrap();
        let mut hs = Vec::new();
        for t in 1..=4 {
            let (m, order) = (Arc::clone(&m), Arc::clone(&order));
            hs.push(thread::spawn(move || {
                m.lock(t, table(1), Exclusive).unwrap();
                order.lock().unwrap().push(t);
                m.unlock(t, table(1)).unwrap();
            }));
            pause();
        }
        m.unlock(0, table(1)).unwrap();
        for h in hs {
            h.join().unwrap();
        }
        assert_eq!(*order.lock().unwrap(), vec![1, 2, 3, 4]);
    });
}

#[test]
fn s4d_03_readers_that_queued_together_are_granted_together() {
    finish_within("batch of readers", || {
        let m = Arc::new(LockManager::new());
        m.lock(0, table(1), Exclusive).unwrap();
        let hs: Vec<_> = (1..=3)
            .map(|t| {
                let m = Arc::clone(&m);
                let h = thread::spawn(move || m.lock(t, table(1), Shared).unwrap());
                pause();
                h
            })
            .collect();
        m.unlock(0, table(1)).unwrap();
        for h in hs {
            h.join().unwrap();
        }
        assert_eq!(m.holders(table(1)).len(), 3, "all three readers hold it at the same time");
    });
}

#[test]
fn s4d_03_unlocking_what_you_do_not_hold_is_an_error() {
    let m = LockManager::new();
    assert_eq!(kind(m.unlock(1, table(1))), LockErrorKind::AttemptedUnlockButNoLockHeld);
    m.lock(2, table(1), Shared).unwrap();
    assert_eq!(kind(m.unlock(1, table(1))), LockErrorKind::AttemptedUnlockButNoLockHeld, "1 does not hold what 2 holds");
    assert_eq!(m.holders(table(1)), vec![(2, Shared)]);
}

#[test]
fn s4d_03_try_lock_never_waits() {
    let m = LockManager::new();
    assert_eq!(m.try_lock(1, row(1, 1), Exclusive), Ok(true));
    assert_eq!(m.try_lock(2, row(1, 1), Shared), Ok(false));
    assert_eq!(m.try_lock(2, row(1, 2), Shared), Ok(true), "another row is free");
    assert_eq!(m.waiting(row(1, 1)), 0, "a refused try_lock leaves nobody waiting");
    m.unlock(1, row(1, 1)).unwrap();
    assert_eq!(m.try_lock(2, row(1, 1), Shared), Ok(true));
}

#[test]
fn s4d_03_try_lock_does_not_jump_the_queue_either() {
    finish_within("try_lock and the queue", || {
        let m = Arc::new(LockManager::new());
        m.lock(1, table(1), Shared).unwrap();
        let h = {
            let m = Arc::clone(&m);
            thread::spawn(move || m.lock(2, table(1), Exclusive).unwrap())
        };
        pause();
        assert_eq!(m.try_lock(3, table(1), Shared), Ok(false), "a writer is waiting ahead of it");
        m.unlock(1, table(1)).unwrap();
        h.join().unwrap();
    });
}

proptest! {
    #![proptest_config(config())]

    /// Property: on one thread with only try_lock and unlock, the manager agrees with a model: a lock is granted exactly when it is compatible with
    /// what the others hold, and nothing ever waits.
    #[test]
    fn s4d_03_property_try_lock_matches_a_model(ops in proptest::collection::vec(
        prop_oneof![
            3 => (1..4i64, 0..2u32, prop::sample::select(vec![Shared, Exclusive, IntentionShared, IntentionExclusive])).prop_map(|(t, r, m)| (true, t, r, m)),
            2 => (1..4i64, 0..2u32).prop_map(|(t, r)| (false, t, r, Shared)),
        ], 1..80)) {
        let m = LockManager::new();
        let mut model: HashMap<(u32, TxnId), LockMode> = HashMap::new();
        for (acquire, t, r, mode) in ops {
            let res = table(r);
            if acquire {
                if model.get(&(r, t)).is_some() { continue; } // upgrades are another stage
                let ok = model.iter().all(|(&(rr, o), &om)| rr != r || o == t || truth(om, mode));
                prop_assert_eq!(m.try_lock(t, res, mode), Ok(ok), "try_lock({}, {}, {:?})", t, r, mode);
                if ok { model.insert((r, t), mode); }
            } else {
                let held = model.remove(&(r, t)).is_some();
                prop_assert_eq!(m.unlock(t, res).is_ok(), held, "unlock({}, {})", t, r);
            }
            for rr in 0..2u32 {
                let mut want: Vec<_> = model.iter().filter(|(&(x, _), _)| x == rr).map(|(&(_, o), &om)| (o, om)).collect();
                want.sort();
                prop_assert_eq!(m.holders(table(rr)), want);
                prop_assert_eq!(m.waiting(table(rr)), 0);
            }
        }
    }
}

// ---- 4d-04: upgrades ---------------------------------------------------------------------------------------------------------------------

#[test]
fn s4d_04_a_lone_holder_upgrades_at_once() {
    let m = LockManager::new();
    m.lock(1, table(1), Shared).unwrap();
    assert_eq!(m.lock(1, table(1), Exclusive), Ok(()));
    assert_eq!(m.holders(table(1)), vec![(1, Exclusive)], "the shared lock became an exclusive one");
    m.lock(2, table(2), IntentionShared).unwrap();
    m.lock(2, table(2), SharedIntentionExclusive).unwrap();
    assert_eq!(m.holders(table(2)), vec![(2, SharedIntentionExclusive)]);
}

#[test]
fn s4d_04_asking_again_for_the_mode_you_hold_changes_nothing() {
    let m = LockManager::new();
    m.lock(1, table(1), Exclusive).unwrap();
    assert_eq!(m.lock(1, table(1), Exclusive), Ok(()));
    assert_eq!(m.holders(table(1)), vec![(1, Exclusive)]);
}

#[test]
fn s4d_04_an_upgrade_waits_for_the_other_holders() {
    finish_within("upgrade waits", || {
        let m = Arc::new(LockManager::new());
        m.lock(1, table(1), Shared).unwrap();
        m.lock(2, table(1), Shared).unwrap();
        let (done, h) = spawn_flag({
            let m = Arc::clone(&m);
            move || m.lock(1, table(1), Exclusive).unwrap()
        });
        pause();
        assert!(!finished(&done), "transaction 2 still holds a shared lock");
        assert_eq!(m.holders(table(1)).len(), 2, "nothing changes while the upgrade waits");
        m.unlock(2, table(1)).unwrap();
        h.join().unwrap();
        assert_eq!(m.holders(table(1)), vec![(1, Exclusive)]);
    });
}

#[test]
fn s4d_04_an_upgrade_goes_before_everybody_already_waiting() {
    finish_within("upgrade first", || {
        let m = Arc::new(LockManager::new());
        let order = Arc::new(Mutex::new(Vec::new()));
        m.lock(1, table(1), Shared).unwrap();
        m.lock(2, table(1), Shared).unwrap();
        let writer = {
            let (m, order) = (Arc::clone(&m), Arc::clone(&order));
            thread::spawn(move || {
                m.lock(3, table(1), Exclusive).unwrap();
                order.lock().unwrap().push(3);
                m.unlock(3, table(1)).unwrap();
            })
        };
        pause();
        let upgrader = {
            let (m, order) = (Arc::clone(&m), Arc::clone(&order));
            thread::spawn(move || {
                m.lock(1, table(1), Exclusive).unwrap();
                order.lock().unwrap().push(1);
                m.unlock(1, table(1)).unwrap();
            })
        };
        pause();
        m.unlock(2, table(1)).unwrap();
        upgrader.join().unwrap();
        writer.join().unwrap();
        assert_eq!(*order.lock().unwrap(), vec![1, 3], "the upgrade was granted first although it asked last");
    });
}

#[test]
fn s4d_04_a_second_upgrade_of_the_same_lock_is_refused() {
    finish_within("upgrade conflict", || {
        let m = Arc::new(LockManager::new());
        m.lock(1, table(1), Shared).unwrap();
        m.lock(2, table(1), Shared).unwrap();
        let (_done, first) = spawn_flag({
            let m = Arc::clone(&m);
            move || m.lock(1, table(1), Exclusive)
        });
        pause();
        assert_eq!(kind(m.lock(2, table(1), Exclusive)), LockErrorKind::UpgradeConflict, "only one transaction may be upgrading");
        m.unlock(2, table(1)).unwrap();
        assert_eq!(first.join().unwrap(), Ok(()), "the first upgrade is not harmed by the refused one");
        assert_eq!(m.holders(table(1)), vec![(1, Exclusive)]);
    });
}

#[test]
fn s4d_04_a_weaker_mode_than_the_one_held_is_not_an_upgrade() {
    let m = LockManager::new();
    m.lock(1, table(1), Exclusive).unwrap();
    assert_eq!(kind(m.lock(1, table(1), Shared)), LockErrorKind::IncompatibleUpgrade);
    assert_eq!(kind(m.lock(1, table(1), IntentionShared)), LockErrorKind::IncompatibleUpgrade);
    m.lock(2, table(2), IntentionExclusive).unwrap();
    assert_eq!(kind(m.lock(2, table(2), Shared)), LockErrorKind::IncompatibleUpgrade, "IX to S is sideways, not up");
    assert_eq!(m.holders(table(1)), vec![(1, Exclusive)], "a refused request changes nothing");
}

#[test]
fn s4d_04_an_upgrade_in_the_middle_of_a_queue_does_not_lose_the_others() {
    finish_within("queue after an upgrade", || {
        let m = Arc::new(LockManager::new());
        m.lock(1, table(1), IntentionShared).unwrap();
        m.lock(2, table(1), IntentionShared).unwrap();
        let mut hs = Vec::new();
        for t in 3..=4 {
            let m = Arc::clone(&m);
            hs.push(thread::spawn(move || {
                m.lock(t, table(1), Exclusive).unwrap();
                m.unlock(t, table(1)).unwrap();
            }));
            pause();
        }
        m.lock(1, table(1), Shared).unwrap();
        assert_eq!(m.holders(table(1)), vec![(1, Shared), (2, IntentionShared)]);
        m.unlock(1, table(1)).unwrap();
        m.unlock(2, table(1)).unwrap();
        for h in hs {
            h.join().unwrap();
        }
        assert!(m.holders(table(1)).is_empty());
    });
}

// ---- 4d-05: two-phase locking and isolation levels ---------------------------------------------------------------------------------------

fn txn(id: TxnId, iso: LockIsolation) -> Arc<LockTxn> {
    LockTxn::new(id, iso)
}

#[test]
fn s4d_05_read_uncommitted_never_takes_shared_locks() {
    for mode in [Shared, IntentionShared, SharedIntentionExclusive] {
        let m = LockManager::new();
        let t = txn(1, LockIsolation::ReadUncommitted);
        assert_eq!(kind(m.lock_table(&t, mode, 1)), LockErrorKind::LockSharedOnReadUncommitted, "{mode:?}");
        assert_eq!(t.state(), LockState::Aborted, "the transaction is aborted by the violation");
    }
    let m = LockManager::new();
    let t = txn(1, LockIsolation::ReadUncommitted);
    assert_eq!(m.lock_table(&t, IntentionExclusive, 1), Ok(()));
    assert_eq!(m.lock_table(&t, Exclusive, 2), Ok(()));
    assert_eq!(t.state(), LockState::Growing);
}

#[test]
fn s4d_05_releasing_an_exclusive_lock_starts_the_shrinking_phase_at_every_level() {
    for iso in [LockIsolation::ReadUncommitted, LockIsolation::ReadCommitted, LockIsolation::RepeatableRead] {
        let m = LockManager::new();
        let t = txn(1, iso);
        m.lock_table(&t, Exclusive, 1).unwrap();
        m.unlock_table(&t, 1).unwrap();
        assert_eq!(t.state(), LockState::Shrinking, "{iso:?}");
        assert_eq!(kind(m.lock_table(&t, Exclusive, 2)), LockErrorKind::LockOnShrinking, "{iso:?}: no new exclusive lock once shrinking");
        assert_eq!(t.state(), LockState::Aborted);
    }
}

#[test]
fn s4d_05_releasing_a_shared_lock_shrinks_only_under_repeatable_read() {
    let m = LockManager::new();
    let rr = txn(1, LockIsolation::RepeatableRead);
    m.lock_table(&rr, Shared, 1).unwrap();
    m.unlock_table(&rr, 1).unwrap();
    assert_eq!(rr.state(), LockState::Shrinking);
    assert_eq!(kind(m.lock_table(&rr, Shared, 2)), LockErrorKind::LockOnShrinking, "repeatable read takes no lock at all once shrinking");

    let rc = txn(2, LockIsolation::ReadCommitted);
    m.lock_table(&rc, Shared, 3).unwrap();
    m.unlock_table(&rc, 3).unwrap();
    assert_eq!(rc.state(), LockState::Growing, "read committed lets go of its read locks freely");
    assert_eq!(m.lock_table(&rc, Shared, 4), Ok(()));
}

#[test]
fn s4d_05_read_committed_may_still_read_while_shrinking() {
    let m = LockManager::new();
    let t = txn(1, LockIsolation::ReadCommitted);
    m.lock_table(&t, Exclusive, 1).unwrap();
    m.unlock_table(&t, 1).unwrap();
    assert_eq!(t.state(), LockState::Shrinking);
    assert_eq!(m.lock_table(&t, IntentionShared, 2), Ok(()), "IS is allowed while shrinking");
    assert_eq!(m.lock_table(&t, Shared, 3), Ok(()), "S is allowed while shrinking");
    assert_eq!(kind(m.lock_table(&t, IntentionExclusive, 4)), LockErrorKind::LockOnShrinking, "writes are not");
}

#[test]
fn s4d_05_a_row_can_only_be_locked_shared_or_exclusive() {
    let m = LockManager::new();
    let t = txn(1, LockIsolation::RepeatableRead);
    m.lock_table(&t, IntentionExclusive, 1).unwrap();
    for mode in [IntentionShared, IntentionExclusive, SharedIntentionExclusive] {
        let t2 = txn(2, LockIsolation::RepeatableRead);
        m.lock_table(&t2, IntentionExclusive, 2).unwrap();
        assert_eq!(kind(m.lock_row(&t2, mode, 2, rid(1))), LockErrorKind::AttemptedIntentionLockOnRow, "{mode:?}");
        assert_eq!(t2.state(), LockState::Aborted);
        m.release_all(&t2);
    }
    assert_eq!(m.lock_row(&t, Exclusive, 1, rid(1)), Ok(()));
}

#[test]
fn s4d_05_a_row_lock_needs_a_table_lock_that_is_enough() {
    let m = LockManager::new();
    let none = txn(1, LockIsolation::RepeatableRead);
    assert_eq!(kind(m.lock_row(&none, Shared, 1, rid(1))), LockErrorKind::TableLockNotPresent, "no table lock at all");

    let is = txn(2, LockIsolation::RepeatableRead);
    m.lock_table(&is, IntentionShared, 1).unwrap();
    assert_eq!(m.lock_row(&is, Shared, 1, rid(1)), Ok(()), "IS is enough to read a row");
    assert_eq!(kind(m.lock_row(&is, Exclusive, 1, rid(2))), LockErrorKind::TableLockNotPresent, "IS is not enough to write a row");

    for (id, table_mode) in [(3, IntentionExclusive), (4, SharedIntentionExclusive), (5, Exclusive)] {
        let t = txn(id, LockIsolation::RepeatableRead);
        let tbl = 10 + id as u32;
        m.lock_table(&t, table_mode, tbl).unwrap();
        assert_eq!(m.lock_row(&t, Exclusive, tbl, rid(1)), Ok(()), "{table_mode:?} is enough to write a row");
    }
    let s = txn(6, LockIsolation::RepeatableRead);
    m.lock_table(&s, Shared, 9).unwrap();
    assert_eq!(kind(m.lock_row(&s, Exclusive, 9, rid(1))), LockErrorKind::TableLockNotPresent, "a shared table lock does not allow writing a row");
}

#[test]
fn s4d_05_a_table_cannot_be_unlocked_while_its_rows_are() {
    let m = LockManager::new();
    let t = txn(1, LockIsolation::RepeatableRead);
    m.lock_table(&t, IntentionExclusive, 1).unwrap();
    m.lock_row(&t, Exclusive, 1, rid(1)).unwrap();
    assert_eq!(kind(m.unlock_table(&t, 1)), LockErrorKind::TableUnlockedBeforeUnlockingRows);
    assert_eq!(t.state(), LockState::Aborted);

    let t = txn(2, LockIsolation::RepeatableRead);
    m.lock_table(&t, IntentionShared, 2).unwrap();
    m.lock_row(&t, Shared, 2, rid(1)).unwrap();
    m.unlock_row(&t, 2, rid(1)).unwrap();
    assert_eq!(m.unlock_table(&t, 2), Ok(()), "with its rows gone the table can go");
}

#[test]
fn s4d_05_unlocking_what_is_not_locked_aborts() {
    let m = LockManager::new();
    let t = txn(1, LockIsolation::RepeatableRead);
    assert_eq!(kind(m.unlock_table(&t, 1)), LockErrorKind::AttemptedUnlockButNoLockHeld);
    assert_eq!(t.state(), LockState::Aborted);
    let t = txn(2, LockIsolation::RepeatableRead);
    m.lock_table(&t, IntentionShared, 1).unwrap();
    assert_eq!(kind(m.unlock_row(&t, 1, rid(5))), LockErrorKind::AttemptedUnlockButNoLockHeld);
}

#[test]
fn s4d_05_upgrades_follow_the_rules_and_a_bad_one_aborts() {
    let m = LockManager::new();
    let t = txn(1, LockIsolation::RepeatableRead);
    m.lock_table(&t, IntentionShared, 1).unwrap();
    assert_eq!(m.lock_table(&t, Exclusive, 1), Ok(()));
    assert_eq!(m.holders(table(1)), vec![(1, Exclusive)]);
    assert_eq!(kind(m.lock_table(&t, Shared, 1)), LockErrorKind::IncompatibleUpgrade);
    assert_eq!(t.state(), LockState::Aborted);
}

#[test]
fn s4d_05_an_aborted_or_committed_transaction_takes_no_locks() {
    let m = LockManager::new();
    let t = txn(1, LockIsolation::RepeatableRead);
    t.set_state(LockState::Aborted);
    assert_eq!(kind(m.lock_table(&t, Shared, 1)), LockErrorKind::NotRunning);
    let t = txn(2, LockIsolation::RepeatableRead);
    t.set_state(LockState::Committed);
    assert_eq!(kind(m.lock_table(&t, Shared, 1)), LockErrorKind::NotRunning);
    assert!(m.holders(table(1)).is_empty());
}

#[test]
fn s4d_05_release_all_lets_go_of_rows_then_tables_and_leaves_the_phase_alone() {
    let m = LockManager::new();
    let t = txn(1, LockIsolation::RepeatableRead);
    m.lock_table(&t, IntentionExclusive, 1).unwrap();
    m.lock_row(&t, Exclusive, 1, rid(1)).unwrap();
    m.lock_row(&t, Exclusive, 1, rid(2)).unwrap();
    m.lock_table(&t, Exclusive, 2).unwrap();
    m.release_all(&t);
    for r in [table(1), table(2), row(1, 1), row(1, 2)] {
        assert!(m.holders(r).is_empty(), "{r:?} is free");
    }
    assert_eq!(t.state(), LockState::Growing, "commit and abort set the state themselves");
    let other = txn(2, LockIsolation::RepeatableRead);
    assert_eq!(m.lock_table(&other, Exclusive, 1), Ok(()));
}

#[derive(Clone, Debug)]
enum TOp {
    Lock(u32, LockMode),
    Unlock(u32),
}

proptest! {
    #![proptest_config(config())]

    /// Property: for one transaction at any isolation level, every answer and every change of phase agrees with the rules written out again here.
    #[test]
    fn s4d_05_property_the_rules_hold_for_any_sequence(iso in prop::sample::select(vec![LockIsolation::ReadUncommitted, LockIsolation::ReadCommitted, LockIsolation::RepeatableRead]),
        ops in proptest::collection::vec(prop_oneof![
            3 => (0..3u32, any_mode()).prop_map(|(t, m)| TOp::Lock(t, m)),
            2 => (0..3u32).prop_map(TOp::Unlock),
        ], 1..40)) {
        let m = LockManager::new();
        let t = txn(1, iso);
        let mut held: HashMap<u32, LockMode> = HashMap::new();
        let mut state = LockState::Growing;
        let up = |from: LockMode, to: LockMode| matches!((ALL.iter().position(|&x| x == from).unwrap(), ALL.iter().position(|&x| x == to).unwrap()), (0, 1..=4) | (1, 3 | 4) | (2, 3 | 4) | (3, 4));
        for op in ops {
            let got: Result<(), LockErrorKind>;
            let want: Result<(), LockErrorKind>;
            match op {
                TOp::Lock(tbl, mode) => {
                    got = m.lock_table(&t, mode, tbl).map_err(|e| e.kind);
                    want = if state == LockState::Aborted {
                        Err(LockErrorKind::NotRunning)
                    } else if iso == LockIsolation::ReadUncommitted && matches!(mode, Shared | IntentionShared | SharedIntentionExclusive) {
                        state = LockState::Aborted;
                        Err(LockErrorKind::LockSharedOnReadUncommitted)
                    } else if state == LockState::Shrinking && !(iso == LockIsolation::ReadCommitted && matches!(mode, IntentionShared | Shared)) {
                        state = LockState::Aborted;
                        Err(LockErrorKind::LockOnShrinking)
                    } else {
                        match held.get(&tbl).copied() {
                            Some(h) if h == mode => Ok(()),
                            Some(h) if !up(h, mode) => { state = LockState::Aborted; Err(LockErrorKind::IncompatibleUpgrade) }
                            _ => { held.insert(tbl, mode); Ok(()) }
                        }
                    };
                }
                TOp::Unlock(tbl) => {
                    got = m.unlock_table(&t, tbl).map_err(|e| e.kind);
                    want = match held.remove(&tbl) {
                        None => { state = LockState::Aborted; Err(LockErrorKind::AttemptedUnlockButNoLockHeld) }
                        Some(mode) => {
                            if state == LockState::Growing {
                                let shrinks = if iso == LockIsolation::RepeatableRead { matches!(mode, Shared | Exclusive) } else { mode == Exclusive };
                                if shrinks { state = LockState::Shrinking; }
                            }
                            Ok(())
                        }
                    };
                }
            }
            prop_assert_eq!(got, want, "{:?}", op);
            prop_assert_eq!(t.state(), state, "state after {:?}", op);
        }
    }
}

// ---- 4d-06: deadlocks --------------------------------------------------------------------------------------------------------------------

fn graph(edges: &[(TxnId, TxnId)]) -> WaitsForGraph {
    let mut g = WaitsForGraph::new();
    for &(a, b) in edges {
        g.add_edge(a, b);
    }
    g
}

#[test]
fn s4d_06_a_graph_without_cycles_has_no_victim() {
    assert_eq!(WaitsForGraph::new().has_cycle(), None);
    assert_eq!(graph(&[(1, 2), (2, 3), (3, 4)]).has_cycle(), None, "a chain");
    assert_eq!(graph(&[(1, 2), (1, 3), (2, 4), (3, 4)]).has_cycle(), None, "a diamond is not a cycle");
}

#[test]
fn s4d_06_the_victim_is_the_youngest_transaction_on_the_cycle() {
    assert_eq!(graph(&[(1, 2), (2, 1)]).has_cycle(), Some(2));
    assert_eq!(graph(&[(1, 2), (2, 3), (3, 1)]).has_cycle(), Some(3));
    assert_eq!(graph(&[(7, 3), (3, 9), (9, 7)]).has_cycle(), Some(9), "ids need not be small or in order");
    assert_eq!(graph(&[(5, 5)]).has_cycle(), Some(5), "waiting for yourself is a cycle");
}

#[test]
fn s4d_06_a_cycle_reached_through_a_tail_is_found() {
    assert_eq!(graph(&[(1, 2), (2, 3), (3, 4), (4, 2)]).has_cycle(), Some(4), "1 is not on the cycle, so it is not the victim");
    assert_eq!(graph(&[(10, 1), (1, 2), (2, 1)]).has_cycle(), Some(2));
}

#[test]
fn s4d_06_removing_an_edge_can_break_the_cycle() {
    let mut g = graph(&[(1, 2), (2, 3), (3, 1)]);
    g.remove_edge(3, 1);
    assert_eq!(g.has_cycle(), None);
    g.add_edge(3, 1);
    g.add_edge(3, 1);
    assert_eq!(g.has_cycle(), Some(3));
    g.remove_edge(9, 9);
    assert_eq!(g.edge_list().len(), 3, "an edge added twice is one edge, and removing a missing edge does nothing");
}

#[test]
fn s4d_06_the_edge_list_is_ordered() {
    let g = graph(&[(3, 1), (1, 3), (1, 2), (2, 1)]);
    assert_eq!(g.edge_list(), vec![(1, 2), (1, 3), (2, 1), (3, 1)]);
}

#[test]
fn s4d_06_two_transactions_that_wait_for_each_other_are_broken_up() {
    finish_within("two-way deadlock", || {
        let m = Arc::new(LockManager::new());
        m.lock(1, table(1), Exclusive).unwrap();
        m.lock(2, table(2), Exclusive).unwrap();
        let t1 = {
            let m = Arc::clone(&m);
            thread::spawn(move || m.lock(1, table(2), Exclusive))
        };
        let t2 = {
            let m = Arc::clone(&m);
            thread::spawn(move || m.lock(2, table(1), Exclusive))
        };
        // both are waiting now; detect until the detector sees it
        let mut victims = Vec::new();
        while victims.is_empty() {
            thread::sleep(Duration::from_millis(20));
            victims = m.detect_deadlocks();
        }
        assert_eq!(victims, vec![2], "the younger transaction is the victim");
        assert_eq!(kind(t2.join().unwrap()), LockErrorKind::Deadlock, "the victim's request gives up");
        m.unlock(2, table(2)).unwrap();
        assert_eq!(t1.join().unwrap(), Ok(()), "the other one now gets what it waited for");
        assert!(m.detect_deadlocks().is_empty(), "no deadlock is left");
    });
}

#[test]
fn s4d_06_a_cycle_of_three_loses_its_youngest() {
    finish_within("three-way deadlock", || {
        let m = Arc::new(LockManager::new());
        for t in 1..=3 {
            m.lock(t, table(t as u32), Exclusive).unwrap();
        }
        // each transaction wants the next one's table; whoever finishes lets go of everything it holds, which is what frees the others
        let hs: Vec<_> = (1..=3i64)
            .map(|t| {
                let m = Arc::clone(&m);
                thread::spawn(move || {
                    let next = (t % 3 + 1) as u32;
                    let r = m.lock(t, table(next), Exclusive);
                    if r.is_ok() {
                        m.unlock(t, table(next)).unwrap();
                    }
                    m.unlock(t, table(t as u32)).unwrap();
                    r
                })
            })
            .collect();
        let mut victims = Vec::new();
        while victims.is_empty() {
            thread::sleep(Duration::from_millis(20));
            victims = m.detect_deadlocks();
        }
        assert_eq!(victims, vec![3], "the youngest of the three");
        let results: Vec<_> = hs.into_iter().map(|h| h.join().unwrap()).collect();
        assert_eq!(kind(results[2].clone()), LockErrorKind::Deadlock);
        assert!(results[0].is_ok() && results[1].is_ok(), "the other two get their locks once the victim lets go");
    });
}

#[test]
fn s4d_06_two_separate_deadlocks_are_both_broken_in_one_pass() {
    finish_within("two deadlocks", || {
        let m = Arc::new(LockManager::new());
        for t in 1..=4 {
            m.lock(t, table(t as u32), Exclusive).unwrap();
        }
        // pairs (1, 2) and (3, 4) each deadlock
        let wants = [(1i64, 2u32), (2, 1), (3, 4), (4, 3)];
        let hs: Vec<_> = wants
            .iter()
            .map(|&(t, other)| {
                let m = Arc::clone(&m);
                thread::spawn(move || {
                    let r = m.lock(t, table(other), Exclusive);
                    m.unlock(t, table(t as u32)).unwrap();
                    if r.is_ok() {
                        m.unlock(t, table(other)).unwrap();
                    }
                    r
                })
            })
            .collect();
        // wait until all four requests are queued, then ask once
        while (1..=4).any(|t| m.waiting(table(t)) != 1) {
            thread::sleep(Duration::from_millis(5));
        }
        assert_eq!(m.detect_deadlocks(), vec![2, 4], "one pass breaks every cycle: the youngest of each pair");
        let results: Vec<_> = hs.into_iter().map(|h| h.join().unwrap()).collect();
        assert_eq!(kind(results[1].clone()), LockErrorKind::Deadlock);
        assert_eq!(kind(results[3].clone()), LockErrorKind::Deadlock);
        assert!(results[0].is_ok() && results[2].is_ok(), "the older transaction of each pair goes on");
    });
}

#[test]
fn s4d_06_the_detector_thread_breaks_a_deadlock_by_itself() {
    finish_within("detector thread", || {
        let m = Arc::new(LockManager::new());
        let _detector = DeadlockDetector::start(Arc::clone(&m), Duration::from_millis(20));
        m.lock(1, table(1), Exclusive).unwrap();
        m.lock(2, table(2), Exclusive).unwrap();
        let t1 = {
            let m = Arc::clone(&m);
            thread::spawn(move || m.lock(1, table(2), Exclusive))
        };
        let t2 = {
            let m = Arc::clone(&m);
            thread::spawn(move || {
                let r = m.lock(2, table(1), Exclusive);
                if r.is_err() {
                    m.unlock(2, table(2)).unwrap();
                }
                r
            })
        };
        assert_eq!(kind(t2.join().unwrap()), LockErrorKind::Deadlock, "the youngest was aborted without anyone calling detect_deadlocks");
        assert_eq!(t1.join().unwrap(), Ok(()));
    });
}

#[test]
fn s4d_06_a_waiting_request_that_is_no_deadlock_is_left_alone() {
    finish_within("no false alarm", || {
        let m = Arc::new(LockManager::new());
        m.lock(1, table(1), Exclusive).unwrap();
        let h = {
            let m = Arc::clone(&m);
            thread::spawn(move || m.lock(2, table(1), Exclusive))
        };
        pause();
        assert!(m.detect_deadlocks().is_empty(), "2 waits for 1, and 1 waits for nobody");
        m.unlock(1, table(1)).unwrap();
        assert_eq!(h.join().unwrap(), Ok(()));
    });
}

proptest! {
    #![proptest_config(config())]

    /// Property: a cycle is found exactly when some transaction can reach itself; the victim lies on a cycle of which it is the youngest; and
    /// removing victims one after another leaves a graph with no cycle.
    #[test]
    fn s4d_06_property_the_graph_finds_exactly_the_cycles(edges in proptest::collection::vec((1..8i64, 1..8i64), 0..24)) {
        let g = graph(&edges);
        let set: BTreeSet<(TxnId, TxnId)> = edges.iter().copied().collect();
        prop_assert_eq!(g.edge_list(), set.iter().copied().collect::<Vec<_>>());
        // brute force: can `a` reach `a` using only transactions no younger than `limit`?
        let reaches_self = |a: TxnId, limit: TxnId, edges: &BTreeSet<(TxnId, TxnId)>| -> bool {
            let mut seen = HashSet::new();
            let mut stack = vec![a];
            while let Some(n) = stack.pop() {
                for &(x, y) in edges.iter() {
                    if x == n && y <= limit {
                        if y == a {
                            return true;
                        }
                        if seen.insert(y) {
                            stack.push(y);
                        }
                    }
                }
            }
            false
        };
        let any_cycle = (1..8).any(|a| reaches_self(a, 7, &set));
        match g.has_cycle() {
            None => prop_assert!(!any_cycle, "a cycle exists but none was found"),
            Some(v) => {
                prop_assert!(any_cycle);
                prop_assert!(reaches_self(v, v, &set), "{} is not the youngest transaction of any cycle it is on", v);
            }
        }
        // breaking cycles by removing victims ends
        let mut g = g;
        let mut rounds = 0;
        while let Some(v) = g.has_cycle() {
            for (a, b) in g.edge_list() {
                if a == v || b == v {
                    g.remove_edge(a, b);
                }
            }
            rounds += 1;
            prop_assert!(rounds <= 8, "never ends");
        }
    }
}

// ---- 4d-07: the whole lock manager under load --------------------------------------------------------------------------------------------

/// The history of one finished transaction: its operations in the global order they happened, (sequence number, row, wrote).
type History = Vec<(u64, u32, bool)>;

/// Conflict serializability: a graph with an edge a -> b when a's operation on a row came before b's conflicting operation (at least one of
/// them a write) on the same row. A history is equal to some serial order exactly when that graph has no cycle.
fn serializable(histories: &[History]) -> bool {
    let n = histories.len();
    let mut edges: Vec<HashSet<usize>> = vec![HashSet::new(); n];
    for a in 0..n {
        for b in 0..n {
            if a == b {
                continue;
            }
            let conflict = histories[a].iter().any(|&(sa, ra, wa)| histories[b].iter().any(|&(sb, rb, wb)| ra == rb && (wa || wb) && sa < sb));
            if conflict {
                edges[a].insert(b);
            }
        }
    }
    // a cycle exists when some node can reach itself
    for start in 0..n {
        let mut seen = vec![false; n];
        let mut stack: Vec<usize> = edges[start].iter().copied().collect();
        while let Some(x) = stack.pop() {
            if x == start {
                return false;
            }
            if !seen[x] {
                seen[x] = true;
                stack.extend(edges[x].iter().copied());
            }
        }
    }
    true
}

#[test]
fn s4d_07_the_serializability_check_itself_is_right() {
    // two transactions that each read before the other writes: a cycle, so not serializable
    let a: History = vec![(1, 1, false), (4, 2, true)];
    let b: History = vec![(2, 2, false), (3, 1, true)];
    assert!(!serializable(&[a, b]));
    let c: History = vec![(1, 1, false), (2, 2, true)];
    let d: History = vec![(3, 1, false), (4, 2, true)];
    assert!(serializable(&[c, d]));
}

/// A bank of `rows` accounts, each started with 100. Each worker runs `transfers` transactions (move an amount between two random accounts, locking
/// them in random order so that deadlocks happen) and retries one that the deadlock detector aborted. Returns the histories of the committed ones.
fn run_bank(iso: LockIsolation, workers: usize, transfers: usize, rows: u32) -> (Vec<History>, Vec<i64>, usize) {
    let m = Arc::new(LockManager::new());
    let _detector = DeadlockDetector::start(Arc::clone(&m), Duration::from_millis(4));
    let balances: Arc<Vec<AtomicI64>> = Arc::new((0..rows).map(|_| AtomicI64::new(100)).collect());
    let seq = Arc::new(AtomicUsize::new(0));
    let next_id = Arc::new(AtomicI64::new(1));
    let aborts = Arc::new(AtomicUsize::new(0));
    let histories: Arc<Mutex<Vec<History>>> = Arc::new(Mutex::new(Vec::new()));
    let hs: Vec<_> = (0..workers)
        .map(|w| {
            let (m, balances, seq, next_id, aborts, histories) = (Arc::clone(&m), Arc::clone(&balances), Arc::clone(&seq), Arc::clone(&next_id), Arc::clone(&aborts), Arc::clone(&histories));
            thread::spawn(move || {
                let mut rng = (w as u64 + 1).wrapping_mul(0x9E37_79B9_7F4A_7C15);
                let mut rand = move |n: u32| {
                    rng ^= rng << 13;
                    rng ^= rng >> 7;
                    rng ^= rng << 17;
                    (rng % n as u64) as u32
                };
                for _ in 0..transfers {
                    let (a, b) = {
                        let a = rand(rows);
                        let mut b = rand(rows);
                        while b == a {
                            b = rand(rows);
                        }
                        (a, b)
                    };
                    let amount = rand(10) as i64 + 1;
                    loop {
                        let id = next_id.fetch_add(1, Ordering::SeqCst);
                        let t = LockTxn::new(id, iso);
                        let mut hist: History = Vec::new();
                        let attempt = (|| -> Result<(), LockError> {
                            m.lock_table(&t, IntentionExclusive, 1)?;
                            m.lock_row(&t, Exclusive, 1, rid(a))?;
                            hist.push((seq.fetch_add(1, Ordering::SeqCst) as u64, a, true));
                            let va = balances[a as usize].load(Ordering::SeqCst);
                            thread::sleep(Duration::from_micros(200));
                            m.lock_row(&t, Exclusive, 1, rid(b))?;
                            hist.push((seq.fetch_add(1, Ordering::SeqCst) as u64, b, true));
                            let vb = balances[b as usize].load(Ordering::SeqCst);
                            balances[a as usize].store(va - amount, Ordering::SeqCst);
                            balances[b as usize].store(vb + amount, Ordering::SeqCst);
                            Ok(())
                        })();
                        match attempt {
                            Ok(()) => {
                                t.set_state(LockState::Committed);
                                m.release_all(&t);
                                histories.lock().unwrap().push(hist);
                                break;
                            }
                            Err(_) => {
                                // aborted: nothing was written (the writes happen after both locks), let go and try again
                                t.set_state(LockState::Aborted);
                                m.release_all(&t);
                                aborts.fetch_add(1, Ordering::SeqCst);
                            }
                        }
                    }
                }
            })
        })
        .collect();
    for h in hs {
        h.join().unwrap();
    }
    let final_balances: Vec<i64> = balances.iter().map(|b| b.load(Ordering::SeqCst)).collect();
    let h = histories.lock().unwrap().clone();
    (h, final_balances, aborts.load(Ordering::SeqCst))
}

#[test]
fn s4d_07_a_bank_under_strict_two_phase_locking_loses_no_money_and_is_serializable() {
    finish_within("bank workload", || {
        let (histories, balances, _aborts) = run_bank(LockIsolation::RepeatableRead, 6, 25, 5);
        assert_eq!(histories.len(), 6 * 25, "every transfer committed in the end, after retries");
        assert_eq!(balances.iter().sum::<i64>(), 5 * 100, "the total never changes: no transfer was lost or half done");
        assert!(serializable(&histories), "the history of the committed transactions is equal to some serial order");
    });
}

#[test]
fn s4d_07_deadlocks_really_happen_in_the_workload_and_are_always_resolved() {
    finish_within("deadlocks resolved", || {
        let mut total_aborts = 0;
        for _ in 0..3 {
            let (histories, balances, aborts) = run_bank(LockIsolation::RepeatableRead, 6, 12, 3);
            total_aborts += aborts;
            assert_eq!(histories.len(), 6 * 12);
            assert_eq!(balances.iter().sum::<i64>(), 300);
        }
        assert!(total_aborts > 0, "three accounts locked in random order by six threads must have deadlocked at least once; the test would prove nothing otherwise");
    });
}

#[test]
fn s4d_07_two_writers_are_never_inside_the_same_row_at_once() {
    finish_within("mutual exclusion", || {
        let m = Arc::new(LockManager::new());
        let inside = Arc::new(AtomicUsize::new(0));
        let worst = Arc::new(AtomicUsize::new(0));
        let hs: Vec<_> = (1..=8i64)
            .map(|id| {
                let (m, inside, worst) = (Arc::clone(&m), Arc::clone(&inside), Arc::clone(&worst));
                thread::spawn(move || {
                    for k in 0..30 {
                        let t = LockTxn::new(id * 1000 + k, LockIsolation::RepeatableRead);
                        m.lock_table(&t, IntentionExclusive, 1).unwrap();
                        m.lock_row(&t, Exclusive, 1, rid(0)).unwrap();
                        let now = inside.fetch_add(1, Ordering::SeqCst) + 1;
                        worst.fetch_max(now, Ordering::SeqCst);
                        thread::yield_now();
                        inside.fetch_sub(1, Ordering::SeqCst);
                        m.release_all(&t);
                    }
                })
            })
            .collect();
        for h in hs {
            h.join().unwrap();
        }
        assert_eq!(worst.load(Ordering::SeqCst), 1, "an exclusive row lock admitted two transactions at once");
    });
}

#[test]
fn s4d_07_readers_share_and_a_table_scan_excludes_row_writers() {
    finish_within("readers and a scan", || {
        let m = Arc::new(LockManager::new());
        // three transactions read rows at the same time under IS and S
        let readers: Vec<_> = (1..=3i64)
            .map(|id| {
                let m = Arc::clone(&m);
                thread::spawn(move || {
                    let t = LockTxn::new(id, LockIsolation::RepeatableRead);
                    m.lock_table(&t, IntentionShared, 1).unwrap();
                    m.lock_row(&t, Shared, 1, rid(1)).unwrap();
                    thread::sleep(Duration::from_millis(30));
                    m.release_all(&t);
                })
            })
            .collect();
        for r in readers {
            r.join().unwrap();
        }
        // a whole-table shared lock keeps row writers (IX) out until it is released
        let scan = LockTxn::new(10, LockIsolation::RepeatableRead);
        m.lock_table(&scan, Shared, 1).unwrap();
        let writer = LockTxn::new(11, LockIsolation::RepeatableRead);
        let (done, h) = spawn_flag({
            let (m, writer) = (Arc::clone(&m), Arc::clone(&writer));
            move || m.lock_table(&writer, IntentionExclusive, 1).unwrap()
        });
        pause();
        assert!(!finished(&done), "IX must wait for the table scan's S lock");
        m.release_all(&scan);
        h.join().unwrap();
    });
}

#[test]
fn s4d_07_a_victim_that_is_waiting_for_a_row_gives_up_and_the_survivor_commits() {
    finish_within("row deadlock", || {
        let m = Arc::new(LockManager::new());
        let _d = DeadlockDetector::start(Arc::clone(&m), Duration::from_millis(15));
        let a = LockTxn::new(1, LockIsolation::RepeatableRead);
        let b = LockTxn::new(2, LockIsolation::RepeatableRead);
        for t in [&a, &b] {
            m.lock_table(t, IntentionExclusive, 1).unwrap();
        }
        m.lock_row(&a, Exclusive, 1, rid(1)).unwrap();
        m.lock_row(&b, Exclusive, 1, rid(2)).unwrap();
        let ha = {
            let (m, a) = (Arc::clone(&m), Arc::clone(&a));
            thread::spawn(move || m.lock_row(&a, Exclusive, 1, rid(2)))
        };
        let hb = {
            let (m, b) = (Arc::clone(&m), Arc::clone(&b));
            thread::spawn(move || {
                let r = m.lock_row(&b, Exclusive, 1, rid(1));
                if r.is_err() {
                    m.release_all(&b);
                }
                r
            })
        };
        assert_eq!(kind(hb.join().unwrap()), LockErrorKind::Deadlock);
        assert_eq!(b.state(), LockState::Aborted, "the victim's transaction is aborted");
        assert_eq!(ha.join().unwrap(), Ok(()));
        assert_eq!(a.state(), LockState::Growing, "the survivor goes on");
    });
}
