//! Tests for module 1g, the page guards. A test name starts with its stage: `s1g_02_…` belongs to stage 1g-02, and
//! `anneal course test` runs just those.
//!
//! The tests use only the public methods of the pool and of the guards, and a disk of their own (`MemDisk`). Anything that could
//! hang (a latch that is never released, a flush that waits for a lock it holds) waits with a timeout, so a deadlock fails the test
//! with a message instead of freezing it.

use std::sync::mpsc;
use std::sync::Arc;
use std::thread;
use std::time::Duration;

use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::{PageData, BUSTUB_PAGE_SIZE};
use bustub::storage::page::page_guard::{ReadPageGuard, WritePageGuard};
use bustub::storage::disk::disk_manager::DiskIo;
#[path = "common/pool.rs"]
mod pool;
use pool::{pool_with, MemDisk, Policy};
use proptest::prelude::*;

mod common;

const PS: usize = BUSTUB_PAGE_SIZE;
const WAIT: Duration = Duration::from_secs(10);

fn pool(frames: usize) -> (Arc<BufferPoolManager>, Arc<MemDisk>) {
    let (bpm, disk) = pool_with(Policy::Fifo, frames);
    (Arc::new(bpm), disk)
}

fn text(guard_data: &PageData, len: usize) -> String {
    String::from_utf8_lossy(&guard_data[..len]).into_owned()
}

// ---- 1g-01 · Guards that release themselves -------------------------------------------------------------------------------


#[derive(Clone, Copy, Debug)]
enum GuardOp {
    Read(usize),
    Write(usize, u8),
    Drop(usize),
    Release(usize),
}

fn guard_ops() -> impl Strategy<Value = Vec<GuardOp>> {
    prop::collection::vec(
        prop_oneof![
            4 => (0..8usize).prop_map(GuardOp::Read),
            3 => (0..8usize, any::<u8>()).prop_map(|(i, b)| GuardOp::Write(i, b)),
            4 => (0..16usize).prop_map(GuardOp::Drop),
            1 => (0..16usize).prop_map(GuardOp::Release),
        ],
        1..150,
    )
}

enum Held<'a> {
    Reader(ReadPageGuard<'a>, usize),
    Writer(WritePageGuard<'a>, usize),
}

impl Held<'_> {
    fn page(&self) -> usize {
        match self {
            Held::Reader(_, page) | Held::Writer(_, page) => *page,
        }
    }
}

