//! Tests for module 1b, the disk scheduler. A test name starts with its stage: `s1b_03_…` belongs to stage 1b-03, and
//! `anneal course test` runs just those.
//!
//! The tests use only the public API: `Channel`, `promise`, `DiskRequest`, `DiskScheduler`, `ShardedDiskScheduler` and
//! `ReaderWriterLatch`. Several are properties: a random sequence of operations is run on your code and on a plain model,
//! and every answer must agree. Anything that could hang waits with a timeout, so a deadlock fails the test with a message
//! instead of freezing it.

use std::collections::VecDeque;
use std::io;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::mpsc;
use std::sync::{Arc, Barrier, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use bustub::common::channel::{consume, Channel};
use bustub::common::config::{PageData, PageId, BUSTUB_PAGE_SIZE};
use bustub::common::promise::{promise, BrokenPromise, Future};
use bustub::common::rwlatch::ReaderWriterLatch;
use bustub::storage::disk::disk_manager::DiskIo;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;
use bustub::storage::disk::disk_scheduler::{DiskRequest, DiskResult, DiskScheduler, ShardedDiskScheduler};
use proptest::prelude::*;

const PS: usize = BUSTUB_PAGE_SIZE;
const WAIT: Duration = Duration::from_secs(10);
const SHORT: Duration = Duration::from_millis(150);

fn config() -> ProptestConfig {
    ProptestConfig { cases: 32, max_shrink_iters: 1000, ..ProptestConfig::default() }
}

/// Runs `f` on a thread and returns its result, or fails the test if it does not finish in time: a hang is a bug, not a stuck run.
fn within<T: Send + 'static>(what: &str, f: impl FnOnce() -> T + Send + 'static) -> T {
    let (tx, rx) = mpsc::channel();
    thread::spawn(move || {
        let _ = tx.send(f());
    });
    rx.recv_timeout(WAIT).unwrap_or_else(|_| panic!("timed out ({WAIT:?}): {what}"))
}

/// Waits for a future, but not forever.
fn wait<T: Send + 'static>(future: Future<T>) -> Result<T, BrokenPromise> {
    within("waiting for a future: a promise that is never set, or one dropped without waking the future", move || future.get())
}

fn page_of(byte: u8) -> Box<PageData> {
    Box::new([byte; PS])
}

fn memory_disk() -> Arc<DiskManagerUnlimitedMemory> {
    Arc::new(DiskManagerUnlimitedMemory::new())
}

/// A disk that keeps pages in memory, logs every operation ("R3", "W3", "D3") in the order the worker performed it, can be slowed
/// down, and can fail or panic for chosen pages.
struct TestDisk {
    inner: DiskManagerUnlimitedMemory,
    log: Mutex<Vec<String>>,
    delay: Duration,
    fail_page: Option<i32>,
    panic_page: Option<i32>,
}

impl TestDisk {
    fn new() -> TestDisk {
        TestDisk { inner: DiskManagerUnlimitedMemory::new(), log: Mutex::new(Vec::new()), delay: Duration::ZERO, fail_page: None, panic_page: None }
    }
    fn slow(ms: u64) -> TestDisk {
        TestDisk { delay: Duration::from_millis(ms), ..TestDisk::new() }
    }
    fn ops(&self) -> Vec<String> {
        self.log.lock().unwrap().clone()
    }
}

impl DiskIo for TestDisk {
    fn read_page(&self, page_id: PageId, buf: &mut PageData) -> io::Result<()> {
        thread::sleep(self.delay);
        self.log.lock().unwrap().push(format!("R{}", page_id.0));
        if Some(page_id.0) == self.panic_page {
            panic!("this disk panics on page {}", page_id.0);
        }
        if Some(page_id.0) == self.fail_page {
            return Err(io::Error::other(format!("boom on page {}", page_id.0)));
        }
        self.inner.read_page(page_id, buf)
    }
    fn write_page(&self, page_id: PageId, data: &PageData) -> io::Result<()> {
        thread::sleep(self.delay);
        self.log.lock().unwrap().push(format!("W{}", page_id.0));
        if Some(page_id.0) == self.panic_page {
            panic!("this disk panics on page {}", page_id.0);
        }
        if Some(page_id.0) == self.fail_page {
            return Err(io::Error::other(format!("boom on page {}", page_id.0)));
        }
        self.inner.write_page(page_id, data)
    }
    fn delete_page(&self, page_id: PageId) {
        self.log.lock().unwrap().push(format!("D{}", page_id.0));
        self.inner.delete_page(page_id)
    }
}

