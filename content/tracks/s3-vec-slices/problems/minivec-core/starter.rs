use std::alloc::{self, Layout};
use std::marker::PhantomData;
use std::ptr::{self, NonNull};

/// A growable array on a raw allocation. Zero-sized `T` isn't supported.
pub struct MiniVec<T> {
    ptr: NonNull<T>,
    cap: usize,
    len: usize,
    _owns: PhantomData<T>,
}

impl<T> MiniVec<T> {
    pub fn new() -> Self {
        todo!()
    }

    pub fn len(&self) -> usize {
        todo!()
    }

    pub fn capacity(&self) -> usize {
        todo!()
    }

    pub fn push(&mut self, value: T) {
        todo!()
    }

    pub fn pop(&mut self) -> Option<T> {
        todo!()
    }

    pub fn get(&self, i: usize) -> Option<&T> {
        todo!()
    }
}

impl<T> Drop for MiniVec<T> {
    fn drop(&mut self) {
        // TODO: drop the remaining elements, then free the buffer.
        // (Left empty rather than todo!(): a panic in drop during a failing test aborts every test.)
    }
}
