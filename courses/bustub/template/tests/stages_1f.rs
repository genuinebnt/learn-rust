//! Tests for module 1f, the buffer pool. A test name starts with its stage: `s1f_02_…` belongs to stage 1f-02, and
//! `anneal course test` runs just those.
//!
//! The tests use only the pool's public methods and a disk of their own (`MemDisk`, which counts what the pool asks of it). Most
//! tests run on a pool with a plain replacer written in this file (`FifoReplacer`), so they test the pool and not your ARC
//! replacer; a few then run the same checks with the replacers you built. The main property is a **model**: a random sequence of
//! new, fetch, write, unpin, flush and delete operations is run on the pool and on a table of "what each page should contain and
//! how often it is pinned". Whatever was evicted in between, a page must read back what was last written to it.

use std::collections::BTreeSet;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;

use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::{FrameId, PageId, BUSTUB_PAGE_SIZE};
use bustub::storage::disk::disk_manager::DiskIo;
use proptest::prelude::*;

mod common;

const PS: usize = BUSTUB_PAGE_SIZE;

fn p(n: i32) -> PageId {
    PageId(n)
}

fn config() -> ProptestConfig {
    ProptestConfig { cases: 48, max_shrink_iters: 2000, ..ProptestConfig::default() }
}

use common::pool::{pool, pool_with, MemDisk, Policy};

/// Fetches a page, writes `text` at the start of its frame, and unpins it dirty (or clean).
fn write_text(bpm: &BufferPoolManager, page: PageId, text: &str, dirty: bool) {
    let frame = bpm.fetch_page(page).expect("a frame for the page");
    bpm.frame_data(frame).write().unwrap()[..text.len()].copy_from_slice(text.as_bytes());
    assert!(bpm.unpin_page(page, dirty), "unpinning a page this helper pinned");
}

/// The first `len` bytes of a page, fetched and unpinned.
fn read_text(bpm: &BufferPoolManager, page: PageId, len: usize) -> String {
    let frame = bpm.fetch_page(page).expect("a frame for the page");
    let text = String::from_utf8_lossy(&bpm.frame_data(frame).read().unwrap()[..len]).into_owned();
    assert!(bpm.unpin_page(page, false), "unpinning a page this helper pinned");
    text
}

// ---- The model ------------------------------------------------------------------------------------------------------------

#[derive(Clone, Copy, Debug)]
enum Op {
    New,
    Fetch(usize),
    Write(usize, u8),
    Unpin(usize, bool),
    Flush(usize),
    Delete(usize),
}

fn ops(with_flush_delete: bool) -> impl Strategy<Value = Vec<Op>> {
    let extra = if with_flush_delete { 2 } else { 0 };
    prop::collection::vec(
        prop_oneof![
            2 => Just(Op::New),
            6 => (0..24usize).prop_map(Op::Fetch),
            4 => (0..24usize, any::<u8>()).prop_map(|(i, b)| Op::Write(i, b)),
            6 => (0..24usize, any::<bool>()).prop_map(|(i, b)| Op::Unpin(i, b)),
            extra => (0..24usize).prop_map(Op::Flush),
            extra => (0..24usize).prop_map(Op::Delete),
        ],
        1..200,
    )
}

struct PageModel {
    id: PageId,
    /// Every byte of the page is this, as last written.
    fill: u8,
    pins: usize,
    /// The frame it was pinned in (while pinned).
    frame: Option<FrameId>,
    /// Written since the last unpin that reported it dirty.
    unreported: bool,
    may_be_written: bool,
    deleted: bool,
}

fn pick(pages: &[PageModel], i: usize) -> Option<&PageModel> {
    if pages.is_empty() { None } else { pages.get(i % pages.len()) }
}
fn pick_mut(pages: &mut [PageModel], i: usize) -> Option<&mut PageModel> {
    let n = pages.len();
    if n == 0 { None } else { pages.get_mut(i % n) }
}

