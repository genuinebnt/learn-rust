from _c import C
M1B, M1F, M1G = "02-disk-scheduler", "06-buffer-pool", "07-page-guards"
CH = []

CH.append(C("1b-c3", M1B, "92-challenge-a-priority-queue", "build", "Challenge: a priority queue of requests", "easy", "stages_1b::s1b_c3",
  ["ordering work by priority and, within a priority, by arrival","keeping a stable order without sorting the whole queue every time"],
  ["condvars-and-blocking-queues","model-based-testing"],
  "`RequestQueue` in `src/storage/disk/request_queue.rs`: the queue a smarter disk scheduler would sit on. `push(priority, item)` adds an item; `pop` returns the item with the **highest priority**, and among equal priorities the one that arrived **first**.",
  "A scheduler that treats a user's read and a background flush alike makes the user wait. Priorities fix that, but a plain priority queue (a binary heap) does not keep arrival order among equals, and starving the oldest request of a class is a bug too. The tie-break is the exercise.",
  ["`push(priority, item)`: a higher number is more urgent.","`pop()` removes and returns the most urgent item, the oldest among equals; `None` when empty.","`len()`, `is_empty()`, and `peek_priority()` (the priority `pop` would return)."],
  ["`len()` equals pushes minus pops.","Every item pushed is popped exactly once.","`peek_priority()` equals the priority of the item the next `pop` returns."],
  ["The pop order is the push order stably sorted by descending priority.","Pushing an item of lower priority than everything in the queue never changes which item pops next.","Two queues given the same pushes pop in the same order."],
  ["push (1,a) (3,b) (3,c) (2,d); pop -> b, c, d, a","push (5,x); pop -> x; pop -> None"],
  ["The order of pops for mixed priorities and ties.","Empty queues.","A property against a stable sort of everything pushed."],
  src=("src/storage/disk/request_queue.rs", '''
//! A queue that returns the most urgent item first, and the oldest among equals.

pub struct RequestQueue<T> {
    // @begin 1b-c3
    /// (priority, arrival number, item); the arrival number makes the order of equals stable.
    items: std::collections::BinaryHeap<(u8, std::cmp::Reverse<u64>, Entry<T>)>,
    arrivals: u64,
    //~ _q: std::marker::PhantomData<T>,
    // @end
}

// @begin 1b-c3
/// Wraps the payload so that it needs no ordering of its own.
struct Entry<T>(T);

impl<T> PartialEq for Entry<T> {
    fn eq(&self, _: &Self) -> bool {
        true
    }
}
impl<T> Eq for Entry<T> {}
impl<T> PartialOrd for Entry<T> {
    fn partial_cmp(&self, other: &Self) -> Option<std::cmp::Ordering> {
        Some(self.cmp(other))
    }
}
impl<T> Ord for Entry<T> {
    fn cmp(&self, _: &Self) -> std::cmp::Ordering {
        std::cmp::Ordering::Equal
    }
}
//~ // TODO(1b-c3): anything else your design needs
// @end

impl<T> RequestQueue<T> {
    pub fn new() -> RequestQueue<T> {
        // @begin 1b-c3
        RequestQueue { items: std::collections::BinaryHeap::new(), arrivals: 0 }
        //~ todo!("1b-c3: an empty queue")
        // @end
    }

    pub fn push(&mut self, priority: u8, item: T) {
        // @begin 1b-c3
        self.items.push((priority, std::cmp::Reverse(self.arrivals), Entry(item)));
        self.arrivals += 1;
        //~ todo!("1b-c3: add the item with its priority and arrival")
        // @end
    }

    pub fn pop(&mut self) -> Option<T> {
        // @begin 1b-c3
        self.items.pop().map(|(_, _, Entry(item))| item)
        //~ todo!("1b-c3: the most urgent, oldest item")
        // @end
    }

    pub fn peek_priority(&self) -> Option<u8> {
        // @begin 1b-c3
        self.items.peek().map(|(p, _, _)| *p)
        //~ todo!("1b-c3: the priority pop would return")
        // @end
    }

    pub fn len(&self) -> usize {
        // @begin 1b-c3
        self.items.len()
        //~ todo!("1b-c3: how many items wait")
        // @end
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
}

impl<T> Default for RequestQueue<T> {
    fn default() -> Self {
        RequestQueue::new()
    }
}
'''),
  test=("tests/stages_1b.rs", '''
use bustub::storage::disk::request_queue::RequestQueue;

#[test]
fn s1b_c3_the_most_urgent_goes_first_and_ties_go_in_arrival_order() {
    let mut q = RequestQueue::new();
    for (p, x) in [(1, 'a'), (3, 'b'), (3, 'c'), (2, 'd')] {
        q.push(p, x);
    }
    assert_eq!(q.peek_priority(), Some(3));
    assert_eq!((q.pop(), q.pop(), q.pop(), q.pop(), q.pop()), (Some('b'), Some('c'), Some('d'), Some('a'), None));
}

#[test]
fn s1b_c3_a_late_urgent_request_overtakes_older_ones() {
    let mut q = RequestQueue::new();
    q.push(1, "old1");
    q.push(1, "old2");
    q.push(9, "urgent");
    assert_eq!(q.pop(), Some("urgent"));
    assert_eq!(q.pop(), Some("old1"), "equals keep their arrival order");
}

#[test]
fn s1b_c3_an_empty_queue_has_nothing() {
    let mut q: RequestQueue<u8> = RequestQueue::new();
    assert!(q.is_empty());
    assert_eq!((q.pop(), q.peek_priority(), q.len()), (None, None, 0));
}

#[test]
fn s1b_c3_items_need_no_ordering_of_their_own() {
    struct NoOrd(u32);
    let mut q = RequestQueue::new();
    q.push(2, NoOrd(10));
    q.push(2, NoOrd(20));
    assert_eq!(q.pop().map(|x| x.0), Some(10));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the pop order is the push order stably sorted by descending priority, with pops mixed between pushes.
    #[test]
    fn s1b_c3_property_pops_equal_a_stable_sort(ops in proptest::collection::vec(prop_oneof![(0u8..4, any::<u16>()).prop_map(Some), Just(None)], 0..60)) {
        let mut q = RequestQueue::new();
        let mut model: Vec<(u8, u16)> = Vec::new(); // in arrival order
        for op in ops {
            match op {
                Some((p, x)) => { q.push(p, x); model.push((p, x)); }
                None => {
                    let best = model.iter().enumerate().max_by_key(|&(i, &(p, _))| (p, std::cmp::Reverse(i))).map(|(i, _)| i);
                    prop_assert_eq!(q.peek_priority(), best.map(|i| model[i].0));
                    prop_assert_eq!(q.pop(), best.map(|i| model.remove(i).1));
                }
            }
            prop_assert_eq!(q.len(), model.len());
        }
    }
}
''')))

CH.append(C("1b-c4", M1B, "93-challenge-write-coalescing", "build", "Challenge: write coalescing", "medium", "stages_1b::s1b_c4",
  ["reordering and dropping requests without changing what any read sees","stating the invariant a reordering must preserve"],
  ["model-based-testing","property-testing-and-fuzzing"],
  "`coalesce` in `src/storage/disk/coalesce.rs`: given a batch of disk operations (`Write(page, value)` and `Read(page)`) in the order they were submitted, return a batch that has **as few writes as possible** and produces exactly the same read results and the same final disk contents.",
  "A scheduler that sees ten writes to the same page in its queue only needs to issue the last one, if nobody reads in between. Dropping the wrong write changes what a reader sees; dropping none wastes the disk. The exercise is finding exactly the writes that are safe to drop.",
  ["`coalesce(ops)` returns a new list of operations. Reads are kept, in order.","A write may be dropped when a **later write to the same page** exists and **no read of that page lies between** them.","The relative order of the operations that remain is the order they had."],
  ["Replaying the output on any starting disk gives the same read results, in the same order, as replaying the input.","The final contents of every page are the same.","The output contains every read of the input."],
  ["No two writes to the same page are adjacent in the output with no read of that page between them.","The output is never longer than the input, and `coalesce(coalesce(x)) == coalesce(x)`.","A batch of only writes comes out with one write per page (the last value)."],
  ["W1=a W1=b W1=c -> W1=c","W1=a R1 W1=b -> unchanged (the read sees a)","W1=a W2=x W1=b -> W2=x W1=b"],
  ["Writes only, reads between, interleaved pages.","Empty batch and a single operation.","A property: same read results and final state; idempotence; minimality."],
  src=("src/storage/disk/coalesce.rs", '''
//! Merging queued disk operations without changing what any read sees.

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Op {
    Write(u32, u8),
    Read(u32),
}

/// Drops every write that a later write to the same page makes pointless, unless a read of that page lies between the two.
pub fn coalesce(ops: &[Op]) -> Vec<Op> {
    // @begin 1b-c4
    let mut keep = vec![true; ops.len()];
    for (i, op) in ops.iter().enumerate() {
        let Op::Write(page, _) = *op else { continue };
        for later in &ops[i + 1..] {
            match *later {
                Op::Read(p) if p == page => break,
                Op::Write(p, _) if p == page => {
                    keep[i] = false;
                    break;
                }
                _ => {}
            }
        }
    }
    ops.iter().zip(keep).filter(|(_, k)| *k).map(|(o, _)| *o).collect()
    //~ todo!("1b-c4: keep every read; keep a write unless a later write to the same page follows with no read of the page between")
    // @end
}
'''),
  test=("tests/stages_1b.rs", '''
use bustub::storage::disk::coalesce::{coalesce, Op};
use std::collections::HashMap;

use Op::{Read as R, Write as W};

/// Replays operations on a disk and returns what the reads saw, and the final contents.
fn replay(ops: &[Op]) -> (Vec<Option<u8>>, Vec<(u32, u8)>) {
    let mut disk: HashMap<u32, u8> = HashMap::new();
    let mut seen = Vec::new();
    for op in ops {
        match *op {
            W(p, v) => {
                disk.insert(p, v);
            }
            R(p) => seen.push(disk.get(&p).copied()),
        }
    }
    let mut fin: Vec<_> = disk.into_iter().collect();
    fin.sort();
    (seen, fin)
}

#[test]
fn s1b_c4_repeated_writes_to_one_page_become_the_last_one() {
    assert_eq!(coalesce(&[W(1, 1), W(1, 2), W(1, 3)]), vec![W(1, 3)]);
}

#[test]
fn s1b_c4_a_read_in_between_protects_the_write_it_would_see() {
    assert_eq!(coalesce(&[W(1, 1), R(1), W(1, 2)]), vec![W(1, 1), R(1), W(1, 2)]);
}

#[test]
fn s1b_c4_writes_to_other_pages_in_between_do_not_matter() {
    assert_eq!(coalesce(&[W(1, 1), W(2, 9), W(1, 2)]), vec![W(2, 9), W(1, 2)]);
}

#[test]
fn s1b_c4_a_read_of_another_page_does_not_protect_a_write() {
    assert_eq!(coalesce(&[W(1, 1), R(2), W(1, 2)]), vec![R(2), W(1, 2)]);
}

#[test]
fn s1b_c4_empty_and_single_operations() {
    assert_eq!(coalesce(&[]), vec![]);
    assert_eq!(coalesce(&[R(5)]), vec![R(5)]);
    assert_eq!(coalesce(&[W(5, 1)]), vec![W(5, 1)]);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: same read results and final contents, idempotent, never longer, and minimal (no two writes to a page without a read between).
    #[test]
    fn s1b_c4_property_coalescing_changes_no_read_and_is_minimal(raw in proptest::collection::vec((any::<bool>(), 0u32..4, 0u8..5), 0..40)) {
        let ops: Vec<Op> = raw.into_iter().map(|(w, p, v)| if w { W(p, v) } else { R(p) }).collect();
        let out = coalesce(&ops);
        prop_assert_eq!(replay(&out), replay(&ops));
        prop_assert!(out.len() <= ops.len());
        prop_assert_eq!(coalesce(&out), out.clone());
        prop_assert_eq!(out.iter().filter(|o| matches!(o, R(_))).count(), ops.iter().filter(|o| matches!(o, R(_))).count());
        for page in 0..4 {
            let mut since_write = false; // a write is pending with no read since
            for op in &out {
                match *op {
                    W(p, _) if p == page => {
                        prop_assert!(!since_write, "two writes to page {} with no read between them in {:?}", page, out);
                        since_write = true;
                    }
                    R(p) if p == page => since_write = false,
                    _ => {}
                }
            }
        }
    }
}
''')))

