//! Port of `src/include/storage/page/table_page.h` and `src/storage/page/table_page.cpp`: a **slotted page** holding tuples.
//!
//! ```text
//! | header (8) | slot 0 | slot 1 | ...                free space                ... | tuple 2 | tuple 1 | tuple 0 |
//! ```
//! The slot array grows from the front, the tuples from the back, and the page is full when they meet. A tuple's address is its
//! **slot number**: tuples never move, so a record id (page, slot) stays valid; deleting only sets a flag in the slot's metadata.
//!
//! Header: `next_page_id i32` (the next page of the table), `num_tuples u16`, `num_deleted_tuples u16`.
//! Slot (24 bytes, BusTub's size; the byte order inside is this port's): `offset u16 | size u16 | (4 unused) | ts i64 | is_deleted u8 | (7 unused)`.

use super::page_bytes::*;
use crate::common::config::{PageId, BUSTUB_PAGE_SIZE};
use crate::common::exception::{Exception, ExceptionType, Result};
use crate::common::rid::Rid;
use crate::storage::table::tuple::{Tuple, TupleMeta};

pub const TABLE_PAGE_HEADER_SIZE: usize = 8;
pub const TUPLE_INFO_SIZE: usize = 24;

const NEXT_PAGE_ID_OFFSET: usize = 0;
const NUM_TUPLES_OFFSET: usize = 4;
const NUM_DELETED_OFFSET: usize = 6;

pub struct TablePage<B> {
    page: B,
}

impl<B> TablePage<B> {
    pub fn new(page: B) -> TablePage<B> {
        TablePage { page }
    }
}

fn slot_at(index: usize) -> usize {
    TABLE_PAGE_HEADER_SIZE + TUPLE_INFO_SIZE * index
}

fn out_of_range() -> Exception {
    Exception::new(ExceptionType::Invalid, "Tuple ID out of range")
}

impl<B: AsRef<[u8]>> TablePage<B> {
    fn bytes(&self) -> &[u8] {
        self.page.as_ref()
    }

    /// The number of tuples in the page (deleted ones included).
    pub fn get_num_tuples(&self) -> u32 {
        todo!("3b-05: the u16 at byte 4")
    }

    /// How many of them are marked deleted.
    pub fn get_num_deleted_tuples(&self) -> u32 {
        todo!("3b-05: the u16 at byte 6")
    }

    /// The next page of the table, if any.
    pub fn get_next_page_id(&self) -> Option<PageId> {
        todo!("3b-05: the id at byte 0 (INVALID is None)")
    }

    fn slot(&self, index: u32) -> (u16, u16, TupleMeta) {
        let at = slot_at(index as usize);
        let b = &self.bytes()[at..at + TUPLE_INFO_SIZE];
        (
            u16::from_le_bytes([b[0], b[1]]),
            u16::from_le_bytes([b[2], b[3]]),
            TupleMeta { ts: i64::from_le_bytes(b[8..16].try_into().unwrap()), is_deleted: b[16] != 0 },
        )
    }

    /// Where a tuple of this size would be stored (the offset of its first byte), or `None` if it does not fit: the new slot and the
    /// tuple must not overlap. BusTub's `GetNextTupleOffset`.
    pub fn get_next_tuple_offset(&self, _meta: &TupleMeta, tuple: &Tuple) -> Option<u16> {
        todo!("3b-05: the tuples grow down from the end of the page: the new tuple starts below the previous one (the page's end for the first); it fits if that is not below the end of the slot array including the new slot (header + 24 * (tuples + 1))")
    }

    /// The tuple in `rid`'s slot and its metadata. An out-of-range slot is an error.
    pub fn get_tuple(&self, rid: Rid) -> Result<(TupleMeta, Tuple)> {
        todo!("3b-06: Err for a slot past the last tuple; otherwise the slot's metadata and a tuple copied from its bytes (with this rid)")
    }

    /// Just the metadata of the slot.
    pub fn get_tuple_meta(&self, rid: Rid) -> Result<TupleMeta> {
        todo!("3b-06: Err for a slot past the last tuple; otherwise its metadata")
    }
}

impl<B: AsRef<[u8]> + AsMut<[u8]>> TablePage<B> {
    /// Formats a fresh page: no next page, no tuples.
    pub fn init(&mut self) {
        todo!("3b-05: no next page (INVALID), zero tuples, zero deleted")
    }

    fn set_u16(&mut self, at: usize, value: u16) {
        self.page.as_mut()[at..at + 2].copy_from_slice(&value.to_le_bytes());
    }

    pub fn set_next_page_id(&mut self, next: Option<PageId>) {
        write_optional_page_id(self.page.as_mut(), NEXT_PAGE_ID_OFFSET, next);
    }

    fn set_slot(&mut self, index: u32, offset: u16, size: u16, meta: &TupleMeta) {
        let at = slot_at(index as usize);
        let b = &mut self.page.as_mut()[at..at + TUPLE_INFO_SIZE];
        b[0..2].copy_from_slice(&offset.to_le_bytes());
        b[2..4].copy_from_slice(&size.to_le_bytes());
        b[8..16].copy_from_slice(&meta.ts.to_le_bytes());
        b[16] = meta.is_deleted as u8;
    }

    /// Stores the tuple in the next slot, at the offset `get_next_tuple_offset` gives; returns the slot number, or `None` if it does not fit.
    pub fn insert_tuple(&mut self, meta: &TupleMeta, tuple: &Tuple) -> Option<u16> {
        todo!("3b-05: find the offset (None: no room); write the slot (offset, size, meta) and the tuple's bytes there; count one more tuple; return the slot number")
    }

    /// Replaces the slot's metadata. Marking a live tuple deleted counts it in `num_deleted_tuples`. A slot past the last tuple is an error.
    pub fn update_tuple_meta(&mut self, meta: &TupleMeta, rid: Rid) -> Result<()> {
        todo!("3b-06: Err for a bad slot; count a live tuple that becomes deleted; store the new metadata keeping the offset and size")
    }

    /// Overwrites the slot's tuple with one **of the same length**, and its metadata. "Unsafe" because nothing stops two writers: the
    /// caller must hold the page's write latch.
    pub fn update_tuple_in_place_unsafe(&mut self, meta: &TupleMeta, tuple: &Tuple, rid: Rid) -> Result<()> {
        todo!("3b-06: Err for a bad slot or a tuple of a different length; count a newly deleted tuple; store the metadata and overwrite the bytes")
    }
}
