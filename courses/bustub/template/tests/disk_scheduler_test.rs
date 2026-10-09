//! Port of `test/storage/disk_scheduler_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database Group).
//! The C++ test hands the scheduler `char *` buffers; here each request owns its buffer and gets it back through the future, and it
//! is built with `DiskRequest::write` / `DiskRequest::read` instead of by filling in its fields.

use bustub::common::config::{PageId, BUSTUB_PAGE_SIZE};
use bustub::storage::disk::disk_manager::DiskIo;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;
use bustub::storage::disk::disk_scheduler::{DiskRequest, DiskScheduler};
use std::sync::Arc;

#[test]
fn schedule_write_read_page_test() {
    let mut data = Box::new([0u8; BUSTUB_PAGE_SIZE]);
    data[..14].copy_from_slice(b"A test string.");

    let dm = Arc::new(DiskManagerUnlimitedMemory::new());
    let disk_scheduler = DiskScheduler::new(dm.clone());

    let (r1, future1) = DiskRequest::write(PageId(0), data.clone());
    disk_scheduler.schedule(vec![r1]);

    let (r2, future2) = DiskRequest::read(PageId(0));
    disk_scheduler.schedule(vec![r2]);

    assert!(future1.get().unwrap().is_ok(), "the write should succeed");
    let buf = future2.get().unwrap().unwrap();
    assert!(*buf == *data, "the page read back differs from the page written");

    drop(disk_scheduler); // Call the DiskScheduler destructor to finish all scheduled jobs.
    let _ = dm.delete_page(PageId(0));
}