CH.append(C("1b-c5", M1B, "94-challenge-the-lost-jobs", "debug", "Challenge: the lost jobs", "medium", "stages_1b::s1b_c5",
  ["finding a shutdown bug that drops queued work","reasoning about when a worker may exit"],
  ["clean-shutdown-drop-and-join","condvars-and-blocking-queues","deadlock-and-lock-ordering"],
  "`src/storage/disk/job_pool.rs` is a small pool of worker threads: `submit` queues a job, `shutdown` is meant to wait until every job that was submitted has run and then stop the workers. It looks right, and under load some jobs never run. Find the bug and fix it.",
  "The disk scheduler of this module has exactly this shape, and a shutdown that drops queued writes loses data without any error: the program exits cleanly with pages not on disk. 'Stop' has to mean 'finish what you were given, then stop'.",
  ["`submit(job)` queues a job; false if the pool is already shut down.","`shutdown()` returns only after every job accepted before it has finished, and no worker is left running.","Dropping the pool shuts it down."],
  ["Every job accepted by `submit` runs exactly once.","After `shutdown` returns, no job is queued and no worker is alive."],
  ["The number of jobs that ran equals the number `submit` accepted, whatever the number of workers and the timing.","Submitting after shutdown runs nothing."],
  ["4 workers, 100 jobs that each add 1 to a counter; shutdown -> counter 100","submit after shutdown -> false"],
  ["All submitted jobs run before `shutdown` returns.","Different numbers of workers; many small jobs.","Submit after shutdown is refused.","Shutting down twice is fine."],
  src=("src/storage/disk/job_pool.rs", '''
//! A small pool of worker threads that run submitted jobs.

use std::collections::VecDeque;
use std::sync::{Arc, Condvar, Mutex};
use std::thread::{self, JoinHandle};

type Job = Box<dyn FnOnce() + Send + 'static>;

struct Shared {
    state: Mutex<State>,
    work: Condvar,
}

struct State {
    queue: VecDeque<Job>,
    stopping: bool,
}

pub struct JobPool {
    shared: Arc<Shared>,
    workers: Vec<JoinHandle<()>>,
}

impl JobPool {
    pub fn new(workers: usize) -> JobPool {
        let shared = Arc::new(Shared { state: Mutex::new(State { queue: VecDeque::new(), stopping: false }), work: Condvar::new() });
        let workers = (0..workers.max(1))
            .map(|_| {
                let shared = Arc::clone(&shared);
                thread::spawn(move || loop {
                    let job = {
                        let mut st = shared.state.lock().unwrap();
                        loop {
                            // @begin 1b-c5
                            if let Some(job) = st.queue.pop_front() {
                                break Some(job);
                            }
                            if st.stopping {
                                break None;
                            }
                            //~ if st.stopping {
                            //~     break None;
                            //~ }
                            //~ if let Some(job) = st.queue.pop_front() {
                            //~     break Some(job);
                            //~ }
                            // @end
                            st = shared.work.wait(st).unwrap();
                        }
                    };
                    match job {
                        Some(job) => job(),
                        None => return,
                    }
                })
            })
            .collect();
        JobPool { shared, workers }
    }

    /// Queues a job; false if the pool has been shut down.
    pub fn submit(&self, job: impl FnOnce() + Send + 'static) -> bool {
        let mut st = self.shared.state.lock().unwrap();
        if st.stopping {
            return false;
        }
        st.queue.push_back(Box::new(job));
        self.shared.work.notify_one();
        true
    }

    /// Waits for every accepted job to run, then stops the workers.
    pub fn shutdown(&mut self) {
        self.shared.state.lock().unwrap().stopping = true;
        self.shared.work.notify_all();
        for w in self.workers.drain(..) {
            let _ = w.join();
        }
    }
}

impl Drop for JobPool {
    fn drop(&mut self) {
        self.shutdown();
    }
}
'''),
  test=("tests/stages_1b.rs", '''
use bustub::storage::disk::job_pool::JobPool;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

fn run(workers: usize, jobs: usize) -> usize {
    let counter = Arc::new(AtomicUsize::new(0));
    let mut pool = JobPool::new(workers);
    let mut accepted = 0;
    for _ in 0..jobs {
        let c = Arc::clone(&counter);
        if pool.submit(move || {
            std::thread::yield_now();
            c.fetch_add(1, Ordering::SeqCst);
        }) {
            accepted += 1;
        }
    }
    pool.shutdown();
    assert_eq!(accepted, jobs);
    counter.load(Ordering::SeqCst)
}

#[test]
fn s1b_c5_every_submitted_job_runs_before_shutdown_returns() {
    assert_eq!(run(4, 200), 200, "jobs were still queued when the workers stopped");
}

#[test]
fn s1b_c5_one_worker_and_many_workers() {
    assert_eq!(run(1, 100), 100);
    assert_eq!(run(8, 300), 300);
}

#[test]
fn s1b_c5_a_job_submitted_after_shutdown_is_refused_and_does_not_run() {
    let ran = Arc::new(AtomicUsize::new(0));
    let mut pool = JobPool::new(2);
    pool.shutdown();
    let r = Arc::clone(&ran);
    assert!(!pool.submit(move || {
        r.fetch_add(1, Ordering::SeqCst);
    }));
    assert_eq!(ran.load(Ordering::SeqCst), 0);
}

#[test]
fn s1b_c5_shutting_down_twice_and_dropping_are_fine() {
    let c = Arc::new(AtomicUsize::new(0));
    let mut pool = JobPool::new(2);
    for _ in 0..20 {
        let c = Arc::clone(&c);
        pool.submit(move || {
            c.fetch_add(1, Ordering::SeqCst);
        });
    }
    pool.shutdown();
    pool.shutdown();
    drop(pool);
    assert_eq!(c.load(Ordering::SeqCst), 20);
}

#[test]
fn s1b_c5_dropping_the_pool_also_finishes_the_queue() {
    let c = Arc::new(AtomicUsize::new(0));
    {
        let pool = JobPool::new(3);
        for _ in 0..150 {
            let c = Arc::clone(&c);
            pool.submit(move || {
                std::thread::yield_now();
                c.fetch_add(1, Ordering::SeqCst);
            });
        }
    }
    assert_eq!(c.load(Ordering::SeqCst), 150);
}
''')))