/// Guards taken and dropped in any order: the pool's pin count of a page is the number of live guards on it, a writer is alone on its
/// page, and what a writer wrote is what the next guard sees even after the page was evicted in between.
fn run_guards(policy: Policy, frames: usize, ops: &[GuardOp]) -> Result<(), TestCaseError> {
    let (bpm, _disk) = pool_with(policy, frames);
    let pages: Vec<_> = (0..8).map(|_| bpm.new_page()).collect();
    let mut fill = [0u8; 8];
    let mut held: Vec<Held> = Vec::new();
    for (step, op) in ops.iter().enumerate() {
        let pinned_pages = |held: &[Held]| (0..8).filter(|&i| held.iter().any(|h| h.page() == i)).count();
        match *op {
            GuardOp::Read(i) | GuardOp::Write(i, _) => {
                let on_page = held.iter().filter(|h| h.page() == i).count();
                let writer_there = held.iter().any(|h| matches!(h, Held::Writer(_, q) if *q == i));
                let write = matches!(op, GuardOp::Write(..));
                if writer_there || (write && on_page > 0) {
                    continue; // this thread would wait for itself
                }
                let should_succeed = on_page > 0 || pinned_pages(&held) < frames;
                if write {
                    let got = bpm.checked_write_page(pages[i]);
                    prop_assert_eq!(got.is_some(), should_succeed, "step {}: checked_write_page with {} of {} frames pinned", step, pinned_pages(&held), frames);
                    if let Some(mut guard) = got {
                        prop_assert!(guard.get_data().iter().all(|&b| b == fill[i]), "step {}: page {} should hold {} in every byte", step, i, fill[i]);
                        if let GuardOp::Write(_, byte) = *op {
                            guard.get_data_mut().fill(byte);
                            fill[i] = byte;
                        }
                        held.push(Held::Writer(guard, i));
                    }
                } else {
                    let got = bpm.checked_read_page(pages[i]);
                    prop_assert_eq!(got.is_some(), should_succeed, "step {}: checked_read_page with {} of {} frames pinned", step, pinned_pages(&held), frames);
                    if let Some(guard) = got {
                        prop_assert!(guard.get_data().iter().all(|&b| b == fill[i]), "step {}: page {} should hold {} in every byte", step, i, fill[i]);
                        held.push(Held::Reader(guard, i));
                    }
                }
            }
            GuardOp::Drop(i) => {
                if !held.is_empty() {
                    let at = i % held.len();
                    drop(held.remove(at));
                }
            }
            GuardOp::Release(i) => {
                if !held.is_empty() {
                    let at = i % held.len();
                    match &mut held[at] {
                        Held::Reader(g, _) => g.release(),
                        Held::Writer(g, _) => g.release(),
                    }
                    // a released guard no longer counts: drop it now so the model and the pool agree
                    drop(held.remove(at));
                }
            }
        }
        for i in 0..8 {
            let live = held.iter().filter(|h| h.page() == i).count();
            if live > 0 {
                prop_assert_eq!(bpm.get_pin_count(pages[i]), Some(live), "step {}: pin count of page {} must be the number of live guards on it", step, i);
            }
        }
    }
    held.clear();
    for i in 0..8 {
        prop_assert!(matches!(bpm.get_pin_count(pages[i]), None | Some(0)), "page {} still pinned after every guard was dropped", i);
    }
    Ok(())
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 48, max_shrink_iters: 2000, failure_persistence: None, ..ProptestConfig::default() })]

    #[test]
    fn s1g_01_pin_counts_match_the_live_guards_for_guards_taken_and_dropped_in_any_order(ops in guard_ops()) {
        run_guards(Policy::Fifo, 3, &ops)?;
    }
}

#[test]
fn s1g_01_a_read_guard_pins_the_page_and_shows_its_bytes() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let guard = bpm.checked_read_page(page).expect("a free frame");
    assert_eq!(guard.get_page_id(), page, "a read guard pins the page and shows its bytes");
    assert_eq!(bpm.get_pin_count(page), Some(1), "a read guard pins the page and shows its bytes");
    assert_eq!(guard.get_data().len(), PS, "a read guard pins the page and shows its bytes");
    assert!(guard.get_data().iter().all(|&b| b == 0), "a read guard pins the page and shows its bytes: expected `guard.get_data().iter().all(|&b| b == 0)`");
}

#[test]
fn s1g_01_the_guard_derefs_to_the_page() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let frame = bpm.fetch_page(page).unwrap();
    bpm.frame_data(frame).write().unwrap()[..2].copy_from_slice(b"hi");
    bpm.unpin_page(page, true);
    let guard = bpm.checked_read_page(page).unwrap();
    assert_eq!(&guard[..2], b"hi", "the guard derefs to the page");
    assert_eq!(&guard.get_data()[..2], b"hi", "the guard derefs to the page");
}

#[test]
fn s1g_01_many_readers_share_a_page() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let a = bpm.checked_read_page(page).unwrap();
    let b = bpm.checked_read_page(page).unwrap();
    let c = bpm.checked_read_page(page).unwrap();
    assert_eq!(bpm.get_pin_count(page), Some(3), "many readers share a page");
    assert_eq!((a.get_page_id(), b.get_page_id(), c.get_page_id()), (page, page, page), "many readers share a page");
}

