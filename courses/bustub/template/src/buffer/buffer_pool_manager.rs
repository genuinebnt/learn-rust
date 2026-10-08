//! Port of `src/buffer/buffer_pool_manager.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database Group).
//!
//! The buffer pool keeps a fixed number of pages in memory. A page is read from disk into a **frame** when it is first needed;
//! callers **pin** a page while they use it, so it can't be taken away; when a frame is needed and none is free, the
//! replacer picks a page nobody has pinned, which is written back first if it was modified.
//!
//! This module has the textbook interface (`fetch_page` / `unpin_page`, as in BusTub's earlier years). The next module wraps it in
//! RAII page guards, the interface BusTub's current tests use.

use std::collections::HashMap;
use std::sync::{Arc, Mutex, RwLock};

use super::arc_replacer::ArcReplacer;
use crate::common::config::{FrameId, PageData, PageId, BUSTUB_PAGE_SIZE};
use crate::storage::disk::disk_manager::DiskIo;
use crate::storage::disk::disk_scheduler::{DiskRequest, DiskScheduler};
use crate::storage::page::page_guard::{ReadPageGuard, WritePageGuard};

/// What the pool knows about a frame besides its bytes.
struct FrameMeta {
    /// The page the frame holds, if any.
    page_id: Option<PageId>,
    /// How many users have the page pinned.
    pin_count: usize,
    /// True if the bytes differ from the page on disk.
    dirty: bool,
}

/// Everything the pool's latch protects (BusTub's `bpm_latch_`).
struct Inner {
    /// Which frame holds each resident page.
    page_table: HashMap<PageId, FrameId>,
    /// Frames that hold no page.
    free_frames: Vec<FrameId>,
    meta: Vec<FrameMeta>,
    replacer: ArcReplacer,
    /// The id the next `new_page` hands out.
    next_page_id: i32,
}

pub struct BufferPoolManager {
    num_frames: usize,
    /// The memory itself: one 8 KiB buffer per frame, each behind its own reader-writer latch.
    frames: Vec<RwLock<Box<PageData>>>,
    inner: Mutex<Inner>,
    disk_scheduler: DiskScheduler,
}

impl BufferPoolManager {
    /// A pool of `num_frames` frames, all free, on top of `disk`.
    pub fn new(num_frames: usize, disk: Arc<dyn DiskIo>) -> BufferPoolManager {
        todo!("1f-01: the frames and their metadata, every frame on the free list, an empty page table, a replacer for num_frames frames, and a disk scheduler")
    }

    /// The number of frames.
    pub fn size(&self) -> usize {
        todo!("1f-01: the number of frames")
    }

    /// The bytes of a frame, behind its latch. Only meaningful for a frame you have pinned.
    pub fn frame_data(&self, frame: FrameId) -> &RwLock<Box<PageData>> {
        &self.frames[frame.0]
    }

    /// Hands out a fresh page id. The page isn't in memory or on disk yet; `fetch_page` brings it in (all zeros, since the disk
    /// has never seen it).
    pub fn new_page(&self) -> PageId {
        todo!("1f-01: the next id, 0, 1, 2, ...; no two callers may get the same one")
    }

    /// Reads a page from disk into `frame`. The caller holds the pool's latch and has the frame to itself.
    fn load(&self, page_id: PageId, frame: FrameId) {
        todo!("1f-01: schedule a read request, wait for the future, copy the bytes into the frame")
    }

    /// Writes the bytes of `frame` to disk as page `page_id`. The caller holds the pool's latch; nobody has the frame latched.
    fn store(&self, page_id: PageId, frame: FrameId) {
        todo!("1f-03: copy the frame's bytes into a Box, schedule a write request, wait for it")
    }

    /// Pins `page_id`, bringing it into memory if needed, and returns its frame. `None` if every frame is pinned.
    /// Each successful call must be matched by an `unpin_page`.
    pub fn fetch_page(&self, page_id: PageId) -> Option<FrameId> {
        todo!("1f-01: a page not in memory goes into a free frame: read it from disk, pin it once, note it in the page table and the replacer")
    }

    /// Releases one pin. `is_dirty` says the caller modified the page. `false` if the page isn't in memory or wasn't pinned.
    pub fn unpin_page(&self, page_id: PageId, is_dirty: bool) -> bool {
        todo!("1f-02: drop one pin; remember the dirt; when the last pin goes, the frame may be evicted")
    }

    /// The page's pin count, or `None` if the page isn't in memory.
    pub fn get_pin_count(&self, page_id: PageId) -> Option<usize> {
        todo!("1f-02: the pin count of the frame holding the page, if there is one")
    }

    /// Writes the page to disk (whether or not it is dirty) and clears its dirty flag. `false` if it isn't in memory.
    pub fn flush_page(&self, page_id: PageId) -> bool {
        todo!("1f-03: write the page out and mark it clean")
    }

    /// Flushes every page in memory.
    pub fn flush_all_pages(&self) {
        todo!("1f-03: flush every resident page")
    }

    /// Removes the page from memory and frees its disk space. `false` if somebody has it pinned; `true` otherwise (also when it
    /// wasn't in memory). A dirty page is simply dropped: it is being deleted.
    pub fn delete_page(&self, page_id: PageId) -> bool {
        todo!("1f-03: refuse if pinned; otherwise take the page out of the page table and the replacer, free its frame, and tell the disk")
    }

    /// Pins `page_id` and takes its read latch. `None` if every frame is pinned.
    pub fn checked_read_page(&self, page_id: PageId) -> Option<ReadPageGuard<'_>> {
        todo!("1g-01: pin the page (fetch_page), then take the frame's read latch, then build the guard")
    }

    /// Pins `page_id` and takes its write latch. `None` if every frame is pinned.
    pub fn checked_write_page(&self, page_id: PageId) -> Option<WritePageGuard<'_>> {
        todo!("1g-01: like checked_read_page, with the write latch")
    }

    /// Like `checked_read_page`, but panics if the page can't be brought in.
    pub fn read_page(&self, page_id: PageId) -> ReadPageGuard<'_> {
        todo!("1g-02: checked_read_page, but a failure is a panic")
    }

    /// Like `checked_write_page`, but panics if the page can't be brought in.
    pub fn write_page(&self, page_id: PageId) -> WritePageGuard<'_> {
        todo!("1g-02: checked_write_page, but a failure is a panic")
    }

    /// Writes `data` to disk as page `page_id` without touching the pool's state. For guards that already hold the page's latch.
    pub fn write_page_data(&self, page_id: PageId, data: &PageData) {
        todo!("1g-02: copy the bytes into a Box, schedule a write, wait for it; no locks needed")
    }
}
