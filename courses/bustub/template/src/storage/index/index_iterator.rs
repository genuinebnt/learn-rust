//! Port of `src/storage/index/index_iterator.cpp`: a range scan over the leaves of a B+ tree. It remembers a position (a leaf page
//! and a slot in it) and, when asked for the next pair, latches the leaf just long enough to copy the pair out. Nothing stays
//! latched between calls, so a scan never blocks writers for longer than one read (the price: a scan that races with a writer may
//! see the tree change under it, which BusTub's own iterator allows too).
//!
//! BusTub's iterator is a C++ iterator (`*it`, `++it`, `it != tree.End()`); Rust's is the `Iterator` trait (`for (k, v) in tree.begin()`),
//! and [`IndexIterator::is_end`] and `==` are there for the tests that spell it the C++ way.

use std::marker::PhantomData;

use crate::buffer::buffer_pool_manager::BufferPoolManager;
use crate::common::config::PageId;
use crate::storage::index::fixed_size::FixedSize;
use crate::storage::page::b_plus_tree_leaf_page::BPlusTreeLeafPage;

pub struct IndexIterator<'a, K, V, const TOMBS: usize = 0> {
    bpm: &'a BufferPoolManager,
    /// The leaf holding the current pair; `None` once the scan is past the last pair (the end).
    page_id: Option<PageId>,
    /// The slot of the current pair in that leaf. Always a real slot unless `page_id` is `None`.
    index: u32,
    _entry: PhantomData<(K, V)>,
}

impl<'a, K: FixedSize + Clone, V: FixedSize + Clone, const TOMBS: usize> IndexIterator<'a, K, V, TOMBS> {
    /// The end: past the last pair of the last leaf.
    pub fn end(bpm: &'a BufferPoolManager) -> IndexIterator<'a, K, V, TOMBS> {
        todo!("2c-06: an iterator with no leaf")
    }

    /// An iterator at slot `index` of leaf `page_id`, moved forward to the first slot that exists if `index` is past the leaf's end
    /// (the next leaf's first pair, and so on; the end if there are none). The tree creates iterators with this.
    pub fn at(bpm: &'a BufferPoolManager, page_id: PageId, index: u32) -> IndexIterator<'a, K, V, TOMBS> {
        todo!("2c-06: remember the position, then move on to the next leaf while the slot is past the end of its leaf")
    }

    /// While the position is past the last pair of its leaf, move to the first slot of the next leaf (or to the end).
    fn skip_past_the_end_of_leaves(&mut self) {
        todo!("2c-06: latch the leaf; if the slot exists, stop; otherwise continue at slot 0 of the next leaf, or become the end")
    }

    pub fn is_end(&self) -> bool {
        todo!("2c-06: there is no leaf to read from")
    }
}

impl<K: FixedSize + Clone, V: FixedSize + Clone, const TOMBS: usize> Iterator for IndexIterator<'_, K, V, TOMBS> {
    type Item = (K, V);

    /// The current pair, and move to the next one.
    fn next(&mut self) -> Option<(K, V)> {
        todo!("2c-06: copy the pair at the current position out of its leaf (latch, read, unlatch), advance, and return the pair; None at the end")
    }
}

/// Two iterators are equal when they are at the same place. (BusTub: `operator==`.)
impl<K, V, const TOMBS: usize> PartialEq for IndexIterator<'_, K, V, TOMBS> {
    fn eq(&self, other: &Self) -> bool {
        todo!("2c-06: the same leaf and the same slot")
    }
}