CH.append(C("1f-c1", M1F, "92-challenge-a-pin-table", "build", "Challenge: a pin table", "easy", "stages_1f::s1f_c1",
  ["counting pins per page and refusing to unpin what is not pinned","keeping the table free of entries for pages with no pins"],
  ["pin-counts-and-dirty-pages","slot-allocation-and-invariants"],
  "`PinTable` in `src/buffer/pin_table.rs`: the pin counts of a buffer pool, on their own: how many users hold each page right now. `pin` adds one, `unpin` removes one and **refuses** to go below zero.",
  "A pin count that goes negative (or wraps) means a page is unpinned while someone still uses it, and the buffer pool evicts it from under them. Making the table refuse that, and report it, turns a silent corruption into an error at the exact call that was wrong.",
  ["`pin(page)` returns the new count.","`unpin(page)` returns the new count, or `Err(NotPinned)` when the page has no pins.","`count(page)`, `is_pinned(page)` and `pinned_pages()` (sorted) report the state."],
  ["No page has a count of 0 in the table: a page with no pins is simply absent.","Every count is the number of `pin`s minus successful `unpin`s of that page."],
  ["`pin` then `unpin` returns the table to its previous state.","`unpin` of an unpinned page changes nothing.","The counts of different pages are independent."],
  ["pin 3, pin 3 -> 2; unpin 3 -> 1; unpin 3 -> 0 (page 3 no longer pinned); unpin 3 -> Err"],
  ["Counting up and down for several pages.","Unpinning what is not pinned.","A property against a map of counts."],
  src=("src/buffer/pin_table.rs", '''
//! Pin counts: how many users hold each page.

use std::collections::BTreeMap;

#[derive(Debug, PartialEq, Eq)]
pub struct NotPinned;

pub struct PinTable {
    // @begin 1f-c1
    counts: BTreeMap<u32, usize>,
    //~ _pins: (),
    // @end
}

impl PinTable {
    pub fn new() -> PinTable {
        // @begin 1f-c1
        PinTable { counts: BTreeMap::new() }
        //~ todo!("1f-c1: no page is pinned")
        // @end
    }

    pub fn pin(&mut self, page: u32) -> usize {
        // @begin 1f-c1
        let c = self.counts.entry(page).or_insert(0);
        *c += 1;
        *c
        //~ todo!("1f-c1: one more pin; the new count")
        // @end
    }

    pub fn unpin(&mut self, page: u32) -> Result<usize, NotPinned> {
        // @begin 1f-c1
        match self.counts.get_mut(&page) {
            None => Err(NotPinned),
            Some(c) if *c == 1 => {
                self.counts.remove(&page);
                Ok(0)
            }
            Some(c) => {
                *c -= 1;
                Ok(*c)
            }
        }
        //~ todo!("1f-c1: one pin fewer, or an error when there is none")
        // @end
    }

    pub fn count(&self, page: u32) -> usize {
        // @begin 1f-c1
        self.counts.get(&page).copied().unwrap_or(0)
        //~ todo!("1f-c1: how many pins")
        // @end
    }

    pub fn is_pinned(&self, page: u32) -> bool {
        self.count(page) > 0
    }

    pub fn pinned_pages(&self) -> Vec<u32> {
        // @begin 1f-c1
        self.counts.keys().copied().collect()
        //~ todo!("1f-c1: the pinned pages, sorted")
        // @end
    }
}

impl Default for PinTable {
    fn default() -> Self {
        PinTable::new()
    }
}
'''),
  test=("tests/stages_1f.rs", '''
use bustub::buffer::pin_table::{NotPinned, PinTable};
use std::collections::BTreeMap;

#[test]
fn s1f_c1_pins_count_up_and_down() {
    let mut t = PinTable::new();
    assert_eq!((t.pin(3), t.pin(3)), (1, 2));
    assert_eq!(t.unpin(3), Ok(1));
    assert_eq!(t.unpin(3), Ok(0));
    assert!(!t.is_pinned(3));
    assert_eq!(t.unpin(3), Err(NotPinned));
}

#[test]
fn s1f_c1_unpinning_what_was_never_pinned_changes_nothing() {
    let mut t = PinTable::new();
    t.pin(1);
    assert_eq!(t.unpin(2), Err(NotPinned));
    assert_eq!(t.pinned_pages(), vec![1]);
    assert_eq!(t.count(1), 1);
}

#[test]
fn s1f_c1_a_page_can_be_pinned_again_after_its_pins_reach_zero() {
    let mut t = PinTable::new();
    t.pin(4);
    assert_eq!(t.unpin(4), Ok(0));
    assert!(!t.is_pinned(4));
    assert_eq!(t.pin(4), 1, "the count starts again from one");
    assert_eq!(t.pinned_pages(), vec![4]);
}

#[test]
fn s1f_c1_pages_are_independent_and_listed_in_order() {
    let mut t = PinTable::new();
    for p in [9, 2, 5, 2] {
        t.pin(p);
    }
    assert_eq!(t.pinned_pages(), vec![2, 5, 9]);
    assert_eq!((t.count(2), t.count(5), t.count(7)), (2, 1, 0));
    t.unpin(5).unwrap();
    assert_eq!(t.pinned_pages(), vec![2, 9], "a page with no pins is not listed");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against a map of counts, with no zero entries.
    #[test]
    fn s1f_c1_property_a_pin_table_matches_a_counting_map(ops in proptest::collection::vec((any::<bool>(), 0u32..5), 0..80)) {
        let mut t = PinTable::new();
        let mut m: BTreeMap<u32, usize> = BTreeMap::new();
        for (pin, p) in ops {
            if pin {
                *m.entry(p).or_insert(0) += 1;
                prop_assert_eq!(t.pin(p), m[&p]);
            } else {
                let want = match m.get_mut(&p) {
                    None => Err(NotPinned),
                    Some(c) => { *c -= 1; let n = *c; if n == 0 { m.remove(&p); } Ok(n) }
                };
                prop_assert_eq!(t.unpin(p), want);
            }
            prop_assert_eq!(t.pinned_pages(), m.keys().copied().collect::<Vec<_>>());
        }
    }
}
''')))

CH.append(C("1f-c2", M1F, "93-challenge-flush-runs", "build", "Challenge: flush runs", "easy", "stages_1f::s1f_c2",
  ["turning a set of dirty pages into the fewest sequential writes","bounding a run's length"],
  ["eviction-and-write-back-ordering","performance-tests-and-measuring"],
  "`flush_runs` in `src/buffer/flush_runs.rs`: given the page numbers of the dirty pages (in any order, maybe with repeats), return the writes to issue as **runs** `(first_page, length)` of consecutive pages in increasing order, with no run longer than `max_run`.",
  "A disk writes a run of neighbouring pages almost as fast as one page. A buffer pool that flushes dirty pages one by one in the order it found them does the most seeks; sorting and merging neighbours is the cheapest big win in write-back, and a cap keeps one run from monopolising the disk.",
  ["Pages are deduplicated and sorted; neighbours (p, p + 1) join a run.","No run is longer than `max_run` (at least 1); a longer stretch is split into runs of exactly `max_run` and a shorter last run.","The result is in increasing page order."],
  ["The runs cover exactly the set of input pages: every page once, no page that was not given.","Runs are disjoint and in increasing order.","Every run has length between 1 and `max_run`."],
  ["The number of runs is the minimum possible for the cap.","Permuting or repeating the input does not change the output.","With `max_run` at least the number of pages, the number of runs is the number of maximal consecutive stretches."],
  ["[5,3,4,10,3] max 8 -> [(3,3), (10,1)]","[1,2,3,4,5] max 2 -> [(1,2), (3,2), (5,1)]"],
  ["Sorting, deduplicating and merging.","The cap, including a cap of 1.","A property: coverage, disjointness, minimality, order independence."],
  src=("src/buffer/flush_runs.rs", '''
//! Planning the writes of a flush: sorted runs of consecutive pages.

/// `(first_page, length)` runs covering exactly the distinct pages, in increasing order, no run longer than `max_run` (at least 1).
pub fn flush_runs(pages: &[u32], max_run: u32) -> Vec<(u32, u32)> {
    // @begin 1f-c2
    let max_run = max_run.max(1);
    let mut sorted: Vec<u32> = pages.to_vec();
    sorted.sort_unstable();
    sorted.dedup();
    let mut runs: Vec<(u32, u32)> = Vec::new();
    for p in sorted {
        match runs.last_mut() {
            Some((start, len)) if *start + *len == p && *len < max_run => *len += 1,
            _ => runs.push((p, 1)),
        }
    }
    runs
    //~ todo!("1f-c2: sort, drop repeats, merge neighbours up to the cap")
    // @end
}
'''),
  test=("tests/stages_1f.rs", '''
use bustub::buffer::flush_runs::flush_runs;
use std::collections::BTreeSet;

#[test]
fn s1f_c2_neighbours_merge_and_the_rest_stand_alone() {
    assert_eq!(flush_runs(&[5, 3, 4, 10, 3], 8), vec![(3, 3), (10, 1)]);
}

#[test]
fn s1f_c2_the_cap_splits_a_long_stretch() {
    assert_eq!(flush_runs(&[1, 2, 3, 4, 5], 2), vec![(1, 2), (3, 2), (5, 1)]);
    assert_eq!(flush_runs(&[1, 2, 3], 1), vec![(1, 1), (2, 1), (3, 1)]);
}

#[test]
fn s1f_c2_nothing_in_nothing_out() {
    assert_eq!(flush_runs(&[], 4), vec![]);
    assert_eq!(flush_runs(&[7, 7, 7], 4), vec![(7, 1)]);
}

#[test]
fn s1f_c2_the_largest_page_numbers_do_not_overflow() {
    assert_eq!(flush_runs(&[u32::MAX, u32::MAX - 1], 8), vec![(u32::MAX - 1, 2)]);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: exact coverage, disjoint increasing runs within the cap, the fewest runs, and the same answer for any order.
    #[test]
    fn s1f_c2_property_runs_cover_the_pages_in_the_fewest_writes(pages in proptest::collection::vec(0u32..40, 0..40), max_run in 1u32..8) {
        let runs = flush_runs(&pages, max_run);
        let set: BTreeSet<u32> = pages.iter().copied().collect();
        let covered: Vec<u32> = runs.iter().flat_map(|&(s, l)| s..s + l).collect();
        prop_assert_eq!(covered.clone(), set.iter().copied().collect::<Vec<_>>());
        prop_assert!(runs.iter().all(|&(_, l)| (1..=max_run).contains(&l)));
        // fewest: each maximal consecutive stretch of length n needs ceil(n / max_run) runs
        let mut want = 0u32;
        let mut stretch = 0u32;
        let mut prev: Option<u32> = None;
        for &p in &set {
            if prev == Some(p.wrapping_sub(1)) && prev.is_some() { stretch += 1; } else { want += stretch.div_ceil(max_run); stretch = 1; }
            prev = Some(p);
        }
        want += stretch.div_ceil(max_run);
        prop_assert_eq!(runs.len() as u32, want);
        let mut rev = pages.clone();
        rev.reverse();
        prop_assert_eq!(flush_runs(&rev, max_run), runs);
    }
}
''')))

