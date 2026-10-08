//! Port of `test/storage/disk_manager_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University
//! Database Group). Same four tests; each gets its own temp directory because Rust runs tests in parallel.

mod common;

use bustub::common::config::{PageId, BUSTUB_PAGE_SIZE};
use bustub::storage::disk::disk_manager::DiskManager;
use common::{page_with, TempDir};

#[test]
fn read_write_page_test() {
    let dir = TempDir::new("rw");
    let mut buf = [0u8; BUSTUB_PAGE_SIZE];
    let data = page_with("A test string.");
    let dm = DiskManager::new(dir.path("test.bustub")).unwrap();

    dm.read_page(PageId(0), &mut buf).unwrap(); // tolerate empty read

    dm.write_page(PageId(0), &data).unwrap();
    dm.read_page(PageId(0), &mut buf).unwrap();
    assert!(buf == data, "page 0 should read back what was written");

    buf.fill(0);
    dm.write_page(PageId(5), &data).unwrap();
    dm.read_page(PageId(5), &mut buf).unwrap();
    assert!(buf == data, "page 5 should read back what was written");

    dm.shut_down().unwrap();
}

#[test]
fn read_write_log_test() {
    let dir = TempDir::new("log");
    let mut buf = [0u8; 16];
    let mut data = [0u8; 16];
    data[..14].copy_from_slice(b"A test string.");
    let dm = DiskManager::new(dir.path("test.bustub")).unwrap();

    dm.read_log(&mut buf, 0).unwrap(); // tolerate empty read

    dm.write_log(&data).unwrap();
    dm.read_log(&mut buf, 0).unwrap();
    assert_eq!(buf, data);

    dm.shut_down().unwrap();
}

#[test]
fn delete_page_test() {
    let dir = TempDir::new("delete");
    let mut buf = [0u8; BUSTUB_PAGE_SIZE];
    let dm = DiskManager::new(dir.path("test.bustub")).unwrap();
    let initial_size = dm.get_db_file_size();

    dm.read_page(PageId(0), &mut buf).unwrap(); // tolerate empty read

    let mut data = page_with("A test string.");
    let mut pages_to_write = 100;
    for page_id in 0..pages_to_write {
        dm.write_page(PageId(page_id), &data).unwrap();
        dm.read_page(PageId(page_id), &mut buf).unwrap();
        assert!(buf == data, "page {page_id} should read back what was written");
    }

    let size_after_write = dm.get_db_file_size();
    assert!(size_after_write >= initial_size);

    pages_to_write *= 2;
    data = page_with("test string version 2");
    for page_id in 0..pages_to_write {
        dm.write_page(PageId(page_id), &data).unwrap();
        dm.read_page(PageId(page_id), &mut buf).unwrap();
        assert!(buf == data, "page {page_id} should read back what was written");

        dm.delete_page(PageId(page_id));
    }

    // expect no change in file size after delete because we're reclaiming space
    let size_after_delete = dm.get_db_file_size();
    assert_eq!(size_after_delete, size_after_write);

    dm.shut_down().unwrap();
}

#[test]
fn throw_bad_file_test() {
    // BusTub throws an `Exception`; here the constructor returns an `Err`.
    assert!(DiskManager::new("dev/null\\/foo/bar/baz/test.bustub").is_err());
}
