//! Port of `src/storage/table/table_iterator.cpp`: a sequential scan of a table heap. It is a cursor of a [`Rid`] and walks slot by slot
//! and page by page along the chain. It returns **every** tuple, deleted ones included (with their metadata): skipping the deleted is the
//! caller's job (the sequential scan executor does it).

use super::table_heap::TableHeap;
use super::tuple::{Tuple, TupleMeta};
use crate::common::config::PageId;
use crate::common::exception::{Exception, ExceptionType, Result};
use crate::common::rid::Rid;
use crate::storage::page::table_page::TablePage;

pub struct TableIterator<'a> {
    heap: &'a TableHeap<'a>,
    /// The tuple the iterator is at; a rid in an invalid page is the end.
    rid: Rid,
    /// Where to stop (exclusive); an invalid page means "at the end of the table, whenever that is".
    stop_at_rid: Rid,
}

impl<'a> TableIterator<'a> {
    /// A cursor at `rid`. If `rid` does not name a tuple (a new, empty table) the iterator is already at the end.
    pub fn new(heap: &'a TableHeap<'a>, rid: Rid, stop_at_rid: Rid) -> TableIterator<'a> {
        todo!("3c-03: remember the heap and the two rids; if the start does not name an existing tuple the iterator starts at the end (an invalid rid)")
    }

    /// The tuple the iterator is at, with its metadata. An error at the end.
    pub fn get_tuple(&self) -> Result<(TupleMeta, Tuple)> {
        todo!("3c-03: an error at the end; otherwise the heap's tuple at the current rid")
    }

    pub fn get_rid(&self) -> Rid {
        self.rid
    }

    pub fn is_end(&self) -> bool {
        todo!("3c-03: the iterator is at the end when its rid is in no page")
    }

    /// Moves to the next tuple: the next slot of the page, or slot 0 of the next page, or the end; and the end if it reaches the stopping rid.
    pub fn advance(&mut self) {
        todo!("3c-03: at the end do nothing; slot + 1; stop (the end) if that is the stopping rid; if the page has more tuples stay; otherwise go to slot 0 of the next page, or the end")
    }
}

/// `for (meta, tuple) in heap.make_iterator()`: every tuple from the cursor to the end, deleted ones included.
impl Iterator for TableIterator<'_> {
    type Item = (TupleMeta, Tuple);

    fn next(&mut self) -> Option<(TupleMeta, Tuple)> {
        todo!("3c-03: None at the end; otherwise the current tuple, after moving on")
    }
}