CH.append(C("1f-c3", M1F, "94-challenge-write-behind", "build", "Challenge: write-behind", "medium", "stages_1f::s1f_c3",
  ["deciding which dirty pages are due for a background flush","keeping time out of the logic so it can be tested"],
  ["eviction-and-write-back-ordering","pin-counts-and-dirty-pages"],
  "`WriteBehind` in `src/buffer/write_behind.rs`: the bookkeeping behind a background flusher. `mark_dirty(page, now)` records that a page became dirty at time `now` (the first time only: re-dirtying an already dirty page does not reset its age). `due(now, max_age)` returns the pages that have been dirty for **at least** `max_age`, oldest first. `flushed(page)` forgets a page.",
  "A buffer pool that only writes pages when it must evict them makes a checkpoint, a crash and an eviction all slow in different ways. A background flusher that cleans pages that have been dirty too long smooths all three, and its rule is small enough to get exactly right when time is a parameter.",
  ["`mark_dirty` keeps the *earliest* dirty time of a page.","`due(now, max_age)` lists pages with `now - dirty_since >= max_age`, oldest first, ties by page number.","`flushed(page)` removes the page; true if it was dirty. `dirty_count()` and `oldest()` report the state.","A `now` earlier than a page's dirty time counts as age 0."],
  ["Every dirty page has exactly one dirty-since time, the earliest it was marked since it was last flushed.","`due` never lists a page that is not dirty."],
  ["A larger `max_age` never lists more pages.","A later `now` never lists fewer pages.","Flushing the pages `due` returned leaves only the younger ones."],
  ["mark 1@0, 2@5, 3@5; due(now 10, age 5) -> [1, 2, 3]; due(10, 6) -> [1]","re-mark 1@8 keeps its dirty time 0"],
  ["Ages, ordering and ties.","Re-dirtying and flushing.","A property against a model with injected time."],
  src=("src/buffer/write_behind.rs", '''
//! Which dirty pages are due for a background flush.

use std::collections::BTreeMap;

pub struct WriteBehind {
    // @begin 1f-c3
    /// page -> the time it first became dirty (since its last flush).
    dirty: BTreeMap<u32, u64>,
    //~ _wb: (),
    // @end
}

impl WriteBehind {
    pub fn new() -> WriteBehind {
        // @begin 1f-c3
        WriteBehind { dirty: BTreeMap::new() }
        //~ todo!("1f-c3: nothing is dirty")
        // @end
    }

    pub fn mark_dirty(&mut self, page: u32, now: u64) {
        // @begin 1f-c3
        self.dirty.entry(page).or_insert(now);
        //~ todo!("1f-c3: remember when the page first became dirty")
        // @end
    }

    /// Pages dirty for at least `max_age` as of `now`, oldest first (ties by page number).
    pub fn due(&self, now: u64, max_age: u64) -> Vec<u32> {
        // @begin 1f-c3
        let mut v: Vec<(u64, u32)> = self.dirty.iter().filter(|&(_, &since)| now.saturating_sub(since) >= max_age).map(|(&p, &since)| (since, p)).collect();
        v.sort();
        v.into_iter().map(|(_, p)| p).collect()
        //~ todo!("1f-c3: the pages that have been dirty long enough, oldest first")
        // @end
    }

    pub fn flushed(&mut self, page: u32) -> bool {
        // @begin 1f-c3
        self.dirty.remove(&page).is_some()
        //~ todo!("1f-c3: forget the page")
        // @end
    }

    pub fn dirty_count(&self) -> usize {
        // @begin 1f-c3
        self.dirty.len()
        //~ todo!("1f-c3: how many pages are dirty")
        // @end
    }

    /// The page that has been dirty longest, with the time it became dirty.
    pub fn oldest(&self) -> Option<(u32, u64)> {
        // @begin 1f-c3
        self.dirty.iter().map(|(&p, &s)| (s, p)).min().map(|(s, p)| (p, s))
        //~ todo!("1f-c3: the oldest dirty page")
        // @end
    }
}

impl Default for WriteBehind {
    fn default() -> Self {
        WriteBehind::new()
    }
}
'''),
  test=("tests/stages_1f.rs", '''
use bustub::buffer::write_behind::WriteBehind;
use std::collections::BTreeMap;

#[test]
fn s1f_c3_pages_dirty_long_enough_are_due_oldest_first() {
    let mut w = WriteBehind::new();
    w.mark_dirty(1, 0);
    w.mark_dirty(3, 5);
    w.mark_dirty(2, 5);
    assert_eq!(w.due(10, 5), vec![1, 2, 3], "ties are by page number");
    assert_eq!(w.due(10, 6), vec![1]);
    assert_eq!(w.due(4, 5), Vec::<u32>::new());
}

#[test]
fn s1f_c3_dirtying_a_dirty_page_again_does_not_make_it_younger() {
    let mut w = WriteBehind::new();
    w.mark_dirty(1, 0);
    w.mark_dirty(1, 8);
    assert_eq!(w.oldest(), Some((1, 0)));
    assert_eq!(w.due(10, 10), vec![1]);
}

#[test]
fn s1f_c3_a_flushed_page_is_clean_and_starts_again_when_dirtied() {
    let mut w = WriteBehind::new();
    w.mark_dirty(1, 0);
    assert!(w.flushed(1));
    assert!(!w.flushed(1));
    assert_eq!((w.dirty_count(), w.oldest()), (0, None));
    w.mark_dirty(1, 20);
    assert_eq!(w.oldest(), Some((1, 20)));
}

#[test]
fn s1f_c3_a_clock_behind_the_dirty_time_counts_as_age_zero() {
    let mut w = WriteBehind::new();
    w.mark_dirty(1, 100);
    assert_eq!(w.due(50, 0), vec![1]);
    assert_eq!(w.due(50, 1), Vec::<u32>::new());
    assert_eq!(w.due(100, 0), vec![1]);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against a map of dirty-since times.
    #[test]
    fn s1f_c3_property_due_pages_match_a_model(ops in proptest::collection::vec((0u8..3, 0u32..6, 0u64..50), 0..60), age in 0u64..30) {
        let mut w = WriteBehind::new();
        let mut m: BTreeMap<u32, u64> = BTreeMap::new();
        let mut clock = 0u64;
        for (op, page, dt) in ops {
            clock += dt % 5;
            match op {
                0 | 1 => { w.mark_dirty(page, clock); m.entry(page).or_insert(clock); }
                _ => prop_assert_eq!(w.flushed(page), m.remove(&page).is_some()),
            }
            let mut want: Vec<(u64, u32)> = m.iter().filter(|&(_, &s)| clock - s >= age).map(|(&p, &s)| (s, p)).collect();
            want.sort();
            prop_assert_eq!(w.due(clock, age), want.into_iter().map(|(_, p)| p).collect::<Vec<_>>());
            prop_assert_eq!(w.dirty_count(), m.len());
        }
    }
}
''')))

