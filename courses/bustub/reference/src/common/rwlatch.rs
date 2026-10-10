//! Port of `src/include/common/rwlatch.h`. BusTub's `ReaderWriterLatch` has `RLock/RUnlock/WLock/WUnlock` over a `std::shared_mutex`.
//! In Rust the lock and unlock are one guard, and the latch owns what it protects.

use std::sync::{RwLockReadGuard, RwLockWriteGuard};

// @begin 1b-05
use std::sync::{PoisonError, RwLock};
//~ // TODO(1b-05): your imports go here.
// @end

/// Many readers or one writer.
pub struct ReaderWriterLatch<T> {
    // @begin 1b-05
    inner: RwLock<T>,
    //~ // TODO(1b-05): the field is yours (the guards below are std's, so wrapping a `std::sync::RwLock` is the natural design).
    //~ _value: std::marker::PhantomData<T>, // delete this line once a field mentions T
    // @end
}

impl<T> ReaderWriterLatch<T> {
    /// A latch protecting `value`.
    pub fn new(value: T) -> ReaderWriterLatch<T> {
        // @begin 1b-05
        ReaderWriterLatch { inner: RwLock::new(value) }
        //~ todo!("1b-05: a latch around the value")
        // @end
    }

    /// Takes a read latch (BusTub's `RLock`); it is released when the guard is dropped (`RUnlock`). Any number of readers may
    /// hold it together, and none while a writer does. A latch whose holder panicked still works.
    pub fn read(&self) -> RwLockReadGuard<'_, T> {
        // @begin 1b-05
        self.inner.read().unwrap_or_else(PoisonError::into_inner)
        //~ todo!("1b-05: take the read latch; a poisoned lock still gives its guard (see the notes)")
        // @end
    }

    /// Takes the write latch (BusTub's `WLock`); it is released when the guard is dropped (`WUnlock`). Only one writer, and no
    /// readers, at a time.
    pub fn write(&self) -> RwLockWriteGuard<'_, T> {
        // @begin 1b-05
        self.inner.write().unwrap_or_else(PoisonError::into_inner)
        //~ todo!("1b-05: take the write latch; a poisoned lock still gives its guard")
        // @end
    }
}
