//! Port of `src/storage/page/page_guard.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database Group).
//!
//! A page guard is an RAII handle on a page in the buffer pool. While it exists the page is **pinned** (it can't be evicted) and
//! **latched** (shared for a `ReadPageGuard`, exclusive for a `WritePageGuard`). When it is dropped, in that order, the page is
//! unlatched and then unpinned, so a caller can't forget either, even on an early `return`, `?` or panic.

use std::ops::{Deref, DerefMut};
use std::sync::{RwLockReadGuard, RwLockWriteGuard};

use crate::buffer::buffer_pool_manager::BufferPoolManager;
use crate::common::config::{FrameId, PageData, PageId};

/// Shared access to a page. Many readers may hold one for the same page at once.
pub struct ReadPageGuard<'a> {
    bpm: &'a BufferPoolManager,
    page_id: PageId,
    frame: FrameId,
    /// `None` once the guard has been released.
    latch: Option<RwLockReadGuard<'a, Box<PageData>>>,
}

impl<'a> ReadPageGuard<'a> {
    /// Only the buffer pool makes guards: the page must already be pinned and its frame latched.
    pub(crate) fn new(bpm: &'a BufferPoolManager, page_id: PageId, frame: FrameId, latch: RwLockReadGuard<'a, Box<PageData>>) -> ReadPageGuard<'a> {
        ReadPageGuard { bpm, page_id, frame, latch: Some(latch) }
    }

    pub fn get_page_id(&self) -> PageId {
        self.page_id
    }

    /// The page's bytes. Panics if the guard has been released.
    pub fn get_data(&self) -> &PageData {
        todo!("1g-01: the bytes behind the read latch you are holding (panic if the guard was released)")
    }

    /// Writes the page to disk now. The guard keeps its pin and latch.
    pub fn flush(&mut self) {
        todo!("1g-01: write the bytes you hold to disk, without taking the frame latch again (you already hold it)")
    }

    /// Unlatches and unpins the page. Does nothing if the guard was already released. (BusTub's `Drop()`; in Rust `drop(guard)`
    /// also works, but it moves the guard, so there is no "drop it twice"; this is the idempotent form.)
    pub fn release(&mut self) {
        todo!("1g-01: if the guard still holds its latch: release the latch, then unpin the page; a second call does nothing")
    }
}

impl Deref for ReadPageGuard<'_> {
    type Target = PageData;
    fn deref(&self) -> &PageData {
        self.get_data()
    }
}

impl Drop for ReadPageGuard<'_> {
    fn drop(&mut self) {
        // TODO(1g-01): dropping a guard releases it
    }
}

/// Exclusive access to a page. Taking `get_data_mut` marks the page dirty, so the pool writes it back before reusing its frame.
pub struct WritePageGuard<'a> {
    bpm: &'a BufferPoolManager,
    page_id: PageId,
    frame: FrameId,
    latch: Option<RwLockWriteGuard<'a, Box<PageData>>>,
    is_dirty: bool,
}

impl<'a> WritePageGuard<'a> {
    pub(crate) fn new(bpm: &'a BufferPoolManager, page_id: PageId, frame: FrameId, latch: RwLockWriteGuard<'a, Box<PageData>>) -> WritePageGuard<'a> {
        WritePageGuard { bpm, page_id, frame, latch: Some(latch), is_dirty: false }
    }

    pub fn get_page_id(&self) -> PageId {
        self.page_id
    }

    pub fn get_data(&self) -> &PageData {
        todo!("1g-01: the bytes behind the write latch")
    }

    /// The page's bytes for modification. Marks the page dirty.
    pub fn get_data_mut(&mut self) -> &mut PageData {
        todo!("1g-01: remember that the page is dirty, then hand out the bytes mutably")
    }

    /// True if `get_data_mut` was called since the last flush.
    pub fn is_dirty(&self) -> bool {
        self.is_dirty
    }

    /// Writes the page to disk now, keeping the pin and the latch, and marks it clean.
    pub fn flush(&mut self) {
        todo!("1g-01: write the bytes you hold to disk, without taking the frame latch again; the page is now clean")
    }

    pub fn release(&mut self) {
        todo!("1g-01: if the guard still holds its latch: release it, then unpin the page, passing on whether it was dirtied; a second call does nothing")
    }
}

impl Deref for WritePageGuard<'_> {
    type Target = PageData;
    fn deref(&self) -> &PageData {
        self.get_data()
    }
}

impl DerefMut for WritePageGuard<'_> {
    fn deref_mut(&mut self) -> &mut PageData {
        self.get_data_mut()
    }
}

impl Drop for WritePageGuard<'_> {
    fn drop(&mut self) {
        // TODO(1g-01): dropping a guard releases it
    }
}