CH.append(C("1f-c4", M1F, "95-challenge-sequential-prefetch", "build", "Challenge: sequential prefetch", "medium", "stages_1f::s1f_c4",
  ["detecting a sequential access pattern from a stream of page numbers","suggesting work ahead of demand without suggesting the same page twice"],
  ["performance-tests-and-measuring","range-scans-and-the-leaf-chain"],
  "`SeqDetector` in `src/buffer/seq_detector.rs`: it sees the page numbers a client reads, one by one, and returns the pages worth **prefetching**. After `trigger` consecutive increasing accesses (`p, p+1, p+2, ...`) it suggests the next `depth` pages; it never suggests a page it has already suggested in the current run, and any non-sequential access resets it.",
  "A table scan reads page after page, and the disk is idle while the CPU waits for the next one. Reading ahead hides that latency, but only if the guess is right: prefetching on a random access wastes I/O and cache. A small state machine is all a pool needs to tell the two apart.",
  ["`access(page)` returns the pages to prefetch now (possibly none), in increasing order.","A run is a sequence of accesses each exactly one more than the last. When the run's length reaches `trigger`, suggest `depth` pages after the current one; as the run goes on, suggest only pages not yet suggested.","An access that is not `last + 1` starts a new run of length 1 (and forgets what was suggested)."],
  ["A suggested page is always greater than the page just accessed.","No page is suggested twice within one run.","No suggestion is made before the run has `trigger` pages."],
  ["Two interleaved scans do not trigger a suggestion unless each is sequential on its own (this detector tracks one run).","A scan of length `n >= trigger` ends with suggestions covering exactly up to `last + depth`.","Repeating an access resets the run."],
  ["trigger 3, depth 2: access 1, 2 -> none; 3 -> [4, 5]; 4 -> [6]; 5 -> [7]; 9 -> none"],
  ["Trigger, depth, and the sliding window.","Reset on a jump or a repeat.","A property against a model of the run."],
  src=("src/buffer/seq_detector.rs", '''
//! Spotting a sequential scan and suggesting pages to read ahead.

pub struct SeqDetector {
    // @begin 1f-c4
    trigger: u32,
    depth: u32,
    last: Option<u32>,
    run: u32,
    /// The highest page suggested in the current run.
    suggested_to: Option<u32>,
    //~ _seq: (),
    // @end
}

impl SeqDetector {
    pub fn new(trigger: u32, depth: u32) -> SeqDetector {
        // @begin 1f-c4
        SeqDetector { trigger: trigger.max(1), depth, last: None, run: 0, suggested_to: None }
        //~ todo!("1f-c4: a detector that has seen nothing")
        // @end
    }

    /// The client read `page`; returns the pages worth prefetching now.
    pub fn access(&mut self, page: u32) -> Vec<u32> {
        // @begin 1f-c4
        if self.last.is_some_and(|l| l.checked_add(1) == Some(page)) {
            self.run += 1;
        } else {
            self.run = 1;
            self.suggested_to = None;
        }
        self.last = Some(page);
        if self.run < self.trigger || self.depth == 0 {
            return Vec::new();
        }
        let from = self.suggested_to.map_or(page + 1, |s| s + 1).max(page + 1);
        let to = page.saturating_add(self.depth);
        if from > to {
            return Vec::new();
        }
        self.suggested_to = Some(to);
        (from..=to).collect()
        //~ todo!("1f-c4: track the run; when it is long enough, suggest the pages not suggested yet up to `depth` ahead")
        // @end
    }
}
'''),
  test=("tests/stages_1f.rs", '''
use bustub::buffer::seq_detector::SeqDetector;

#[test]
fn s1f_c4_nothing_is_suggested_before_the_run_is_long_enough() {
    let mut d = SeqDetector::new(3, 2);
    assert_eq!(d.access(1), Vec::<u32>::new());
    assert_eq!(d.access(2), Vec::<u32>::new());
    assert_eq!(d.access(3), vec![4, 5]);
}

#[test]
fn s1f_c4_a_continuing_scan_only_gets_the_new_pages() {
    let mut d = SeqDetector::new(3, 2);
    for p in 1..=3 {
        d.access(p);
    }
    assert_eq!(d.access(4), vec![6], "5 was suggested already");
    assert_eq!(d.access(5), vec![7]);
}

#[test]
fn s1f_c4_a_jump_or_a_repeat_starts_over() {
    let mut d = SeqDetector::new(2, 3);
    d.access(10);
    assert_eq!(d.access(11), vec![12, 13, 14]);
    assert_eq!(d.access(30), Vec::<u32>::new(), "a jump resets the run");
    assert_eq!(d.access(31), vec![32, 33, 34], "and the next run can be prefetched afresh");
    assert_eq!(d.access(31), Vec::<u32>::new(), "a repeat is not sequential");
}

#[test]
fn s1f_c4_a_depth_of_zero_never_suggests_and_a_trigger_of_one_suggests_at_once() {
    let mut z = SeqDetector::new(2, 0);
    z.access(1);
    assert_eq!(z.access(2), Vec::<u32>::new());
    let mut one = SeqDetector::new(1, 1);
    assert_eq!(one.access(7), vec![8]);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: suggestions are above the accessed page, never repeated within a run, and only made once the run is long enough; a long run
    /// ends with everything up to `last + depth` suggested.
    #[test]
    fn s1f_c4_property_suggestions_follow_the_run(trigger in 1u32..5, depth in 0u32..5, steps in proptest::collection::vec((any::<bool>(), 0u32..50), 0..60)) {
        let mut d = SeqDetector::new(trigger, depth);
        let mut last: Option<u32> = None;
        let mut run = 0u32;
        let mut seen: std::collections::BTreeSet<u32> = Default::default();
        for (seq, jump) in steps {
            let page = match (seq, last) { (true, Some(l)) => l + 1, _ => 1000 + jump * 7 };
            if last.is_some_and(|l| l + 1 == page) { run += 1; } else { run = 1; seen.clear(); }
            last = Some(page);
            let s = d.access(page);
            prop_assert!(s.iter().all(|&x| x > page && x <= page + depth));
            prop_assert!(s.windows(2).all(|w| w[0] < w[1]));
            for x in &s { prop_assert!(seen.insert(*x), "page {} suggested twice in one run", x); }
            if run < trigger { prop_assert!(s.is_empty()); }
            if run >= trigger && depth > 0 {
                prop_assert!((page + 1..=page + depth).all(|x| seen.contains(&x)), "pages up to {} must have been suggested", page + depth);
            }
        }
    }
}
''')))

CH.append(C("1f-c5", M1F, "96-challenge-the-stale-mapping", "debug", "Challenge: the stale mapping", "easy", "stages_1f::s1f_c5",
  ["finding a bug where two maps that must mirror each other drift apart"],
  ["checking-invariants","property-testing-and-fuzzing","pin-counts-and-dirty-pages"],
  "`src/buffer/page_table.rs` keeps which frame holds which page in two maps (page to frame, frame to page) that must always agree. It looks right, and after some sequences it answers that a frame holds a page it no longer holds. Find the bug and fix it.",
  "A buffer pool lives on this mapping, and two maps that mirror each other are a classic source of bugs: every operation has to update both, and the one that forgets leaves a stale entry that is only noticed when a frame is reused. The invariant to test is the mirror itself.",
  ["`insert(page, frame)` records that `frame` holds `page`; if the page was in another frame, or the frame held another page, the old pairing is dropped.","`remove_page(page)` forgets the page and its frame; returns the frame.","`frame_of(page)` and `page_of(frame)` answer from the maps; `len()` is the number of pairs."],
  ["`frame_of(p) == Some(f)` exactly when `page_of(f) == Some(p)`.","Each page is in at most one frame and each frame holds at most one page.","`len()` is the number of pages known, and the number of frames known."],
  ["`remove_page(p)` makes both `frame_of(p)` and `page_of(its old frame)` empty.","Inserting then removing a page leaves the table as it was.","The table equals a set of (page, frame) pairs with both columns unique."],
  ["insert(1, A); remove_page(1); insert(2, A) -> page_of(A) = 2, frame_of(1) = None","insert(1, A); insert(1, B) -> A is free"],
  ["Insert, remove, replace.","A frame reused after its page was removed.","A property: the mirror invariant after every step."],
  src=("src/buffer/page_table.rs", '''
//! Which frame holds which page: two maps that must mirror each other.

use std::collections::HashMap;

#[derive(Default)]
pub struct PageTable {
    page_to_frame: HashMap<u32, u32>,
    frame_to_page: HashMap<u32, u32>,
}

impl PageTable {
    pub fn new() -> PageTable {
        PageTable::default()
    }

    pub fn insert(&mut self, page: u32, frame: u32) {
        if let Some(old_frame) = self.page_to_frame.remove(&page) {
            self.frame_to_page.remove(&old_frame);
        }
        if let Some(old_page) = self.frame_to_page.remove(&frame) {
            self.page_to_frame.remove(&old_page);
        }
        self.page_to_frame.insert(page, frame);
        self.frame_to_page.insert(frame, page);
    }

    /// Forgets `page`; returns the frame that held it.
    pub fn remove_page(&mut self, page: u32) -> Option<u32> {
        // @begin 1f-c5
        let frame = self.page_to_frame.remove(&page)?;
        self.frame_to_page.remove(&frame);
        Some(frame)
        //~ self.page_to_frame.remove(&page)
        // @end
    }

    pub fn frame_of(&self, page: u32) -> Option<u32> {
        self.page_to_frame.get(&page).copied()
    }

    pub fn page_of(&self, frame: u32) -> Option<u32> {
        self.frame_to_page.get(&frame).copied()
    }

    pub fn len(&self) -> usize {
        self.page_to_frame.len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }
}
'''),
  test=("tests/stages_1f.rs", '''
use bustub::buffer::page_table::PageTable;
use std::collections::BTreeMap;

#[test]
fn s1f_c5_insert_and_look_up_both_ways() {
    let mut t = PageTable::new();
    t.insert(1, 10);
    assert_eq!((t.frame_of(1), t.page_of(10), t.len()), (Some(10), Some(1), 1));
}

#[test]
fn s1f_c5_a_removed_page_leaves_no_trace_in_either_direction() {
    let mut t = PageTable::new();
    t.insert(1, 10);
    assert_eq!(t.remove_page(1), Some(10));
    assert_eq!((t.frame_of(1), t.page_of(10), t.len()), (None, None, 0), "the frame no longer claims to hold page 1");
    assert_eq!(t.remove_page(1), None);
}

#[test]
fn s1f_c5_a_frame_reused_after_its_page_was_removed_holds_only_the_new_page() {
    let mut t = PageTable::new();
    t.insert(1, 10);
    t.remove_page(1);
    t.insert(2, 10);
    assert_eq!((t.page_of(10), t.frame_of(1), t.frame_of(2)), (Some(2), None, Some(10)));
}

#[test]
fn s1f_c5_moving_a_page_to_another_frame_frees_the_old_one() {
    let mut t = PageTable::new();
    t.insert(1, 10);
    t.insert(1, 11);
    assert_eq!((t.page_of(10), t.page_of(11), t.len()), (None, Some(1), 1));
}

#[test]
fn s1f_c5_putting_another_page_in_a_used_frame_evicts_the_old_page_from_the_table() {
    let mut t = PageTable::new();
    t.insert(1, 10);
    t.insert(2, 10);
    assert_eq!((t.frame_of(1), t.frame_of(2), t.len()), (None, Some(10), 1));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the table equals a set of (page, frame) pairs with unique columns, and the two directions always mirror each other.
    #[test]
    fn s1f_c5_property_the_two_maps_mirror(ops in proptest::collection::vec((any::<bool>(), 0u32..5, 0u32..5), 0..60)) {
        let mut t = PageTable::new();
        let mut m: BTreeMap<u32, u32> = BTreeMap::new(); // page -> frame
        for (ins, page, frame) in ops {
            if ins {
                t.insert(page, frame);
                m.retain(|&p, &mut f| p != page && f != frame);
                m.insert(page, frame);
            } else {
                prop_assert_eq!(t.remove_page(page), m.remove(&page));
            }
            prop_assert_eq!(t.len(), m.len());
            for p in 0..5 {
                prop_assert_eq!(t.frame_of(p), m.get(&p).copied());
            }
            for f in 0..5 {
                prop_assert_eq!(t.page_of(f), m.iter().find(|&(_, &x)| x == f).map(|(&p, _)| p), "frame {}", f);
            }
        }
    }
}
''')))