/// Runs `ops` on `bpm` and on the model. With `max_pages`, `New` stops creating pages at that many (so no eviction is ever needed).
fn run_model(bpm: &BufferPoolManager, disk: &MemDisk, frames: usize, ops: &[Op], max_pages: usize) -> Result<(), TestCaseError> {
    let mut pages: Vec<PageModel> = Vec::new();
    for (step, op) in ops.iter().enumerate() {
        let pinned = pages.iter().filter(|m| m.pins > 0).count();
        match *op {
            Op::New => {
                if pages.len() >= max_pages {
                    continue;
                }
                let id = bpm.new_page();
                prop_assert!(pages.iter().all(|m| m.id != id), "step {}: new_page returned {:?} twice", step, id);
                pages.push(PageModel { id, fill: 0, pins: 0, frame: None, unreported: false, may_be_written: false, deleted: false });
            }
            Op::Fetch(i) => {
                let Some(m) = pick_mut(&mut pages, i).filter(|m| !m.deleted) else { continue };
                let got = bpm.fetch_page(m.id);
                // a pinned page is in memory; any other page can be brought in exactly when some frame is not pinned
                let should_succeed = m.pins > 0 || pinned < frames;
                prop_assert_eq!(got.is_some(), should_succeed, "step {}: fetch_page({:?}) with {} of {} frames pinned and this page pinned {} times", step, m.id, pinned, frames, m.pins);
                if let Some(frame) = got {
                    if m.pins > 0 {
                        prop_assert_eq!(Some(frame), m.frame, "step {}: a page that is in memory keeps its frame", step);
                    } else {
                        let data = bpm.frame_data(frame).read().unwrap();
                        prop_assert!(data.iter().all(|&b| b == m.fill), "step {}: page {:?} should hold {} in every byte but starts with {} (it was evicted and brought back, or never written)", step, m.id, m.fill, data[0]);
                    }
                    m.pins += 1;
                    m.frame = Some(frame);
                }
            }
            Op::Write(i, byte) => {
                let Some(m) = pick_mut(&mut pages, i).filter(|m| m.pins > 0) else { continue };
                bpm.frame_data(m.frame.unwrap()).write().unwrap().fill(byte);
                m.fill = byte;
                m.unreported = true;
                m.may_be_written = true;
            }
            Op::Unpin(i, flag) => {
                let Some(m) = pick_mut(&mut pages, i).filter(|m| !m.deleted) else { continue };
                if m.pins == 0 {
                    // nothing to unpin: the pool says so (and a page that is not in memory has no pin either)
                    prop_assert!(!bpm.unpin_page(m.id, false), "step {}: unpin_page of {:?}, which is not pinned, must return false", step, m.id);
                    continue;
                }
                // report the writes at the last unpin at the latest; an earlier unpin may report them or not
                let report = if m.pins == 1 { m.unreported } else { m.unreported && flag };
                prop_assert!(bpm.unpin_page(m.id, report), "step {}: unpin_page of {:?}, pinned {} times, must return true", step, m.id, m.pins);
                if report {
                    m.unreported = false;
                }
                m.pins -= 1;
                if m.pins == 0 {
                    m.frame = None;
                }
            }
            Op::Flush(i) => {
                let Some(m) = pick_mut(&mut pages, i).filter(|m| !m.deleted) else { continue };
                m.may_be_written = true; // flush writes the page whether or not it is dirty
                let ok = bpm.flush_page(m.id);
                if m.pins > 0 {
                    prop_assert!(ok, "step {}: flush_page of the pinned page {:?} must succeed", step, m.id);
                    prop_assert!(disk.stored(m.id.0).iter().all(|&b| b == m.fill), "step {}: flush_page must write the page's current bytes ({} in every byte)", step, m.fill);
                }
            }
            Op::Delete(i) => {
                let Some(m) = pick_mut(&mut pages, i).filter(|m| !m.deleted) else { continue };
                let ok = bpm.delete_page(m.id);
                prop_assert_eq!(ok, m.pins == 0, "step {}: delete_page({:?}) succeeds exactly when nobody has the page pinned (pins: {})", step, m.id, m.pins);
                if ok {
                    m.deleted = true;
                }
            }
        }
        for m in pages.iter().filter(|m| m.pins > 0) {
            prop_assert_eq!(bpm.get_pin_count(m.id), Some(m.pins), "step {}: pin count of {:?}", step, m.id);
        }
    }
    // a page that was never modified and never flushed is never written to disk
    let modified: BTreeSet<i32> = pages.iter().filter(|m| m.may_be_written).map(|m| m.id.0).collect();
    let written = disk.written_pages();
    prop_assert!(written.is_subset(&modified), "pages {:?} were written to disk but never modified or flushed", written.difference(&modified).collect::<Vec<_>>());
    Ok(())
}

