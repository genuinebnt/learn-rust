//! Tests for the buffer pool stages (1f-01 … 1f-04). A test named `s1f_05_…` belongs to stage 1f-02.

use std::io;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;

use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::{PageData, PageId, BUSTUB_PAGE_SIZE};
use bustub::storage::disk::disk_manager::DiskIo;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;

const PS: usize = BUSTUB_PAGE_SIZE;

fn p(n: i32) -> PageId {
    PageId(n)
}

/// An in-memory disk that counts what the pool asks of it.
struct CountingDisk {
    inner: DiskManagerUnlimitedMemory,
    reads: AtomicUsize,
    writes: AtomicUsize,
    deletes: Mutex<Vec<i32>>,
}

impl CountingDisk {
    fn new() -> Arc<CountingDisk> {
        Arc::new(CountingDisk { inner: DiskManagerUnlimitedMemory::new(), reads: AtomicUsize::new(0), writes: AtomicUsize::new(0), deletes: Mutex::new(Vec::new()) })
    }
    fn reads(&self) -> usize {
        self.reads.load(Ordering::SeqCst)
    }
    fn writes(&self) -> usize {
        self.writes.load(Ordering::SeqCst)
    }
}

impl DiskIo for CountingDisk {
    fn read_page(&self, page_id: PageId, buf: &mut PageData) -> io::Result<()> {
        self.reads.fetch_add(1, Ordering::SeqCst);
        self.inner.read_page(page_id, buf)
    }
    fn write_page(&self, page_id: PageId, data: &PageData) -> io::Result<()> {
        self.writes.fetch_add(1, Ordering::SeqCst);
        self.inner.write_page(page_id, data)
    }
    fn delete_page(&self, page_id: PageId) {
        self.deletes.lock().unwrap().push(page_id.0);
        self.inner.delete_page(page_id)
    }
}

fn pool(frames: usize) -> (BufferPoolManager, Arc<CountingDisk>) {
    let disk = CountingDisk::new();
    (BufferPoolManager::new(frames, disk.clone()), disk)
}

/// Fetches a page, writes `text` at the start of its frame, and unpins it dirty (or clean).
fn write_text(bpm: &BufferPoolManager, page: PageId, text: &str, dirty: bool) {
    let frame = bpm.fetch_page(page).expect("a frame for the page");
    bpm.frame_data(frame).write().unwrap()[..text.len()].copy_from_slice(text.as_bytes());
    assert!(bpm.unpin_page(page, dirty), "in helper `write_text`: expected `bpm.unpin_page(page, dirty)`");
}

/// The first `len` bytes of a page, fetched and unpinned.
fn read_text(bpm: &BufferPoolManager, page: PageId, len: usize) -> String {
    let frame = bpm.fetch_page(page).expect("a frame for the page");
    let text = String::from_utf8_lossy(&bpm.frame_data(frame).read().unwrap()[..len]).into_owned();
    assert!(bpm.unpin_page(page, false), "in helper `read_text`: expected `bpm.unpin_page(page, false)`");
    text
}

// ---- 1f-01 · new and size ----------------------------------------------------------------------------------------------

#[test]
fn s1f_01_the_pool_reports_its_size() {
    assert_eq!(pool(10).0.size(), 10, "the pool reports its size");
    assert_eq!(pool(1).0.size(), 1, "the pool reports its size");
    assert_eq!(pool(0).0.size(), 0, "the pool reports its size");
}

#[test]
fn s1f_01_the_frames_start_zeroed() {
    let (bpm, _) = pool(3);
    for n in 0..3 {
        // frame_data is public so tests can look: every frame is an 8 KiB buffer of zeros
        let data = bpm.frame_data(bustub::common::config::FrameId(n)).read().unwrap();
        assert_eq!(data.len(), PS, "the frames start zeroed");
        assert!(data.iter().all(|&b| b == 0), "the frames start zeroed: expected `data.iter().all(|&b| b == 0)`");
    }
}

// ---- 1f-01 · new_page --------------------------------------------------------------------------------------------------

