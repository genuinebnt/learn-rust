//! Port of `src/storage/disk/disk_scheduler.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database Group).
//!
//! The disk scheduler runs disk reads and writes on a background thread. Callers hand it requests and wait on a future when they
//! need the result, so the buffer pool can start several I/Os and do other work meanwhile.

use std::io;
use std::panic::{catch_unwind, AssertUnwindSafe};
use std::sync::Arc;
use std::thread::JoinHandle;

use super::disk_manager::DiskIo;
use crate::common::channel::{consume, Channel};
use crate::common::config::{PageData, PageId, BUSTUB_PAGE_SIZE};
use crate::common::promise::{promise, Future, Promise};

/// What a finished request reports: the page buffer (the page read, or the page just written), or the I/O error.
pub type DiskResult = io::Result<Box<PageData>>;

/// One read or write of a page.
///
/// BusTub passes a `char *data` that the worker reads from or fills in, so the buffer is shared between two threads by convention.
/// Here the request **owns** the buffer: a write carries the page to write; a read carries an empty buffer to fill. Either way the
/// buffer comes back through the callback when the request is done.
pub struct DiskRequest {
    pub is_write: bool,
    pub data: Box<PageData>,
    pub page_id: PageId,
    /// Completed with the result when the request is done.
    pub callback: Promise<DiskResult>,
}

impl DiskRequest {
    /// A read of `page_id` into a zeroed buffer, and the future for its result.
    pub fn read(page_id: PageId) -> (DiskRequest, Future<DiskResult>) {
        todo!("1b-07: a promise/future pair, and a request with is_write false and a zeroed buffer")
    }

    /// A write of `data` as `page_id`, and the future for its result.
    pub fn write(page_id: PageId, data: Box<PageData>) -> (DiskRequest, Future<DiskResult>) {
        todo!("1b-07: a promise/future pair, and a request with is_write true carrying the data")
    }
}

/// Does the I/O of one request.
fn run(disk: &dyn DiskIo, is_write: bool, page_id: PageId, data: &mut PageData) -> io::Result<()> {
    todo!("1b-08: write_page when is_write, read_page (into data) otherwise")
}

/// Runs one request against `disk`, then completes its callback with the buffer on success, or with the error.
pub fn execute(disk: &dyn DiskIo, request: DiskRequest) {
    todo!("1b-08: do the I/O (run), then complete the callback: the buffer if it worked, the error if not")
}

/// Runs disk requests, one at a time and in the order they were scheduled, on one background thread.
pub struct DiskScheduler {
    disk: Arc<dyn DiskIo>,
    /// `None` is the stop signal (BusTub's `std::nullopt`).
    request_queue: Arc<Channel<Option<DiskRequest>>>,
    background_thread: Option<JoinHandle<()>>,
}

impl DiskScheduler {
    /// Starts the worker thread.
    pub fn new(disk: Arc<dyn DiskIo>) -> DiskScheduler {
        todo!("1b-09: create the queue, spawn the worker (consume the queue, execute each request on the disk), build the scheduler")
    }

    /// Queues the requests, in order. Returns at once; the futures say when they are done.
    pub fn schedule(&self, requests: Vec<DiskRequest>) {
        todo!("1b-09: put each request on the queue, in order")
    }

    /// A promise and its future for a request's callback. (BusTub's `CreatePromise()`.)
    pub fn create_promise(&self) -> (Promise<DiskResult>, Future<DiskResult>) {
        todo!("1b-12: a fresh promise/future pair")
    }

    /// Frees a page on the disk. (BusTub's `DeallocatePage()`.)
    pub fn deallocate_page(&self, page_id: PageId) {
        todo!("1b-12: ask the disk to delete the page")
    }
}

impl Drop for DiskScheduler {
    /// Stops the worker after it has finished everything already scheduled, and waits for it.
    fn drop(&mut self) {
        // TODO(1b-10): put the stop signal in the queue, then join the worker thread
    }
}

/// A scheduler with several workers that still runs the requests for each page in order: requests for page `p` go to worker
/// `p % workers`, so two requests for the same page can never overtake each other, and requests for different pages overlap.
pub struct ShardedDiskScheduler {
    queues: Vec<Arc<Channel<Option<DiskRequest>>>>,
    workers: Vec<JoinHandle<()>>,
}

impl ShardedDiskScheduler {
    pub fn new(disk: Arc<dyn DiskIo>, workers: usize) -> ShardedDiskScheduler {
        todo!("1b-14: one queue and one worker thread per worker, like DiskScheduler::new but `workers` times")
    }

    pub fn schedule(&self, requests: Vec<DiskRequest>) {
        todo!("1b-14: put each request on the queue of its page's shard (page id modulo the number of workers)")
    }
}

impl Drop for ShardedDiskScheduler {
    fn drop(&mut self) {
        // TODO(1b-14): stop and join every worker
    }
}