// ---- 1b-01 · A queue that waits -----------------------------------------------------------------------------------

#[test]
fn s1b_01_put_never_blocks_and_len_counts_what_is_waiting() {
    let ch = within("putting into a channel nobody reads", || {
        let ch = Channel::new();
        for i in 0..10_000 {
            ch.put(i);
        }
        ch
    });
    assert_eq!(ch.len(), 10_000, "ten thousand elements are waiting");
    assert!(!ch.is_empty());
    assert!(Channel::<u8>::new().is_empty(), "a new channel is empty");
}

#[test]
fn s1b_01_get_waits_until_something_is_put() {
    let ch = Arc::new(Channel::new());
    let (tx, rx) = mpsc::channel();
    let getter = {
        let ch = Arc::clone(&ch);
        thread::spawn(move || tx.send(ch.get()).unwrap())
    };
    assert!(rx.recv_timeout(SHORT).is_err(), "get returned from an empty channel instead of waiting");
    ch.put(42);
    assert_eq!(rx.recv_timeout(WAIT).expect("get never noticed the put: a waiting getter must be woken"), 42);
    getter.join().unwrap();
}

#[test]
fn s1b_01_consume_calls_f_on_each_element_in_order_and_eats_the_stop_signal() {
    let ch = Channel::new();
    for x in [Some(1), Some(2), None, Some(3)] {
        ch.put(x);
    }
    let mut seen = Vec::new();
    within("consume must return when it gets a None", move || {
        consume(&ch, |x| seen.push(x));
        (seen, ch)
    });
}

#[test]
fn s1b_01_consume_leaves_what_follows_the_stop_signal_in_the_channel() {
    let ch = Channel::new();
    for x in [Some(1), Some(2), None, Some(3)] {
        ch.put(x);
    }
    let (seen, ch) = within("consume must return when it gets a None", move || {
        let mut seen = Vec::new();
        consume(&ch, |x| seen.push(x));
        (seen, ch)
    });
    assert_eq!(seen, vec![1, 2], "f is called on the Some elements before the None, in order");
    assert_eq!(ch.len(), 1, "the None itself is consumed, and the element after it stays");
}

#[test]
fn s1b_01_every_element_reaches_exactly_one_of_many_consumers() {
    let ch: Arc<Channel<Option<u32>>> = Arc::new(Channel::new());
    let consumers: Vec<_> = (0..4)
        .map(|_| {
            let ch = Arc::clone(&ch);
            thread::spawn(move || {
                let mut got = Vec::new();
                consume(&ch, |x| got.push(x));
                got
            })
        })
        .collect();
    let producers: Vec<_> = (0..4u32)
        .map(|p| {
            let ch = Arc::clone(&ch);
            thread::spawn(move || {
                for i in 0..500 {
                    ch.put(Some(p * 1000 + i));
                }
            })
        })
        .collect();
    for p in producers {
        p.join().unwrap();
    }
    for _ in 0..4 {
        ch.put(None); // one stop signal per consumer
    }
    let mut all: Vec<u32> = within("the consumers should all stop", move || consumers.into_iter().flat_map(|c| c.join().unwrap()).collect());
    all.sort();
    let mut expected: Vec<u32> = (0..4u32).flat_map(|p| (0..500).map(move |i| p * 1000 + i)).collect();
    expected.sort();
    assert_eq!(all, expected, "every element must be delivered exactly once: none lost, none twice");
}

