//! Port of `test/buffer/buffer_pool_manager_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database Group).
//! The C++ tests share one file name (`test.bustub`); here each test has its own temp directory so they can run in parallel.
//! `page.Drop()` is `release()` (or `drop(guard)`), `GetDataMut()` is `get_data_mut()`, strings are NUL-terminated byte arrays as in C.

mod common;

use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Condvar, Mutex};
use std::thread;
use std::time::Duration;

use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::{PageData, PageId, BUSTUB_PAGE_SIZE};
use bustub::storage::disk::disk_manager::DiskManager;
use bustub::storage::page::page_guard::WritePageGuard;
use common::TempDir;

/// The number of frames we give to the buffer pool.
const FRAMES: usize = 10;

/// `snprintf(dest, BUSTUB_PAGE_SIZE, "%s", src)`: the string and its terminating NUL.
fn copy_string(dest: &mut PageData, src: &str) {
    assert!(src.len() < BUSTUB_PAGE_SIZE, "CopyString src too long");
    dest[..src.len()].copy_from_slice(src.as_bytes());
    dest[src.len()] = 0;
}

/// The C string at the start of `data`.
fn c_str(data: &[u8]) -> &str {
    let end = data.iter().position(|&b| b == 0).unwrap_or(data.len());
    std::str::from_utf8(&data[..end]).unwrap()
}

fn new_bpm(dir: &TempDir, frames: usize) -> (BufferPoolManager, Arc<DiskManager>) {
    let disk_manager = Arc::new(DiskManager::new(dir.path("test.bustub")).unwrap());
    (BufferPoolManager::new(frames, disk_manager.clone()), disk_manager)
}

#[test]
fn very_basic_test() {
    // A very basic test.
    let dir = TempDir::new("bpm-very-basic");
    let (bpm, _dm) = new_bpm(&dir, FRAMES);

    let pid = bpm.new_page();
    let s = "Hello, world!";

    // Check `WritePageGuard` basic functionality.
    {
        let mut guard = bpm.write_page(pid);
        copy_string(guard.get_data_mut(), s);
        assert_eq!(c_str(guard.get_data()), s);
    }

    // Check `ReadPageGuard` basic functionality.
    {
        let guard = bpm.read_page(pid);
        assert_eq!(c_str(guard.get_data()), s);
    }

    // Check `ReadPageGuard` basic functionality (again).
    {
        let guard = bpm.read_page(pid);
        assert_eq!(c_str(guard.get_data()), s);
    }

    assert!(bpm.delete_page(pid));
}

#[test]
fn page_pin_easy_test() {
    let dir = TempDir::new("bpm-pin-easy");
    let (bpm, _dm) = new_bpm(&dir, 2);

    let pageid0 = bpm.new_page();
    let pageid1 = bpm.new_page();

    let str0 = "page0";
    let str1 = "page1";
    let str0updated = "page0updated";
    let str1updated = "page1updated";

    {
        let mut page0_write = bpm.checked_write_page(pageid0).expect("page 0");
        copy_string(page0_write.get_data_mut(), str0);

        let mut page1_write = bpm.checked_write_page(pageid1).expect("page 1");
        copy_string(page1_write.get_data_mut(), str1);

        assert_eq!(Some(1), bpm.get_pin_count(pageid0));
        assert_eq!(Some(1), bpm.get_pin_count(pageid1));

        let temp_page_id1 = bpm.new_page();
        assert!(bpm.checked_read_page(temp_page_id1).is_none());

        let temp_page_id2 = bpm.new_page();
        assert!(bpm.checked_write_page(temp_page_id2).is_none());

        assert_eq!(Some(1), bpm.get_pin_count(pageid0));
        page0_write.release();
        assert_eq!(Some(0), bpm.get_pin_count(pageid0));

        assert_eq!(Some(1), bpm.get_pin_count(pageid1));
        page1_write.release();
        assert_eq!(Some(0), bpm.get_pin_count(pageid1));
    }

    {
        let temp_page_id1 = bpm.new_page();
        let temp_page1_opt = bpm.checked_read_page(temp_page_id1);
        assert!(temp_page1_opt.is_some());

        let temp_page_id2 = bpm.new_page();
        let temp_page2_opt = bpm.checked_write_page(temp_page_id2);
        assert!(temp_page2_opt.is_some());

        assert!(bpm.get_pin_count(pageid0).is_none());
        assert!(bpm.get_pin_count(pageid1).is_none());
    }

    {
        let mut page0_write = bpm.checked_write_page(pageid0).expect("page 0");
        assert_eq!(c_str(page0_write.get_data()), str0);
        copy_string(page0_write.get_data_mut(), str0updated);

        let mut page1_write = bpm.checked_write_page(pageid1).expect("page 1");
        assert_eq!(c_str(page1_write.get_data()), str1);
        copy_string(page1_write.get_data_mut(), str1updated);

        assert_eq!(Some(1), bpm.get_pin_count(pageid0));
        assert_eq!(Some(1), bpm.get_pin_count(pageid1));
    }

    assert_eq!(Some(0), bpm.get_pin_count(pageid0));
    assert_eq!(Some(0), bpm.get_pin_count(pageid1));

    {
        let page0_read = bpm.checked_read_page(pageid0).expect("page 0");
        assert_eq!(c_str(page0_read.get_data()), str0updated);

        let page1_read = bpm.checked_read_page(pageid1).expect("page 1");
        assert_eq!(c_str(page1_read.get_data()), str1updated);

        assert_eq!(Some(1), bpm.get_pin_count(pageid0));
        assert_eq!(Some(1), bpm.get_pin_count(pageid1));
    }

    assert_eq!(Some(0), bpm.get_pin_count(pageid0));
    assert_eq!(Some(0), bpm.get_pin_count(pageid1));
}