// ---- 1f-01 · Pages in memory ---------------------------------------------------------------------------------------------

#[test]
fn s1f_01_the_pool_reports_its_size() {
    let (bpm, _) = pool(7);
    assert_eq!(bpm.size(), 7);
}

#[test]
fn s1f_01_new_page_ids_are_distinct_and_cost_no_frame_and_no_io() {
    let (bpm, disk) = pool(2);
    let ids: BTreeSet<i32> = (0..50).map(|_| bpm.new_page().0).collect();
    assert_eq!(ids.len(), 50, "fifty calls give fifty different ids");
    assert_eq!((disk.reads(), disk.writes().len()), (0, 0), "new_page does not touch the disk");
    // and no frame was used up: two pages can still be pinned
    let (a, b) = (bpm.new_page(), bpm.new_page());
    assert!(bpm.fetch_page(a).is_some() && bpm.fetch_page(b).is_some(), "new_page must not occupy a frame");
}

#[test]
fn s1f_01_threads_never_get_the_same_page_id() {
    let (bpm, _) = pool(2);
    let bpm = Arc::new(bpm);
    let handles: Vec<_> = (0..8).map(|_| thread::spawn({ let bpm = Arc::clone(&bpm); move || (0..200).map(|_| bpm.new_page().0).collect::<Vec<_>>() })).collect();
    let all: Vec<i32> = handles.into_iter().flat_map(|h| h.join().unwrap()).collect();
    assert_eq!(all.iter().collect::<BTreeSet<_>>().len(), all.len(), "1600 ids from 8 threads must all be different");
}

#[test]
fn s1f_01_a_page_nobody_wrote_arrives_zeroed_and_a_page_on_disk_arrives_as_stored() {
    let (bpm, disk) = pool(2);
    let fresh = bpm.new_page();
    let frame = bpm.fetch_page(fresh).unwrap();
    assert!(bpm.frame_data(frame).read().unwrap().iter().all(|&b| b == 0), "a new page reads as zeros");
    bpm.unpin_page(fresh, false);
    disk.write_page(p(40), &[7; PS]).unwrap();
    let frame = bpm.fetch_page(p(40)).unwrap();
    assert!(bpm.frame_data(frame).read().unwrap().iter().all(|&b| b == 7), "a page that is on disk is read from disk");
}

#[test]
fn s1f_01_fetching_pins_and_unpinning_releases() {
    let (bpm, _) = pool(3);
    let a = bpm.new_page();
    assert_eq!(bpm.get_pin_count(a), None, "a page that was not fetched is not in memory");
    for expected in 1..=3 {
        bpm.fetch_page(a).unwrap();
        assert_eq!(bpm.get_pin_count(a), Some(expected));
    }
    assert!(bpm.unpin_page(a, false));
    assert_eq!(bpm.get_pin_count(a), Some(2));
    assert!(bpm.unpin_page(a, false) && bpm.unpin_page(a, false));
    assert_eq!(bpm.get_pin_count(a), Some(0));
    assert!(!bpm.unpin_page(a, false), "a page that is not pinned cannot be unpinned");
    assert!(!bpm.unpin_page(p(99), false), "neither can a page that is not in memory");
}

#[test]
fn s1f_01_a_page_in_memory_keeps_its_frame_and_its_bytes_and_other_pages_get_other_frames() {
    let (bpm, disk) = pool(3);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    let fa = bpm.fetch_page(a).unwrap();
    bpm.frame_data(fa).write().unwrap()[..5].copy_from_slice(b"hello");
    let fa2 = bpm.fetch_page(a).unwrap();
    let fb = bpm.fetch_page(b).unwrap();
    assert_eq!(fa, fa2, "fetching a page that is in memory returns its frame");
    assert_ne!(fa, fb, "two pages in memory are in different frames");
    assert_eq!(&bpm.frame_data(fa2).read().unwrap()[..5], b"hello", "and the bytes are still there");
    assert_eq!(disk.reads(), 2, "a hit does not read the disk again");
}

#[test]
fn s1f_01_with_every_frame_pinned_no_other_page_can_be_fetched() {
    let (bpm, _) = pool(2);
    let (a, b, c) = (bpm.new_page(), bpm.new_page(), bpm.new_page());
    bpm.fetch_page(a).unwrap();
    bpm.fetch_page(b).unwrap();
    assert_eq!(bpm.fetch_page(c), None, "both frames are pinned: no room for a third page");
    assert!(bpm.fetch_page(a).is_some(), "but a page that is already in memory can be pinned again");
}

