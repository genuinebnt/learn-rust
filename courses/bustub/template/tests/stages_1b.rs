//! Tests for the disk scheduler stages (1b-01 … 1b-04). A test named `s1b_04_…` belongs to stage 1b-01.

use std::io;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::mpsc;
use std::sync::{Arc, Barrier, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use bustub::common::channel::{consume, Channel};
use bustub::common::config::{PageData, PageId, BUSTUB_PAGE_SIZE};
use bustub::common::promise::{promise, BrokenPromise};
use bustub::common::rwlatch::ReaderWriterLatch;
use bustub::storage::disk::disk_manager::DiskIo;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;
use bustub::storage::disk::disk_scheduler::{execute, DiskRequest, DiskScheduler, ShardedDiskScheduler};

const PS: usize = BUSTUB_PAGE_SIZE;
const WAIT: Duration = Duration::from_secs(10);

/// Waits for a future, but not forever: a request that is never completed fails the test instead of hanging it.
fn wait<T: Send + 'static>(future: bustub::common::promise::Future<T>) -> Result<T, BrokenPromise> {
    let (tx, rx) = mpsc::channel();
    thread::spawn(move || {
        let _ = tx.send(future.get());
    });
    rx.recv_timeout(WAIT).expect("timed out waiting for a future: a promise that is never set, or one dropped without waking it")
}

fn page_of(byte: u8) -> Box<PageData> {
    Box::new([byte; PS])
}

fn memory_disk() -> Arc<DiskManagerUnlimitedMemory> {
    Arc::new(DiskManagerUnlimitedMemory::new())
}

/// A disk that logs every operation as "R<page>" or "W<page>", in the order the worker performed it, and can be slowed down.
struct RecordingDisk {
    inner: DiskManagerUnlimitedMemory,
    log: Mutex<Vec<String>>,
    delay: Duration,
}

impl RecordingDisk {
    fn new(delay_ms: u64) -> Arc<RecordingDisk> {
        Arc::new(RecordingDisk { inner: DiskManagerUnlimitedMemory::new(), log: Mutex::new(Vec::new()), delay: Duration::from_millis(delay_ms) })
    }
    fn ops(&self) -> Vec<String> {
        self.log.lock().unwrap().clone()
    }
}

impl DiskIo for RecordingDisk {
    fn read_page(&self, page_id: PageId, buf: &mut PageData) -> io::Result<()> {
        thread::sleep(self.delay);
        self.log.lock().unwrap().push(format!("R{}", page_id.0));
        self.inner.read_page(page_id, buf)
    }
    fn write_page(&self, page_id: PageId, data: &PageData) -> io::Result<()> {
        thread::sleep(self.delay);
        self.log.lock().unwrap().push(format!("W{}", page_id.0));
        self.inner.write_page(page_id, data)
    }
    fn delete_page(&self, page_id: PageId) {
        self.log.lock().unwrap().push(format!("D{}", page_id.0));
        self.inner.delete_page(page_id)
    }
}

/// Writes fail with an error; reads of page 13 panic.
struct BadDisk;

impl DiskIo for BadDisk {
    fn read_page(&self, page_id: PageId, buf: &mut PageData) -> io::Result<()> {
        assert!(page_id.0 != 13, "unlucky page");
        buf.fill(7);
        Ok(())
    }
    fn write_page(&self, _: PageId, _: &PageData) -> io::Result<()> {
        Err(io::Error::new(io::ErrorKind::PermissionDenied, "disk is read-only"))
    }
    fn delete_page(&self, _: PageId) {}
}

// ---- 1b-01 · Channel::put ----------------------------------------------------------------------------------------------

#[test]
fn s1b_01_a_new_channel_is_empty() {
    let ch: Channel<u32> = Channel::new();
    assert!(ch.is_empty());
    assert_eq!(ch.len(), 0);
}

#[test]
fn s1b_01_put_adds_elements() {
    let ch = Channel::new();
    ch.put("a");
    ch.put("b");
    ch.put("c");
    assert_eq!(ch.len(), 3);
    assert!(!ch.is_empty());
}

#[test]
fn s1b_01_put_takes_elements_that_cannot_be_cloned() {
    let ch = Channel::new();
    ch.put(Box::new(5));
    ch.put(Box::new(6));
    assert_eq!(ch.len(), 2);
}