#[test]
fn s1f_02_page_ids_count_up_from_zero() {
    let (bpm, _) = pool(4);
    assert_eq!([bpm.new_page(), bpm.new_page(), bpm.new_page()], [p(0), p(1), p(2)], "page ids count up from zero");
}

#[test]
fn s1f_02_new_page_does_not_touch_the_disk_or_the_frames() {
    let (bpm, disk) = pool(2);
    for _ in 0..10 {
        bpm.new_page();
    }
    assert_eq!((disk.reads(), disk.writes()), (0, 0), "new page does not touch the disk or the frames");
}

#[test]
fn s1f_02_threads_never_get_the_same_id() {
    let (bpm, _) = pool(2);
    let bpm = Arc::new(bpm);
    let handles: Vec<_> = (0..4)
        .map(|_| {
            let bpm = Arc::clone(&bpm);
            thread::spawn(move || (0..50).map(|_| bpm.new_page().0).collect::<Vec<_>>())
        })
        .collect();
    let mut all: Vec<i32> = handles.into_iter().flat_map(|h| h.join().unwrap()).collect();
    all.sort();
    assert_eq!(all, (0..200).collect::<Vec<_>>(), "threads never get the same id");
}

// ---- 1f-01 · fetch_page: a page that is not in memory ----------------------------------------------------------------------

#[test]
fn s1f_03_a_new_page_arrives_zeroed() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let frame = bpm.fetch_page(page).expect("a free frame");
    assert!(bpm.frame_data(frame).read().unwrap().iter().all(|&b| b == 0), "a new page arrives zeroed: expected `bpm.frame_data(frame).read().unwrap().iter().all(|&b| b == 0)`");
}

#[test]
fn s1f_03_a_page_on_disk_is_read_into_the_frame() {
    let (bpm, disk) = pool(3);
    let mut data = [0u8; PS];
    data[..5].copy_from_slice(b"hello");
    disk.write_page(p(7), &data).unwrap();
    let frame = bpm.fetch_page(p(7)).unwrap();
    assert_eq!(&bpm.frame_data(frame).read().unwrap()[..5], b"hello", "a page on disk is read into the frame");
    assert_eq!(disk.reads(), 1, "a page on disk is read into the frame");
}

#[test]
fn s1f_03_different_pages_get_different_frames() {
    let (bpm, _) = pool(4);
    let frames: Vec<_> = (0..4).map(|_| bpm.fetch_page(bpm.new_page()).unwrap()).collect();
    let mut sorted: Vec<usize> = frames.iter().map(|f| f.0).collect();
    sorted.sort();
    sorted.dedup();
    assert_eq!(sorted.len(), 4, "different pages get different frames");
    assert!(sorted.iter().all(|&f| f < 4), "different pages get different frames: expected `sorted.iter().all(|&f| f < 4)`");
}

#[test]
fn s1f_03_each_miss_reads_the_disk_once() {
    let (bpm, disk) = pool(5);
    for _ in 0..5 {
        bpm.fetch_page(bpm.new_page()).unwrap();
    }
    assert_eq!(disk.reads(), 5, "each miss reads the disk once");
}

// ---- 1f-02 · pin counts and hits -------------------------------------------------------------------------------------------

#[test]
fn s1f_04_a_fetched_page_has_one_pin() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    assert_eq!(bpm.get_pin_count(page), None, "not in memory yet");
    bpm.fetch_page(page).unwrap();
    assert_eq!(bpm.get_pin_count(page), Some(1), "a fetched page has one pin");
}

#[test]
fn s1f_04_fetching_a_resident_page_adds_a_pin_and_reuses_the_frame() {
    let (bpm, disk) = pool(3);
    let page = bpm.new_page();
    let first = bpm.fetch_page(page).unwrap();
    let second = bpm.fetch_page(page).unwrap();
    assert_eq!(first, second, "fetching a resident page adds a pin and reuses the frame");
    assert_eq!(bpm.get_pin_count(page), Some(2), "fetching a resident page adds a pin and reuses the frame");
    assert_eq!(disk.reads(), 1, "the second fetch is a hit: no disk read");
}

