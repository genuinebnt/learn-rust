//! Tests for the page guard stages (1g-01 … 1g-03). A test named `s1g_03_…` belongs to stage 1g-01.

use std::io;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::mpsc;
use std::sync::Arc;
use std::thread;
use std::time::Duration;

use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::{PageData, PageId, BUSTUB_PAGE_SIZE};
use bustub::storage::disk::disk_manager::DiskIo;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;

const PS: usize = BUSTUB_PAGE_SIZE;
const WAIT: Duration = Duration::from_secs(10);

struct CountingDisk {
    inner: DiskManagerUnlimitedMemory,
    writes: AtomicUsize,
}

impl DiskIo for CountingDisk {
    fn read_page(&self, page_id: PageId, buf: &mut PageData) -> io::Result<()> {
        self.inner.read_page(page_id, buf)
    }
    fn write_page(&self, page_id: PageId, data: &PageData) -> io::Result<()> {
        self.writes.fetch_add(1, Ordering::SeqCst);
        self.inner.write_page(page_id, data)
    }
    fn delete_page(&self, page_id: PageId) {
        self.inner.delete_page(page_id)
    }
}

fn pool(frames: usize) -> (Arc<BufferPoolManager>, Arc<CountingDisk>) {
    let disk = Arc::new(CountingDisk { inner: DiskManagerUnlimitedMemory::new(), writes: AtomicUsize::new(0) });
    (Arc::new(BufferPoolManager::new(frames, disk.clone())), disk)
}

fn text(guard_data: &PageData, len: usize) -> String {
    String::from_utf8_lossy(&guard_data[..len]).into_owned()
}

// ---- 1g-01 · checked_read_page ---------------------------------------------------------------------------------------------

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

// ---- 1g-01 · dropping a read guard -------------------------------------------------------------------------------------------

#[test]
fn s1g_02_dropping_a_read_guard_unpins_the_page() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let guard = bpm.checked_read_page(page).unwrap();
    assert_eq!(bpm.get_pin_count(page), Some(1), "dropping a read guard unpins the page");
    drop(guard);
    assert_eq!(bpm.get_pin_count(page), Some(0), "dropping a read guard unpins the page");
}

#[test]
fn s1g_02_leaving_a_scope_drops_the_guard() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    {
        let _guard = bpm.checked_read_page(page).expect("a frame");
    }
    assert_eq!(bpm.get_pin_count(page), Some(0), "leaving a scope drops the guard");
}