#[test]
fn s1g_01_no_guard_when_every_frame_is_pinned() {
    let (bpm, _) = pool(2);
    let (a, b, c) = (bpm.new_page(), bpm.new_page(), bpm.new_page());
    let _ga = bpm.checked_read_page(a).unwrap();
    let _gb = bpm.checked_read_page(b).unwrap();
    assert!(bpm.checked_read_page(c).is_none(), "no guard when every frame is pinned: expected `bpm.checked_read_page(c).is_none()`");
}


#[test]
fn s1g_01_dropping_a_read_guard_unpins_the_page() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let guard = bpm.checked_read_page(page).unwrap();
    assert_eq!(bpm.get_pin_count(page), Some(1), "dropping a read guard unpins the page");
    drop(guard);
    assert_eq!(bpm.get_pin_count(page), Some(0), "dropping a read guard unpins the page");
}

#[test]
fn s1g_01_leaving_a_scope_drops_the_guard() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    {
        let _guard = bpm.checked_read_page(page).expect("a frame");
    }
    assert_eq!(bpm.get_pin_count(page), Some(0), "leaving a scope drops the guard");
}

#[test]
fn s1g_01_release_is_idempotent() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let mut guard = bpm.checked_read_page(page).unwrap();
    guard.release();
    assert_eq!(bpm.get_pin_count(page), Some(0), "release is idempotent");
    guard.release(); // "Another drop should have no effect."
    assert_eq!(bpm.get_pin_count(page), Some(0), "release is idempotent");
    drop(guard); // and so does the destructor
    assert_eq!(bpm.get_pin_count(page), Some(0), "release is idempotent");
}

#[test]
fn s1g_01_a_released_guard_gives_up_the_latch() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let mut guard = bpm.checked_read_page(page).unwrap();
    let frame = bpm.fetch_page(page).unwrap(); // just to learn the frame; one more pin
    assert!(bpm.frame_data(frame).try_write().is_err(), "a reader holds the latch");
    guard.release();
    assert!(bpm.frame_data(frame).try_write().is_ok(), "released: the latch is free");
    bpm.unpin_page(page, false);
}

#[test]
fn s1g_01_an_unpinned_page_can_be_evicted() {
    let (bpm, _) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    let guard = bpm.checked_read_page(a).unwrap();
    assert!(bpm.checked_read_page(b).is_none(), "a is pinned");
    drop(guard);
    assert!(bpm.checked_read_page(b).is_some(), "a was unpinned, so b can take its frame");
}

#[test]
fn s1g_01_each_guard_releases_only_its_own_pin() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let a = bpm.checked_read_page(page).unwrap();
    let b = bpm.checked_read_page(page).unwrap();
    drop(a);
    assert_eq!(bpm.get_pin_count(page), Some(1), "each guard releases only its own pin");
    drop(b);
    assert_eq!(bpm.get_pin_count(page), Some(0), "each guard releases only its own pin");
}


#[test]
fn s1g_01_a_write_guard_changes_the_page_and_the_change_is_seen() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    {
        let mut guard = bpm.checked_write_page(page).unwrap();
        assert_eq!(bpm.get_pin_count(page), Some(1), "a write guard changes the page and the change is seen");
        guard.get_data_mut()[..5].copy_from_slice(b"hello");
        assert_eq!(&guard.get_data()[..5], b"hello", "a write guard changes the page and the change is seen");
    }
    assert_eq!(bpm.get_pin_count(page), Some(0), "a write guard changes the page and the change is seen");
    assert_eq!(text(bpm.checked_read_page(page).unwrap().get_data(), 5), "hello", "a write guard changes the page and the change is seen");
}