#[test]
fn page_pin_medium_test() {
    let dir = TempDir::new("bpm-pin-medium");
    let (bpm, _dm) = new_bpm(&dir, FRAMES);

    // Scenario: The buffer pool is empty. We should be able to create a new page.
    let pid0 = bpm.new_page();
    let mut page0 = bpm.write_page(pid0);

    // Scenario: Once we have a page, we should be able to read and write content.
    let hello = "Hello";
    copy_string(page0.get_data_mut(), hello);
    assert_eq!(c_str(page0.get_data()), hello);

    page0.release();

    // A vector of guards keeps them alive (the C++ test uses a vector of guards too).
    let mut pages: Vec<WritePageGuard> = Vec::new();

    // Scenario: We should be able to create new pages until we fill up the buffer pool.
    for _ in 0..FRAMES {
        let pid = bpm.new_page();
        pages.push(bpm.write_page(pid));
    }

    // Scenario: All of the pin counts should be 1.
    for page in &pages {
        assert_eq!(Some(1), bpm.get_pin_count(page.get_page_id()));
    }

    // Scenario: Once the buffer pool is full, we should not be able to create any new pages.
    for _ in 0..FRAMES {
        let pid = bpm.new_page();
        assert!(bpm.checked_write_page(pid).is_none());
    }

    // Scenario: Drop the first 5 pages to unpin them.
    for _ in 0..FRAMES / 2 {
        let pid = pages[0].get_page_id();
        assert_eq!(Some(1), bpm.get_pin_count(pid));
        pages.remove(0);
        assert_eq!(Some(0), bpm.get_pin_count(pid));
    }

    // Scenario: All of the pin counts of the pages we haven't dropped yet should still be 1.
    for page in &pages {
        assert_eq!(Some(1), bpm.get_pin_count(page.get_page_id()));
    }

    // Scenario: After unpinning pages {1, 2, 3, 4, 5}, we should be able to create 4 new pages and bring them into memory.
    // Bringing those 4 pages into memory should evict the first 4 pages {1, 2, 3, 4}.
    for _ in 0..(FRAMES / 2) - 1 {
        let pid = bpm.new_page();
        pages.push(bpm.write_page(pid));
    }

    // Scenario: There should be one frame available, and we should be able to fetch the data we wrote a while ago.
    {
        let original_page = bpm.read_page(pid0);
        assert_eq!(c_str(original_page.get_data()), hello);
    }

    // Scenario: Once we unpin page 0 and then make a new page, all the buffer pages should now be pinned. Fetching page 0 again
    // should fail.
    let last_pid = bpm.new_page();
    let _last_page = bpm.read_page(last_pid);

    assert!(bpm.checked_read_page(pid0).is_none());
}