#[test]
fn s1b_01_put_never_blocks_and_works_from_many_threads() {
    let ch = Arc::new(Channel::new());
    let handles: Vec<_> = (0..4)
        .map(|t| {
            let ch = Arc::clone(&ch);
            thread::spawn(move || (0..25).for_each(|i| ch.put(t * 100 + i)))
        })
        .collect();
    handles.into_iter().for_each(|h| h.join().unwrap());
    assert_eq!(ch.len(), 100);
}

// ---- 1b-01 · Channel::get ----------------------------------------------------------------------------------------------

#[test]
fn s1b_02_get_returns_elements_in_the_order_they_were_put() {
    let ch = Channel::new();
    for i in 0..5 {
        ch.put(i);
    }
    let got: Vec<i32> = (0..5).map(|_| ch.get()).collect();
    assert_eq!(got, [0, 1, 2, 3, 4]);
    assert!(ch.is_empty());
}

#[test]
fn s1b_02_get_waits_for_an_element() {
    let ch = Arc::new(Channel::new());
    let (tx, rx) = mpsc::channel();
    let getter = {
        let ch = Arc::clone(&ch);
        thread::spawn(move || tx.send(ch.get()).unwrap())
    };
    thread::sleep(Duration::from_millis(100));
    assert!(rx.try_recv().is_err(), "get returned although nothing was put");
    ch.put("hello");
    assert_eq!(rx.recv_timeout(WAIT).expect("get never woke up"), "hello");
    getter.join().unwrap();
}

#[test]
fn s1b_02_each_element_goes_to_exactly_one_getter() {
    let ch = Arc::new(Channel::new());
    let (tx, rx) = mpsc::channel();
    let getters: Vec<_> = (0..4)
        .map(|_| {
            let (ch, tx) = (Arc::clone(&ch), tx.clone());
            thread::spawn(move || (0..25).for_each(|_| tx.send(ch.get()).unwrap()))
        })
        .collect();
    drop(tx);
    for i in 0..100 {
        ch.put(i);
    }
    let mut got: Vec<i32> = rx.iter().collect();
    getters.into_iter().for_each(|g| g.join().unwrap());
    got.sort();
    assert_eq!(got, (0..100).collect::<Vec<_>>());
}

#[test]
fn s1b_02_producers_and_a_consumer_lose_nothing() {
    let ch = Arc::new(Channel::new());
    let producers: Vec<_> = (0..4)
        .map(|_| {
            let ch = Arc::clone(&ch);
            thread::spawn(move || (1..=1000u64).for_each(|i| ch.put(i)))
        })
        .collect();
    let sum: u64 = (0..4000).map(|_| ch.get()).sum();
    producers.into_iter().for_each(|p| p.join().unwrap());
    assert_eq!(sum, 4 * 500_500);
}

#[test]
fn s1b_02_each_producers_elements_stay_in_order() {
    let ch = Arc::new(Channel::new());
    let producers: Vec<_> = (0..3)
        .map(|p| {
            let ch = Arc::clone(&ch);
            thread::spawn(move || (0..200).for_each(|i| ch.put((p, i))))
        })
        .collect();
    let got: Vec<(i32, i32)> = (0..600).map(|_| ch.get()).collect();
    producers.into_iter().for_each(|p| p.join().unwrap());
    for p in 0..3 {
        let mine: Vec<i32> = got.iter().filter(|(q, _)| *q == p).map(|(_, i)| *i).collect();
        assert_eq!(mine, (0..200).collect::<Vec<_>>(), "producer {p}");
    }
}

// ---- 1b-01 · consume ---------------------------------------------------------------------------------------------------

#[test]
fn s1b_03_consume_calls_f_on_each_element_in_order() {
    let ch = Channel::new();
    for i in [1, 2, 3] {
        ch.put(Some(i));
    }
    ch.put(None);
    let mut seen = Vec::new();
    consume(&ch, |x| seen.push(x));
    assert_eq!(seen, [1, 2, 3]);
}