CH.append(C("1g-c1", M1G, "92-challenge-a-scope-guard", "build", "Challenge: a scope guard", "easy", "stages_1g::s1g_c1",
  ["running cleanup code on every exit path with Drop","cancelling a guard, and what happens on a panic"],
  ["raii-guards-and-lifetimes","ownership-of-files-and-raii","panics-unwinding-and-catch-unwind"],
  "`Defer` in `src/common/defer.rs`: a guard that runs a closure when it goes out of scope, however it goes out of scope (normal exit, early return, `?`, a panic). `cancel()` disarms it; `run_now()` runs the closure immediately, once.",
  "A page guard is a `Defer` that unpins: the point of RAII is that the cleanup cannot be forgotten on the path nobody tested. Building the general guard shows exactly what the language promises (drop order, drop on unwinding) and what it does not (a leaked guard does not run).",
  ["The closure runs exactly once: on drop, or on `run_now()`, or never if `cancel()` was called first.","Guards drop in reverse order of creation.","A panic in the scope still runs the guard while unwinding."],
  ["The closure never runs twice.","After `cancel()` the closure never runs.","After `run_now()`, dropping does not run it again."],
  ["The number of runs equals the number of guards that were neither cancelled nor leaked.","Declaring guards A then B runs B's closure first.","Moving a guard moves the obligation: it runs once, when the new owner drops."],
  ["{ let _g = Defer::new(|| log(1)); log(0); } -> 0, 1","cancel -> never runs","two guards: runs in reverse order"],
  ["Run on drop, cancel, run_now.","Order of several guards, early return and `?`.","Run on panic.","Moving a guard."],
  src=("src/common/defer.rs", '''
//! A scope guard: runs a closure when it is dropped.

pub struct Defer<F: FnOnce()> {
    // @begin 1g-c1
    f: Option<F>,
    //~ _defer: std::marker::PhantomData<F>,
    // @end
}

impl<F: FnOnce()> Defer<F> {
    pub fn new(f: F) -> Defer<F> {
        // @begin 1g-c1
        Defer { f: Some(f) }
        //~ todo!("1g-c1: remember the closure")
        // @end
    }

    /// The closure will not run.
    pub fn cancel(&mut self) {
        // @begin 1g-c1
        self.f = None;
        //~ todo!("1g-c1: forget the closure")
        // @end
    }

    /// Runs the closure now, once.
    pub fn run_now(&mut self) {
        // @begin 1g-c1
        if let Some(f) = self.f.take() {
            f();
        }
        //~ todo!("1g-c1: run it and make sure it is not run again")
        // @end
    }
}

impl<F: FnOnce()> Drop for Defer<F> {
    fn drop(&mut self) {
        // @begin 1g-c1
        if let Some(f) = self.f.take() {
            f();
        }
        //~ // TODO(1g-c1): run the closure unless it was cancelled or already run
        // @end
    }
}
'''),
  test=("tests/stages_1g.rs", '''
use bustub::common::defer::Defer;
use std::cell::RefCell;
use std::rc::Rc;

fn log() -> Rc<RefCell<Vec<u32>>> {
    Rc::new(RefCell::new(Vec::new()))
}

#[test]
fn s1g_c1_runs_when_the_scope_ends() {
    let l = log();
    {
        let l2 = l.clone();
        let _g = Defer::new(move || l2.borrow_mut().push(1));
        l.borrow_mut().push(0);
    }
    assert_eq!(*l.borrow(), vec![0, 1]);
}

#[test]
fn s1g_c1_a_cancelled_guard_never_runs() {
    let l = log();
    {
        let l2 = l.clone();
        let mut g = Defer::new(move || l2.borrow_mut().push(1));
        g.cancel();
    }
    assert!(l.borrow().is_empty());
}

#[test]
fn s1g_c1_run_now_runs_once_and_drop_does_not_run_it_again() {
    let l = log();
    {
        let l2 = l.clone();
        let mut g = Defer::new(move || l2.borrow_mut().push(1));
        g.run_now();
        g.run_now();
        assert_eq!(*l.borrow(), vec![1]);
    }
    assert_eq!(*l.borrow(), vec![1]);
}

#[test]
fn s1g_c1_guards_run_in_reverse_order_of_creation() {
    let l = log();
    {
        let (a, b, c) = (l.clone(), l.clone(), l.clone());
        let _x = Defer::new(move || a.borrow_mut().push(1));
        let _y = Defer::new(move || b.borrow_mut().push(2));
        let _z = Defer::new(move || c.borrow_mut().push(3));
    }
    assert_eq!(*l.borrow(), vec![3, 2, 1]);
}

#[test]
fn s1g_c1_an_early_return_and_a_question_mark_still_run_the_guard() {
    fn work(l: Rc<RefCell<Vec<u32>>>, fail: bool) -> Result<u32, ()> {
        let l2 = l.clone();
        let _g = Defer::new(move || l2.borrow_mut().push(99));
        if fail {
            Err(())?;
        }
        Ok(1)
    }
    let l = log();
    assert_eq!(work(l.clone(), true), Err(()));
    assert_eq!(work(l.clone(), false), Ok(1));
    assert_eq!(*l.borrow(), vec![99, 99]);
}

#[test]
fn s1g_c1_a_panic_runs_the_guard_while_unwinding() {
    use std::sync::{Arc, Mutex};
    let l = Arc::new(Mutex::new(Vec::new()));
    let l2 = l.clone();
    let r = std::panic::catch_unwind(std::panic::AssertUnwindSafe(move || {
        let _g = Defer::new(move || l2.lock().unwrap().push(1));
        panic!("boom");
    }));
    assert!(r.is_err());
    assert_eq!(*l.lock().unwrap(), vec![1]);
}

#[test]
fn s1g_c1_a_moved_guard_runs_once_when_its_new_owner_drops() {
    let l = log();
    let l2 = l.clone();
    let g = Defer::new(move || l2.borrow_mut().push(7));
    let holder = vec![g];
    assert!(l.borrow().is_empty(), "moving a guard into a vector does not run it");
    drop(holder);
    assert_eq!(*l.borrow(), vec![7]);
}
''')))

CH.append(C("1g-c2", M1G, "93-challenge-counted-pins", "build", "Challenge: counted pins", "easy", "stages_1g::s1g_c2",
  ["a handle whose clone and drop keep a shared count exact","what `Clone` must do for a resource-owning type"],
  ["raii-guards-and-lifetimes","smart-pointers-box-rc-arc","atomics-ordering-and-the-log"],
  "`Pins` and `PinHandle` in `src/common/pin_handle.rs`: `Pins::pin()` returns a handle and raises the shared pin count by one; **cloning** a handle raises it; **dropping** a handle lowers it. `count()` is always the number of live handles, from any thread.",
  "A pin count is a reference count with a meaning: while it is above zero the page may not be evicted. Doing it by hand (increment here, decrement there) is how counts drift; tying it to the handle's lifetime makes the count correct by construction, and `Clone` is the case people forget.",
  ["`Pins::new()` starts at 0; `pin()` returns a handle and counts it.","`PinHandle::clone` counts as another pin.","Dropping a handle uncounts it; `count()` reads the live total."],
  ["`count()` equals the number of live handles at every moment.","The count never underflows."],
  ["Cloning and then dropping the clone leaves the count as it was.","The count at the end of a scope is the count at the start, whatever happened inside.","Handles moved to other threads still count, and uncount when dropped there."],
  ["pin, pin -> 2; clone one -> 3; drop two -> 1; drop the last -> 0"],
  ["Pin, clone, drop.","Counts across threads.","A property: random clones and drops against a live-handle count."],
  src=("src/common/pin_handle.rs", '''
//! Pins counted by the handles that exist.

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

pub struct Pins {
    // @begin 1g-c2
    count: Arc<AtomicUsize>,
    //~ _pins: (),
    // @end
}

pub struct PinHandle {
    // @begin 1g-c2
    count: Arc<AtomicUsize>,
    //~ _handle: (),
    // @end
}

impl Pins {
    pub fn new() -> Pins {
        // @begin 1g-c2
        Pins { count: Arc::new(AtomicUsize::new(0)) }
        //~ todo!("1g-c2: nothing is pinned")
        // @end
    }

    pub fn pin(&self) -> PinHandle {
        // @begin 1g-c2
        self.count.fetch_add(1, Ordering::SeqCst);
        PinHandle { count: Arc::clone(&self.count) }
        //~ todo!("1g-c2: count one more pin and give out a handle")
        // @end
    }

    pub fn count(&self) -> usize {
        // @begin 1g-c2
        self.count.load(Ordering::SeqCst)
        //~ todo!("1g-c2: the live handles")
        // @end
    }
}

impl Default for Pins {
    fn default() -> Self {
        Pins::new()
    }
}

impl Clone for PinHandle {
    fn clone(&self) -> PinHandle {
        // @begin 1g-c2
        self.count.fetch_add(1, Ordering::SeqCst);
        PinHandle { count: Arc::clone(&self.count) }
        //~ todo!("1g-c2: a clone is another pin")
        // @end
    }
}

impl Drop for PinHandle {
    fn drop(&mut self) {
        // @begin 1g-c2
        self.count.fetch_sub(1, Ordering::SeqCst);
        //~ // TODO(1g-c2): uncount this pin
        // @end
    }
}
'''),
  test=("tests/stages_1g.rs", '''
use bustub::common::pin_handle::Pins;

#[test]
fn s1g_c2_pin_clone_and_drop_keep_the_count_exact() {
    let pins = Pins::new();
    let a = pins.pin();
    let b = pins.pin();
    assert_eq!(pins.count(), 2);
    let c = a.clone();
    assert_eq!(pins.count(), 3);
    drop(b);
    drop(a);
    assert_eq!(pins.count(), 1);
    drop(c);
    assert_eq!(pins.count(), 0);
}

#[test]
fn s1g_c2_a_scope_leaves_the_count_as_it_found_it() {
    let pins = Pins::new();
    let keep = pins.pin();
    {
        let h = pins.pin();
        let _c = h.clone();
        assert_eq!(pins.count(), 3);
    }
    assert_eq!(pins.count(), 1);
    drop(keep);
}

#[test]
fn s1g_c2_handles_on_other_threads_count_and_uncount() {
    let pins = Pins::new();
    let hs: Vec<_> = (0..8).map(|_| pins.pin()).collect();
    assert_eq!(pins.count(), 8);
    let threads: Vec<_> = hs.into_iter().map(|h| std::thread::spawn(move || drop(h))).collect();
    for t in threads {
        t.join().unwrap();
    }
    assert_eq!(pins.count(), 0);
}

#[test]
fn s1g_c2_a_moved_handle_is_counted_once() {
    let pins = Pins::new();
    let h = pins.pin();
    let moved = h;
    assert_eq!(pins.count(), 1);
    drop(moved);
    assert_eq!(pins.count(), 0);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: after any sequence of pins, clones and drops the count is the number of live handles.
    #[test]
    fn s1g_c2_property_the_count_is_the_number_of_live_handles(ops in proptest::collection::vec((0u8..3, 0usize..8), 0..80)) {
        let pins = Pins::new();
        let mut live = Vec::new();
        for (op, i) in ops {
            match op {
                0 => live.push(pins.pin()),
                1 if !live.is_empty() => { let h = live[i % live.len()].clone(); live.push(h); }
                _ if !live.is_empty() => { live.swap_remove(i % live.len()); }
                _ => {}
            }
            prop_assert_eq!(pins.count(), live.len());
        }
    }
}
''')))