#[test]
fn page_access_test() {
    let rounds = 50;
    let dir = TempDir::new("bpm-access");
    let (bpm, _dm) = new_bpm(&dir, 1);

    let pid = bpm.new_page();

    thread::scope(|scope| {
        scope.spawn(|| {
            // The writer can keep writing to the same page.
            for i in 0..rounds {
                thread::sleep(Duration::from_millis(5));
                let mut guard = bpm.write_page(pid);
                copy_string(guard.get_data_mut(), &i.to_string());
            }
        });

        for _ in 0..rounds {
            // Wait for a bit before taking the latch, allowing the writer to write some stuff.
            thread::sleep(Duration::from_millis(10));

            // While we are reading, nobody should be able to modify the data.
            let guard = bpm.read_page(pid);

            // Save the data we observe.
            let buf: PageData = *guard.get_data();

            // Sleep for a bit. If latching is working properly, nothing should be writing to the page.
            thread::sleep(Duration::from_millis(10));

            // Check that the data is unmodified.
            assert_eq!(c_str(guard.get_data()), c_str(&buf));
        }
    });
}

#[test]
fn contention_test() {
    let dir = TempDir::new("bpm-contention");
    let (bpm, _dm) = new_bpm(&dir, FRAMES);

    let rounds = 100_000;
    let pid = bpm.new_page();

    thread::scope(|scope| {
        for _ in 0..4 {
            scope.spawn(|| {
                for i in 0..rounds {
                    let mut guard = bpm.write_page(pid);
                    copy_string(guard.get_data_mut(), &i.to_string());
                }
            });
        }
    });
}

#[test]
fn deadlock_test() {
    let dir = TempDir::new("bpm-deadlock");
    let (bpm, _dm) = new_bpm(&dir, FRAMES);

    let pid0 = bpm.new_page();
    let pid1 = bpm.new_page();

    let mut guard0 = bpm.write_page(pid0);

    // A crude way of synchronizing threads, but works for this small case.
    let start = AtomicBool::new(false);

    thread::scope(|scope| {
        let child = scope.spawn(|| {
            // Acknowledge that we can begin the test.
            start.store(true, Ordering::SeqCst);

            // Attempt to write to page 0.
            let _guard0 = bpm.write_page(pid0);
        });

        // Wait for the other thread to begin before we start the test.
        while !start.load(Ordering::SeqCst) {}

        // Make the other thread wait for a bit.
        // This mimics the main thread doing some work while holding the write latch on page 0.
        thread::sleep(Duration::from_millis(1000));

        // If your latching mechanism is incorrect, the next line of code will deadlock.
        // Think about what might happen if you hold a certain "all-encompassing" latch for too long...

        // While holding page 0, take the latch on page 1.
        let _guard1 = bpm.write_page(pid1);

        // Let the child thread have the page 0 since we're done with it.
        guard0.release();

        child.join().unwrap();
    });
}

#[test]
fn evictable_test() {
    // Test if the evictable status of a frame is always correct.
    let rounds = 1000;
    let num_readers = 8;

    let dir = TempDir::new("bpm-evictable");
    // Only allocate one frame of memory to the buffer pool manager.
    let (bpm, _dm) = new_bpm(&dir, 1);

    for i in 0..rounds {
        let gate = (Mutex::new(false), Condvar::new());

        // This page will be loaded into the only available frame.
        let winner_pid: PageId = bpm.new_page();
        // We will attempt to load this page into the occupied frame, and it should fail every time.
        let loser_pid: PageId = bpm.new_page();

        thread::scope(|scope| {
            let mut readers = Vec::new();
            for _ in 0..num_readers {
                readers.push(scope.spawn(|| {
                    // Wait until the main thread has taken a read latch on the page.
                    let mut signal = gate.0.lock().unwrap();
                    while !*signal {
                        signal = gate.1.wait(signal).unwrap();
                    }
                    drop(signal);

                    // Read the page in shared mode.
                    let _read_guard = bpm.read_page(winner_pid);

                    // Since the only frame is pinned, no thread should be able to bring in a new page.
                    assert!(bpm.checked_read_page(loser_pid).is_none());
                }));
            }

            if i % 2 == 0 {
                // Take the read latch on the page and pin it.
                let mut read_guard = bpm.read_page(winner_pid);

                // Wake up all of the readers.
                *gate.0.lock().unwrap() = true;
                gate.1.notify_all();

                // Allow other threads to read.
                read_guard.release();
            } else {
                // Take the write latch on the page and pin it.
                let mut write_guard = bpm.write_page(winner_pid);

                // Wake up all of the readers.
                *gate.0.lock().unwrap() = true;
                gate.1.notify_all();

                // Allow other threads to read.
                write_guard.release();
            }

            for reader in readers {
                reader.join().unwrap();
            }
        });
    }
}