#[test]
fn s1b_03_a_none_stops_it_and_what_follows_stays_in_the_channel() {
    let ch = Channel::new();
    ch.put(Some("a"));
    ch.put(None);
    ch.put(Some("b"));
    let mut seen = Vec::new();
    consume(&ch, |x| seen.push(x));
    assert_eq!(seen, ["a"]);
    assert_eq!(ch.len(), 1, "the element after the stop signal is not consumed");
}

#[test]
fn s1b_03_a_stop_signal_alone_ends_it_at_once() {
    let ch: Channel<Option<u8>> = Channel::new();
    ch.put(None);
    consume(&ch, |_| panic!("nothing to consume"));
}

#[test]
fn s1b_03_a_worker_thread_runs_until_stopped() {
    let ch = Arc::new(Channel::new());
    let total = Arc::new(AtomicUsize::new(0));
    let worker = {
        let (ch, total) = (Arc::clone(&ch), Arc::clone(&total));
        thread::spawn(move || consume(&ch, |n: usize| drop(total.fetch_add(n, Ordering::SeqCst))))
    };
    for n in 1..=10 {
        ch.put(Some(n));
    }
    ch.put(None);
    worker.join().unwrap();
    assert_eq!(total.load(Ordering::SeqCst), 55);
}

#[test]
fn s1b_03_f_may_keep_state_between_calls() {
    let ch = Channel::new();
    for i in 0..4 {
        ch.put(Some(i));
    }
    ch.put(None);
    let mut running = 0;
    let mut sums = Vec::new();
    consume(&ch, |x| {
        running += x;
        sums.push(running);
    });
    assert_eq!(sums, [0, 1, 3, 6]);
}

// ---- 1b-01 · Promise::set ----------------------------------------------------------------------------------------------

#[test]
fn s1b_04_a_future_is_not_ready_before_the_value_is_set() {
    let (p, f) = promise::<u32>();
    assert!(!f.is_ready());
    p.set(1);
    assert!(f.is_ready());
}

#[test]
fn s1b_04_set_takes_values_that_cannot_be_cloned() {
    let (p, f) = promise();
    p.set(Box::new([1u8; 16]));
    assert!(f.is_ready());
}

#[test]
fn s1b_04_set_from_another_thread() {
    let (p, f) = promise();
    let setter = thread::spawn(move || p.set("done"));
    setter.join().unwrap();
    assert!(f.is_ready());
}

#[test]
fn s1b_04_pairs_are_independent() {
    let (p1, f1) = promise::<i32>();
    let (_p2, f2) = promise::<i32>();
    p1.set(1);
    assert!(f1.is_ready());
    assert!(!f2.is_ready());
}

// ---- 1b-01 · Future::get -----------------------------------------------------------------------------------------------

#[test]
fn s1b_05_get_returns_the_value() {
    let (p, f) = promise();
    p.set(42);
    assert_eq!(wait(f), Ok(42));
}

#[test]
fn s1b_05_get_returns_the_very_value_that_was_set() {
    let (p, f) = promise();
    p.set(String::from("not cloned, moved"));
    assert_eq!(wait(f).unwrap(), "not cloned, moved");
}

#[test]
fn s1b_05_get_waits_until_the_value_is_set() {
    let (p, f) = promise();
    let (tx, rx) = mpsc::channel();
    let getter = thread::spawn(move || tx.send(wait(f)).unwrap());
    thread::sleep(Duration::from_millis(100));
    assert!(rx.try_recv().is_err(), "get returned before anything was set");
    p.set(7);
    assert_eq!(rx.recv_timeout(WAIT).expect("get never woke up"), Ok(7));
    getter.join().unwrap();
}

#[test]
fn s1b_05_a_hundred_promises_through_a_channel() {
    let ch = Arc::new(Channel::new());
    let worker = {
        let ch = Arc::clone(&ch);
        thread::spawn(move || consume(&ch, |(n, p): (u32, bustub::common::promise::Promise<u32>)| p.set(n * n)))
    };
    let futures: Vec<_> = (0..100)
        .map(|n| {
            let (p, f) = promise();
            ch.put(Some((n, p)));
            f
        })
        .collect();
    let got: Vec<u32> = futures.into_iter().map(|f| wait(f).unwrap()).collect();
    ch.put(None);
    worker.join().unwrap();
    assert_eq!(got, (0..100).map(|n| n * n).collect::<Vec<_>>());
}

