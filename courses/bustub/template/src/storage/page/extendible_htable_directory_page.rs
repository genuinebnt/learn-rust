//! Port of `src/storage/page/extendible_htable_directory_page.cpp`: the middle level. A directory has 2^global_depth slots; slot
//! `hash & mask` holds the page id of the bucket for that hash, and each slot records its bucket's **local depth** (how many bits
//! of the hash that bucket really distinguishes). Several slots may share one bucket.
//!
//! ```text
//! | max_depth u32 | global_depth u32 | local_depths [u8; 512] | bucket_page_ids [i32; 512] |
//! ```

use std::collections::HashMap;

use super::layout::*;
use super::page_bytes::*;
use crate::common::config::PageId;

pub struct ExtendibleHTableDirectoryPage<B> {
    page: B,
}

impl<B> ExtendibleHTableDirectoryPage<B> {
    pub fn new(page: B) -> ExtendibleHTableDirectoryPage<B> {
        ExtendibleHTableDirectoryPage { page }
    }
}

impl<B: AsRef<[u8]>> ExtendibleHTableDirectoryPage<B> {
    pub fn get_max_depth(&self) -> u32 {
        todo!("2b-02: the max depth field")
    }

    pub fn get_global_depth(&self) -> u32 {
        todo!("2b-02: the global depth field")
    }

    /// The number of slots in use: 2^global_depth.
    pub fn size(&self) -> u32 {
        todo!("2b-02: 2 to the global depth")
    }

    /// The most slots the directory may ever have: 2^max_depth.
    pub fn max_size(&self) -> u32 {
        todo!("2b-02: 2 to the max depth")
    }

    pub fn get_bucket_page_id(&self, bucket_idx: u32) -> PageId {
        todo!("2b-02: panic past max_size; otherwise the bucket page id stored in the slot")
    }

    pub fn get_local_depth(&self, bucket_idx: u32) -> u32 {
        todo!("2b-02: panic past max_size; otherwise the local depth byte of the slot")
    }

    /// A mask of `global_depth` ones from the low end: `0b111` for depth 3.
    pub fn get_global_depth_mask(&self) -> u32 {
        todo!("2b-02: global_depth one-bits")
    }

    /// The same for the local depth of the bucket in slot `bucket_idx`.
    pub fn get_local_depth_mask(&self, bucket_idx: u32) -> u32 {
        todo!("2b-02: local_depth one-bits")
    }

    /// The slot a hash maps to: its low `global_depth` bits.
    pub fn hash_to_bucket_index(&self, hash: u32) -> u32 {
        todo!("2b-02: the hash masked down to the global depth")
    }

    /// The slot of the bucket this bucket would split from or merge with: flip the highest bit its local depth distinguishes.
    /// A bucket of local depth 0 has no sibling and is its own split image.
    pub fn get_split_image_index(&self, bucket_idx: u32) -> u32 {
        todo!("2b-02: bucket_idx with bit (local_depth - 1) flipped; depth 0 returns bucket_idx itself")
    }

    /// True if no bucket uses all global_depth bits, so halving the directory loses nothing.
    pub fn can_shrink(&self) -> bool {
        todo!("2b-03: the global depth is above 0 and every slot in use has a local depth below it")
    }

    /// Checks the invariants: (1) every local depth <= the global depth; (2) a bucket with local depth d is pointed to by exactly
    /// 2^(global - d) slots; (3) all slots with the same bucket page id have the same local depth. Panics if one fails.
    pub fn verify_integrity(&self) {
        todo!("2b-03: check the three invariants and panic with a message naming the slot or bucket that breaks one")
    }
}

impl<B: AsRef<[u8]> + AsMut<[u8]>> ExtendibleHTableDirectoryPage<B> {
    /// Formats a fresh page: the given max depth (at most 9), global depth 0, every local depth 0, every bucket id `INVALID`.
    pub fn init(&mut self, max_depth: u32) {
        todo!("2b-02: store the max depth, global depth 0, zero the local depths, mark every bucket slot INVALID")
    }

    pub fn set_bucket_page_id(&mut self, bucket_idx: u32, bucket_page_id: PageId) {
        todo!("2b-02: panic past max_size; otherwise store the id")
    }

    pub fn set_local_depth(&mut self, bucket_idx: u32, local_depth: u8) {
        todo!("2b-02: panic past max_size or for a depth above the max depth; otherwise store the byte")
    }

    pub fn incr_local_depth(&mut self, bucket_idx: u32) {
        todo!("2b-02: one more bit of the hash distinguishes this bucket (not past the max depth)")
    }

    pub fn decr_local_depth(&mut self, bucket_idx: u32) {
        todo!("2b-02: one fewer bit (not below 0)")
    }

    /// Doubles the directory: the new upper half of the slots is a copy of the lower half (bucket ids and local depths), because
    /// until a bucket splits, a hash with the new top bit set still goes to the same bucket. Panics at the max depth.
    pub fn incr_global_depth(&mut self) {
        todo!("2b-03: copy slots 0..size into size..2*size (ids and depths), then raise the global depth; panic at the max depth")
    }

    /// Halves the directory. The caller has checked `can_shrink`.
    pub fn decr_global_depth(&mut self) {
        todo!("2b-03: lower the global depth (not below 0)")
    }
}