proptest! {
    #![proptest_config(config())]

    #[test]
    fn s1b_01_a_single_thread_sees_a_first_in_first_out_queue(ops in prop::collection::vec(prop::option::of(any::<i32>()), 1..80)) {
        // Some(x) = put x; None = get (only done when the model says something is waiting)
        let ch = Channel::new();
        let mut model: VecDeque<i32> = VecDeque::new();
        for op in ops {
            match op {
                Some(x) => { ch.put(x); model.push_back(x); }
                None if !model.is_empty() => prop_assert_eq!(ch.get(), model.pop_front().unwrap(), "get must return the oldest element"),
                None => {}
            }
            prop_assert_eq!(ch.len(), model.len(), "len must be the number of elements waiting");
        }
    }
}

// ---- 1b-02 · A promise to answer later ------------------------------------------------------------------------

#[test]
fn s1b_02_a_value_set_before_get_is_returned() {
    let (p, f) = promise();
    assert!(!f.is_ready(), "nothing has been set yet");
    p.set(vec![1, 2, 3]);
    assert!(f.is_ready(), "a set value makes the future ready");
    assert_eq!(f.get(), Ok(vec![1, 2, 3]), "values that are not Clone move through");
}

#[test]
fn s1b_02_get_waits_for_a_promise_that_is_set_later_on_another_thread() {
    let (p, f) = promise();
    let (tx, rx) = mpsc::channel();
    let waiter = thread::spawn(move || tx.send(f.get()).unwrap());
    assert!(rx.recv_timeout(SHORT).is_err(), "get returned before anything was set");
    p.set("hello".to_string());
    assert_eq!(rx.recv_timeout(WAIT).expect("a set value must wake the waiting future"), Ok("hello".to_string()));
    waiter.join().unwrap();
}

#[test]
fn s1b_02_a_promise_dropped_without_a_value_breaks_the_future() {
    let (p, f) = promise::<u32>();
    drop(p);
    assert!(f.is_ready(), "a broken promise makes get return at once");
    assert_eq!(f.get(), Err(BrokenPromise));
}

#[test]
fn s1b_02_dropping_the_promise_wakes_a_future_that_is_already_waiting() {
    let (p, f) = promise::<u32>();
    let (tx, rx) = mpsc::channel();
    let waiter = thread::spawn(move || tx.send(f.get()).unwrap());
    assert!(rx.recv_timeout(SHORT).is_err(), "get returned before the promise was dropped");
    drop(p);
    assert_eq!(rx.recv_timeout(WAIT).expect("a dropped promise must wake the waiting future, or the waiter hangs forever"), Err(BrokenPromise));
    waiter.join().unwrap();
}

#[test]
fn s1b_02_a_set_promise_that_is_then_dropped_still_gives_its_value() {
    let (p, f) = promise();
    p.set(7u8); // `set` takes the promise by value, so it is dropped here
    assert_eq!(f.get(), Ok(7), "the drop that follows a set must not turn the value into BrokenPromise");
}

proptest! {
    #![proptest_config(config())]

    #[test]
    fn s1b_02_any_value_set_from_another_thread_arrives(value in prop::collection::vec(any::<u8>(), 0..64), set_first in any::<bool>()) {
        let (p, f) = promise();
        let expected = value.clone();
        let setter = thread::spawn(move || {
            if !set_first { thread::sleep(Duration::from_millis(5)); }
            p.set(value);
        });
        if set_first { setter.join().unwrap(); prop_assert_eq!(f.get(), Ok(expected)); } else { prop_assert_eq!(wait(f), Ok(expected)); setter.join().unwrap(); }
    }
}

// ---- 1b-03 · The scheduler -----------------------------------------------------------------------------------------

fn write_req(page: i32, byte: u8) -> (DiskRequest, Future<DiskResult>) {
    DiskRequest::write(PageId(page), page_of(byte))
}

