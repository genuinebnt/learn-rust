//! Port of `test/storage/disk_scheduler_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database Group).
//! The C++ test hands the scheduler `char *` buffers; here each request owns its buffer and gets it back through the future.

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

    let (promise1, future1) = disk_scheduler.create_promise();
    let (promise2, future2) = disk_scheduler.create_promise();

    let r1 = DiskRequest { is_write: true, data: data.clone(), page_id: PageId(0), callback: promise1 };
    disk_scheduler.schedule(vec![r1]);

    let r2 = DiskRequest { is_write: false, data: Box::new([0u8; BUSTUB_PAGE_SIZE]), page_id: PageId(0), callback: promise2 };
    disk_scheduler.schedule(vec![r2]);

    assert!(future1.get().unwrap().is_ok());
    let buf = future2.get().unwrap().unwrap();
    assert!(*buf == *data, "the page read back differs from the page written");

    drop(disk_scheduler); // Call the DiskScheduler destructor to finish all scheduled jobs.
    let _ = dm.delete_page(PageId(0));
}