proptest! {
    #![proptest_config(config())]

    /// With no more pages than frames nothing is ever evicted: the pool is a table of pinned buffers.
    #[test]
    fn s1f_01_a_pool_with_room_for_every_page_behaves_like_the_model(ops in ops(false)) {
        let (bpm, disk) = pool(6);
        run_model(&bpm, &disk, 6, &ops, 6)?;
    }
}

// ---- 1f-02 · Eviction that loses nothing -----------------------------------------------------------------------------------

#[test]
fn s1f_02_an_unpinned_page_makes_room_for_another() {
    let (bpm, _) = pool(2);
    let (a, b, c) = (bpm.new_page(), bpm.new_page(), bpm.new_page());
    bpm.fetch_page(a).unwrap();
    bpm.fetch_page(b).unwrap();
    assert_eq!(bpm.fetch_page(c), None);
    bpm.unpin_page(a, false);
    assert!(bpm.fetch_page(c).is_some(), "page a is not pinned, so its frame can be reused");
    assert_eq!(bpm.get_pin_count(a), None, "and page a is no longer in memory");
}

#[test]
fn s1f_02_pinned_pages_are_never_the_victim() {
    let (bpm, _) = pool(3);
    let pages: Vec<PageId> = (0..10).map(|_| bpm.new_page()).collect();
    bpm.fetch_page(pages[0]).unwrap(); // stays pinned throughout
    write_text(&bpm, pages[0], "pinned", true);
    bpm.fetch_page(pages[0]).unwrap();
    for &page in &pages[1..] {
        bpm.fetch_page(page).unwrap();
        bpm.unpin_page(page, false);
    }
    assert!(bpm.get_pin_count(pages[0]).is_some_and(|n| n >= 1), "the pinned page is still in memory");
}

#[test]
fn s1f_02_a_dirty_page_survives_eviction() {
    let (bpm, _) = pool(2);
    let pages: Vec<PageId> = (0..6).map(|_| bpm.new_page()).collect();
    write_text(&bpm, pages[0], "remember me", true);
    for &page in &pages[1..] {
        write_text(&bpm, page, "other", true); // forces page 0 out
    }
    assert_eq!(read_text(&bpm, pages[0], 11), "remember me", "an evicted dirty page is written back and read again");
}

#[test]
fn s1f_02_a_clean_page_costs_no_write_and_its_unreported_changes_are_not_promised() {
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    bpm.fetch_page(a).unwrap();
    bpm.unpin_page(a, false); // unchanged
    bpm.fetch_page(b).unwrap(); // evicts a
    bpm.unpin_page(b, false);
    bpm.fetch_page(a).unwrap();
    assert_eq!(disk.writes(), Vec::<i32>::new(), "clean pages are never written back");
}

#[test]
fn s1f_02_dirt_accumulates_across_pins() {
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    let frame = bpm.fetch_page(a).unwrap();
    bpm.fetch_page(a).unwrap(); // two pins
    bpm.frame_data(frame).write().unwrap()[0] = 9;
    bpm.unpin_page(a, true); // reports the change
    bpm.unpin_page(a, false); // the last unpin says "clean": the earlier report must not be forgotten
    bpm.fetch_page(b).unwrap();
    assert_eq!(disk.written_pages(), BTreeSet::from([a.0]), "the page was reported dirty once, so it is written back");
    bpm.unpin_page(b, false);
    assert_eq!(read_text(&bpm, a, 1).as_bytes(), [9], "and its change survived");
}

#[test]
fn s1f_02_many_pages_pass_through_a_small_pool() {
    let (bpm, _) = pool(3);
    let pages: Vec<PageId> = (0..100).map(|_| bpm.new_page()).collect();
    for (i, &page) in pages.iter().enumerate() {
        write_text(&bpm, page, &format!("page number {i}"), true);
    }
    for (i, &page) in pages.iter().enumerate().rev() {
        let text = format!("page number {i}");
        assert_eq!(read_text(&bpm, page, text.len()), text);
    }
}

