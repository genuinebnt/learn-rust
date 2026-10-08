//! Port of `src/include/common/rwlatch.h`. BusTub's `ReaderWriterLatch` has `RLock/RUnlock/WLock/WUnlock` over a `std::shared_mutex`.
//! In Rust the lock and unlock are one guard, and the latch owns what it protects.

use std::sync::{PoisonError, RwLock, RwLockReadGuard, RwLockWriteGuard};

/// Many readers or one writer.
pub struct ReaderWriterLatch<T> {
    inner: RwLock<T>,
}

impl<T> ReaderWriterLatch<T> {
    pub fn new(value: T) -> ReaderWriterLatch<T> {
        ReaderWriterLatch { inner: RwLock::new(value) }
    }

    /// Takes a read latch (BusTub's `RLock`); it is released when the guard is dropped (`RUnlock`).
    pub fn read(&self) -> RwLockReadGuard<'_, T> {
        todo!("1b-03: take the read lock; a poisoned lock still gives its guard (see the notes)")
    }

    /// Takes the write latch (BusTub's `WLock`); it is released when the guard is dropped (`WUnlock`).
    pub fn write(&self) -> RwLockWriteGuard<'_, T> {
        todo!("1b-03: take the write lock; a poisoned lock still gives its guard")
    }
}
