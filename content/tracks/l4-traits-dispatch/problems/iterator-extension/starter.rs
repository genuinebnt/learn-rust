use std::collections::HashMap;
use std::hash::Hash;

/// Extra adapters for every iterator.
pub trait IterExt: Iterator + Sized {
    /// Items 0, n, 2n, ... Panics if `n` is 0.
    fn every_nth(self, n: usize) -> EveryNth<Self> {
        todo!()
    }

    /// Drops each item equal to the item just before it.
    fn dedup_adjacent(self) -> DedupAdjacent<Self>
    where
        Self::Item: PartialEq + Clone,
    {
        todo!()
    }

    /// How many times each item occurs.
    fn counts(self) -> HashMap<Self::Item, usize>
    where
        Self::Item: Eq + Hash,
    {
        todo!()
    }
}

impl<I: Iterator> IterExt for I {}

pub struct EveryNth<I> {
    iter: I,
    // TODO: more fields
}

impl<I: Iterator> Iterator for EveryNth<I> {
    type Item = I::Item;

    fn next(&mut self) -> Option<I::Item> {
        todo!()
    }
}

pub struct DedupAdjacent<I: Iterator> {
    iter: I,
    // TODO: more fields
}

impl<I> Iterator for DedupAdjacent<I>
where
    I: Iterator,
    I::Item: PartialEq + Clone,
{
    type Item = I::Item;

    fn next(&mut self) -> Option<I::Item> {
        todo!()
    }
}