proptest! {
    #![proptest_config(config())]

    /// More pages than frames, any interleaving of pins, writes and unpins: what was last written is what is read, `fetch_page`
    /// fails exactly when every frame is pinned, pin counts are exact, and a page that was never modified is never written.
    #[test]
    fn s1f_02_a_small_pool_behaves_like_the_model_whatever_is_evicted(ops in ops(false)) {
        let (bpm, disk) = pool(3);
        run_model(&bpm, &disk, 3, &ops, usize::MAX)?;
    }
}

#[test]
fn s1f_02_the_pool_works_under_the_replacers_you_built() {
    for policy in [Policy::Arc, Policy::LruK(2)] {
        let (bpm, disk) = pool_with(policy, 4);
        let pages: Vec<PageId> = (0..40).map(|_| bpm.new_page()).collect();
        for round in 0..3u8 {
            for (i, &page) in pages.iter().enumerate() {
                if (i + round as usize) % 3 == 0 {
                    write_text(&bpm, page, &format!("{policy:?}-{round}-{i}"), true);
                } else {
                    read_text(&bpm, page, 1);
                }
            }
        }
        for (i, &page) in pages.iter().enumerate() {
            let last = (0..3u8).rev().find(|&r| (i + r as usize) % 3 == 0);
            if let Some(r) = last {
                let text = format!("{policy:?}-{r}-{i}");
                assert_eq!(read_text(&bpm, page, text.len()), text, "{policy:?}: page {i}");
            }
        }
        assert!(disk.written_pages().len() <= 40);
    }
}

// ---- 1f-03 · Flush and delete ----------------------------------------------------------------------------------------------

#[test]
fn s1f_03_flush_page_writes_the_page_even_when_it_is_clean() {
    let (bpm, disk) = pool(2);
    let a = bpm.new_page();
    write_text(&bpm, a, "flushed", false); // not reported dirty
    assert!(bpm.flush_page(a));
    assert_eq!(&disk.stored(a.0)[..7], b"flushed", "flush writes the page's current bytes");
}

#[test]
fn s1f_03_flushing_a_page_that_is_not_in_memory_fails() {
    let (bpm, disk) = pool(2);
    assert!(!bpm.flush_page(p(5)));
    assert!(disk.writes().is_empty());
}

#[test]
fn s1f_03_a_flushed_page_is_clean_so_eviction_does_not_write_it_again() {
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    write_text(&bpm, a, "x", true);
    assert!(bpm.flush_page(a));
    assert_eq!(disk.writes(), vec![a.0]);
    bpm.fetch_page(b).unwrap(); // evicts a
    assert_eq!(disk.writes(), vec![a.0], "page a was clean after the flush: evicting it writes nothing more");
}

#[test]
fn s1f_03_a_pinned_page_can_be_flushed_and_stays_pinned() {
    let (bpm, disk) = pool(2);
    let a = bpm.new_page();
    let frame = bpm.fetch_page(a).unwrap();
    bpm.frame_data(frame).write().unwrap()[0] = 42;
    assert!(bpm.flush_page(a));
    assert_eq!(disk.stored(a.0)[0], 42);
    assert_eq!(bpm.get_pin_count(a), Some(1), "flushing does not change the pin count");
}

#[test]
fn s1f_03_flush_all_pages_writes_every_page_in_memory() {
    let (bpm, disk) = pool(4);
    let pages: Vec<PageId> = (0..3).map(|_| bpm.new_page()).collect();
    for (i, &page) in pages.iter().enumerate() {
        write_text(&bpm, page, &format!("p{i}"), false);
    }
    bpm.flush_all_pages();
    assert_eq!(disk.written_pages(), pages.iter().map(|q| q.0).collect::<BTreeSet<_>>());
}

#[test]
fn s1f_03_a_pinned_page_cannot_be_deleted_but_an_unpinned_one_can_and_its_frame_is_free_again() {
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    bpm.fetch_page(a).unwrap();
    assert!(!bpm.delete_page(a), "a pinned page cannot be deleted");
    bpm.unpin_page(a, false);
    assert!(bpm.delete_page(a));
    assert_eq!(bpm.get_pin_count(a), None, "a deleted page is not in memory");
    assert!(bpm.fetch_page(b).is_some(), "and its frame can be used again");
    assert!(disk.deletes.lock().unwrap().contains(&a.0), "the disk is told to free the page");
}