// ---- 1b-01 · broken promises -------------------------------------------------------------------------------------------

#[test]
fn s1b_06_dropping_the_promise_breaks_the_future() {
    let (p, f) = promise::<u32>();
    drop(p);
    assert!(f.is_ready(), "a broken promise is 'ready': get won't wait");
    assert_eq!(wait(f), Err(BrokenPromise));
}

#[test]
fn s1b_06_a_waiting_getter_is_woken_by_the_drop() {
    let (p, f) = promise::<u32>();
    let (tx, rx) = mpsc::channel();
    let getter = thread::spawn(move || tx.send(wait(f)).unwrap());
    thread::sleep(Duration::from_millis(100));
    drop(p);
    assert_eq!(rx.recv_timeout(WAIT).expect("get never woke up"), Err(BrokenPromise));
    getter.join().unwrap();
}

#[test]
fn s1b_06_setting_then_dropping_is_not_a_break() {
    let (p, f) = promise();
    p.set(5);
    assert_eq!(wait(f), Ok(5));
}

#[test]
fn s1b_06_a_panicking_thread_breaks_the_promises_it_held() {
    let (p, f) = promise::<u32>();
    let t = thread::spawn(move || {
        let _p = p;
        panic!("worker died");
    });
    assert!(t.join().is_err());
    assert_eq!(wait(f), Err(BrokenPromise));
}

#[test]
fn s1b_06_a_promise_inside_a_dropped_channel_breaks() {
    let ch = Channel::new();
    let (p, f) = promise::<u8>();
    ch.put(p);
    drop(ch);
    assert_eq!(wait(f), Err(BrokenPromise));
}

// ---- 1b-02 · DiskRequest -----------------------------------------------------------------------------------------------

#[test]
fn s1b_07_a_read_request_has_a_zeroed_buffer() {
    let (req, fut) = DiskRequest::read(PageId(3));
    assert!(!req.is_write);
    assert_eq!(req.page_id, PageId(3));
    assert!(req.data.iter().all(|&b| b == 0));
    assert_eq!(req.data.len(), PS);
    assert!(!fut.is_ready());
}

#[test]
fn s1b_07_a_write_request_carries_the_data() {
    let (req, fut) = DiskRequest::write(PageId(9), page_of(0xAB));
    assert!(req.is_write);
    assert_eq!(req.page_id, PageId(9));
    assert!(req.data.iter().all(|&b| b == 0xAB));
    assert!(!fut.is_ready());
}

#[test]
fn s1b_07_the_future_belongs_to_the_requests_callback() {
    let (req, fut) = DiskRequest::read(PageId(0));
    req.callback.set(Ok(page_of(5)));
    assert!(fut.is_ready());
    assert!(wait(fut).unwrap().unwrap().iter().all(|&b| b == 5));
}

#[test]
fn s1b_07_dropping_a_request_breaks_its_future() {
    let (req, fut) = DiskRequest::write(PageId(0), page_of(1));
    drop(req);
    assert_eq!(wait(fut).err(), Some(BrokenPromise), "a dropped request has no result");
}

// ---- 1b-02 · execute ---------------------------------------------------------------------------------------------------

#[test]
fn s1b_08_a_write_then_a_read_round_trip() {
    let disk = memory_disk();
    let (w, wf) = DiskRequest::write(PageId(2), page_of(0x5A));
    execute(&*disk, w);
    let (r, rf) = DiskRequest::read(PageId(2));
    execute(&*disk, r);
    assert!(wait(wf).unwrap().is_ok_and_page(0x5A));
    assert!(wait(rf).unwrap().is_ok_and_page(0x5A));
}

trait PageCheck {
    fn is_ok_and_page(&self, byte: u8) -> bool;
}
impl PageCheck for io::Result<Box<PageData>> {
    fn is_ok_and_page(&self, byte: u8) -> bool {
        matches!(self, Ok(p) if p.iter().all(|&b| b == byte))
    }
}

#[test]
fn s1b_08_a_write_gives_the_buffer_back() {
    let disk = memory_disk();
    let (w, f) = DiskRequest::write(PageId(0), page_of(3));
    execute(&*disk, w);
    let buf = wait(f).unwrap().unwrap();
    assert!(buf.iter().all(|&b| b == 3));
}

