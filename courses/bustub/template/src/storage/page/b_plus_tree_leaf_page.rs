//! Port of `src/storage/page/b_plus_tree_leaf_page.cpp`: a B+ tree's leaf. It holds the actual `(key, value)` pairs, sorted by
//! key, and the page id of the next leaf, so a scan can walk the bottom of the tree like a linked list. Keys are unique.
//!
//! ```text
//! | page_type u32 | size u32 | max_size u32 | next_page_id i32 | (key, value) | (key, value) | ... |
//! ```
//! With `TOMBS > 0` (BusTub's `NumTombs`) a **tombstone buffer** sits between the header and the entries: a pair that is "deleted"
//! stays in the page and its key is noted in the buffer, so the delete shifts nothing; the buffer holds the last `TOMBS` such keys,
//! oldest first, and when it is full the oldest pair is really removed to make room (module 2d).
//!
//! ```text
//! | header (16) | num_tombstones u32 | tombstone keys [K; TOMBS] | (key, value) | (key, value) | ... |
//! ```
//! `size` counts every pair physically in the page, tombstoned or not.

use std::cmp::Ordering;
use std::marker::PhantomData;

use super::b_plus_tree_page::*;
use super::page_array::PageArray;
use super::page_bytes::*;
use crate::common::config::PageId;
use crate::storage::index::fixed_size::{array_size, FixedSize};
use crate::storage::index::generic_key::KeyComparator;

const NEXT_PAGE_ID_OFFSET: usize = 12;
const NUM_TOMBSTONES_OFFSET: usize = 16;

pub struct BPlusTreeLeafPage<B, K, V, const TOMBS: usize = 0> {
    page: B,
    _entry: PhantomData<(K, V)>,
}

impl<B, K, V, const TOMBS: usize> BPlusTreeLeafPage<B, K, V, TOMBS> {
    pub fn new(page: B) -> BPlusTreeLeafPage<B, K, V, TOMBS> {
        BPlusTreeLeafPage { page, _entry: PhantomData }
    }
}

impl<B: AsRef<[u8]>, K: FixedSize, V: FixedSize, const TOMBS: usize> BPlusTreeLeafPage<B, K, V, TOMBS> {
    /// Bytes between the header and the entries: none without tombstones; with them a count and room for `TOMBS` keys.
    const TOMB_REGION: usize = if TOMBS == 0 { 0 } else { 4 + TOMBS * K::SIZE };
    /// Where the entries start in the page.
    const ENTRIES_AT: usize = LEAF_PAGE_HEADER_SIZE + Self::TOMB_REGION;

    /// How many pairs fit in a leaf. BusTub's `LEAF_PAGE_SLOT_CNT`.
    pub fn capacity() -> usize {
        todo!("2c-01: the space after the 16-byte header (Self::ENTRIES_AT: the tombstone region is empty until module 2d) divided by the size of a (key, value) pair")
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
        PageArray::new(&self.page.as_ref()[Self::ENTRIES_AT..])
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

    /// The slot holding exactly `key`, tombstoned or not.
    pub fn find(&self, key: &K, cmp: &impl KeyComparator<K>) -> Option<u32> {
        let at = self.lower_bound(key, cmp);
        (at < self.size() && cmp.compare(&self.key_at(at), key) == Ordering::Equal).then_some(at)
    }

    /// The value stored for `key`, if there is a live (not tombstoned) pair for it.
    pub fn lookup(&self, key: &K, cmp: &impl KeyComparator<K>) -> Option<V> {
        todo!("2c-02: find the first key not less than the target; it is a hit only if it is equal")
    }

    // ---- tombstones (module 2d) ---------------------------------------------------------------------------------------------

    /// How many tombstones the buffer holds now (always 0 without tombstones).
    pub fn num_tombstones(&self) -> u32 {
        todo!("2d-01: 0 without tombstones; otherwise the count stored right after the header")
    }

    /// The keys with pending deletes, in order of recency (oldest first). BusTub's `GetTombstones`.
    pub fn tombstones(&self) -> Vec<K> {
        todo!("2d-01: decode the stored keys (they follow the count, K::SIZE bytes each)")
    }

    /// Is the pair in slot `index` deleted but still in the page? (Compares the stored bytes, so no comparator is needed: the tombstone
    /// is a copy of the entry's key.)
    pub fn is_deleted_at(&self, index: u32) -> bool {
        todo!("2d-01: is the key of slot `index` one of the buffered tombstones (compare their encoded bytes)")
    }

    /// Is the pair for `key` deleted but still in the page?
    pub fn is_tombstoned(&self, key: &K, cmp: &impl KeyComparator<K>) -> bool {
        todo!("2d-01: is `key` one of the buffered tombstones (compare with the comparator)")
    }
}

impl<B: AsRef<[u8]> + AsMut<[u8]>, K: FixedSize, V: FixedSize, const TOMBS: usize> BPlusTreeLeafPage<B, K, V, TOMBS> {
    /// Formats a fresh page: a leaf with no pairs, no tombstones and no next leaf, holding at most `max_size` (not more than fits).
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
        PageArray::new(&mut self.page.as_mut()[Self::ENTRIES_AT..])
    }

