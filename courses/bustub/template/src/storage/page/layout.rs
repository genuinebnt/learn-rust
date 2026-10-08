//! Where the fields of BusTub's extendible hash pages live inside a page, written down as constants and checked at compile time.
//!
//! BusTub declares each page as a C++ class (`class ExtendibleHTableDirectoryPage { uint32_t max_depth_; ... }`) and reinterprets
//! the page's bytes as one. The compiler lays the fields out: this module states the same layout explicitly, so the Rust page
//! views can read and write by offset, and a mismatch between the two descriptions is a compile error.

use std::mem::{offset_of, size_of};

use crate::common::config::BUSTUB_PAGE_SIZE;

/// log2 of the number of directory entries (512) a directory page and a header page hold.
pub const HTABLE_DIRECTORY_MAX_DEPTH: u32 = 9;
pub const HTABLE_DIRECTORY_ARRAY_SIZE: usize = 1 << HTABLE_DIRECTORY_MAX_DEPTH;
pub const HTABLE_HEADER_MAX_DEPTH: u32 = 9;
pub const HTABLE_HEADER_ARRAY_SIZE: usize = 1 << HTABLE_HEADER_MAX_DEPTH;
/// A bucket page starts with `size` and `max_size`, 4 bytes each.
pub const HTABLE_BUCKET_PAGE_METADATA_SIZE: usize = 8;

// TODO(2a-12): describe the two pages as #[repr(C)] structs and compute these with offset_of! and size_of; add const assertions
pub const DIRECTORY_MAX_DEPTH_OFFSET: usize = 0;
pub const DIRECTORY_GLOBAL_DEPTH_OFFSET: usize = 0;
pub const DIRECTORY_LOCAL_DEPTHS_OFFSET: usize = 0;
pub const DIRECTORY_BUCKET_PAGE_IDS_OFFSET: usize = 0;
pub const DIRECTORY_PAGE_SIZE: usize = 0;
pub const HEADER_DIRECTORY_PAGE_IDS_OFFSET: usize = 0;
pub const HEADER_MAX_DEPTH_OFFSET: usize = 0;
pub const HEADER_PAGE_SIZE: usize = 0;
