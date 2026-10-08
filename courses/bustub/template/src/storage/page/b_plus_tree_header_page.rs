//! Port of `src/include/storage/page/b_plus_tree_header_page.h`. "The header page is just used to retrieve the root page,
//! preventing potential race condition under concurrent environment": the root's page id changes when the tree grows or shrinks,
//! so it lives in a page of its own that can be latched like any other.
//!
//! ```text
//! | root_page_id i32 |
//! ```

use super::page_bytes::*;
use crate::common::config::PageId;

pub struct BPlusTreeHeaderPage<B> {
    page: B,
}

impl<B> BPlusTreeHeaderPage<B> {
    pub fn new(page: B) -> BPlusTreeHeaderPage<B> {
        BPlusTreeHeaderPage { page }
    }
}

impl<B: AsRef<[u8]>> BPlusTreeHeaderPage<B> {
    /// The root's page id, or `PageId::INVALID` for an empty tree.
    pub fn root_page_id(&self) -> PageId {
        todo!("2c-01: the page id stored at offset 0")
    }
}

impl<B: AsRef<[u8]> + AsMut<[u8]>> BPlusTreeHeaderPage<B> {
    /// Formats a fresh page: an empty tree. (A zero page would say the root is page 0.)
    pub fn init(&mut self) {
        todo!("2c-01: the root is INVALID")
    }

    pub fn set_root_page_id(&mut self, root_page_id: PageId) {
        todo!("2c-01: store the id at offset 0")
    }
}