#[test]
fn s1f_04_pin_counts_are_per_page() {
    let (bpm, _) = pool(3);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    bpm.fetch_page(a).unwrap();
    bpm.fetch_page(a).unwrap();
    bpm.fetch_page(b).unwrap();
    assert_eq!((bpm.get_pin_count(a), bpm.get_pin_count(b)), (Some(2), Some(1)), "pin counts are per page");
}

#[test]
fn s1f_04_a_hit_does_not_reload_the_page() {
    let (bpm, _) = pool(2);
    let page = bpm.new_page();
    let frame = bpm.fetch_page(page).unwrap();
    bpm.frame_data(frame).write().unwrap()[0] = 42;
    let again = bpm.fetch_page(page).unwrap();
    assert_eq!(bpm.frame_data(again).read().unwrap()[0], 42, "an unsaved change must still be there");
}

// ---- 1f-02 · unpin_page ------------------------------------------------------------------------------------------------------

#[test]
fn s1f_05_unpin_releases_one_pin() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    bpm.fetch_page(page).unwrap();
    bpm.fetch_page(page).unwrap();
    assert!(bpm.unpin_page(page, false), "unpin releases one pin: expected `bpm.unpin_page(page, false)`");
    assert_eq!(bpm.get_pin_count(page), Some(1), "unpin releases one pin");
    assert!(bpm.unpin_page(page, false), "unpin releases one pin: expected `bpm.unpin_page(page, false)`");
    assert_eq!(bpm.get_pin_count(page), Some(0), "unpinned but still in memory");
}

#[test]
fn s1f_05_unpinning_a_page_that_is_not_pinned_fails() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    assert!(!bpm.unpin_page(page, false), "not in memory");
    bpm.fetch_page(page).unwrap();
    assert!(bpm.unpin_page(page, false), "unpinning a page that is not pinned fails: expected `bpm.unpin_page(page, false)`");
    assert!(!bpm.unpin_page(page, false), "its pin count is already 0");
    assert_eq!(bpm.get_pin_count(page), Some(0), "and must not go below 0");
}

#[test]
fn s1f_05_a_page_can_be_fetched_again_after_unpinning() {
    let (bpm, disk) = pool(3);
    let page = bpm.new_page();
    bpm.fetch_page(page).unwrap();
    bpm.unpin_page(page, false);
    bpm.fetch_page(page).unwrap();
    assert_eq!(bpm.get_pin_count(page), Some(1), "a page can be fetched again after unpinning");
    assert_eq!(disk.reads(), 1, "still resident: no second read");
}

// ---- 1f-02 · eviction ----------------------------------------------------------------------------------------------------------

#[test]
fn s1f_06_a_full_pool_of_pinned_pages_cannot_take_another() {
    let (bpm, _) = pool(2);
    let (a, b, c) = (bpm.new_page(), bpm.new_page(), bpm.new_page());
    bpm.fetch_page(a).unwrap();
    bpm.fetch_page(b).unwrap();
    assert_eq!(bpm.fetch_page(c), None, "a full pool of pinned pages cannot take another");
    assert_eq!(bpm.get_pin_count(c), None, "a full pool of pinned pages cannot take another");
}

#[test]
fn s1f_06_an_unpinned_page_makes_room() {
    let (bpm, _) = pool(2);
    let (a, b, c) = (bpm.new_page(), bpm.new_page(), bpm.new_page());
    bpm.fetch_page(a).unwrap();
    bpm.fetch_page(b).unwrap();
    bpm.unpin_page(a, false);
    assert!(bpm.fetch_page(c).is_some(), "an unpinned page makes room: expected `bpm.fetch_page(c).is_some()`");
    assert_eq!(bpm.get_pin_count(a), None, "a was evicted");
    assert_eq!(bpm.get_pin_count(b), Some(1), "an unpinned page makes room");
    assert_eq!(bpm.get_pin_count(c), Some(1), "an unpinned page makes room");
}