#[test]
fn s1b_03_a_read_scheduled_after_a_write_of_the_same_page_sees_it() {
    let sched = DiskScheduler::new(memory_disk());
    let (w, wf) = write_req(4, 0xAB);
    let (r, rf) = DiskRequest::read(PageId(4));
    sched.schedule(vec![w, r]);
    assert!(wait(wf).unwrap().is_ok(), "the write succeeds");
    let page = wait(rf).unwrap().unwrap();
    assert!(page.iter().all(|&b| b == 0xAB), "the read must come back with the bytes the earlier write stored");
}

#[test]
fn s1b_03_a_page_never_written_reads_back_as_zeros() {
    let sched = DiskScheduler::new(memory_disk());
    let (r, rf) = DiskRequest::read(PageId(9));
    sched.schedule(vec![r]);
    assert!(wait(rf).unwrap().unwrap().iter().all(|&b| b == 0), "an unwritten page reads as zeros through the scheduler too");
}

#[test]
fn s1b_03_a_write_future_hands_the_buffer_back() {
    let sched = DiskScheduler::new(memory_disk());
    let (w, wf) = write_req(1, 0x11);
    sched.schedule(vec![w]);
    let buf = wait(wf).unwrap().unwrap();
    assert!(buf.iter().all(|&b| b == 0x11), "the buffer that comes back is the page that was written");
}

#[test]
fn s1b_03_schedule_returns_before_the_io_is_done() {
    let disk = Arc::new(TestDisk::slow(120));
    let sched = DiskScheduler::new(disk);
    let (w, wf) = write_req(0, 1);
    let start = Instant::now();
    sched.schedule(vec![w]);
    assert!(start.elapsed() < Duration::from_millis(60), "schedule must hand the request over and return, not do the I/O itself");
    assert!(wait(wf).unwrap().is_ok());
}

#[test]
fn s1b_03_create_promise_gives_a_connected_pair() {
    let sched = DiskScheduler::new(memory_disk());
    let (p, f) = sched.create_promise();
    p.set(Ok(page_of(5)));
    assert!(wait(f).unwrap().unwrap().iter().all(|&b| b == 5), "a promise from create_promise completes its own future");
}

#[derive(Clone, Debug)]
enum Req {
    Write(i32, u8),
    Read(i32),
}

proptest! {
    #![proptest_config(config())]

    /// Whatever batches the requests arrive in, the scheduler behaves like running them one after another on a model.
    #[test]
    fn s1b_03_scheduled_requests_behave_like_running_them_in_order_on_a_model(
        reqs in prop::collection::vec(prop_oneof![(0..6i32, any::<u8>()).prop_map(|(p, b)| Req::Write(p, b)), (0..6i32).prop_map(Req::Read)], 1..50),
        batch in 1usize..6,
    ) {
        let sched = DiskScheduler::new(memory_disk());
        let mut model: std::collections::HashMap<i32, u8> = std::collections::HashMap::new();
        let mut futures: Vec<(Req, u8, Future<DiskResult>)> = Vec::new();
        for chunk in reqs.chunks(batch) {
            let mut requests = Vec::new();
            for r in chunk {
                match r {
                    Req::Write(p, b) => { let (req, f) = write_req(*p, *b); model.insert(*p, *b); requests.push(req); futures.push((r.clone(), *b, f)); }
                    Req::Read(p) => { let (req, f) = DiskRequest::read(PageId(*p)); requests.push(req); futures.push((r.clone(), *model.get(p).unwrap_or(&0), f)); }
                }
            }
            sched.schedule(requests);
        }
        for (req, expected, f) in futures {
            let page = wait(f).unwrap().unwrap();
            prop_assert!(page.iter().all(|&b| b == expected), "{req:?} should have produced a page full of {expected}, in the order the requests were scheduled");
        }
    }
}

// ---- 1b-04 · Shutdown and a failing disk ----------------------------------------------------------------------