#[test]
fn s1g_01_get_data_mut_marks_the_page_dirty_and_a_look_does_not() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let mut guard = bpm.checked_write_page(page).unwrap();
    assert!(!guard.is_dirty(), "get data mut marks the page dirty and a look does not: expected `!guard.is_dirty()`");
    let _ = guard.get_data();
    assert!(!guard.is_dirty(), "get data mut marks the page dirty and a look does not: expected `!guard.is_dirty()`");
    guard.get_data_mut()[0] = 1;
    assert!(guard.is_dirty(), "get data mut marks the page dirty and a look does not: expected `guard.is_dirty()`");
}

#[test]
fn s1g_01_dirt_reaches_the_pool_so_the_page_survives_eviction() {
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    bpm.checked_write_page(a).unwrap().get_data_mut()[..4].copy_from_slice(b"data");
    bpm.checked_write_page(b).unwrap(); // evicts a: written because the guard reported the dirt
    assert_eq!(disk.writes().len(), 1, "dirt reaches the pool so the page survives eviction");
    assert_eq!(text(bpm.checked_read_page(a).unwrap().get_data(), 4), "data", "dirt reaches the pool so the page survives eviction");
}

#[test]
fn s1g_01_an_untouched_write_guard_leaves_the_page_clean() {
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    drop(bpm.checked_write_page(a).unwrap());
    drop(bpm.checked_write_page(b).unwrap());
    assert_eq!(disk.writes().len(), 0, "nobody called get_data_mut: nothing to write back");
}

#[test]
fn s1g_01_a_writer_excludes_everyone_else_until_it_is_dropped() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let guard = bpm.checked_write_page(page).unwrap();
    let (tx, rx) = mpsc::channel();
    let reader = {
        let bpm = Arc::clone(&bpm);
        thread::spawn(move || {
            let g = bpm.checked_read_page(page).unwrap();
            tx.send(g.get_data()[0]).unwrap();
        })
    };
    thread::sleep(Duration::from_millis(100));
    assert!(rx.try_recv().is_err(), "the reader got in while the writer held the page");
    drop(guard);
    rx.recv_timeout(WAIT).expect("the reader never got in: was the latch released?");
    reader.join().unwrap();
}

#[test]
fn s1g_01_release_is_idempotent_for_writers_too() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let mut guard = bpm.checked_write_page(page).unwrap();
    guard.release();
    guard.release();
    assert_eq!(bpm.get_pin_count(page), Some(0), "release is idempotent for writers too");
    assert!(bpm.checked_write_page(page).is_some(), "this will hang if the latch was not released");
}

#[test]
fn s1g_01_deref_mut_works_like_get_data_mut() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let mut guard = bpm.checked_write_page(page).unwrap();
    guard[0] = 7;
    assert!(guard.is_dirty(), "deref mut works like get data mut: expected `guard.is_dirty()`");
    assert_eq!(guard[0], 7, "deref mut works like get data mut");
}


#[test]
fn s1g_02_they_return_a_guard_when_there_is_room() {
    let (bpm, _) = pool(2);
    let page = bpm.new_page();
    let _r = bpm.read_page(page);
    let _w = bpm.read_page(page);
    assert_eq!(bpm.get_pin_count(page), Some(2), "they return a guard when there is room");
}

#[test]
#[should_panic(expected = "every frame is pinned")]
fn s1g_02_read_page_panics_when_nothing_can_be_evicted() {
    let (bpm, _) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    let _ga = bpm.read_page(a);
    let _gb = bpm.read_page(b);
}

#[test]
#[should_panic(expected = "every frame is pinned")]
fn s1g_02_write_page_panics_when_nothing_can_be_evicted() {
    let (bpm, _) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    let _ga = bpm.write_page(a);
    let _gb = bpm.write_page(b);
}


#[test]
fn s1g_02_a_write_guard_can_flush_its_page() {
    let (bpm, disk) = pool(2);
    let page = bpm.new_page();
    let mut guard = bpm.write_page(page);
    guard.get_data_mut()[..5].copy_from_slice(b"flush");
    assert!(guard.is_dirty(), "a write guard can flush its page: expected `guard.is_dirty()`");
    guard.flush();
    assert!(!guard.is_dirty(), "flushed: clean");
    assert_eq!(disk.writes().len(), 1, "a write guard can flush its page");
    let mut buf = [0u8; PS];
    disk.read_page(page, &mut buf).unwrap();
    assert_eq!(&buf[..5], b"flush", "a write guard can flush its page");
    assert_eq!(bpm.get_pin_count(page), Some(1), "the guard keeps its pin");
}

