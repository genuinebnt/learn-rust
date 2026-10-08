//! Port of `src/storage/page/b_plus_tree_page.cpp`: the header every B+ tree page starts with, shared by internal and leaf pages.
//!
//! ```text
//! | page_type u32 | size u32 | max_size u32 | ... (the rest depends on the type)
//! ```
//! BusTub's `BPlusTreePage` is a class whose destructor and constructors are deleted: pages are never constructed, only cast
//! from the buffer pool's bytes. This view reads and writes the same bytes by offset.

use super::page_bytes::*;

/// BusTub's `IndexPageType`. The numbers are stored in the page, so they are part of the file format.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum IndexPageType {
    Invalid = 0,
    Leaf = 1,
    Internal = 2,
}

pub const PAGE_TYPE_OFFSET: usize = 0;
pub const SIZE_OFFSET: usize = 4;
pub const MAX_SIZE_OFFSET: usize = 8;
/// Bytes of the header an internal page has (the three fields above).
pub const INTERNAL_PAGE_HEADER_SIZE: usize = 12;
/// A leaf page's header adds the next leaf's page id.
pub const LEAF_PAGE_HEADER_SIZE: usize = 16;

pub struct BPlusTreePage<B> {
    page: B,
}

impl<B> BPlusTreePage<B> {
    pub fn new(page: B) -> BPlusTreePage<B> {
        BPlusTreePage { page }
    }
}

impl<B: AsRef<[u8]>> BPlusTreePage<B> {
    pub fn page_type(&self) -> IndexPageType {
        todo!("2c-01: read the type field and turn 1 and 2 into Leaf and Internal; anything else (a fresh zero page) is Invalid")
    }

    pub fn is_leaf_page(&self) -> bool {
        todo!("2c-01: the type is Leaf")
    }

    /// Entries in the page: key/value pairs in a leaf, **children** in an internal page (an internal page has one key fewer).
    pub fn size(&self) -> u32 {
        todo!("2c-01: the size field")
    }

    pub fn max_size(&self) -> u32 {
        todo!("2c-01: the max size field")
    }

    /// The fewest entries a page that is not the root may have. A leaf: `max_size / 2`. An internal page: `(max_size + 1) / 2`, which
    /// is `ceil(max_size / 2)` children. (BusTub's `GetMinSize`; the root is exempt, see the delete stages.)
    pub fn min_size(&self) -> u32 {
        todo!("2c-01: a leaf holds at least max_size / 2 entries, an internal page at least ceil(max_size / 2) children")
    }
}

impl<B: AsRef<[u8]> + AsMut<[u8]>> BPlusTreePage<B> {
    pub fn set_page_type(&mut self, page_type: IndexPageType) {
        todo!("2c-01: store the type as its number")
    }

    pub fn set_size(&mut self, size: u32) {
        todo!("2c-01: store the size")
    }

    /// Adds `amount` (which may be negative) to the size. Panics if that would leave a negative size.
    pub fn change_size_by(&mut self, amount: i32) {
        todo!("2c-01: size plus amount; below zero is a bug, so panic")
    }

    pub fn set_max_size(&mut self, max_size: u32) {
        todo!("2c-01: store the max size")
    }
}