#[test]
fn s1f_03_deleting_a_page_that_is_not_in_memory_succeeds_and_a_deleted_dirty_page_is_not_written() {
    let (bpm, disk) = pool(2);
    assert!(bpm.delete_page(p(77)), "nothing to do counts as success");
    let a = bpm.new_page();
    write_text(&bpm, a, "doomed", true);
    assert!(bpm.delete_page(a));
    assert!(bpm.delete_page(a), "deleting twice is fine");
    assert!(disk.writes().is_empty(), "a page that is deleted is not written back");
}

proptest! {
    #![proptest_config(config())]

    /// The same model with flush and delete in the mix, on a pool smaller than the set of pages.
    #[test]
    fn s1f_03_flush_and_delete_agree_with_the_model(ops in ops(true)) {
        let (bpm, disk) = pool(3);
        run_model(&bpm, &disk, 3, &ops, usize::MAX)?;
    }
}

// ---- 1f-04 · Boss -------------------------------------------------------------------------------------------------------

#[test]
fn s1f_04_threads_share_a_small_pool_without_losing_updates() {
    // 8 threads x 300 increments on random pages out of 40, through a pool of 12 frames. Every increment is a fetch, a change
    // under the frame's write latch, and an unpin(dirty). At the end every page holds exactly the number of increments applied.
    let (bpm, _) = pool_with(Policy::Arc, 12);
    let bpm = Arc::new(bpm);
    let pages: Vec<PageId> = (0..40).map(|_| bpm.new_page()).collect();
    let applied: Arc<Vec<AtomicUsize>> = Arc::new((0..40).map(|_| AtomicUsize::new(0)).collect());
    let handles: Vec<_> = (0..8)
        .map(|t| {
            let (bpm, pages, applied) = (Arc::clone(&bpm), pages.clone(), Arc::clone(&applied));
            thread::spawn(move || {
                let mut x = 1 + t as u64;
                for _ in 0..300 {
                    x = x.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
                    let i = ((x >> 33) % 40) as usize;
                    let frame = loop {
                        if let Some(frame) = bpm.fetch_page(pages[i]) {
                            break frame;
                        }
                        thread::yield_now(); // every frame is pinned right now: try again
                    };
                    {
                        let mut data = bpm.frame_data(frame).write().unwrap();
                        let n = u32::from_le_bytes(data[..4].try_into().unwrap()) + 1;
                        data[..4].copy_from_slice(&n.to_le_bytes());
                    }
                    applied[i].fetch_add(1, Ordering::SeqCst);
                    assert!(bpm.unpin_page(pages[i], true));
                }
            })
        })
        .collect();
    handles.into_iter().for_each(|h| h.join().unwrap());
    for (i, &page) in pages.iter().enumerate() {
        let frame = bpm.fetch_page(page).expect("a free frame at the end");
        let n = u32::from_le_bytes(bpm.frame_data(frame).read().unwrap()[..4].try_into().unwrap());
        bpm.unpin_page(page, false);
        assert_eq!(n as usize, applied[i].load(Ordering::SeqCst), "page {i}");
    }
}

#[test]
fn s1f_04_the_replacer_changes_which_pages_are_in_memory_but_not_what_they_contain() {
    // The same sequence of writes through three pools with three different replacers must leave every page with the same bytes.
    let mut seen: Vec<Vec<String>> = Vec::new();
    for policy in [Policy::Fifo, Policy::Arc, Policy::LruK(2)] {
        let (bpm, _) = pool_with(policy, 5);
        let pages: Vec<PageId> = (0..30).map(|_| bpm.new_page()).collect();
        let mut x = 7u64;
        for step in 0..600 {
            x = x.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
            let page = pages[((x >> 33) % 30) as usize];
            write_text(&bpm, page, &format!("{step:04}"), true);
        }
        seen.push(pages.iter().map(|&page| read_text(&bpm, page, 4)).collect());
    }
    assert_eq!(seen[0], seen[1], "FIFO and ARC pools must hold the same data");
    assert_eq!(seen[0], seen[2], "FIFO and LRU-K pools must hold the same data");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 16, ..config() })]

    /// The model, run once under each replacer you built.
    #[test]
    fn s1f_04_the_model_holds_under_arc_and_lru_k(ops in ops(true)) {
        for policy in [Policy::Arc, Policy::LruK(2)] {
            let (bpm, disk) = pool_with(policy, 4);
            run_model(&bpm, &disk, 4, &ops, usize::MAX)?;
        }
    }
}
