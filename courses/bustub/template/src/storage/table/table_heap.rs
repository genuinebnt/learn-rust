//! Port of `src/storage/table/table_heap.cpp`: a table on disk, which is just a linked list of table pages in the buffer pool. A tuple
//! is added to the last page, and when that page is full a new page is allocated and linked after it. A tuple is found by its
//! [`Rid`] (page, slot); because slots never move (module 3b), a rid stays valid.

use std::sync::Mutex;

use super::table_iterator::TableIterator;
use super::tuple::{Tuple, TupleMeta};
use crate::buffer::buffer_pool_manager::BufferPoolManager;
use crate::common::config::PageId;
use crate::common::exception::{Exception, ExceptionType, Result};
use crate::common::rid::Rid;
use crate::storage::page::table_page::TablePage;

pub struct TableHeap<'a> {
    pub(crate) bpm: &'a BufferPoolManager,
    first_page_id: PageId,
    /// The id of the last page of the table; the lock also serialises inserts (one at a time, or two inserters could both extend the table).
    last_page_id: Mutex<PageId>,
}

impl<'a> TableHeap<'a> {
    /// Creates an empty table: allocates the first page and formats it as a table page.
    pub fn new(bpm: &'a BufferPoolManager) -> TableHeap<'a> {
        todo!("3c-01: allocate a page for the first table page and init it; it is also the last page; remember the pool")
    }

    /// The id of the first page of the table.
    pub fn get_first_page_id(&self) -> PageId {
        self.first_page_id
    }

    /// Adds the tuple at the end of the table and returns where it went. If the last page has no room, a new page is allocated and linked
    /// after it (and becomes the last page). A tuple that does not fit even an empty page is an error ("tuple is too large, cannot
    /// insert"). Inserts are serialised by the heap's lock.
    pub fn insert_tuple(&self, meta: &TupleMeta, tuple: &Tuple) -> Result<Rid> {
        todo!("3c-01: hold the heap's lock; write-latch the last page; while the tuple does not fit: (an empty page means too large: Err) allocate and init a new page, link it after this one, make it the last; then insert into the page and return its rid")
    }

    /// Replaces the metadata of the tuple at `rid` (for instance to mark it deleted).
    pub fn update_tuple_meta(&self, meta: &TupleMeta, rid: Rid) -> Result<()> {
        todo!("3c-02: write-latch the rid's page and update the slot's metadata")
    }

    /// The tuple at `rid` and its metadata (read together under one latch). The tuple carries `rid`.
    pub fn get_tuple(&self, rid: Rid) -> Result<(TupleMeta, Tuple)> {
        todo!("3c-02: read-latch the rid's page and read the slot")
    }

    /// Just the metadata of the tuple at `rid`.
    pub fn get_tuple_meta(&self, rid: Rid) -> Result<TupleMeta> {
        todo!("3c-02: read-latch the rid's page and read the slot's metadata")
    }

    /// Overwrites the tuple at `rid` with one of the same length, and its metadata, if `check` (when given) approves the old tuple.
    /// Returns whether it did. The check runs under the page's write latch, so nothing can change between the check and the write.
    pub fn update_tuple_in_place(&self, meta: &TupleMeta, tuple: &Tuple, rid: Rid, check: Option<&dyn Fn(&TupleMeta, &Tuple, Rid) -> bool>) -> Result<bool> {
        todo!("3c-02: write-latch the page; read the old tuple; if there is no check or the check approves, overwrite in place and say true; otherwise false")
    }

    /// Runs `f` on the table page of `rid` while holding its **read** latch (module 4a: reading a tuple and its version link together).
    pub fn with_page<R>(&self, rid: Rid, f: impl FnOnce(&TablePage<&[u8]>) -> R) -> R {
        let guard = self.bpm.read_page(rid.page_id());
        f(&TablePage::new(&guard[..]))
    }

    /// Runs `f` on the table page of `rid` while holding its **write** latch (module 4a: changing a tuple and its version link together).
    pub fn with_page_mut<R>(&self, rid: Rid, f: impl FnOnce(&mut TablePage<&mut [u8]>) -> R) -> R {
        let mut guard = self.bpm.write_page(rid.page_id());
        f(&mut TablePage::new(&mut guard[..]))
    }

    /// An iterator over the table as it is **now**: it stops at the last tuple that exists when it is created, so a statement that inserts
    /// into the table it scans (the "Halloween problem") does not see its own output. BusTub's `MakeIterator`.
    pub fn make_iterator(&self) -> TableIterator<'_> {
        todo!("3c-03: remember the last page and how many tuples it has now; start at (first page, slot 0) and stop at (last page, that count)")
    }

    /// An iterator that sees tuples inserted while it runs: it goes on until the table's end. BusTub's `MakeEagerIterator`.
    pub fn make_eager_iterator(&self) -> TableIterator<'_> {
        todo!("3c-03: start at (first page, slot 0) with no stopping point (an invalid rid)")
    }
}