#[test]
fn s1g_02_release_is_idempotent() {
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
fn s1g_02_a_released_guard_gives_up_the_latch() {
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
fn s1g_02_an_unpinned_page_can_be_evicted() {
    let (bpm, _) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    let guard = bpm.checked_read_page(a).unwrap();
    assert!(bpm.checked_read_page(b).is_none(), "a is pinned");
    drop(guard);
    assert!(bpm.checked_read_page(b).is_some(), "a was unpinned, so b can take its frame");
}

#[test]
fn s1g_02_each_guard_releases_only_its_own_pin() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let a = bpm.checked_read_page(page).unwrap();
    let b = bpm.checked_read_page(page).unwrap();
    drop(a);
    assert_eq!(bpm.get_pin_count(page), Some(1), "each guard releases only its own pin");
    drop(b);
    assert_eq!(bpm.get_pin_count(page), Some(0), "each guard releases only its own pin");
}

// ---- 1g-01 · write guards ---------------------------------------------------------------------------------------------------

#[test]
fn s1g_03_a_write_guard_changes_the_page_and_the_change_is_seen() {
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
fn s1g_03_get_data_mut_marks_the_page_dirty_and_a_look_does_not() {
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
fn s1g_03_dirt_reaches_the_pool_so_the_page_survives_eviction() {
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    bpm.checked_write_page(a).unwrap().get_data_mut()[..4].copy_from_slice(b"data");
    bpm.checked_write_page(b).unwrap(); // evicts a: written because the guard reported the dirt
    assert_eq!(disk.writes.load(Ordering::SeqCst), 1, "dirt reaches the pool so the page survives eviction");
    assert_eq!(text(bpm.checked_read_page(a).unwrap().get_data(), 4), "data", "dirt reaches the pool so the page survives eviction");
}

#[test]
fn s1g_03_an_untouched_write_guard_leaves_the_page_clean() {
    let (bpm, disk) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    drop(bpm.checked_write_page(a).unwrap());
    drop(bpm.checked_write_page(b).unwrap());
    assert_eq!(disk.writes.load(Ordering::SeqCst), 0, "nobody called get_data_mut: nothing to write back");
}

#[test]
fn s1g_03_a_writer_excludes_everyone_else_until_it_is_dropped() {
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
fn s1g_03_release_is_idempotent_for_writers_too() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let mut guard = bpm.checked_write_page(page).unwrap();
    guard.release();
    guard.release();
    assert_eq!(bpm.get_pin_count(page), Some(0), "release is idempotent for writers too");
    assert!(bpm.checked_write_page(page).is_some(), "this will hang if the latch was not released");
}

#[test]
fn s1g_03_deref_mut_works_like_get_data_mut() {
    let (bpm, _) = pool(3);
    let page = bpm.new_page();
    let mut guard = bpm.checked_write_page(page).unwrap();
    guard[0] = 7;
    assert!(guard.is_dirty(), "deref mut works like get data mut: expected `guard.is_dirty()`");
    assert_eq!(guard[0], 7, "deref mut works like get data mut");
}

// ---- 1g-02 · read_page and write_page --------------------------------------------------------------------------------------------

#[test]
fn s1g_04_they_return_a_guard_when_there_is_room() {
    let (bpm, _) = pool(2);
    let page = bpm.new_page();
    let _r = bpm.read_page(page);
    let _w = bpm.read_page(page);
    assert_eq!(bpm.get_pin_count(page), Some(2), "they return a guard when there is room");
}

#[test]
#[should_panic(expected = "every frame is pinned")]
fn s1g_04_read_page_panics_when_nothing_can_be_evicted() {
    let (bpm, _) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    let _ga = bpm.read_page(a);
    let _gb = bpm.read_page(b);
}

#[test]
#[should_panic(expected = "every frame is pinned")]
fn s1g_04_write_page_panics_when_nothing_can_be_evicted() {
    let (bpm, _) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    let _ga = bpm.write_page(a);
    let _gb = bpm.write_page(b);
}

// ---- 1g-02 · flush through a guard --------------------------------------------------------------------------------------------------

#[test]
fn s1g_05_a_write_guard_can_flush_its_page() {
    let (bpm, disk) = pool(2);
    let page = bpm.new_page();
    let mut guard = bpm.write_page(page);
    guard.get_data_mut()[..5].copy_from_slice(b"flush");
    assert!(guard.is_dirty(), "a write guard can flush its page: expected `guard.is_dirty()`");
    guard.flush();
    assert!(!guard.is_dirty(), "flushed: clean");
    assert_eq!(disk.writes.load(Ordering::SeqCst), 1, "a write guard can flush its page");
    let mut buf = [0u8; PS];
    disk.read_page(page, &mut buf).unwrap();
    assert_eq!(&buf[..5], b"flush", "a write guard can flush its page");
    assert_eq!(bpm.get_pin_count(page), Some(1), "the guard keeps its pin");
}

#[test]
fn s1g_05_flushing_a_clean_guard_still_writes() {
    let (bpm, disk) = pool(2);
    let page = bpm.new_page();
    let mut guard = bpm.write_page(page);
    guard.flush();
    assert_eq!(disk.writes.load(Ordering::SeqCst), 1, "flushing a clean guard still writes");
}

#[test]
fn s1g_05_a_read_guard_can_flush_too() {
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
fn s1g_05_flushing_while_holding_the_latch_does_not_deadlock() {
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

// ---- 1g-02 · flush_page must not hold the pool lock while it waits for a latch -----------------------------------------------------

#[test]
fn s1g_06_a_blocked_flush_does_not_block_the_rest_of_the_pool() {
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
fn s1g_06_flush_page_still_writes_the_latest_bytes() {
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
fn s1g_06_a_flushed_page_is_not_left_pinned_so_it_can_be_evicted() {
    let (bpm, _) = pool(1);
    let (a, b) = (bpm.new_page(), bpm.new_page());
    bpm.write_page(a).get_data_mut()[0] = 1;
    assert!(bpm.flush_page(a), "a flushed page is not left pinned so it can be evicted: expected `bpm.flush_page(a)`");
    assert!(bpm.checked_read_page(b).is_some(), "a is unpinned again: its frame can be reused");
}

// ---- 1g-03 · the module as a whole -------------------------------------------------------------------------------------------------

#[test]
fn s1g_07_guards_moved_into_a_vec_keep_their_pages_pinned_until_dropped() {
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
fn s1g_07_assigning_a_guard_drops_the_one_it_replaces() {
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
fn s1g_07_many_threads_incrementing_one_page_lose_nothing() {
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
