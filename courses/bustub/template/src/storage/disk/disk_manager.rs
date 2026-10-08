//! Port of `src/storage/disk/disk_manager.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University
//! Database Group).
//!
//! The disk manager reads and writes pages to and from a file. The file is a row of *slots*, `BUSTUB_PAGE_SIZE`
//! bytes each; a page table says which page lives in which slot, and slots of deleted pages are reused.

use std::collections::HashMap;
use std::fs::{File, OpenOptions};
use std::io::{self, Write};
use std::os::unix::fs::FileExt;
use std::path::{Path, PathBuf};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;

use crate::common::config::{PageData, PageId, BUSTUB_PAGE_SIZE, DEFAULT_DB_IO_SIZE};

/// The byte offset where slot `slot` starts. Slots lie end to end: slot 0 at byte 0, slot 1 at `BUSTUB_PAGE_SIZE`, ...
pub fn slot_offset(slot: usize) -> u64 {
    todo!("1a-01: slot * BUSTUB_PAGE_SIZE, computed as a u64")
}

/// The size of a db file that has room for `capacity` pages. BusTub keeps one spare page: `(capacity + 1)` pages.
pub fn file_size_for(capacity: usize) -> u64 {
    todo!("1a-02: room for capacity pages plus the one spare page")
}

/// Writes `data` into slot `slot` of `file`, extending the file if the slot is past its end.
pub fn write_slot(file: &File, slot: usize, data: &PageData) -> io::Result<()> {
    todo!("1a-05: write the whole page at the slot's byte offset, without moving any cursor")
}

/// Reads into `buf` starting at byte `offset`, until `buf` is full or the file ends. Returns how many bytes it read.
/// A single `read_at` may return fewer bytes than asked for even when more are there, so this keeps asking.
pub fn read_full_at(file: &File, buf: &mut [u8], offset: u64) -> io::Result<usize> {
    todo!("1a-06: loop on read_at until the buffer is full or read_at returns 0 (end of file)")
}

/// Reads slot `slot` into `buf`. Whatever part of the slot the file doesn't have yet reads as zeros.
pub fn read_slot(file: &File, slot: usize, buf: &mut PageData) -> io::Result<()> {
    todo!("1a-07: read_full_at, then zero-fill the rest of the buffer")
}

/// Everything the db file's latch protects: the file itself and the bookkeeping that says where pages are.
struct DbIo {
    file: File,
    /// page id -> the slot holding it. BusTub's `pages_` (which stores byte offsets instead).
    pages: HashMap<PageId, usize>,
    /// Slots whose pages were deleted, newest last. BusTub's `free_slots_`.
    free_slots: Vec<usize>,
    /// How many slots have ever been handed out; the next fresh slot is this number.
    num_slots: usize,
    /// How many pages the file has room for: its length is `file_size_for(page_capacity)`. BusTub's `page_capacity_`.
    page_capacity: usize,
}

impl DbIo {
    /// A slot for a new page: a freed one if there is one, otherwise a fresh slot at the end, growing the file
    /// (doubling `page_capacity`) when the fresh slot would not fit.
    fn allocate_slot(&mut self) -> io::Result<usize> {
        // TODO(1a-12): reuse a freed slot before taking a fresh one
        let slot: usize = todo!("1a-08: the next fresh slot; remember that you've handed it out");
        // TODO(1a-11): when the slot doesn't fit, double page_capacity and resize the file to match
        Ok(slot)
    }
}

/// Reads and writes pages to a database file, and a log to a log file. All methods take `&self`: the disk manager is
/// shared between threads, and the latches inside it (BusTub's `db_io_latch_`) do the locking.
pub struct DiskManager {
    db_file_name: PathBuf,
    log_file_name: PathBuf,
    db_io: Mutex<DbIo>,
    log_io: Mutex<File>,
    num_flushes: AtomicUsize,
    num_writes: AtomicUsize,
    num_deletes: AtomicUsize,
}

impl DiskManager {
    /// Opens the database file `db_file`, creating it if it doesn't exist, and the log file next to it
    /// (`db_file` with its extension replaced by `.log`, also created). Fails if either can't be opened.
    pub fn new(db_file: impl AsRef<Path>) -> io::Result<DiskManager> {
        let db_file_name = db_file.as_ref().to_path_buf();
        let log_file_name: PathBuf = todo!("1a-03: db_file_name with the extension replaced by .log");
        let log_io: File = todo!("1a-03: open (creating) the log file for reading and appending");
        let db: File = todo!("1a-03: open (creating, not truncating) the db file for reading and writing");
        // TODO(1a-04): give the db file room for DEFAULT_DB_IO_SIZE pages (plus the spare one)
        Ok(DiskManager {
            db_file_name,
            log_file_name,
            db_io: Mutex::new(DbIo {
                file: db,
                pages: HashMap::new(),
                free_slots: Vec::new(),
                num_slots: 0,
                page_capacity: DEFAULT_DB_IO_SIZE,
            }),
            log_io: Mutex::new(log_io),
            num_flushes: AtomicUsize::new(0),
            num_writes: AtomicUsize::new(0),
            num_deletes: AtomicUsize::new(0),
        })
    }