#[test]
fn s1f_06_pinned_pages_are_never_the_victim() {
    let (bpm, _) = pool(3);
    let pages: Vec<_> = (0..3).map(|_| bpm.new_page()).collect();
    for &page in &pages {
        bpm.fetch_page(page).unwrap();
    }
    bpm.unpin_page(pages[1], false); // only the middle one is evictable
    let extra = bpm.new_page();
    bpm.fetch_page(extra).unwrap();
    assert_eq!((bpm.get_pin_count(pages[0]), bpm.get_pin_count(pages[1]), bpm.get_pin_count(pages[2])), (Some(1), None, Some(1)), "pinned pages are never the victim");
}

#[test]
fn s1f_06_the_replacer_decides_least_recently_accessed_first() {
    let (bpm, _) = pool(2);
    let (a, b, c) = (bpm.new_page(), bpm.new_page(), bpm.new_page());
    bpm.fetch_page(a).unwrap();
    bpm.fetch_page(b).unwrap();
    bpm.unpin_page(b, false);
    bpm.unpin_page(a, false); // unpinned in the opposite order: access order still decides
    bpm.fetch_page(c).unwrap();
    assert_eq!(bpm.get_pin_count(a), None, "a was accessed first, so a goes");
    assert_eq!(bpm.get_pin_count(b), Some(0), "the replacer decides least recently accessed first");
}

#[test]
fn s1f_06_a_page_touched_twice_survives_longer_than_one_touched_once() {
    // ARC: the second access moved page a to the frequent side; with p = 0 the recent side is evicted first.
    let (bpm, _) = pool(2);
    let (a, b, c) = (bpm.new_page(), bpm.new_page(), bpm.new_page());
    bpm.fetch_page(a).unwrap();
    bpm.unpin_page(a, false);
    bpm.fetch_page(a).unwrap(); // hit
    bpm.unpin_page(a, false);
    bpm.fetch_page(b).unwrap();
    bpm.unpin_page(b, false);
    bpm.fetch_page(c).unwrap();
    assert_eq!(bpm.get_pin_count(b), None, "b (touched once) goes before a (touched twice)");
    assert_eq!(bpm.get_pin_count(a), Some(0), "a page touched twice survives longer than one touched once");
}

#[test]
fn s1f_06_clean_victims_cost_no_disk_writes() {
    let (bpm, disk) = pool(1);
    for _ in 0..5 {
        let page = bpm.new_page();
        bpm.fetch_page(page).unwrap();
        bpm.unpin_page(page, false);
    }
    assert_eq!(disk.writes(), 0, "clean victims cost no disk writes");
    assert_eq!(disk.reads(), 5, "clean victims cost no disk writes");
}

// ---- 1f-03 · dirty pages are written back before their frame is reused ------------------------------------------------------

#[test]
fn s1f_07_a_dirty_page_survives_eviction() {
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    write_text(&bpm, a, "page a", true);
    write_text(&bpm, b, "page b", true); // evicts a: written first
    assert_eq!(disk.writes(), 1, "a dirty page survives eviction");
    assert_eq!(read_text(&bpm, a, 6), "page a", "a dirty page survives eviction");
    assert_eq!(read_text(&bpm, b, 6), "page b", "a dirty page survives eviction");
    assert_eq!(disk.writes(), 2, "reading a evicted b, which was dirty");
}

#[test]
fn s1f_07_a_clean_page_is_not_written_and_its_changes_are_lost() {
    // The dirty flag is the caller's word. Unpinning with is_dirty = false means "I didn't change it".
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    write_text(&bpm, a, "lost", false);
    write_text(&bpm, b, "other", false);
    assert_eq!(disk.writes(), 0, "a clean page is not written and its changes are lost");
    assert_eq!(read_text(&bpm, a, 4), "\0\0\0\0", "a clean page is not written and its changes are lost");
}

#[test]
fn s1f_07_dirt_accumulates_across_pins() {
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    let frame = bpm.fetch_page(a).unwrap();
    bpm.fetch_page(a).unwrap(); // pinned twice
    bpm.frame_data(frame).write().unwrap()[0] = 9;
    bpm.unpin_page(a, true);
    bpm.unpin_page(a, false); // the second unpinner says "clean", the first said "dirty": dirty wins
    bpm.fetch_page(b).unwrap();
    assert_eq!(disk.writes(), 1, "dirt accumulates across pins");
    bpm.unpin_page(b, false);
    let frame = bpm.fetch_page(a).unwrap();
    assert_eq!(bpm.frame_data(frame).read().unwrap()[0], 9, "dirt accumulates across pins");
}