CH.append(C("1g-c3", M1G, "94-challenge-released-twice", "debug", "Challenge: released twice", "easy", "stages_1g::s1g_c3",
  ["finding a double release caused by a guard that is consumed explicitly","moving out of a guard that has a Drop"],
  ["raii-guards-and-lifetimes","ownership-of-files-and-raii","property-testing-and-fuzzing"],
  "`src/common/scoped_pin.rs` has a guard that unpins a page when dropped and can also be released early with `release(self)`, which returns the count after unpinning. It looks right, and after an early release the count is one too low. Find the bug and fix it.",
  "Explicit early release is common (`drop(guard)` is not always possible because you want the return value), and it is the one place where RAII guards go wrong: the explicit path does the cleanup and then `Drop` does it again when `self` ends. The fix is a Rust idiom worth knowing.",
  ["`ScopedPin::new(&counter)` counts one pin; dropping it uncounts it.","`release(self)` uncounts the pin now and returns the count after that; the guard is consumed and must not uncount again."],
  ["The counter equals the number of live, unreleased guards.","Every pin is uncounted exactly once."],
  ["Releasing a guard and dropping a guard have the same effect on the counter.","`release` returns the count after the release."],
  ["new, new -> 2; release one -> returns 1; drop the other -> 0"],
  ["Drop, release, and a mix.","The value `release` returns.","A property: the counter equals live guards."],
  src=("src/common/scoped_pin.rs", '''
//! A pin that is uncounted when dropped, or earlier by `release`.

use std::cell::Cell;

pub struct ScopedPin<'a> {
    counter: &'a Cell<usize>,
}

impl<'a> ScopedPin<'a> {
    pub fn new(counter: &'a Cell<usize>) -> ScopedPin<'a> {
        counter.set(counter.get() + 1);
        ScopedPin { counter }
    }

    /// Uncounts the pin now and returns the count after that.
    pub fn release(self) -> usize {
        // @begin 1g-c3
        let counter = self.counter;
        std::mem::forget(self);
        counter.set(counter.get() - 1);
        counter.get()
        //~ self.counter.set(self.counter.get() - 1);
        //~ self.counter.get()
        // @end
    }
}

impl Drop for ScopedPin<'_> {
    fn drop(&mut self) {
        self.counter.set(self.counter.get() - 1);
    }
}
'''),
  test=("tests/stages_1g.rs", '''
use bustub::common::scoped_pin::ScopedPin;
use std::cell::Cell;

#[test]
fn s1g_c3_dropping_uncounts() {
    let c = Cell::new(0);
    {
        let _a = ScopedPin::new(&c);
        let _b = ScopedPin::new(&c);
        assert_eq!(c.get(), 2);
    }
    assert_eq!(c.get(), 0);
}

#[test]
fn s1g_c3_releasing_uncounts_once_and_returns_the_count_after() {
    let c = Cell::new(0);
    let a = ScopedPin::new(&c);
    let _b = ScopedPin::new(&c);
    assert_eq!(a.release(), 1);
    assert_eq!(c.get(), 1, "the released guard must not uncount again when it goes out of scope");
}

#[test]
fn s1g_c3_a_mix_of_releases_and_drops() {
    let c = Cell::new(0);
    let guards: Vec<_> = (0..5).map(|_| ScopedPin::new(&c)).collect();
    let mut left = 5;
    for (i, g) in guards.into_iter().enumerate() {
        if i % 2 == 0 {
            left -= 1;
            assert_eq!(g.release(), left);
        } else {
            drop(g);
            left -= 1;
        }
        assert_eq!(c.get(), left);
    }
    assert_eq!(c.get(), 0);
}

#[test]
fn s1g_c3_releasing_the_last_guard_leaves_zero_and_the_value_returned_is_zero() {
    let c = Cell::new(0);
    let g = ScopedPin::new(&c);
    assert_eq!(g.release(), 0);
    assert_eq!(c.get(), 0, "it must stay at zero: a second uncount would underflow");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the counter is always the number of guards that are neither dropped nor released.
    #[test]
    fn s1g_c3_property_the_counter_equals_the_live_guards(ops in proptest::collection::vec((0u8..3, 0usize..6), 0..60)) {
        let c = Cell::new(0);
        let mut live = Vec::new();
        for (op, i) in ops {
            match op {
                0 => live.push(ScopedPin::new(&c)),
                1 if !live.is_empty() => { let g = live.swap_remove(i % live.len()); let n = g.release(); prop_assert_eq!(n, live.len()); }
                _ if !live.is_empty() => { live.swap_remove(i % live.len()); }
                _ => {}
            }
            prop_assert_eq!(c.get(), live.len());
        }
    }
}
''')))

CH.append(C("1g-c4", M1G, "95-challenge-a-latch-with-a-timeout", "build", "Challenge: a latch with a timeout", "medium", "stages_1g::s1g_c4",
  ["waiting for a resource for a bounded time","telling 'timed out' from 'woken'"],
  ["condvars-and-blocking-queues","deadlock-and-lock-ordering","raii-guards-and-lifetimes"],
  "`TimedLatch` in `src/common/timed_latch.rs`: an exclusive latch with `try_acquire`, `acquire_timeout(d)` (waits at most `d` for the latch, returns whether it got it), and `release`. The latch is not owned by a thread: any thread may release it.",
  "A latch that can be waited on for ever is how a buffer pool deadlocks, and the usual defence is a bounded wait that fails loudly instead. Doing it with a condition variable has two traps: a spurious wake-up must not count as success, and a timeout that expires just as the latch is released must not lose the grant.",
  ["`try_acquire()` takes the latch if it is free and returns whether it did.","`acquire_timeout(d)` returns true as soon as the latch is acquired, and false if `d` passes first; it never returns true without holding the latch.","`release()` frees the latch and wakes a waiter; returns false if the latch was not held."],
  ["At most one holder at any time.","A `true` from `acquire_timeout` or `try_acquire` means the caller holds the latch until `release`.","A wait that times out leaves the latch state unchanged."],
  ["`acquire_timeout(0)` behaves like `try_acquire`.","Releasing within the timeout makes a waiter succeed; not releasing makes it fail after about `d`.","Of N threads waiting, exactly one gets the latch per release."],
  ["held; acquire_timeout(50ms) -> false after ~50ms","held; another thread releases after 20ms; acquire_timeout(1s) -> true"],
  ["Free, held and timed-out cases.","Release within the timeout.","Release of a latch that is not held.","Many waiters, one grant per release."],
  src=("src/common/timed_latch.rs", '''
//! An exclusive latch with a bounded wait.

use std::sync::{Condvar, Mutex};
use std::time::{Duration, Instant};

pub struct TimedLatch {
    // @begin 1g-c4
    held: Mutex<bool>,
    free: Condvar,
    //~ _latch: (),
    // @end
}

impl TimedLatch {
    pub fn new() -> TimedLatch {
        // @begin 1g-c4
        TimedLatch { held: Mutex::new(false), free: Condvar::new() }
        //~ todo!("1g-c4: a free latch")
        // @end
    }

    pub fn try_acquire(&self) -> bool {
        // @begin 1g-c4
        let mut held = self.held.lock().unwrap();
        if *held {
            false
        } else {
            *held = true;
            true
        }
        //~ todo!("1g-c4: take the latch if it is free")
        // @end
    }

    /// Waits at most `timeout` for the latch; true if it was acquired.
    pub fn acquire_timeout(&self, timeout: Duration) -> bool {
        // @begin 1g-c4
        let deadline = Instant::now() + timeout;
        let mut held = self.held.lock().unwrap();
        loop {
            if !*held {
                *held = true;
                return true;
            }
            let now = Instant::now();
            if now >= deadline {
                return false;
            }
            held = self.free.wait_timeout(held, deadline - now).unwrap().0;
        }
        //~ todo!("1g-c4: wait on the condition variable until the latch is free or the time is up; check the condition again after every wake-up")
        // @end
    }

    /// Frees the latch; false if it was not held.
    pub fn release(&self) -> bool {
        // @begin 1g-c4
        let mut held = self.held.lock().unwrap();
        if !*held {
            return false;
        }
        *held = false;
        self.free.notify_one();
        true
        //~ todo!("1g-c4: free it and wake one waiter")
        // @end
    }
}

impl Default for TimedLatch {
    fn default() -> Self {
        TimedLatch::new()
    }
}
'''),
  test=("tests/stages_1g.rs", '''
use bustub::common::timed_latch::TimedLatch;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::time::{Duration, Instant};

#[test]
fn s1g_c4_a_free_latch_is_taken_at_once() {
    let l = TimedLatch::new();
    assert!(l.try_acquire());
    assert!(!l.try_acquire());
    assert!(l.release());
    assert!(l.acquire_timeout(Duration::from_millis(0)));
}

#[test]
fn s1g_c4_a_held_latch_times_out_after_about_the_timeout() {
    let l = TimedLatch::new();
    l.try_acquire();
    let t = Instant::now();
    assert!(!l.acquire_timeout(Duration::from_millis(60)));
    let waited = t.elapsed();
    assert!(waited >= Duration::from_millis(55), "returned after {waited:?}, before the timeout");
    assert!(waited < Duration::from_secs(5));
    assert!(l.release(), "a timed-out wait leaves the latch held by its owner");
}

#[test]
fn s1g_c4_a_release_within_the_timeout_hands_the_latch_to_the_waiter() {
    let l = Arc::new(TimedLatch::new());
    l.try_acquire();
    let l2 = l.clone();
    let h = std::thread::spawn(move || l2.acquire_timeout(Duration::from_secs(10)));
    std::thread::sleep(Duration::from_millis(40));
    assert!(l.release());
    assert!(h.join().unwrap(), "the waiter must be woken by the release");
    assert!(!l.try_acquire(), "and now the waiter holds it");
}

#[test]
fn s1g_c4_releasing_a_latch_that_is_not_held_says_so() {
    let l = TimedLatch::new();
    assert!(!l.release());
    assert!(l.try_acquire());
}

#[test]
fn s1g_c4_each_release_lets_exactly_one_of_many_waiters_in() {
    let l = Arc::new(TimedLatch::new());
    l.try_acquire();
    let got = Arc::new(AtomicUsize::new(0));
    let hs: Vec<_> = (0..4)
        .map(|_| {
            let (l, got) = (l.clone(), got.clone());
            std::thread::spawn(move || {
                if l.acquire_timeout(Duration::from_millis(600)) {
                    got.fetch_add(1, Ordering::SeqCst);
                }
            })
        })
        .collect();
    std::thread::sleep(Duration::from_millis(80));
    l.release();
    for h in hs {
        h.join().unwrap();
    }
    assert_eq!(got.load(Ordering::SeqCst), 1, "one release, one grant; the others timed out");
}
''')))

