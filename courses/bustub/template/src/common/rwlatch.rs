//! Port of `src/include/common/rwlatch.h`. BusTub's `ReaderWriterLatch` has `RLock/RUnlock/WLock/WUnlock` over a `std::shared_mutex`.
//! In Rust the lock and unlock are one guard, and the latch owns what it protects.

use std::sync::{RwLockReadGuard, RwLockWriteGuard};

// TODO(1b-05): your imports go here.

/// Many readers or one writer.
pub struct ReaderWriterLatch<T> {
    // TODO(1b-05): the field is yours (the guards below are std's, so wrapping a `std::sync::RwLock` is the natural design).
    _value: std::marker::PhantomData<T>, // delete this line once a field mentions T
}

impl<T> ReaderWriterLatch<T> {
    /// A latch protecting `value`.
    pub fn new(value: T) -> ReaderWriterLatch<T> {
        todo!("1b-05: a latch around the value")
    }

    /// Takes a read latch (BusTub's `RLock`); it is released when the guard is dropped (`RUnlock`). Any number of readers may
    /// hold it together, and none while a writer does. A latch whose holder panicked still works.
    pub fn read(&self) -> RwLockReadGuard<'_, T> {
        todo!("1b-05: take the read latch; a poisoned lock still gives its guard (see the notes)")
    }

    /// Takes the write latch (BusTub's `WLock`); it is released when the guard is dropped (`WUnlock`). Only one writer, and no
    /// readers, at a time.
    pub fn write(&self) -> RwLockWriteGuard<'_, T> {
        todo!("1b-05: take the write latch; a poisoned lock still gives its guard")
    }
}