    /// Syncs both files to disk and releases the disk manager's hold on them. (BusTub's `ShutDown()`.)
    pub fn shut_down(&self) -> io::Result<()> {
        todo!("1a-19: sync_all both files")
    }

    pub fn db_file_name(&self) -> &Path {
        &self.db_file_name
    }

    pub fn log_file_name(&self) -> &Path {
        &self.log_file_name
    }

    /// The db file's size in bytes right now. (BusTub's `GetDbFileSize()`.)
    pub fn get_db_file_size(&self) -> u64 {
        todo!("1a-04: the length of the db file, from its metadata")
    }

    /// Hands out a slot (see `DbIo::allocate_slot`). Public so the stages can check the allocator on its own;
    /// `write_page` uses it for pages it hasn't seen.
    pub fn allocate_slot(&self) -> io::Result<usize> {
        self.db_io.lock().unwrap().allocate_slot()
    }

    /// The slot holding `page_id`, if the page has been written.
    pub fn slot_of(&self, page_id: PageId) -> Option<usize> {
        self.db_io.lock().unwrap().pages.get(&page_id).copied()
    }

    /// Writes a page. A page the disk manager hasn't seen gets a slot first.
    pub fn write_page(&self, page_id: PageId, data: &PageData) -> io::Result<()> {
        assert!(page_id.is_valid(), "write of invalid page id {}", page_id.0);
        let mut io = self.db_io.lock().unwrap();
        todo!("1a-09: find the page's slot (allocating one for a new page, and remembering it), then write_slot");
        // TODO(1a-13): count this write
        Ok(())
    }

    /// Reads a page into `buf`. A page that was never written reads as zeros.
    pub fn read_page(&self, page_id: PageId, buf: &mut PageData) -> io::Result<()> {
        assert!(page_id.is_valid(), "read of invalid page id {}", page_id.0);
        let io = self.db_io.lock().unwrap();
        todo!("1a-10: read_slot if the page has a slot, otherwise zero the buffer")
    }

    /// Forgets a page and frees its slot for reuse. Deleting a page that doesn't exist does nothing.
    pub fn delete_page(&self, page_id: PageId) {
        let mut io = self.db_io.lock().unwrap();
        // TODO(1a-12): remove the page from the page table and free its slot; return early if it isn't there
        // TODO(1a-13): count this delete
    }

    /// Appends `data` to the log file and counts a flush. An empty `data` does nothing.
    pub fn write_log(&self, data: &[u8]) -> io::Result<()> {
        if data.is_empty() {
            return Ok(());
        }
        let mut log = self.log_io.lock().unwrap();
        todo!("1a-14: append data to the log file and count a flush");
        Ok(())
    }

    /// Reads up to `buf.len()` bytes of the log starting at byte `offset`. Returns `false` if `offset` is at or past
    /// the end of the log (then `buf` is untouched); otherwise `true`, with whatever the log doesn't have zero-filled.
    pub fn read_log(&self, buf: &mut [u8], offset: u64) -> io::Result<bool> {
        let log = self.log_io.lock().unwrap();
        todo!("1a-15: false past the end of the log; otherwise read_full_at and zero-fill the rest")
    }

    pub fn get_num_flushes(&self) -> usize {
        todo!("1a-13: load the counter")
    }

    pub fn get_num_writes(&self) -> usize {
        todo!("1a-13: load the counter")
    }

    pub fn get_num_deletes(&self) -> usize {
        todo!("1a-13: load the counter")
    }
}

/// What the rest of BusTub needs from a disk: read, write and delete pages. [`DiskManager`] is the real one;
/// [`DiskManagerMemory`](super::disk_manager_memory::DiskManagerMemory) and `DiskManagerUnlimitedMemory` keep pages in
/// memory. In BusTub these are virtual methods of the `DiskManager` base class; in Rust that is a trait.
pub trait DiskIo: Send + Sync {
    fn read_page(&self, page_id: PageId, buf: &mut PageData) -> io::Result<()>;
    fn write_page(&self, page_id: PageId, data: &PageData) -> io::Result<()>;
    fn delete_page(&self, page_id: PageId);
}

impl DiskIo for DiskManager {
    fn read_page(&self, page_id: PageId, buf: &mut PageData) -> io::Result<()> {
        todo!("1a-16: call DiskManager's own read_page")
    }
    
    fn write_page(&self, page_id: PageId, data: &PageData) -> io::Result<()> {
        todo!("1a-16: call DiskManager's own write_page")
    }
    
    fn delete_page(&self, page_id: PageId) {
        todo!("1a-16: call DiskManager's own delete_page")
    }
}

/// Copies page `from` to page `to` through any disk.
pub fn copy_page(disk: &dyn DiskIo, from: PageId, to: PageId) -> io::Result<()> {
    todo!("1a-16: read page `from` into a buffer, write the buffer as page `to`")
}