#[test]
fn s1f_07_after_the_write_back_the_page_is_clean() {
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    write_text(&bpm, a, "x", true);
    write_text(&bpm, b, "y", false); // evicts a (dirty): 1 write
    write_text(&bpm, a, "x", false); // evicts b (clean): no write; a is read back, clean
    write_text(&bpm, b, "y", false); // evicts a: a is clean again, no write
    assert_eq!(disk.writes(), 1, "after the write back the page is clean");
}

#[test]
fn s1f_07_many_pages_through_a_small_pool() {
    let (bpm, _) = pool(3);
    let pages: Vec<_> = (0..20).map(|_| bpm.new_page()).collect();
    for (i, &page) in pages.iter().enumerate() {
        write_text(&bpm, page, &format!("page {i:02}"), true);
    }
    for (i, &page) in pages.iter().enumerate() {
        assert_eq!(read_text(&bpm, page, 7), format!("page {i:02}"), "many pages through a small pool");
    }
}

// ---- 1f-03 · flushing ------------------------------------------------------------------------------------------------------------

#[test]
fn s1f_08_flush_page_writes_the_page_to_disk() {
    let (bpm, disk) = pool(3);
    let page = bpm.new_page();
    write_text(&bpm, page, "flushed", true);
    assert_eq!(disk.writes(), 0, "flush page writes the page to disk");
    assert!(bpm.flush_page(page), "flush page writes the page to disk: expected `bpm.flush_page(page)`");
    assert_eq!(disk.writes(), 1, "flush page writes the page to disk");
    let mut buf = [0u8; PS];
    disk.read_page(page, &mut buf).unwrap();
    assert_eq!(&buf[..7], b"flushed", "flush page writes the page to disk");
}

#[test]
fn s1f_08_flush_page_writes_even_a_clean_page() {
    let (bpm, disk) = pool(3);
    let page = bpm.new_page();
    bpm.fetch_page(page).unwrap();
    bpm.unpin_page(page, false);
    assert!(bpm.flush_page(page), "flush page writes even a clean page: expected `bpm.flush_page(page)`");
    assert_eq!(disk.writes(), 1, "flush page writes even a clean page");
}

#[test]
fn s1f_08_flushing_a_page_that_is_not_in_memory_fails() {
    let (bpm, disk) = pool(3);
    assert!(!bpm.flush_page(p(5)), "flushing a page that is not in memory fails: expected `!bpm.flush_page(p(5))`");
    assert_eq!(disk.writes(), 0, "flushing a page that is not in memory fails");
}

#[test]
fn s1f_08_a_flushed_page_is_clean_so_eviction_does_not_write_it_again() {
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    write_text(&bpm, a, "once", true);
    bpm.flush_page(a);
    write_text(&bpm, b, "two", false); // evicts a
    assert_eq!(disk.writes(), 1, "only the flush");
}

#[test]
fn s1f_08_a_pinned_page_can_be_flushed() {
    let (bpm, disk) = pool(2);
    let page = bpm.new_page();
    let frame = bpm.fetch_page(page).unwrap();
    bpm.frame_data(frame).write().unwrap()[..3].copy_from_slice(b"abc");
    assert!(bpm.flush_page(page), "a pinned page can be flushed: expected `bpm.flush_page(page)`");
    let mut buf = [0u8; PS];
    disk.read_page(page, &mut buf).unwrap();
    assert_eq!(&buf[..3], b"abc", "a pinned page can be flushed");
    assert_eq!(bpm.get_pin_count(page), Some(1), "flushing doesn't unpin");
}

#[test]
fn s1f_08_flush_all_pages_writes_every_resident_page() {
    let (bpm, disk) = pool(5);
    let pages: Vec<_> = (0..4).map(|_| bpm.new_page()).collect();
    for &page in &pages {
        write_text(&bpm, page, "data", true);
    }
    bpm.flush_all_pages();
    assert_eq!(disk.writes(), 4, "flush all pages writes every resident page");
    bpm.flush_all_pages();
    assert_eq!(disk.writes(), 8, "flushing doesn't depend on the dirty flag");
}

