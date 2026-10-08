//! BusTub's earlier buffer pool tests (`buffer_pool_manager_instance_test.cpp`, BinaryDataTest and SampleTest, Fall 2019-2022),
//! adapted to this interface: BusTub's old `NewPage(&id)` returned a pinned page; here `new_page()` hands out an id and `fetch_page`
//! pins it. (Copyright (c) 2015-2022 Carnegie Mellon University Database Group, MIT licence.)

use std::sync::Arc;

use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::{PageData, PageId, BUSTUB_PAGE_SIZE};
use bustub::storage::disk::disk_manager::DiskManager;

mod common;
use common::TempDir;

fn write(bpm: &BufferPoolManager, page: PageId, bytes: &[u8]) {
    let frame = bpm.fetch_page(page).expect("a frame");
    bpm.frame_data(frame).write().unwrap()[..bytes.len()].copy_from_slice(bytes);
    // fetch pinned it once; leave that pin to the caller
}

#[test]
fn binary_data_test() {
    let dir = TempDir::new("classic-binary");
    let buffer_pool_size = 10;
    let disk_manager = Arc::new(DiskManager::new(dir.path("test.db")).unwrap());
    let bpm = BufferPoolManager::new(buffer_pool_size, disk_manager.clone());

    // Scenario: The buffer pool is empty. We should be able to create a new page.
    let page_id_temp = bpm.new_page();
    assert_eq!(PageId(0), page_id_temp);
    let frame0 = bpm.fetch_page(page_id_temp).expect("a new page");

    // Generate random binary data
    let mut x: u64 = 0xBEEF;
    let mut random_binary_data: PageData = [0; BUSTUB_PAGE_SIZE];
    for b in random_binary_data.iter_mut() {
        x = x.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        *b = (x >> 33) as u8;
    }
    // Insert terminal characters both in the middle and at end
    random_binary_data[BUSTUB_PAGE_SIZE / 2] = 0;
    random_binary_data[BUSTUB_PAGE_SIZE - 1] = 0;

    // Scenario: Once we have a page, we should be able to read and write content.
    bpm.frame_data(frame0).write().unwrap().copy_from_slice(&random_binary_data);
    assert!(**bpm.frame_data(frame0).read().unwrap() == random_binary_data);

    // Scenario: We should be able to create new pages until we fill up the buffer pool.
    for _ in 1..buffer_pool_size {
        assert!(bpm.fetch_page(bpm.new_page()).is_some());
    }

    // Scenario: Once the buffer pool is full, we should not be able to create any new pages.
    for _ in buffer_pool_size..buffer_pool_size * 2 {
        assert!(bpm.fetch_page(bpm.new_page()).is_none());
    }

    // Scenario: After unpinning pages {0, 1, 2, 3, 4} we should be able to create 5 new pages
    for i in 0..5 {
        assert!(bpm.unpin_page(PageId(i), true));
        bpm.flush_page(PageId(i));
    }
    for _ in 0..5 {
        let page = bpm.new_page();
        assert!(bpm.fetch_page(page).is_some());
        bpm.unpin_page(page, false);
    }

    // Scenario: We should be able to fetch the data we wrote a while ago.
    let frame0 = bpm.fetch_page(PageId(0)).expect("page 0 comes back from disk");
    assert!(**bpm.frame_data(frame0).read().unwrap() == random_binary_data);
    assert!(bpm.unpin_page(PageId(0), true));

    disk_manager.shut_down().unwrap();
}

#[test]
fn sample_test() {
    let dir = TempDir::new("classic-sample");
    let buffer_pool_size = 10;
    let disk_manager = Arc::new(DiskManager::new(dir.path("test.db")).unwrap());
    let bpm = BufferPoolManager::new(buffer_pool_size, disk_manager.clone());

    // Scenario: The buffer pool is empty. We should be able to create a new page.
    let page_id_temp = bpm.new_page();
    assert_eq!(PageId(0), page_id_temp);

    // Scenario: Once we have a page, we should be able to read and write content.
    write(&bpm, page_id_temp, b"Hello\0");
    let frame0 = bpm.fetch_page(page_id_temp).unwrap();
    assert_eq!(&bpm.frame_data(frame0).read().unwrap()[..6], b"Hello\0");
    bpm.unpin_page(page_id_temp, false); // the extra pin from the read above

    // Scenario: We should be able to create new pages until we fill up the buffer pool.
    for _ in 1..buffer_pool_size {
        assert!(bpm.fetch_page(bpm.new_page()).is_some());
    }

    // Scenario: Once the buffer pool is full, we should not be able to create any new pages.
    for _ in buffer_pool_size..buffer_pool_size * 2 {
        assert!(bpm.fetch_page(bpm.new_page()).is_none());
    }

    // Scenario: After unpinning pages {0, 1, 2, 3, 4} and pinning another 4 new pages, there would still be one buffer page
    // left for reading page 0.
    for i in 0..5 {
        assert!(bpm.unpin_page(PageId(i), true));
    }
    for _ in 0..4 {
        assert!(bpm.fetch_page(bpm.new_page()).is_some());
    }

    // Scenario: We should be able to fetch the data we wrote a while ago.
    let frame0 = bpm.fetch_page(PageId(0)).expect("page 0 comes back");
    assert_eq!(&bpm.frame_data(frame0).read().unwrap()[..6], b"Hello\0");

    // Scenario: If we unpin page 0 and then make a new page, all the buffer pages should now be pinned. Fetching page 0 again
    // should fail.
    assert!(bpm.unpin_page(PageId(0), true));
    assert!(bpm.fetch_page(bpm.new_page()).is_some());
    assert!(bpm.fetch_page(PageId(0)).is_none());

    disk_manager.shut_down().unwrap();
}