#[test]
fn s1g_02_flushing_a_clean_guard_still_writes() {
    let (bpm, disk) = pool(2);
    let page = bpm.new_page();
    let mut guard = bpm.write_page(page);
    guard.flush();
    assert_eq!(disk.writes().len(), 1, "flushing a clean guard still writes");
}

#[test]
fn s1g_02_a_read_guard_can_flush_too() {
    let (bpm, disk) = pool(2);
    let page = bpm.new_page();
    bpm.write_page(page).get_data_mut()[0] = 9;
    let mut guard = bpm.read_page(page);
    guard.flush();
    let mut buf = [0u8; PS];
    disk.read_page(page, &mut buf).unwrap();
    assert_eq!(buf[0], 9, "a read guard can flush too");
}

#[test]
fn s1g_02_flushing_while_holding_the_latch_does_not_deadlock() {
    let (bpm, _) = pool(2);
    let page = bpm.new_page();
    let (tx, rx) = mpsc::channel();
    let t = {
        let bpm = Arc::clone(&bpm);
        thread::spawn(move || {
            let mut guard = bpm.write_page(page);
            guard.get_data_mut()[0] = 1;
            guard.flush();
            tx.send(()).unwrap();
        })
    };
    rx.recv_timeout(WAIT).expect("flush() hung: it must not ask for the latch the guard already holds");
    t.join().unwrap();
}


#[test]
fn s1g_02_a_blocked_flush_does_not_block_the_rest_of_the_pool() {
    // Thread W holds the write latch on page P. Thread F calls flush_page(P): it has to wait for W. Meanwhile W asks the pool for
    // another page. If F waits while holding the pool's lock, W waits for F and F waits for W: deadlock.
    let (bpm, _) = pool(4);
    let (p, q) = (bpm.new_page(), bpm.new_page());
    let (done_tx, done_rx) = mpsc::channel();
    let main_bpm = Arc::clone(&bpm);
    let worker = thread::spawn(move || {
        let bpm = main_bpm;
        let mut guard_p = bpm.write_page(p);
        guard_p.get_data_mut()[0] = 5;
        let flusher = {
            let bpm = Arc::clone(&bpm);
            thread::spawn(move || bpm.flush_page(p))
        };
        thread::sleep(Duration::from_millis(200)); // F is now waiting for P's latch
        let guard_q = bpm.write_page(q); // needs the pool's lock
        drop(guard_q);
        drop(guard_p); // F can go on
        let flushed = flusher.join().unwrap();
        done_tx.send(flushed).unwrap();
    });
    let flushed = done_rx.recv_timeout(WAIT).expect("deadlock: flush_page waits for a latch while holding the pool's lock");
    assert!(flushed, "a blocked flush does not block the rest of the pool: expected `flushed`");
    worker.join().unwrap();
}

#[test]
fn s1g_02_flush_page_still_writes_the_latest_bytes() {
    let (bpm, disk) = pool(2);
    let page = bpm.new_page();
    {
        let mut guard = bpm.write_page(page);
        guard.get_data_mut()[..3].copy_from_slice(b"abc");
    }
    assert!(bpm.flush_page(page), "flush page still writes the latest bytes: expected `bpm.flush_page(page)`");
    let mut buf = [0u8; PS];
    disk.read_page(page, &mut buf).unwrap();
    assert_eq!(&buf[..3], b"abc", "flush page still writes the latest bytes");
    assert_eq!(bpm.get_pin_count(page), Some(0), "flush_page leaves the pin count where it found it");
}