#[test]
fn s1b_04_dropping_the_scheduler_finishes_everything_scheduled_before_it() {
    let disk = Arc::new(TestDisk::slow(1));
    let sched = DiskScheduler::new(disk.clone());
    let requests: Vec<_> = (0..100).map(|i| write_req(i, i as u8).0).collect();
    sched.schedule(requests);
    drop(sched); // no future was waited for: the drop itself must run the queue dry
    assert_eq!(disk.ops().len(), 100, "all 100 writes must have reached the disk by the time the drop returns");
}

#[test]
fn s1b_04_dropping_an_idle_scheduler_does_not_hang() {
    within("dropping a scheduler with an empty queue", || drop(DiskScheduler::new(memory_disk())));
}

#[test]
fn s1b_04_a_disk_error_is_reported_through_the_future() {
    let mut disk = TestDisk::new();
    disk.fail_page = Some(3);
    let sched = DiskScheduler::new(Arc::new(disk));
    let (w, wf) = write_req(3, 1);
    sched.schedule(vec![w]);
    let result = wait(wf).expect("the promise must be completed even when the I/O fails");
    let err = result.expect_err("the write failed, so the future carries the error");
    assert!(err.to_string().contains("boom"), "the disk's own error reaches the caller: {err}");
}

#[test]
fn s1b_04_a_panicking_disk_gives_an_error_and_the_worker_keeps_going() {
    let mut disk = TestDisk::new();
    disk.panic_page = Some(13);
    let sched = DiskScheduler::new(Arc::new(disk));
    let (bad, bad_f) = write_req(13, 1);
    let (good, good_f) = write_req(2, 2);
    sched.schedule(vec![bad, good]);
    let outcome = wait(bad_f).expect("a promise the worker never completes leaves the caller waiting forever");
    assert!(outcome.is_err(), "a disk that panics must be reported as an I/O error");
    assert!(wait(good_f).unwrap().is_ok(), "the next request must still be served: one bad request must not kill the worker thread");
}

#[test]
fn s1b_04_deallocate_page_asks_the_disk_to_delete_it() {
    let disk = Arc::new(TestDisk::new());
    let sched = DiskScheduler::new(disk.clone());
    sched.deallocate_page(PageId(8));
    assert_eq!(disk.ops(), vec!["D8".to_string()], "the disk is asked to delete page 8, once");
}

proptest! {
    #![proptest_config(config())]

    #[test]
    fn s1b_04_the_disk_sees_the_requests_in_the_order_they_were_scheduled(pages in prop::collection::vec(0..8i32, 1..40)) {
        let disk = Arc::new(TestDisk::new());
        let sched = DiskScheduler::new(disk.clone());
        let expected: Vec<String> = pages.iter().map(|p| format!("W{p}")).collect();
        sched.schedule(pages.iter().map(|&p| write_req(p, 1).0).collect());
        drop(sched);
        prop_assert_eq!(disk.ops(), expected);
    }
}

// ---- 1b-05 · The reader-writer latch ---------------------------------------------------------------------------

#[test]
fn s1b_05_a_write_changes_what_the_next_read_sees() {
    let latch = ReaderWriterLatch::new(vec![1, 2]);
    latch.write().push(3);
    assert_eq!(*latch.read(), vec![1, 2, 3]);
}

#[test]
fn s1b_05_many_writers_never_lose_an_update() {
    let latch = Arc::new(ReaderWriterLatch::new(0u64));
    let handles: Vec<_> = (0..8)
        .map(|_| {
            let latch = Arc::clone(&latch);
            thread::spawn(move || {
                for _ in 0..2000 {
                    *latch.write() += 1;
                }
            })
        })
        .collect();
    within("eight writers", move || handles.into_iter().for_each(|h| h.join().unwrap()));
    assert_eq!(*latch.read(), 16_000, "an increment under the write latch is never lost");
}