    /// Stores the pair in slot `index`. It does not change the size.
    pub fn set_entry_at(&mut self, index: u32, key: &K, value: &V)
    where
        K: Clone,
        V: Clone,
    {
        todo!("2c-01: encode the pair into slot `index`")
    }

    /// Replaces the whole tombstone buffer (oldest first). Panics if there are more than `TOMBS`.
    pub fn set_tombstones(&mut self, keys: &[K]) {
        todo!("2d-01: encode the keys one after another after the count, and store the count")
    }

    /// Notes `key` as the newest tombstone. Panics if the buffer is full: make room first (`remove_oldest_tombstone`).
    pub fn add_tombstone(&mut self, key: &K)
    where
        K: Clone,
    {
        todo!("2d-01: append the key to the buffer (panic if it is full)")
    }

    /// Forgets `key`'s tombstone, if it has one. `true` if it had.
    pub fn remove_tombstone(&mut self, key: &K, cmp: &impl KeyComparator<K>) -> bool
    where
        K: Clone,
    {
        todo!("2d-01: take the key out of the buffer, keeping the others in order")
    }

    /// Adds the pair in key order. `false` (and nothing changes) if a live pair for `key` is already in the page. A *tombstoned* pair for
    /// the same key is brought back to life with the new value (its tombstone is dropped); no slot is used. Panics if the page has no
    /// room (a tree splits a leaf the moment it reaches `max_size`, so it always has room for one more).
    pub fn insert(&mut self, key: &K, value: &V, cmp: &impl KeyComparator<K>) -> bool
    where
        K: Clone,
        V: Clone,
    {
        todo!("2c-03: find the slot with lower_bound; refuse an equal key; otherwise shift the later pairs right (PageArray::insert_at) and count one more")
    }

    /// Physically removes the pair for `key` (and its tombstone, if it has one), keeping the order. `false` if there is none.
    pub fn remove(&mut self, key: &K, cmp: &impl KeyComparator<K>) -> bool
    where
        K: Clone,
    {
        todo!("2c-07: find the slot with lower_bound; if the key is there, shift the later pairs left (PageArray::remove_at) and count one fewer")
    }

    /// Physically removes the pair in slot `index`, keeping the order, and its tombstone if it had one.
    pub fn remove_at(&mut self, index: u32)
    where
        K: Clone,
    {
        todo!("2c-07: shift the later pairs left and count one fewer")
    }

    /// Drops `key` from the tombstone buffer by byte comparison of the stored key (the key is physically in the page, so it matches).
    fn drop_tombstone_of(&mut self, key: &K)
    where
        K: Clone,
    {
        if TOMBS == 0 {
            return;
        }
        let bytes = |k: &K| {
            let mut b = vec![0u8; K::SIZE];
            k.encode(&mut b);
            b
        };
        let mine = bytes(key);
        let mut keys = self.tombstones();
        if let Some(at) = keys.iter().position(|t| bytes(t) == mine) {
            keys.remove(at);
            self.set_tombstones(&keys);
        }
    }

    /// Adds the pair at the front, shifting the others right. Used when a leaf borrows from its left neighbour.
    pub fn insert_at_front(&mut self, key: &K, value: &V)
    where
        K: Clone,
        V: Clone,
    {
        todo!("2c-07: insert at slot 0 and count one more")
    }

    /// Deletes `key` logically: the pair stays in the page and its key becomes the newest tombstone. If the buffer is full, the oldest
    /// tombstoned pair is removed for real first. `false` if there is no live pair for `key`. Only for `TOMBS > 0`.
    pub fn remove_logically(&mut self, key: &K, cmp: &impl KeyComparator<K>) -> bool
    where
        K: Clone,
    {
        todo!("2d-02: a missing or already tombstoned key is false; with a full buffer really remove the oldest tombstoned pair; then buffer the key as the newest tombstone")
    }

    /// Really removes every tombstoned pair (and empties the buffer). Returns how many pairs went.
    pub fn purge_tombstones(&mut self, cmp: &impl KeyComparator<K>) -> usize
    where
        K: Clone,
    {
        todo!("2d-03: remove each buffered key's pair for real; the buffer ends up empty")
    }
}