#[test]
fn s1b_08_reading_a_page_never_written_gives_zeros() {
    let disk = memory_disk();
    let (r, f) = DiskRequest::read(PageId(40));
    execute(&*disk, r);
    assert!(wait(f).unwrap().unwrap().iter().all(|&b| b == 0));
}

#[test]
fn s1b_08_each_request_hits_its_own_page() {
    let disk = memory_disk();
    for id in 0..5u8 {
        let (w, _f) = DiskRequest::write(PageId(id as i32), page_of(id + 1));
        execute(&*disk, w);
    }
    for id in (0..5u8).rev() {
        let (r, f) = DiskRequest::read(PageId(id as i32));
        execute(&*disk, r);
        assert!(wait(f).unwrap().unwrap().iter().all(|&b| b == id + 1), "page {id}");
    }
}

#[test]
fn s1b_08_an_io_error_comes_back_through_the_future() {
    let (w, f) = DiskRequest::write(PageId(1), page_of(1));
    execute(&BadDisk, w);
    let err = wait(f).unwrap().err().expect("the write should have failed");
    assert_eq!(err.kind(), io::ErrorKind::PermissionDenied);
}

#[test]
fn s1b_08_a_successful_read_from_a_disk_that_fills_the_buffer() {
    let (r, f) = DiskRequest::read(PageId(1));
    execute(&BadDisk, r);
    assert!(wait(f).unwrap().unwrap().iter().all(|&b| b == 7));
}

// ---- 1b-02 · DiskScheduler::new and schedule -----------------------------------------------------------------------------

#[test]
fn s1b_09_a_scheduled_write_and_read() {
    let sched = DiskScheduler::new(memory_disk());
    let (w, wf) = DiskRequest::write(PageId(0), page_of(0x42));
    let (r, rf) = DiskRequest::read(PageId(0));
    sched.schedule(vec![w]);
    sched.schedule(vec![r]);
    assert!(wait(wf).unwrap().is_ok());
    assert!(wait(rf).unwrap().unwrap().iter().all(|&b| b == 0x42), "the read, scheduled after the write, sees it");
}

#[test]
fn s1b_09_a_batch_runs_in_order() {
    let disk = RecordingDisk::new(0);
    let sched = DiskScheduler::new(disk.clone());
    let mut futures = Vec::new();
    let mut batch = Vec::new();
    for id in [5, 3, 9, 1] {
        let (r, f) = DiskRequest::write(PageId(id), page_of(1));
        batch.push(r);
        futures.push(f);
    }
    let (r, f) = DiskRequest::read(PageId(3));
    batch.push(r);
    futures.push(f);
    sched.schedule(batch);
    futures.into_iter().for_each(|f| drop(wait(f).unwrap().unwrap()));
    assert_eq!(disk.ops(), ["W5", "W3", "W9", "W1", "R3"]);
}

#[test]
fn s1b_09_schedule_returns_before_the_requests_finish() {
    let disk = RecordingDisk::new(100);
    let sched = DiskScheduler::new(disk.clone());
    let (r, f) = DiskRequest::read(PageId(0));
    let start = Instant::now();
    sched.schedule(vec![r]);
    assert!(start.elapsed() < Duration::from_millis(80), "schedule must not wait for the I/O");
    assert!(!f.is_ready());
    wait(f).unwrap().unwrap();
}

#[test]
fn s1b_09_many_threads_can_schedule() {
    let disk = memory_disk();
    let sched = Arc::new(DiskScheduler::new(disk));
    let handles: Vec<_> = (0..4)
        .map(|t| {
            let sched = Arc::clone(&sched);
            thread::spawn(move || {
                for i in 0..25 {
                    let id = PageId(t * 25 + i);
                    let (w, wf) = DiskRequest::write(id, page_of(id.0 as u8 + 1));
                    sched.schedule(vec![w]);
                    wait(wf).unwrap().unwrap();
                    let (r, rf) = DiskRequest::read(id);
                    sched.schedule(vec![r]);
                    assert!(wait(rf).unwrap().unwrap().iter().all(|&b| b == id.0 as u8 + 1));
                }
            })
        })
        .collect();
    handles.into_iter().for_each(|h| h.join().unwrap());
}

