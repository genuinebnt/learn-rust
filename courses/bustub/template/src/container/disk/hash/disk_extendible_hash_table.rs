//! Port of `src/container/disk/hash/disk_extendible_hash_table.cpp`: an extendible hash table whose header, directories and buckets
//! are pages in the buffer pool. Three levels: the header maps the top bits of a hash to a directory; a directory maps the low
//! bits to a bucket; a bucket holds a few pairs. A full bucket splits (and the directory doubles if the bucket was already
//! as deep as the directory); an empty one merges with its split image (and the directory halves if it can).
//!
//! Latching is by guards, top down, releasing a parent once the child is known to be safe ("latch crabbing"):
//! `get_value` read-latches header -> directory -> bucket; `insert` and `remove` write-latch them.

use crate::buffer::buffer_pool_manager::BufferPoolManager;
use crate::common::config::PageId;
use crate::container::hash::hash_function::HashFunction;
use crate::storage::index::fixed_size::FixedSize;
use crate::storage::index::generic_key::KeyComparator;
use crate::storage::page::extendible_htable_bucket_page::ExtendibleHTableBucketPage as Bucket;
use crate::storage::page::extendible_htable_directory_page::ExtendibleHTableDirectoryPage as Directory;
use crate::storage::page::extendible_htable_header_page::ExtendibleHTableHeaderPage as Header;
use crate::storage::page::layout::{HTABLE_DIRECTORY_MAX_DEPTH, HTABLE_HEADER_MAX_DEPTH};

pub struct DiskExtendibleHashTable<'a, K, V, C> {
    index_name: String,
    bpm: &'a BufferPoolManager,
    cmp: C,
    hash_fn: HashFunction<K>,
    header_max_depth: u32,
    directory_max_depth: u32,
    bucket_max_size: u32,
    header_page_id: PageId,
    _value: std::marker::PhantomData<V>,
}

impl<'a, K, V, C> DiskExtendibleHashTable<'a, K, V, C>
where
    K: FixedSize + Clone,
    V: FixedSize + Clone,
    C: KeyComparator<K>,
{
    /// Creates an empty table: allocates and formats the header page. `bucket_max_size` is how many pairs a bucket holds before it
    /// splits (use [`DiskExtendibleHashTable::default_bucket_max_size`] for "as many as fit in a page").
    pub fn new(
        index_name: &str,
        bpm: &'a BufferPoolManager,
        cmp: C,
        hash_fn: HashFunction<K>,
        header_max_depth: u32,
        directory_max_depth: u32,
        bucket_max_size: u32,
    ) -> Self {
        todo!("2b-06: allocate a page for the header and format it (Header::init); remember its id and the parameters")
    }

    pub fn default_header_max_depth() -> u32 {
        HTABLE_HEADER_MAX_DEPTH
    }

    pub fn default_directory_max_depth() -> u32 {
        HTABLE_DIRECTORY_MAX_DEPTH
    }

    /// As many pairs as fit in one bucket page.
    pub fn default_bucket_max_size() -> u32 {
        Bucket::<&[u8], K, V>::capacity() as u32
    }

    pub fn get_header_page_id(&self) -> PageId {
        self.header_page_id
    }

    pub fn index_name(&self) -> &str {
        &self.index_name
    }

    /// The 32 bits of hash the table works with: the low half of the 64-bit hash (BusTub: `static_cast<uint32_t>`).
    fn hash(&self, key: &K) -> u32 {
        todo!("2b-01: the 64-bit hash truncated to 32 bits")
    }

    /// The value stored for `key`: empty or one element (keys are unique; BusTub's `GetValue` fills a vector).
    pub fn get_value(&self, key: &K) -> Vec<V> {
        todo!("2b-06: an empty table has no directory, so no value")
    }

    /// Adds the pair. `false` if the key is already there, or the table can't grow any further to make room.
    pub fn insert(&self, key: &K, value: &V) -> bool {
        todo!("2b-06: hash the key; find the directory slot in the header (write-latched); create the directory and bucket if there are none")
    }

    /// First key under this header slot: allocate a directory, then its first bucket, and put the pair there.
    fn insert_to_new_directory(&self, header: &mut [u8], directory_idx: u32, hash: u32, key: &K, value: &V) -> bool {
        todo!("2b-06: a new directory page (init), recorded in the header; then insert_to_new_bucket for the hash's slot")
    }

    /// First key for this directory slot: allocate a bucket (local depth 0), point the slot at it, and put the pair there.
    fn insert_to_new_bucket(&self, directory: &mut Directory<&mut [u8]>, bucket_idx: u32, key: &K, value: &V) -> bool {
        todo!("2b-06: a new bucket page (init), the directory slot pointing at it with local depth 0, then insert the pair")
    }

    /// Splits the full bucket in slot `bucket_idx` (one more hash bit now distinguishes it): a new bucket takes the entries whose
    /// new bit is 1, and the directory slots that pointed at the old bucket are divided between the two.
    fn split_bucket(&self, directory: &mut Directory<&mut [u8]>, old_bucket: &mut Bucket<&mut [u8], K, V>, bucket_idx: u32, old_page_id: PageId) {
        todo!("2b-07: allocate the new bucket; move the entries whose hash has the new bit set; deepen and redirect the directory slots")
    }

    /// Removes `key`. `false` if it wasn't there.
    pub fn remove(&self, key: &K) -> bool {
        todo!("2b-08: find the directory and the bucket (write-latched), remove the key from the bucket; say whether it was there")
    }

    /// Merges the empty bucket in slot `bucket_idx` into its split image, as long as the two have the same local depth, repeating
    /// while the merged bucket is empty or its new split image is, and finally halves the directory as far as it can shrink.
    fn merge_empty_buckets(&self, directory_page: &mut [u8], mut bucket_idx: u32) {
        todo!("2b-08: while the empty bucket's split image has the same local depth: redirect the slots, lower the local depth, delete the empty page")
    }

    /// Checks every directory's invariants (see `Directory::verify_integrity`). Panics if one fails.
    pub fn verify_integrity(&self) {
        todo!("2b-06: for every directory in the header, verify_integrity")
    }
}
