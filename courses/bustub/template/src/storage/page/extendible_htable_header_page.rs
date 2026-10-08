//! Port of `src/storage/page/extendible_htable_header_page.cpp`: the top of an extendible hash table. It maps the **upper bits** of
//! a hash to one of up to 2^max_depth directory pages, so a table can have many directories, each growing independently.
//!
//! ```text
//! | directory_page_ids [i32; 512] | max_depth u32 |
//! ```
//! BusTub reinterprets the page as this struct; this view reads and writes the same bytes by offset.

use super::layout::*;
use super::page_bytes::*;
use crate::common::config::PageId;

/// A view of a page as a header page. `B` is the page's bytes: `&[u8]` to read, `&mut [u8]` to read and write.
pub struct ExtendibleHTableHeaderPage<B> {
    page: B,
}

impl<B> ExtendibleHTableHeaderPage<B> {
    pub fn new(page: B) -> ExtendibleHTableHeaderPage<B> {
        ExtendibleHTableHeaderPage { page }
    }
}

impl<B: AsRef<[u8]>> ExtendibleHTableHeaderPage<B> {
    pub fn max_depth(&self) -> u32 {
        todo!("2b-02: the max depth field")
    }

    /// How many directory slots the header uses: 2^max_depth.
    pub fn max_size(&self) -> u32 {
        todo!("2b-02: 2 to the max depth")
    }

    /// The directory page id in slot `directory_idx` (`PageId::INVALID` if there isn't one yet).
    pub fn get_directory_page_id(&self, directory_idx: u32) -> PageId {
        todo!("2b-02: panic for a slot past max_size; otherwise the id stored in that slot")
    }

    /// Which directory a hash belongs to: its **top** `max_depth` bits. With max depth 0 there is one directory, index 0.
    pub fn hash_to_directory_index(&self, hash: u32) -> u32 {
        todo!("2b-02: shift the hash right so only its top max_depth bits remain; max depth 0 must give 0 (a shift by 32 is not allowed)")
    }
}

impl<B: AsRef<[u8]> + AsMut<[u8]>> ExtendibleHTableHeaderPage<B> {
    /// Formats a fresh page: the given max depth, and every directory slot empty (`INVALID`). Panics if `max_depth` is more than 9.
    pub fn init(&mut self, max_depth: u32) {
        todo!("2b-02: store the max depth (at most 9), and mark every slot INVALID: a fresh page is zeros, and 0 is a real page id")
    }

    pub fn set_directory_page_id(&mut self, directory_idx: u32, directory_page_id: PageId) {
        todo!("2b-02: panic for a slot past max_size; otherwise store the id in that slot")
    }
}