#[test]
fn s1b_09_an_empty_batch_is_fine() {
    let sched = DiskScheduler::new(memory_disk());
    sched.schedule(Vec::new());
}

// ---- 1b-02 · shutting down -----------------------------------------------------------------------------------------------

#[test]
fn s1b_10_dropping_the_scheduler_finishes_the_scheduled_work_first() {
    let disk = RecordingDisk::new(5);
    let sched = DiskScheduler::new(disk.clone());
    let mut futures = Vec::new();
    for id in 0..20 {
        let (w, f) = DiskRequest::write(PageId(id), page_of(1));
        sched.schedule(vec![w]);
        futures.push(f);
    }
    drop(sched);
    assert_eq!(disk.ops().len(), 20, "drop must wait until every scheduled request has run");
    assert!(futures.into_iter().all(|f| f.is_ready()));
}

#[test]
fn s1b_10_dropping_stops_the_worker_thread() {
    let disk = memory_disk();
    let sched = DiskScheduler::new(disk.clone());
    assert_eq!(Arc::strong_count(&disk), 3, "the test, the scheduler and the worker each hold the disk");
    drop(sched);
    assert_eq!(Arc::strong_count(&disk), 1, "after the drop the worker has ended and let go of the disk");
}

#[test]
fn s1b_10_an_unused_scheduler_drops_cleanly() {
    drop(DiskScheduler::new(memory_disk()));
}

#[test]
fn s1b_10_many_schedulers_can_come_and_go() {
    let disk = memory_disk();
    for round in 0..20u8 {
        let sched = DiskScheduler::new(disk.clone());
        let (w, f) = DiskRequest::write(PageId(round as i32), page_of(round + 1));
        sched.schedule(vec![w]);
        wait(f).unwrap().unwrap();
    }
    assert_eq!(Arc::strong_count(&disk), 1);
}

// ---- 1b-02 · a panicking disk does not kill the worker ---------------------------------------------------------------------

#[test]
fn s1b_11_a_panic_becomes_an_error_for_that_request() {
    let (r, f) = DiskRequest::read(PageId(13));
    execute(&BadDisk, r);
    let err = wait(f).unwrap().err().expect("the request should report an error");
    assert!(err.to_string().contains("panicked"), "got {err}");
}

#[test]
fn s1b_11_the_worker_keeps_going_after_a_panic() {
    let sched = DiskScheduler::new(Arc::new(BadDisk));
    let (bad, bad_f) = DiskRequest::read(PageId(13));
    let (good, good_f) = DiskRequest::read(PageId(1));
    sched.schedule(vec![bad, good]);
    assert!(wait(bad_f).unwrap().is_err());
    assert!(wait(good_f).unwrap().unwrap().iter().all(|&b| b == 7), "the request after the panic still ran");
}

#[test]
fn s1b_11_panics_are_caught_every_time() {
    let sched = DiskScheduler::new(Arc::new(BadDisk));
    for _ in 0..5 {
        let (bad, f) = DiskRequest::read(PageId(13));
        sched.schedule(vec![bad]);
        assert!(wait(f).unwrap().is_err());
    }
}

#[test]
fn s1b_11_requests_that_dont_panic_are_unchanged() {
    let disk = memory_disk();
    let (w, f) = DiskRequest::write(PageId(0), page_of(4));
    execute(&*disk, w);
    assert!(wait(f).unwrap().is_ok_and_page(4));
}

// ---- 1b-02 · create_promise and deallocate_page ----------------------------------------------------------------------------

#[test]
fn s1b_12_create_promise_gives_a_working_pair() {
    let sched = DiskScheduler::new(memory_disk());
    let (p, f) = sched.create_promise();
    assert!(!f.is_ready());
    p.set(Ok(page_of(1)));
    assert!(wait(f).unwrap().unwrap().iter().all(|&b| b == 1));
}

#[test]
fn s1b_12_deallocate_page_reaches_the_disk() {
    let disk = RecordingDisk::new(0);
    let sched = DiskScheduler::new(disk.clone());
    sched.deallocate_page(PageId(6));
    sched.deallocate_page(PageId(2));
    assert_eq!(disk.ops(), ["D6", "D2"]);
}

