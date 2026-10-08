//! Port of `src/storage/page/b_plus_tree_leaf_page.cpp`: a B+ tree's leaf. It holds the actual `(key, value)` pairs, sorted by
//! key, and the page id of the next leaf, so a scan can walk the bottom of the tree like a linked list. Keys are unique.
//! (BusTub's leaf also has a tombstone buffer; the course adds it in module 2d.)
//!
//! ```text
//! | page_type u32 | size u32 | max_size u32 | next_page_id i32 | (key, value) | (key, value) | ... |
//! ```

use std::cmp::Ordering;
use std::marker::PhantomData;

use super::b_plus_tree_page::*;
use super::page_array::PageArray;
use super::page_bytes::*;
use crate::common::config::PageId;
use crate::storage::index::fixed_size::{array_size, FixedSize};
use crate::storage::index::generic_key::KeyComparator;

const NEXT_PAGE_ID_OFFSET: usize = 12;

pub struct BPlusTreeLeafPage<B, K, V> {
    page: B,
    _entry: PhantomData<(K, V)>,
}

impl<B, K, V> BPlusTreeLeafPage<B, K, V> {
    pub fn new(page: B) -> BPlusTreeLeafPage<B, K, V> {
        BPlusTreeLeafPage { page, _entry: PhantomData }
    }
}

impl<B: AsRef<[u8]>, K: FixedSize, V: FixedSize> BPlusTreeLeafPage<B, K, V> {
    /// How many pairs fit in a leaf. BusTub's `LEAF_PAGE_SLOT_CNT`.
    pub fn capacity() -> usize {
        todo!("2c-01: the space after the 16-byte header divided by the size of a (key, value) pair")
    }

    pub fn size(&self) -> u32 {
        BPlusTreePage::new(self.page.as_ref()).size()
    }

    pub fn max_size(&self) -> u32 {
        BPlusTreePage::new(self.page.as_ref()).max_size()
    }

    pub fn min_size(&self) -> u32 {
        BPlusTreePage::new(self.page.as_ref()).min_size()
    }

    /// The next leaf to the right, or `None` for the last leaf.
    pub fn next_page_id(&self) -> Option<PageId> {
        todo!("2c-01: the id stored in the header (read_optional_page_id turns INVALID into None)")
    }

    fn entries(&self) -> PageArray<&[u8], (K, V)> {
        PageArray::new(&self.page.as_ref()[LEAF_PAGE_HEADER_SIZE..])
    }

    /// The pair in slot `index`. Panics past `size`.
    pub fn entry_at(&self, index: u32) -> (K, V) {
        todo!("2c-01: panic past size; otherwise decode the pair in that slot")
    }

    pub fn key_at(&self, index: u32) -> K {
        todo!("2c-01: the key of entry_at")
    }

    pub fn value_at(&self, index: u32) -> V {
        todo!("2c-01: the value of entry_at")
    }

    /// The first slot whose key is not less than `key`; `size` if every key is less.
    pub fn lower_bound(&self, key: &K, cmp: &impl KeyComparator<K>) -> u32 {
        todo!("2c-02: binary search the sorted keys (PageArray::lower_bound)")
    }

    /// The value stored for `key`, if any.
    pub fn lookup(&self, key: &K, cmp: &impl KeyComparator<K>) -> Option<V> {
        todo!("2c-02: find the first key not less than the target; it is a hit only if it is equal")
    }
}

impl<B: AsRef<[u8]> + AsMut<[u8]>, K: FixedSize, V: FixedSize> BPlusTreeLeafPage<B, K, V> {
    /// Formats a fresh page: a leaf with no pairs and no next leaf, holding at most `max_size` (not more than fits).
    pub fn init(&mut self, max_size: u32) {
        todo!("2c-01: type Leaf, size 0, the given max size (not more than fits), no next leaf")
    }

    pub fn set_size(&mut self, size: u32) {
        BPlusTreePage::new(self.page.as_mut()).set_size(size);
    }

    pub fn set_next_page_id(&mut self, next: Option<PageId>) {
        todo!("2c-01: store the id (write_optional_page_id stores INVALID for None)")
    }

    fn entries_mut(&mut self) -> PageArray<&mut [u8], (K, V)> {
        PageArray::new(&mut self.page.as_mut()[LEAF_PAGE_HEADER_SIZE..])
    }

    /// Stores the pair in slot `index`. It does not change the size.
    pub fn set_entry_at(&mut self, index: u32, key: &K, value: &V)
    where
        K: Clone,
        V: Clone,
    {
        todo!("2c-01: encode the pair into slot `index`")
    }

    /// Adds the pair in key order. `false` (and nothing changes) if `key` is already in the page. Panics if the page has no room
    /// (a tree splits a leaf the moment it reaches `max_size`, so it always has room for one more).
    pub fn insert(&mut self, key: &K, value: &V, cmp: &impl KeyComparator<K>) -> bool
    where
        K: Clone,
        V: Clone,
    {
        todo!("2c-03: find the slot with lower_bound; refuse an equal key; otherwise shift the later pairs right (PageArray::insert_at) and count one more")
    }

    /// Removes the pair for `key`, keeping the order. `false` if there is none.
    pub fn remove(&mut self, key: &K, cmp: &impl KeyComparator<K>) -> bool {
        todo!("2c-07: find the slot with lower_bound; if the key is there, shift the later pairs left (PageArray::remove_at) and count one fewer")
    }

    /// Removes the pair in slot `index`, keeping the order.
    pub fn remove_at(&mut self, index: u32) {
        todo!("2c-07: shift the later pairs left and count one fewer")
    }

    /// Adds the pair at the front, shifting the others right. Used when a leaf borrows from its left neighbour.
    pub fn insert_at_front(&mut self, key: &K, value: &V)
    where
        K: Clone,
        V: Clone,
    {
        todo!("2c-07: insert at slot 0 and count one more")
    }
}
