//! An iterator that can go back to a marked position.

use std::collections::VecDeque;

pub struct Rewindable<I: Iterator> {
    _rewind: std::marker::PhantomData<I>,
}

impl<I: Iterator> Rewindable<I>
where
    I::Item: Clone,
{
    pub fn new(inner: I) -> Rewindable<I> {
        todo!("3e-c5: wrap the iterator, nothing marked")
    }

    pub fn mark(&mut self) {
        todo!("3e-c5: forget what was read before this point, keep what is yet to be replayed")
    }

    pub fn reset(&mut self) {
        todo!("3e-c5: replay everything since the mark")
    }

    /// How many items are being held for a possible reset.
    pub fn buffered(&self) -> usize {
        todo!("3e-c5: how many items are kept")
    }
}

impl<I: Iterator> Iterator for Rewindable<I>
where
    I::Item: Clone,
{
    type Item = I::Item;

    fn next(&mut self) -> Option<I::Item> {
        todo!("3e-c5: replayed items first, then the underlying iterator (keeping what is read since the mark)")
    }
}