#[test]
fn s1b_12_a_request_can_be_built_by_hand_with_a_created_promise() {
    let sched = DiskScheduler::new(memory_disk());
    let (callback, future) = sched.create_promise();
    let req = DiskRequest { is_write: true, data: page_of(9), page_id: PageId(1), callback };
    sched.schedule(vec![req]);
    assert!(wait(future).unwrap().is_ok());
}

// ---- 1b-03 · ReaderWriterLatch ---------------------------------------------------------------------------------------------

#[test]
fn s1b_13_the_latch_guards_its_value() {
    let latch = ReaderWriterLatch::new(5);
    *latch.write() += 1;
    assert_eq!(*latch.read(), 6);
}

#[test]
fn s1b_13_readers_share_the_latch() {
    // Four readers each wait for the other three while holding a read latch: only possible if read latches can overlap.
    let latch = Arc::new(ReaderWriterLatch::new(0));
    let barrier = Arc::new(Barrier::new(4));
    let handles: Vec<_> = (0..4)
        .map(|_| {
            let (latch, barrier) = (Arc::clone(&latch), Arc::clone(&barrier));
            thread::spawn(move || {
                let guard = latch.read();
                barrier.wait();
                *guard
            })
        })
        .collect();
    for h in handles {
        assert_eq!(h.join().unwrap(), 0);
    }
}

#[test]
fn s1b_13_writers_exclude_each_other() {
    let latch = Arc::new(ReaderWriterLatch::new(0usize));
    let handles: Vec<_> = (0..8)
        .map(|_| {
            let latch = Arc::clone(&latch);
            thread::spawn(move || {
                for _ in 0..1000 {
                    let mut g = latch.write();
                    let v = *g;
                    *g = v + 1;
                }
            })
        })
        .collect();
    handles.into_iter().for_each(|h| h.join().unwrap());
    assert_eq!(*latch.read(), 8000);
}

#[test]
fn s1b_13_a_writer_waits_for_the_readers() {
    let latch = Arc::new(ReaderWriterLatch::new(0));
    let reader = latch.read();
    let (tx, rx) = mpsc::channel();
    let writer = {
        let latch = Arc::clone(&latch);
        thread::spawn(move || {
            *latch.write() = 1;
            tx.send(()).unwrap();
        })
    };
    thread::sleep(Duration::from_millis(100));
    assert!(rx.try_recv().is_err(), "the write latch was granted while a read latch was held");
    drop(reader);
    rx.recv_timeout(WAIT).expect("the writer never got in");
    writer.join().unwrap();
    assert_eq!(*latch.read(), 1);
}

#[test]
fn s1b_13_a_panic_while_latched_does_not_lock_everyone_out() {
    let latch = Arc::new(ReaderWriterLatch::new(1));
    let l2 = Arc::clone(&latch);
    let _ = thread::spawn(move || {
        let _g = l2.write();
        panic!("died holding the latch");
    })
    .join();
    assert_eq!(*latch.read(), 1, "BusTub's latch has no notion of poisoning, and neither does this one");
    *latch.write() = 2;
    assert_eq!(*latch.read(), 2);
}

// ---- 1b-03 · ShardedDiskScheduler -----------------------------------------------------------------------------------------

#[test]
fn s1b_14_requests_for_one_page_stay_in_order() {
    let disk = RecordingDisk::new(1);
    let sched = ShardedDiskScheduler::new(disk.clone(), 4);
    let mut futures = Vec::new();
    for v in 1..=10u8 {
        let (w, wf) = DiskRequest::write(PageId(7), page_of(v));
        let (r, rf) = DiskRequest::read(PageId(7));
        sched.schedule(vec![w, r]);
        futures.push((v, wf, rf));
    }
    for (v, wf, rf) in futures {
        wait(wf).unwrap().unwrap();
        assert!(wait(rf).unwrap().unwrap().iter().all(|&b| b == v), "the read after write {v} must see it");
    }
}

#[test]
fn s1b_14_every_page_sees_its_own_writes() {
    let sched = ShardedDiskScheduler::new(memory_disk(), 3);
    let mut futures = Vec::new();
    for id in 0..30 {
        let (w, wf) = DiskRequest::write(PageId(id), page_of(id as u8 + 1));
        let (r, rf) = DiskRequest::read(PageId(id));
        sched.schedule(vec![w, r]);
        futures.push((id, wf, rf));
    }
    for (id, wf, rf) in futures {
        wait(wf).unwrap().unwrap();
        assert!(wait(rf).unwrap().unwrap().iter().all(|&b| b == id as u8 + 1), "page {id}");
    }
}