CH.append(C("1g-c5", M1G, "96-challenge-two-latches-at-once", "build", "Challenge: two latches at once", "medium", "stages_1g::s1g_c5",
  ["taking two locks without a deadlock","a global order as the cure for the circular wait"],
  ["deadlock-and-lock-ordering","raii-guards-and-lifetimes","condvars-and-blocking-queues"],
  "`Slots` in `src/common/slot_pair.rs`: a table of balances, each behind its own lock. `transfer(from, to, amount)` moves `amount` between two slots **atomically** (no thread ever sees the amount in neither slot or in both), and `total()` reads every balance at one instant. Any number of threads may call them, in any order of slots, and nothing may deadlock.",
  "A pool needs two pages at once all the time (a split holds a page and its sibling, a merge two leaves). Two threads asking for the same pair in opposite orders is the textbook circular wait, and it only shows up under load. The cure is not a smarter lock but an agreement: every thread takes locks in the same global order.",
  ["`new(&balances)` makes one slot per balance; `balance(i)` is `None` for an unknown slot.","`transfer(from, to, amount)` is `Err(NoSuchSlot(i))` for an unknown slot (checking `from` first), `Err(Insufficient)` if `from` holds less than `amount` (nothing changes), and otherwise moves the amount. `from == to` succeeds and changes nothing.","`total()` is the sum of all balances at one instant."],
  ["The sum of all balances never changes.","No balance goes below zero through a transfer.","Whatever the interleaving, every call returns."],
  ["A transfer from `a` to `b` followed by one from `b` to `a` of the same amount restores every balance.","Two threads transferring in opposite directions between the same two slots both finish.","`total()` called while transfers run always equals the initial total."],
  ["[10, 5]: transfer(0, 1, 4) -> [6, 9]; transfer(1, 0, 20) -> Err(Insufficient)","two threads: 5000 times 0->1 and 5000 times 1->0, both return"],
  ["Moves, failures and the no-op transfer.","Opposite-order threads finish (watchdog).","Many threads on random pairs conserve the total.","`total()` is a consistent snapshot."],
  src=("src/common/slot_pair.rs", '''
//! A table of balances with one lock per slot.

use std::sync::Mutex;

#[derive(Debug, PartialEq, Eq)]
pub enum TransferError {
    NoSuchSlot(usize),
    Insufficient,
}

pub struct Slots {
    // @begin 1g-c5
    slots: Vec<Mutex<i64>>,
    //~ _slots: (),
    // @end
}

impl Slots {
    pub fn new(balances: &[i64]) -> Slots {
        // @begin 1g-c5
        Slots { slots: balances.iter().map(|&b| Mutex::new(b)).collect() }
        //~ todo!("1g-c5: one lock per slot")
        // @end
    }

    pub fn balance(&self, i: usize) -> Option<i64> {
        // @begin 1g-c5
        self.slots.get(i).map(|m| *m.lock().unwrap())
        //~ todo!("1g-c5: the balance of one slot")
        // @end
    }

    pub fn total(&self) -> i64 {
        // @begin 1g-c5
        let guards: Vec<_> = self.slots.iter().map(|m| m.lock().unwrap()).collect();
        guards.iter().map(|g| **g).sum()
        //~ todo!("1g-c5: every balance at one instant")
        // @end
    }

    pub fn transfer(&self, from: usize, to: usize, amount: i64) -> Result<(), TransferError> {
        // @begin 1g-c5
        let n = self.slots.len();
        if from >= n {
            return Err(TransferError::NoSuchSlot(from));
        }
        if to >= n {
            return Err(TransferError::NoSuchSlot(to));
        }
        if from == to {
            return Ok(());
        }
        let (lo, hi) = if from < to { (from, to) } else { (to, from) };
        let mut a = self.slots[lo].lock().unwrap();
        let mut b = self.slots[hi].lock().unwrap();
        let (src, dst) = if from < to { (&mut *a, &mut *b) } else { (&mut *b, &mut *a) };
        if *src < amount {
            return Err(TransferError::Insufficient);
        }
        *src -= amount;
        *dst += amount;
        Ok(())
        //~ todo!("1g-c5: both locks, in an order every thread agrees on; then the move")
        // @end
    }
}
'''),
  test=("tests/stages_1g.rs", '''
use bustub::common::slot_pair::{Slots, TransferError};
use std::sync::Arc;
use std::time::Duration;

/// Runs `f` on its own thread and fails the test if it has not returned in `secs` seconds (a deadlock would otherwise hang the run).
fn finish_within<T: Send + 'static>(secs: u64, f: impl FnOnce() -> T + Send + 'static) -> T {
    let (tx, rx) = std::sync::mpsc::channel();
    std::thread::spawn(move || {
        let _ = tx.send(f());
    });
    rx.recv_timeout(Duration::from_secs(secs)).expect("did not finish: a deadlock?")
}

#[test]
fn s1g_c5_a_transfer_moves_the_amount_and_failures_change_nothing() {
    let s = Slots::new(&[10, 5]);
    assert_eq!(s.transfer(0, 1, 4), Ok(()));
    assert_eq!((s.balance(0), s.balance(1)), (Some(6), Some(9)));
    assert_eq!(s.transfer(1, 0, 20), Err(TransferError::Insufficient));
    assert_eq!(s.transfer(0, 7, 1), Err(TransferError::NoSuchSlot(7)));
    assert_eq!(s.transfer(9, 1, 1), Err(TransferError::NoSuchSlot(9)));
    assert_eq!((s.balance(0), s.balance(1), s.total()), (Some(6), Some(9), 15));
    assert_eq!(s.balance(2), None);
}

#[test]
fn s1g_c5_a_transfer_to_the_same_slot_succeeds_and_does_not_lock_twice() {
    let s = Arc::new(Slots::new(&[3, 3]));
    let s2 = s.clone();
    let r = finish_within(5, move || s2.transfer(1, 1, 2));
    assert_eq!(r, Ok(()));
    assert_eq!(s.balance(1), Some(3));
}

#[test]
fn s1g_c5_opposite_directions_between_the_same_two_slots_both_finish() {
    let s = Arc::new(Slots::new(&[100, 100]));
    let (a, b) = (s.clone(), s.clone());
    finish_within(20, move || {
        let t1 = std::thread::spawn(move || {
            for _ in 0..5000 {
                let _ = a.transfer(0, 1, 1);
            }
        });
        let t2 = std::thread::spawn(move || {
            for _ in 0..5000 {
                let _ = b.transfer(1, 0, 1);
            }
        });
        t1.join().unwrap();
        t2.join().unwrap();
    });
    assert_eq!(s.total(), 200);
}

#[test]
fn s1g_c5_many_threads_on_random_pairs_conserve_the_total() {
    let s = Arc::new(Slots::new(&[50; 6]));
    let s2 = s.clone();
    finish_within(30, move || {
        let hs: Vec<_> = (0..6u64)
            .map(|t| {
                let s = s2.clone();
                std::thread::spawn(move || {
                    let mut x = t * 7919 + 1;
                    for _ in 0..3000 {
                        x = x.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
                        let (f, to) = ((x >> 33) as usize % 6, (x >> 17) as usize % 6);
                        let _ = s.transfer(f, to, ((x >> 8) % 20) as i64);
                    }
                })
            })
            .collect();
        for h in hs {
            h.join().unwrap();
        }
    });
    assert_eq!(s.total(), 300);
    assert!((0..6).all(|i| s.balance(i).unwrap() >= 0));
}

#[test]
fn s1g_c5_total_is_a_consistent_snapshot_while_transfers_run() {
    let s = Arc::new(Slots::new(&[100, 100, 100]));
    let mover = {
        let s = s.clone();
        std::thread::spawn(move || {
            for i in 0..4000usize {
                let _ = s.transfer(i % 3, (i + 1) % 3, 1);
            }
        })
    };
    let s2 = s.clone();
    finish_within(20, move || {
        for _ in 0..500 {
            assert_eq!(s2.total(), 300, "a total taken in the middle of a transfer saw the amount in neither slot");
        }
    });
    mover.join().unwrap();
}
''')))
