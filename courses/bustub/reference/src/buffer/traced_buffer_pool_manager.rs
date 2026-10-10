//! Port of `src/include/buffer/traced_buffer_pool_manager.h`: a thin wrapper around the buffer pool that counts how many pages
//! the index latched for reading and for writing. BusTub's B+ tree keeps one (`bpm_`) so tests can check that an insert which does
//! not split touches the disk-resident tree with a single write latch (an *optimistic* insert). Not part of any stage: nothing here
//! for you to write.

use std::sync::atomic::{AtomicUsize, Ordering};

use super::buffer_pool_manager::BufferPoolManager;
use crate::common::config::PageId;
use crate::storage::page::page_guard::{ReadPageGuard, WritePageGuard};

pub struct TracedBufferPoolManager<'a> {
    bpm: &'a BufferPoolManager,
    reads: AtomicUsize,
    writes: AtomicUsize,
}

impl<'a> TracedBufferPoolManager<'a> {
    pub fn new(bpm: &'a BufferPoolManager) -> TracedBufferPoolManager<'a> {
        TracedBufferPoolManager { bpm, reads: AtomicUsize::new(0), writes: AtomicUsize::new(0) }
    }

    /// The buffer pool underneath, for calls that are not counted.
    pub fn inner(&self) -> &'a BufferPoolManager {
        self.bpm
    }

    pub fn new_page(&self) -> PageId {
        self.bpm.new_page()
    }

    pub fn delete_page(&self, page_id: PageId) -> bool {
        self.bpm.delete_page(page_id)
    }

    /// Latches `page_id` for reading, and counts it.
    pub fn read_page(&self, page_id: PageId) -> ReadPageGuard<'a> {
        self.reads.fetch_add(1, Ordering::Relaxed);
        self.bpm.read_page(page_id)
    }

    /// Latches `page_id` for writing, and counts it.
    pub fn write_page(&self, page_id: PageId) -> WritePageGuard<'a> {
        self.writes.fetch_add(1, Ordering::Relaxed);
        self.bpm.write_page(page_id)
    }

    pub fn get_reads(&self) -> usize {
        self.reads.load(Ordering::Relaxed)
    }

    pub fn get_writes(&self) -> usize {
        self.writes.load(Ordering::Relaxed)
    }
}