#[test]
fn s1b_05_a_reader_never_sees_a_write_half_done() {
    let latch = Arc::new(ReaderWriterLatch::new((0u32, 0u32)));
    let stop = Arc::new(AtomicUsize::new(0));
    let writer = {
        let (latch, stop) = (Arc::clone(&latch), Arc::clone(&stop));
        thread::spawn(move || {
            for i in 1..=3000 {
                let mut g = latch.write();
                g.0 = i;
                thread::yield_now(); // a window in which a reader could look, if the latch let it
                g.1 = i;
            }
            stop.store(1, Ordering::SeqCst);
        })
    };
    let readers: Vec<_> = (0..3)
        .map(|_| {
            let (latch, stop) = (Arc::clone(&latch), Arc::clone(&stop));
            thread::spawn(move || {
                while stop.load(Ordering::SeqCst) == 0 {
                    let g = latch.read();
                    assert_eq!(g.0, g.1, "a reader saw the two halves of a write at different values");
                }
            })
        })
        .collect();
    within("the writer and readers", move || {
        writer.join().unwrap();
        readers.into_iter().for_each(|r| r.join().unwrap());
    });
}

#[test]
fn s1b_05_several_readers_can_hold_the_latch_at_the_same_time() {
    let latch = Arc::new(ReaderWriterLatch::new(1));
    let barrier = Arc::new(Barrier::new(4));
    let handles: Vec<_> = (0..4)
        .map(|_| {
            let (latch, barrier) = (Arc::clone(&latch), Arc::clone(&barrier));
            thread::spawn(move || {
                let _g = latch.read();
                barrier.wait(); // returns only if all four threads are inside the latch together
            })
        })
        .collect();
    within("four readers meeting inside the read latch: readers must not exclude each other", move || handles.into_iter().for_each(|h| h.join().unwrap()));
}

#[test]
fn s1b_05_a_writer_keeps_readers_out_until_it_lets_go() {
    let latch = Arc::new(ReaderWriterLatch::new(0));
    let guard = latch.write();
    let (tx, rx) = mpsc::channel();
    let reader = {
        let latch = Arc::clone(&latch);
        thread::spawn(move || tx.send(*latch.read()).unwrap())
    };
    assert!(rx.recv_timeout(SHORT).is_err(), "a reader got in while a writer held the latch");
    drop(guard);
    assert_eq!(rx.recv_timeout(WAIT).expect("the reader must be let in when the writer lets go"), 0);
    reader.join().unwrap();
}

#[test]
fn s1b_05_a_latch_is_still_usable_after_a_holder_panicked() {
    let latch = Arc::new(ReaderWriterLatch::new(5));
    let l2 = Arc::clone(&latch);
    let _ = thread::spawn(move || {
        let _g = l2.write();
        panic!("a holder panics");
    })
    .join();
    assert_eq!(*latch.read(), 5, "a latch whose holder panicked must still give its guard (poisoning is not this latch's business)");
    *latch.write() = 6;
    assert_eq!(*latch.read(), 6);
}

// ---- 1b-06 · Several workers, one page at a time ---------------------------------------------------------------

#[test]
fn s1b_06_a_sharded_scheduler_needs_at_least_one_worker() {
    let result = std::panic::catch_unwind(|| ShardedDiskScheduler::new(memory_disk(), 0));
    assert!(result.is_err(), "zero workers is a bug in the caller: it panics");
}

#[test]
fn s1b_06_requests_for_different_pages_overlap_in_time() {
    let disk = Arc::new(TestDisk::slow(60));
    let sched = ShardedDiskScheduler::new(disk, 4);
    let start = Instant::now();
    let futures: Vec<_> = (0..8)
        .map(|p| {
            let (req, f) = write_req(p, 1);
            sched.schedule(vec![req]);
            f
        })
        .collect();
    for f in futures {
        assert!(wait(f).unwrap().is_ok());
    }
    let took = start.elapsed();
    assert!(took < Duration::from_millis(8 * 60 * 3 / 4), "8 writes of 60 ms to different pages on 4 workers took {took:?}: one worker would take 480 ms, they should overlap");
}

