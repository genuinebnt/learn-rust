//! Port of `src/storage/page/extendible_htable_bucket_page.cpp`: the bottom level. A bucket is a small unsorted array of
//! `(key, value)` pairs. Keys are unique.
//!
//! ```text
//! | size u32 | max_size u32 | (key, value) | (key, value) | ... |
//! ```

use std::marker::PhantomData;

use super::layout::HTABLE_BUCKET_PAGE_METADATA_SIZE;
use super::page_array::PageArray;
use super::page_bytes::*;
use crate::storage::index::fixed_size::{array_size, FixedSize};
use crate::storage::index::generic_key::KeyComparator;

pub struct ExtendibleHTableBucketPage<B, K, V> {
    page: B,
    _entry: PhantomData<(K, V)>,
}

const SIZE_OFFSET: usize = 0;
const MAX_SIZE_OFFSET: usize = 4;

impl<B, K, V> ExtendibleHTableBucketPage<B, K, V> {
    pub fn new(page: B) -> ExtendibleHTableBucketPage<B, K, V> {
        ExtendibleHTableBucketPage { page, _entry: PhantomData }
    }
}

impl<B: AsRef<[u8]>, K: FixedSize, V: FixedSize> ExtendibleHTableBucketPage<B, K, V> {
    /// How many pairs fit in a bucket page.
    pub fn capacity() -> usize {
        array_size(HTABLE_BUCKET_PAGE_METADATA_SIZE, <(K, V)>::SIZE)
    }

    pub fn size(&self) -> u32 {
        todo!("2b-04: the size field")
    }

    pub fn max_size(&self) -> u32 {
        todo!("2b-04: the max size field")
    }

    pub fn is_full(&self) -> bool {
        todo!("2b-04: size has reached max_size")
    }

    pub fn is_empty(&self) -> bool {
        todo!("2b-04: size is 0")
    }

    fn entries(&self) -> PageArray<&[u8], (K, V)> {
        PageArray::new(&self.page.as_ref()[HTABLE_BUCKET_PAGE_METADATA_SIZE..])
    }

    /// The pair in slot `bucket_idx`. Panics past `size`.
    pub fn entry_at(&self, bucket_idx: u32) -> (K, V) {
        todo!("2b-04: panic past size; otherwise decode the pair in that slot (a PageArray over the bytes after the metadata does it)")
    }

    pub fn key_at(&self, bucket_idx: u32) -> K {
        todo!("2b-04: the key of entry_at")
    }

    pub fn value_at(&self, bucket_idx: u32) -> V {
        todo!("2b-04: the value of entry_at")
    }

    /// The value stored for `key`, if any. The array is unsorted, so this looks at every entry.
    pub fn lookup(&self, key: &K, cmp: &impl KeyComparator<K>) -> Option<V> {
        todo!("2b-04: scan the entries for an equal key (compare with the comparator, not ==)")
    }
}

impl<B: AsRef<[u8]> + AsMut<[u8]>, K: FixedSize, V: FixedSize> ExtendibleHTableBucketPage<B, K, V> {
    /// Formats a fresh page: empty, with room for `max_size` pairs (at most [`capacity`](Self::capacity)).
    pub fn init(&mut self, max_size: u32) {
        todo!("2b-04: size 0, the given max size (not more than fits)")
    }

    fn entries_mut(&mut self) -> PageArray<&mut [u8], (K, V)> {
        PageArray::new(&mut self.page.as_mut()[HTABLE_BUCKET_PAGE_METADATA_SIZE..])
    }

    /// Adds the pair. `false` (and nothing changes) if the bucket is full or already holds `key`.
    pub fn insert(&mut self, key: &K, value: &V, cmp: &impl KeyComparator<K>) -> bool
    where
        K: Clone,
        V: Clone,
    {
        todo!("2b-04: refuse if full or the key is already there; otherwise append the pair and count it")
    }

    /// Removes the pair in slot `bucket_idx`, shifting the later ones down so the order is kept.
    pub fn remove_at(&mut self, bucket_idx: u32) {
        todo!("2b-04: shift the later entries down (PageArray::remove_at) and count one fewer")
    }

    /// Removes the pair with this key. `false` if there isn't one.
    pub fn remove(&mut self, key: &K, cmp: &impl KeyComparator<K>) -> bool {
        todo!("2b-04: find the key; remove_at it; say whether it was there")
    }
}
