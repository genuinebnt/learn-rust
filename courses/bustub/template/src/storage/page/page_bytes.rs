//! Reading and writing integers inside a page. BusTub casts the page's `char *` to a struct pointer (`reinterpret_cast`) and reads
//! fields through it. Safe Rust reads the bytes it wants, in a stated byte order, at a stated offset: no alignment requirements,
//! no padding surprises, the same result on every machine.

use crate::common::config::PageId;

/// The `u32` stored little-endian at byte `offset` of `page`.
pub fn read_u32(page: &[u8], offset: usize) -> u32 {
    todo!("2a-01: take the 4 bytes at offset and build a u32 from them, little-endian")
}

/// Stores `value` little-endian at byte `offset` of `page`.
pub fn write_u32(page: &mut [u8], offset: usize, value: u32) {
    todo!("2a-01: the 4 little-endian bytes of the value go to offset..offset + 4")
}

pub fn read_u64(page: &[u8], offset: usize) -> u64 {
    todo!("2a-01: like read_u32, with 8 bytes")
}

pub fn write_u64(page: &mut [u8], offset: usize, value: u64) {
    todo!("2a-01: like write_u32, with 8 bytes")
}

/// The page id stored at `offset`. On disk "no page" is `-1` (`INVALID_PAGE_ID`), which `PageId::INVALID` is.
pub fn read_page_id(page: &[u8], offset: usize) -> PageId {
    todo!("2a-01: an i32 (signed: -1 must survive) from 4 little-endian bytes")
}

pub fn write_page_id(page: &mut [u8], offset: usize, id: PageId) {
    todo!("2a-01: the id's i32 as 4 little-endian bytes")
}

/// The page id at `offset`, or `None` if it holds `INVALID`.
pub fn read_optional_page_id(page: &[u8], offset: usize) -> Option<PageId> {
    todo!("2a-01: read_page_id, but INVALID (-1) becomes None")
}

/// Stores `id`, or `INVALID` for `None`.
pub fn write_optional_page_id(page: &mut [u8], offset: usize, id: Option<PageId>) {
    todo!("2a-01: write the id, or INVALID for None")
}
