//! Port of `src/storage/page/b_plus_tree_internal_page.cpp`: a B+ tree's inner node. It stores `n` children and `n - 1` keys that
//! separate them. Child `i` covers the keys `K` with `key(i) <= K < key(i + 1)`. BusTub keeps the keys and the child ids in two
//! parallel arrays and leaves `key(0)` unused; this port stores `(key, child)` pairs side by side, which is the same information
//! in one array (so one `PageArray`, one shift when inserting).
//!
//! ```text
//! | page_type u32 | size u32 | max_size u32 | (key0 unused, child0) | (key1, child1) | ... | (key n-1, child n-1) |
//! ```
//! `size` counts children. A search ignores `key(0)`.

use std::marker::PhantomData;

use super::b_plus_tree_page::*;
use super::page_array::PageArray;
use crate::common::config::PageId;
use crate::storage::index::fixed_size::{array_size, FixedSize};
use crate::storage::index::generic_key::KeyComparator;

pub struct BPlusTreeInternalPage<B, K> {
    page: B,
    _key: PhantomData<K>,
}

impl<B, K> BPlusTreeInternalPage<B, K> {
    pub fn new(page: B) -> BPlusTreeInternalPage<B, K> {
        BPlusTreeInternalPage { page, _key: PhantomData }
    }
}

impl<B: AsRef<[u8]>, K: FixedSize> BPlusTreeInternalPage<B, K> {
    /// How many `(key, child)` pairs fit in a page. BusTub's `INTERNAL_PAGE_SLOT_CNT`.
    pub fn capacity() -> usize {
        todo!("2c-01: the space after the 12-byte header divided by the size of a (key, page id) pair")
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

    fn entries(&self) -> PageArray<&[u8], (K, PageId)> {
        PageArray::new(&self.page.as_ref()[INTERNAL_PAGE_HEADER_SIZE..])
    }

    /// The pair in slot `index` (slot 0's key is meaningless). Panics past `size`.
    pub fn entry_at(&self, index: u32) -> (K, PageId) {
        todo!("2c-01: panic past size; otherwise decode the pair in that slot (a PageArray over the bytes after the header does it)")
    }

    pub fn key_at(&self, index: u32) -> K {
        todo!("2c-01: the key of entry_at")
    }

    pub fn value_at(&self, index: u32) -> PageId {
        todo!("2c-01: the child of entry_at")
    }

    /// The slot holding child `value`, if any. BusTub's `ValueIndex` (it returns -1 when missing).
    pub fn value_index(&self, value: PageId) -> Option<u32> {
        todo!("2c-01: look through the children for this page id")
    }

    /// The child to follow when searching for `key`: the child `i` with `key(i) <= key < key(i + 1)`, i.e. the last slot whose key is
    /// at most `key` (slot 0 if there is none). The keys of slots `1..size` are sorted; slot 0's key is not looked at.
    pub fn child_for(&self, key: &K, cmp: &impl KeyComparator<K>) -> PageId {
        todo!("2c-02: binary search the keys of slots 1..size for the first one greater than `key` (PageArray::lower_bound on the slice after slot 0 does it); the child just before it is the answer")
    }
}

impl<B: AsRef<[u8]> + AsMut<[u8]>, K: FixedSize> BPlusTreeInternalPage<B, K> {
    /// Formats a fresh page: an internal page with no children, holding at most `max_size`.
    pub fn init(&mut self, max_size: u32) {
        todo!("2c-01: type Internal, size 0, the given max size (not more than fits)")
    }

    pub fn set_size(&mut self, size: u32) {
        BPlusTreePage::new(self.page.as_mut()).set_size(size);
    }

    fn entries_mut(&mut self) -> PageArray<&mut [u8], (K, PageId)> {
        PageArray::new(&mut self.page.as_mut()[INTERNAL_PAGE_HEADER_SIZE..])
    }

    /// Stores the pair in slot `index`. It does not change the size.
    pub fn set_entry_at(&mut self, index: u32, key: &K, value: PageId)
    where
        K: Clone,
    {
        todo!("2c-01: encode the pair into slot `index`")
    }

    pub fn set_key_at(&mut self, index: u32, key: &K)
    where
        K: Clone,
    {
        todo!("2c-01: replace the key of slot `index`, keeping its child")
    }

    pub fn set_value_at(&mut self, index: u32, value: PageId)
    where
        K: Clone,
    {
        todo!("2c-01: replace the child of slot `index`, keeping its key")
    }

    /// Adds the pair `(key, child)` where it belongs: after the last key that is at most `key`. The new key is the lower bound of
    /// `child`, which therefore sits to the right of the child that was split. Panics if the page is full or `key` is already there.
    pub fn insert_child(&mut self, key: &K, child: PageId, cmp: &impl KeyComparator<K>)
    where
        K: Clone,
    {
        todo!("2c-04: find where `key` belongs among the keys of slots 1..size, shift the later pairs right (PageArray::insert_at) and count one more")
    }

    /// Removes the pair in slot `index`, shifting the later ones down. Removing slot 0 makes the next pair slot 0, so its key
    /// becomes the unused one.
    pub fn remove_at(&mut self, index: u32) {
        todo!("2c-07: shift the later pairs down (PageArray::remove_at) and count one fewer")
    }

    /// Adds a pair at the front, shifting the others right: the new pair becomes slot 0 (its key is the unused one). Used when an
    /// internal page borrows a child from its left neighbour.
    pub fn insert_at_front(&mut self, key: &K, child: PageId)
    where
        K: Clone,
    {
        todo!("2c-07: insert at slot 0 (PageArray::insert_at) and count one more")
    }
}