#[test]
fn s1b_14_pages_on_different_workers_overlap_in_time() {
    // 8 requests of ~40 ms on 4 distinct pages: one worker needs 320 ms, four workers about 80 ms.
    let sched = ShardedDiskScheduler::new(RecordingDisk::new(40), 4);
    let start = Instant::now();
    let mut futures = Vec::new();
    for round in 0..2 {
        for id in 0..4 {
            let (w, f) = DiskRequest::write(PageId(id), page_of(round + 1));
            sched.schedule(vec![w]);
            futures.push(f);
        }
    }
    futures.into_iter().for_each(|f| drop(wait(f).unwrap().unwrap()));
    assert!(start.elapsed() < Duration::from_millis(240), "took {:?}; the workers did not overlap", start.elapsed());
}

#[test]
fn s1b_14_dropping_finishes_everything_scheduled() {
    let disk = RecordingDisk::new(2);
    let sched = ShardedDiskScheduler::new(disk.clone(), 4);
    for id in 0..40 {
        let (w, _f) = DiskRequest::write(PageId(id), page_of(1));
        sched.schedule(vec![w]);
    }
    drop(sched);
    assert_eq!(disk.ops().len(), 40);
    assert_eq!(Arc::strong_count(&disk), 1, "all four workers have ended");
}

#[test]
fn s1b_14_one_worker_is_just_a_scheduler() {
    let sched = ShardedDiskScheduler::new(memory_disk(), 1);
    let (w, wf) = DiskRequest::write(PageId(-3), page_of(8));
    sched.schedule(vec![w]);
    wait(wf).unwrap().unwrap_err();
}

#[test]
#[should_panic(expected = "at least one worker")]
fn s1b_14_no_workers_is_a_bug() {
    let _ = ShardedDiskScheduler::new(memory_disk(), 0);
}

// ---- 1b-04 · the module as a whole -----------------------------------------------------------------------------------------

#[test]
fn s1b_15_eight_threads_hammer_one_scheduler() {
    let disk = memory_disk();
    let sched = Arc::new(DiskScheduler::new(disk.clone()));
    let handles: Vec<_> = (0..8)
        .map(|t| {
            let sched = Arc::clone(&sched);
            thread::spawn(move || {
                for round in 0..50u8 {
                    let id = PageId(t * 100 + round as i32 % 5);
                    let (w, wf) = DiskRequest::write(id, page_of(round.wrapping_add(t as u8)));
                    let (r, rf) = DiskRequest::read(id);
                    sched.schedule(vec![w, r]);
                    wait(wf).unwrap().unwrap();
                    let page = wait(rf).unwrap().unwrap();
                    assert!(page.iter().all(|&b| b == round.wrapping_add(t as u8)), "thread {t} round {round}");
                }
            })
        })
        .collect();
    handles.into_iter().for_each(|h| h.join().unwrap());
    drop(Arc::try_unwrap(sched).ok().expect("all threads are done"));
    assert_eq!(Arc::strong_count(&disk), 1);
}

#[test]
fn s1b_15_both_schedulers_leave_the_same_pages() {
    let plain = memory_disk();
    let sharded = memory_disk();
    {
        let a = DiskScheduler::new(plain.clone());
        let b = ShardedDiskScheduler::new(sharded.clone(), 4);
        for i in 0..200u32 {
            let id = PageId((i * 7 % 23) as i32);
            let (w1, _f1) = DiskRequest::write(id, page_of(i as u8));
            let (w2, _f2) = DiskRequest::write(id, page_of(i as u8));
            a.schedule(vec![w1]);
            b.schedule(vec![w2]);
        }
    }
    for id in 0..23 {
        let (mut x, mut y) = ([0u8; PS], [0u8; PS]);
        plain.read_page(PageId(id), &mut x).unwrap();
        sharded.read_page(PageId(id), &mut y).unwrap();
        assert!(x == y, "page {id}: the last write to a page must win under either scheduler");
    }
}