#[test]
fn s1g_02_a_flushed_page_is_not_left_pinned_so_it_can_be_evicted() {
    let (bpm, _) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    bpm.write_page(a).get_data_mut()[0] = 1;
    assert!(bpm.flush_page(a), "a flushed page is not left pinned so it can be evicted: expected `bpm.flush_page(a)`");
    assert!(bpm.checked_read_page(b).is_some(), "a is unpinned again: its frame can be reused");
}


#[test]
fn s1g_03_guards_moved_into_a_vec_keep_their_pages_pinned_until_dropped() {
    let (bpm, _) = pool(4);
    let pages: Vec<_> = (0..4).map(|_| bpm.new_page()).collect();
    let mut guards: Vec<_> = pages.iter().map(|&p| bpm.write_page(p)).collect();
    assert!(pages.iter().all(|&p| bpm.get_pin_count(p) == Some(1)), "guards moved into a vec keep their pages pinned until dropped: expected `pages.iter().all(|&p| bpm.get_pin_count(p) == Some(1))`");
    assert!(bpm.checked_read_page(bpm.new_page()).is_none(), "guards moved into a vec keep their pages pinned until dropped: expected `bpm.checked_read_page(bpm.new_page()).is_none()`");
    let first = guards.remove(0); // moved out of the Vec
    assert_eq!(bpm.get_pin_count(pages[0]), Some(1), "moving a guard doesn't release it");
    drop(first);
    assert_eq!(bpm.get_pin_count(pages[0]), Some(0), "guards moved into a vec keep their pages pinned until dropped");
    guards.clear();
    assert!(pages.iter().all(|&p| bpm.get_pin_count(p) == Some(0)), "guards moved into a vec keep their pages pinned until dropped: expected `pages.iter().all(|&p| bpm.get_pin_count(p) == Some(0))`");
}

#[test]
fn s1g_03_assigning_a_guard_drops_the_one_it_replaces() {
    let (bpm, _) = pool(4);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    let mut guard = bpm.read_page(a);
    let other = bpm.read_page(b);
    assert_eq!((bpm.get_pin_count(a), bpm.get_pin_count(b)), (Some(1), Some(1)), "assigning a guard drops the one it replaces");
    guard = other; // the old guard (page a) is dropped here
    assert_eq!(bpm.get_pin_count(a), Some(0), "assigning a guard drops the one it replaces");
    assert_eq!(bpm.get_pin_count(b), Some(1), "assigning a guard drops the one it replaces");
    assert_eq!(guard.get_page_id(), b, "assigning a guard drops the one it replaces");
}

#[test]
fn s1g_03_many_threads_incrementing_one_page_lose_nothing() {
    let (bpm, _) = pool(4);
    let page = bpm.new_page();
    let handles: Vec<_> = (0..4)
        .map(|_| {
            let bpm = Arc::clone(&bpm);
            thread::spawn(move || {
                for _ in 0..500 {
                    let mut guard = bpm.write_page(page);
                    let n = u32::from_le_bytes(guard.get_data()[..4].try_into().unwrap()) + 1;
                    guard.get_data_mut()[..4].copy_from_slice(&n.to_le_bytes());
                }
            })
        })
        .collect();
    handles.into_iter().for_each(|h| h.join().unwrap());
    let n = u32::from_le_bytes(bpm.read_page(page).get_data()[..4].try_into().unwrap());
    assert_eq!(n, 2000, "many threads incrementing one page lose nothing");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 24, max_shrink_iters: 2000, failure_persistence: None, ..ProptestConfig::default() })]

    /// The guard model once more, on a pool that uses the replacers you built.
    #[test]
    fn s1g_03_guards_behave_the_same_under_arc_and_lru_k(ops in guard_ops()) {
        run_guards(Policy::Arc, 3, &ops)?;
        run_guards(Policy::LruK(2), 3, &ops)?;
    }
}