#[test]
fn s1b_06_dropping_an_idle_sharded_scheduler_does_not_hang() {
    within("dropping a sharded scheduler with empty queues", || drop(ShardedDiskScheduler::new(memory_disk(), 3)));
}

#[test]
fn s1b_06_dropping_a_sharded_scheduler_finishes_everything_scheduled() {
    let disk = Arc::new(TestDisk::slow(1));
    let sched = ShardedDiskScheduler::new(disk.clone(), 3);
    sched.schedule((0..60).map(|i| write_req(i, 1).0).collect());
    drop(sched);
    assert_eq!(disk.ops().len(), 60, "all 60 writes must have reached the disk when the drop returns");
}

proptest! {
    #![proptest_config(config())]

    /// The covariant: any number of workers gives the same answers as one, because requests for one page never overtake each other.
    #[test]
    fn s1b_06_requests_for_one_page_stay_in_order_whatever_the_number_of_workers(
        reqs in prop::collection::vec(prop_oneof![(0..5i32, any::<u8>()).prop_map(|(p, b)| Req::Write(p, b)), (0..5i32).prop_map(Req::Read)], 1..40),
        workers in 1usize..5,
    ) {
        let sched = ShardedDiskScheduler::new(memory_disk(), workers);
        let mut model: std::collections::HashMap<i32, u8> = std::collections::HashMap::new();
        let mut futures: Vec<(Req, u8, Future<DiskResult>)> = Vec::new();
        for r in &reqs {
            match r {
                Req::Write(p, b) => { let (req, f) = write_req(*p, *b); model.insert(*p, *b); sched.schedule(vec![req]); futures.push((r.clone(), *b, f)); }
                Req::Read(p) => { let (req, f) = DiskRequest::read(PageId(*p)); sched.schedule(vec![req]); futures.push((r.clone(), *model.get(p).unwrap_or(&0), f)); }
            }
        }
        for (req, expected, f) in futures {
            let page = wait(f).unwrap().unwrap();
            prop_assert!(page.iter().all(|&b| b == expected), "{req:?} with {workers} workers should have produced a page full of {expected}");
        }
    }
}

// ---- 1b-07 · Boss: threads on every side, and BusTub's own tests -------------------------------------------------

#[test]
fn s1b_07_many_threads_scheduling_at_once_each_get_their_own_answers() {
    let sched = Arc::new(DiskScheduler::new(memory_disk()));
    let handles: Vec<_> = (0..4i32)
        .map(|t| {
            let sched = Arc::clone(&sched);
            thread::spawn(move || {
                for i in 0..50i32 {
                    let page = t * 100 + i;
                    let (w, wf) = write_req(page, (page % 251) as u8);
                    let (r, rf) = DiskRequest::read(PageId(page));
                    sched.schedule(vec![w]);
                    sched.schedule(vec![r]);
                    assert!(wait(wf).unwrap().is_ok());
                    let got = wait(rf).unwrap().unwrap();
                    assert!(got.iter().all(|&b| b == (page % 251) as u8), "thread {t} read the wrong bytes for page {page}");
                }
            })
        })
        .collect();
    within("four scheduling threads", move || handles.into_iter().for_each(|h| h.join().unwrap()));
}

#[test]
fn s1b_07_the_scheduler_works_over_the_real_disk_manager_too() {
    let dir = std::env::temp_dir().join(format!("bustub-rs-1b-{}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    let dm = Arc::new(bustub::storage::disk::disk_manager::DiskManager::new(dir.join("t.bustub")).unwrap());
    let sched = DiskScheduler::new(dm);
    let (w, wf) = write_req(7, 0x5A);
    let (r, rf) = DiskRequest::read(PageId(7));
    sched.schedule(vec![w, r]);
    assert!(wait(wf).unwrap().is_ok());
    assert!(wait(rf).unwrap().unwrap().iter().all(|&b| b == 0x5A), "a page written through the scheduler to a real file reads back");
    drop(sched);
    let _ = std::fs::remove_dir_all(&dir);
}
