//! Port of `src/include/common/channel.h` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database Group).
//!
//! A multi-producer multi-consumer queue: `put` never blocks, `get` waits until there is something to get. The disk scheduler's
//! request queue, and the pattern behind every thread pool.

use std::collections::VecDeque;
use std::sync::{Condvar, Mutex};

pub struct Channel<T> {
    queue: Mutex<VecDeque<T>>,
    /// Signalled when an element is put; getters wait on it while the queue is empty.
    ready: Condvar,
}

impl<T> Channel<T> {
    pub fn new() -> Channel<T> {
        Channel { queue: Mutex::new(VecDeque::new()), ready: Condvar::new() }
    }

    /// How many elements are waiting.
    pub fn len(&self) -> usize {
        self.queue.lock().unwrap().len()
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    /// Adds an element at the back and wakes one getter. Never blocks.
    pub fn put(&self, element: T) {
        todo!("1b-01: push the element on the queue, then wake one waiting getter")
    }

    /// Takes the element at the front, waiting for one if the queue is empty.
    pub fn get(&self) -> T {
        todo!("1b-01: wait while the queue is empty, then pop the front")
    }
}

impl<T> Default for Channel<T> {
    fn default() -> Self {
        Self::new()
    }
}

/// The worker loop of the disk scheduler: BusTub stops a worker by putting `std::nullopt` in the queue, so the elements are
/// `Option<T>` and `None` means "stop". Calls `f` on each element until it gets a `None`, which it consumes.
pub fn consume<T>(channel: &Channel<Option<T>>, mut f: impl FnMut(T)) {
    todo!("1b-01: get elements and call f on each, until a None arrives")
}