// ---- 1f-03 · delete_page ---------------------------------------------------------------------------------------------------------

#[test]
fn s1f_09_a_pinned_page_cannot_be_deleted() {
    let (bpm, disk) = pool(2);
    let page = bpm.new_page();
    bpm.fetch_page(page).unwrap();
    assert!(!bpm.delete_page(page), "a pinned page cannot be deleted: expected `!bpm.delete_page(page)`");
    assert_eq!(bpm.get_pin_count(page), Some(1), "a pinned page cannot be deleted");
    assert!(disk.deletes.lock().unwrap().is_empty(), "a pinned page cannot be deleted: expected `disk.deletes.lock().unwrap().is_empty()`");
}

#[test]
fn s1f_09_an_unpinned_page_is_deleted_and_its_frame_freed() {
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    bpm.fetch_page(a).unwrap();
    bpm.unpin_page(a, false);
    assert!(bpm.delete_page(a), "an unpinned page is deleted and its frame freed: expected `bpm.delete_page(a)`");
    assert_eq!(bpm.get_pin_count(a), None, "an unpinned page is deleted and its frame freed");
    assert_eq!(*disk.deletes.lock().unwrap(), vec![a.0], "the disk is told to free the page");
    assert!(bpm.fetch_page(b).is_some(), "the freed frame takes another page");
}

#[test]
fn s1f_09_deleting_a_page_that_is_not_in_memory_succeeds() {
    let (bpm, disk) = pool(2);
    assert!(bpm.delete_page(p(77)), "deleting a page that is not in memory succeeds: expected `bpm.delete_page(p(77))`");
    assert_eq!(*disk.deletes.lock().unwrap(), vec![77], "deleting a page that is not in memory succeeds");
}

#[test]
fn s1f_09_a_deleted_dirty_page_is_not_written() {
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    write_text(&bpm, a, "gone", true);
    assert!(bpm.delete_page(a), "a deleted dirty page is not written: expected `bpm.delete_page(a)`");
    write_text(&bpm, b, "next", true);
    bpm.flush_all_pages();
    assert_eq!(disk.writes(), 1, "only b's flush: a's dirt died with a");
}

#[test]
fn s1f_09_deleting_twice_is_fine() {
    let (bpm, _) = pool(2);
    let page = bpm.new_page();
    bpm.fetch_page(page).unwrap();
    bpm.unpin_page(page, false);
    assert!(bpm.delete_page(page), "deleting twice is fine: expected `bpm.delete_page(page)`");
    assert!(bpm.delete_page(page), "deleting twice is fine: expected `bpm.delete_page(page)`");
}

#[test]
fn s1f_09_the_replacer_forgets_a_deleted_frame() {
    // If the replacer still listed the frame, it could be chosen as a victim while it holds a different page.
    let (bpm, _) = pool(2);
    let (a, b, c, d) = (bpm.new_page(), bpm.new_page(), bpm.new_page(), bpm.new_page());
    bpm.fetch_page(a).unwrap();
    bpm.unpin_page(a, false);
    bpm.delete_page(a);
    bpm.fetch_page(b).unwrap(); // takes a free frame
    bpm.fetch_page(c).unwrap(); // takes the other
    assert_eq!(bpm.fetch_page(d), None, "b and c are pinned: nothing is evictable");
}

// ---- 1f-04 · the module as a whole -------------------------------------------------------------------------------------------------

#[test]
fn s1f_10_threads_share_a_small_pool_without_losing_updates() {
    // 8 threads x 300 increments on random pages out of 40, through a pool of 12 frames. Every increment is a fetch, a
    // change under the frame's write latch, and an unpin(dirty). At the end every page holds exactly the number of increments
    // its threads applied.
    let (bpm, _) = pool(12);
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
                    assert!(bpm.unpin_page(pages[i], true), "threads share a small pool without losing updates: expected `bpm.unpin_page(pages[i], true)`");
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
