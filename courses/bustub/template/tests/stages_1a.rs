//! Tests for the disk manager stages (1a-01 … 1a-04). Each test name starts with its stage: `s1a_04_…` belongs to
//! stage 1a-01, and `anneal course test` runs just those.

mod common;

use std::fs::OpenOptions;
use std::io;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::thread;

use bustub::common::config::{PageData, PageId, BUSTUB_PAGE_SIZE, DEFAULT_DB_IO_SIZE};
use bustub::storage::disk::disk_manager::{copy_page, file_size_for, read_full_at, read_slot, slot_offset, write_slot, DiskIo, DiskManager};
use bustub::storage::disk::disk_manager_memory::{DiskManagerMemory, DiskManagerUnlimitedMemory};
use common::{page_of, page_with, pattern, TempDir};

const PS: usize = BUSTUB_PAGE_SIZE;

fn open_rw(path: &std::path::Path) -> std::fs::File {
    OpenOptions::new().read(true).write(true).create(true).truncate(false).open(path).unwrap()
}

fn new_dm(dir: &TempDir) -> DiskManager {
    DiskManager::new(dir.path("test.bustub")).unwrap()
}

// ---- 1a-01 · slot_offset -----------------------------------------------------------------------------------------

#[test]
fn s1a_01_slot_zero_starts_at_byte_zero() {
    assert_eq!(slot_offset(0), 0);
}

#[test]
fn s1a_01_slots_are_one_page_apart() {
    assert_eq!(slot_offset(1), 8192);
    assert_eq!(slot_offset(3), 3 * 8192);
    assert_eq!(slot_offset(10) - slot_offset(9), PS as u64);
}

#[test]
fn s1a_01_offsets_past_four_gigabytes_dont_overflow() {
    // 1_000_000 * 8192 = 8_192_000_000 does not fit in a u32.
    assert_eq!(slot_offset(1_000_000), 8_192_000_000);
}

// ---- 1a-01 · file_size_for ---------------------------------------------------------------------------------------

#[test]
fn s1a_02_file_size_has_one_spare_page() {
    assert_eq!(file_size_for(0), 8192);
    assert_eq!(file_size_for(16), 17 * 8192);
    assert_eq!(file_size_for(DEFAULT_DB_IO_SIZE), 139_264);
}

#[test]
fn s1a_02_file_size_doubles_with_capacity() {
    assert_eq!(file_size_for(32) - file_size_for(16), 16 * 8192);
}

// ---- 1a-01 · DiskManager::new ------------------------------------------------------------------------------------

#[test]
fn s1a_03_creates_the_db_file() {
    let dir = TempDir::new("s03a");
    let path = dir.path("test.bustub");
    assert!(!path.exists());
    let _dm = DiskManager::new(&path).unwrap();
    assert!(path.is_file());
}

#[test]
fn s1a_03_creates_the_log_file_next_to_it() {
    let dir = TempDir::new("s03b");
    let dm = DiskManager::new(dir.path("test.bustub")).unwrap();
    assert_eq!(dm.log_file_name(), dir.path("test.log"));
    assert!(dm.log_file_name().is_file());
    assert_eq!(dm.db_file_name(), dir.path("test.bustub"));
}

#[test]
fn s1a_03_the_log_name_replaces_only_the_last_extension() {
    let dir = TempDir::new("s03c");
    let dm = DiskManager::new(dir.path("my.data.db")).unwrap();
    assert_eq!(dm.log_file_name(), dir.path("my.data.log"));
}

#[test]
fn s1a_03_a_file_without_an_extension_gets_one() {
    let dir = TempDir::new("s03d");
    let dm = DiskManager::new(dir.path("plain")).unwrap();
    assert_eq!(dm.log_file_name(), dir.path("plain.log"));
}

#[test]
fn s1a_03_keeps_what_an_existing_db_file_holds() {
    let dir = TempDir::new("s03e");
    let path = dir.path("test.bustub");
    std::fs::write(&path, b"hello").unwrap();
    let _dm = DiskManager::new(&path).unwrap();
    assert_eq!(&std::fs::read(&path).unwrap()[..5], b"hello");
}

#[test]
fn s1a_03_a_directory_that_doesnt_exist_is_an_error_not_a_panic() {
    let dir = TempDir::new("s03f");
    let err = DiskManager::new(dir.path("no/such/dir/test.bustub")).err().expect("new should fail");
    assert_eq!(err.kind(), io::ErrorKind::NotFound);
}

#[test]
fn s1a_03_a_path_that_is_a_directory_is_an_error() {
    let dir = TempDir::new("s03g");
    assert!(DiskManager::new(dir.dir()).is_err());
}

// ---- 1a-01 · pre-size the file -----------------------------------------------------------------------------------

#[test]
fn s1a_04_a_new_db_file_has_room_for_the_default_pages() {
    let dir = TempDir::new("s04a");
    let dm = new_dm(&dir);
    assert_eq!(dm.get_db_file_size(), file_size_for(DEFAULT_DB_IO_SIZE));
    assert_eq!(dm.get_db_file_size(), 17 * 8192);
}

#[test]
fn s1a_04_the_size_is_what_the_file_system_says() {
    let dir = TempDir::new("s04b");
    let dm = new_dm(&dir);
    assert_eq!(std::fs::metadata(dir.path("test.bustub")).unwrap().len(), dm.get_db_file_size());
}

#[test]
fn s1a_04_the_new_room_reads_as_zeros() {
    let dir = TempDir::new("s04c");
    let _dm = new_dm(&dir);
    let bytes = std::fs::read(dir.path("test.bustub")).unwrap();
    assert!(bytes.iter().all(|&b| b == 0));
}

#[test]
fn s1a_04_opening_again_keeps_the_size() {
    let dir = TempDir::new("s04d");
    let first = new_dm(&dir).get_db_file_size();
    let second = new_dm(&dir).get_db_file_size();
    assert_eq!(first, second);
}

#[test]
fn s1a_04_contents_inside_the_room_survive_reopening() {
    let dir = TempDir::new("s04e");
    let path = dir.path("test.bustub");
    std::fs::write(&path, vec![7u8; 100]).unwrap();
    let dm = DiskManager::new(&path).unwrap();
    let bytes = std::fs::read(&path).unwrap();
    assert_eq!(bytes.len() as u64, dm.get_db_file_size());
    assert!(bytes[..100].iter().all(|&b| b == 7));
    assert!(bytes[100..].iter().all(|&b| b == 0));
}

// ---- 1a-01 · write_slot ------------------------------------------------------------------------------------------

#[test]
fn s1a_05_writes_at_the_slots_offset() {
    let dir = TempDir::new("s05a");
    let path = dir.path("f");
    let file = open_rw(&path);
    write_slot(&file, 2, &page_of(0xAB)).unwrap();
    let bytes = std::fs::read(&path).unwrap();
    assert_eq!(bytes.len(), 3 * PS, "writing slot 2 makes the file 3 pages long");
    assert!(bytes[..2 * PS].iter().all(|&b| b == 0), "slots 0 and 1 are a hole of zeros");
    assert!(bytes[2 * PS..].iter().all(|&b| b == 0xAB));
}

#[test]
fn s1a_05_slot_zero_is_the_start_of_the_file() {
    let dir = TempDir::new("s05b");
    let path = dir.path("f");
    let file = open_rw(&path);
    write_slot(&file, 0, &pattern(1)).unwrap();
    assert!(std::fs::read(&path).unwrap() == pattern(1));
}

#[test]
fn s1a_05_overwriting_a_slot_replaces_it_in_place() {
    let dir = TempDir::new("s05c");
    let path = dir.path("f");
    let file = open_rw(&path);
    write_slot(&file, 1, &page_of(1)).unwrap();
    write_slot(&file, 1, &page_of(2)).unwrap();
    let bytes = std::fs::read(&path).unwrap();
    assert_eq!(bytes.len(), 2 * PS);
    assert!(bytes[PS..].iter().all(|&b| b == 2));
}

#[test]
fn s1a_05_neighbouring_slots_dont_disturb_each_other() {
    let dir = TempDir::new("s05d");
    let path = dir.path("f");
    let file = open_rw(&path);
    write_slot(&file, 0, &page_of(1)).unwrap();
    write_slot(&file, 2, &page_of(3)).unwrap();
    write_slot(&file, 1, &page_of(2)).unwrap();
    let bytes = std::fs::read(&path).unwrap();
    for (slot, want) in [(0, 1u8), (1, 2), (2, 3)] {
        assert!(bytes[slot * PS..(slot + 1) * PS].iter().all(|&b| b == want), "slot {slot}");
    }
}

#[test]
fn s1a_05_the_order_of_writes_doesnt_matter_because_nothing_has_a_cursor() {
    let dir = TempDir::new("s05e");
    let path = dir.path("f");
    let file = open_rw(&path);
    for slot in [5, 1, 3, 0, 4, 2] {
        write_slot(&file, slot, &pattern(slot)).unwrap();
    }
    let bytes = std::fs::read(&path).unwrap();
    for slot in 0..6 {
        assert!(bytes[slot * PS..(slot + 1) * PS] == pattern(slot), "slot {slot}");
    }
}

#[test]
fn s1a_05_a_read_only_file_is_an_error() {
    let dir = TempDir::new("s05f");
    let path = dir.path("f");
    std::fs::write(&path, b"x").unwrap();
    let file = OpenOptions::new().read(true).open(&path).unwrap();
    assert!(write_slot(&file, 0, &page_of(1)).is_err());
}

// ---- 1a-01 · read_full_at ----------------------------------------------------------------------------------------

#[test]
fn s1a_06_read_full_at_says_how_many_bytes_it_got() {
    let dir = TempDir::new("s06e");
    let path = dir.path("f");
    std::fs::write(&path, b"0123456789").unwrap();
    let file = open_rw(&path);
    let mut buf = [0u8; 4];
    assert_eq!(read_full_at(&file, &mut buf, 0).unwrap(), 4);
    assert_eq!(&buf, b"0123");
    assert_eq!(read_full_at(&file, &mut buf, 8).unwrap(), 2);
    assert_eq!(&buf[..2], b"89");
    assert_eq!(read_full_at(&file, &mut buf, 10).unwrap(), 0);
    assert_eq!(read_full_at(&file, &mut buf, 1000).unwrap(), 0);
}

#[test]
fn s1a_06_read_full_at_leaves_the_rest_of_the_buffer_alone() {
    let dir = TempDir::new("s06f");
    let path = dir.path("f");
    std::fs::write(&path, b"ab").unwrap();
    let file = open_rw(&path);
    let mut buf = [b'x'; 5];
    assert_eq!(read_full_at(&file, &mut buf, 0).unwrap(), 2);
    assert_eq!(&buf, b"abxxx");
}

#[test]
fn s1a_06_read_full_at_with_an_empty_buffer_reads_nothing() {
    let dir = TempDir::new("s06g");
    let file = open_rw(&dir.path("f"));
    assert_eq!(read_full_at(&file, &mut [], 0).unwrap(), 0);
}

#[test]
fn s1a_06_big_reads_arrive_complete() {
    // One `read_at` call may return less than asked for; the loop has to go on.
    let dir = TempDir::new("s06h");
    let path = dir.path("f");
    let data: Vec<u8> = (0..3_000_000u32).map(|i| (i % 253) as u8).collect();
    std::fs::write(&path, &data).unwrap();
    let file = open_rw(&path);
    let mut buf = vec![0u8; data.len()];
    assert_eq!(read_full_at(&file, &mut buf, 0).unwrap(), data.len());
    assert!(buf == data);
}

// ---- 1a-01 · read_slot -------------------------------------------------------------------------------------------

#[test]
fn s1a_07_reads_back_what_write_slot_wrote() {
    let dir = TempDir::new("s07a");
    let file = open_rw(&dir.path("f"));
    write_slot(&file, 3, &pattern(9)).unwrap();
    let mut buf = [0u8; PS];
    read_slot(&file, 3, &mut buf).unwrap();
    assert!(buf == pattern(9));
}

#[test]
fn s1a_07_a_short_file_reads_as_data_then_zeros() {
    let dir = TempDir::new("s07b");
    let path = dir.path("f");
    std::fs::write(&path, vec![7u8; 100]).unwrap();
    let file = open_rw(&path);
    let mut buf = [0xFFu8; PS];
    read_slot(&file, 0, &mut buf).unwrap();
    assert!(buf[..100].iter().all(|&b| b == 7));
    assert!(buf[100..].iter().all(|&b| b == 0), "the part the file doesn't have must be zeroed, not left alone");
}

#[test]
fn s1a_07_a_slot_past_the_end_is_all_zeros() {
    let dir = TempDir::new("s07c");
    let file = open_rw(&dir.path("f"));
    let mut buf = [0xFFu8; PS];
    read_slot(&file, 40, &mut buf).unwrap();
    assert!(buf == page_of(0));
}

#[test]
fn s1a_07_a_slot_that_ends_exactly_at_the_end_needs_no_filling() {
    let dir = TempDir::new("s07d");
    let file = open_rw(&dir.path("f"));
    write_slot(&file, 1, &page_of(5)).unwrap();
    let mut buf = [0u8; PS];
    read_slot(&file, 1, &mut buf).unwrap();
    assert!(buf == page_of(5));
}

// ---- 1a-02 · allocate_slot (fresh slots) -------------------------------------------------------------------------

#[test]
fn s1a_08_the_first_slot_is_zero() {
    let dir = TempDir::new("s08a");
    assert_eq!(new_dm(&dir).allocate_slot().unwrap(), 0);
}

#[test]
fn s1a_08_slots_count_up() {
    let dir = TempDir::new("s08b");
    let dm = new_dm(&dir);
    let got: Vec<usize> = (0..10).map(|_| dm.allocate_slot().unwrap()).collect();
    assert_eq!(got, (0..10).collect::<Vec<_>>());
}

#[test]
fn s1a_08_every_slot_is_handed_out_once() {
    let dir = TempDir::new("s08c");
    let dm = new_dm(&dir);
    let mut seen = std::collections::HashSet::new();
    for _ in 0..200 {
        assert!(seen.insert(dm.allocate_slot().unwrap()));
    }
}

#[test]
fn s1a_08_threads_never_get_the_same_slot() {
    let dir = TempDir::new("s08d");
    let dm = Arc::new(new_dm(&dir));
    let handles: Vec<_> = (0..4)
        .map(|_| {
            let dm = Arc::clone(&dm);
            thread::spawn(move || (0..25).map(|_| dm.allocate_slot().unwrap()).collect::<Vec<_>>())
        })
        .collect();
    let mut all: Vec<usize> = handles.into_iter().flat_map(|h| h.join().unwrap()).collect();
    all.sort();
    assert_eq!(all, (0..100).collect::<Vec<_>>());
}

// ---- 1a-02 · write_page ------------------------------------------------------------------------------------------

#[test]
fn s1a_09_page_ids_need_not_be_dense() {
    // The page table maps ids to slots: ids 1000 and 3 take slots 0 and 1, not slots 1000 and 3.
    let dir = TempDir::new("s09d");
    let dm = new_dm(&dir);
    dm.write_page(PageId(1000), &pattern(1)).unwrap();
    dm.write_page(PageId(3), &pattern(2)).unwrap();
    assert_eq!(dm.slot_of(PageId(1000)), Some(0));
    assert_eq!(dm.slot_of(PageId(3)), Some(1));
    assert_eq!(dm.slot_of(PageId(4)), None);
    assert_eq!(dm.allocate_slot().unwrap(), 2);
}

#[test]
fn s1a_09_rewriting_a_page_keeps_its_slot() {
    let dir = TempDir::new("s09e");
    let dm = new_dm(&dir);
    dm.write_page(PageId(5), &page_of(1)).unwrap();
    dm.write_page(PageId(5), &page_of(2)).unwrap();
    assert_eq!(dm.slot_of(PageId(5)), Some(0));
    assert_eq!(dm.allocate_slot().unwrap(), 1, "a rewrite must not use up a second slot");
    let bytes = std::fs::read(dir.path("test.bustub")).unwrap();
    assert!(bytes[..PS] == page_of(2), "the second write replaced the first, in the same slot");
}

#[test]
fn s1a_09_a_new_page_gets_the_next_slot_and_is_remembered() {
    let dir = TempDir::new("s09a");
    let dm = new_dm(&dir);
    assert_eq!(dm.slot_of(PageId(7)), None);
    dm.write_page(PageId(7), &page_of(1)).unwrap();
    assert_eq!(dm.slot_of(PageId(7)), Some(0));
    dm.write_page(PageId(8), &page_of(2)).unwrap();
    assert_eq!(dm.slot_of(PageId(8)), Some(1));
    assert_eq!(dm.slot_of(PageId(7)), Some(0), "earlier pages stay where they are");
}

#[test]
fn s1a_09_every_page_lands_in_its_own_slot_of_the_file() {
    let dir = TempDir::new("s09b");
    let dm = new_dm(&dir);
    for id in [30, 10, 20] {
        dm.write_page(PageId(id), &pattern(id as usize)).unwrap();
    }
    let bytes = std::fs::read(dir.path("test.bustub")).unwrap();
    for (slot, id) in [30usize, 10, 20].into_iter().enumerate() {
        assert!(bytes[slot * PS..(slot + 1) * PS] == pattern(id), "page {id} should be in slot {slot}");
    }
}

#[test]
fn s1a_09_written_pages_are_in_the_file_at_their_slots() {
    let dir = TempDir::new("s09g");
    let dm = new_dm(&dir);
    dm.write_page(PageId(42), &pattern(42)).unwrap();
    let bytes = std::fs::read(dir.path("test.bustub")).unwrap();
    assert!(bytes[..PS] == pattern(42), "page 42 is the first page written, so it lives in slot 0");
}

#[test]
#[should_panic(expected = "invalid page id")]
fn s1a_09_writing_the_invalid_page_id_panics() {
    let dir = TempDir::new("s09h");
    let _ = new_dm(&dir).write_page(PageId::INVALID, &page_of(1));
}

// ---- 1a-02 · read_page -------------------------------------------------------------------------------------------

#[test]
fn s1a_10_a_page_reads_back_what_was_written() {
    let dir = TempDir::new("s10a");
    let dm = new_dm(&dir);
    dm.write_page(PageId(0), &page_with("A test string.")).unwrap();
    let mut buf = [0u8; PS];
    dm.read_page(PageId(0), &mut buf).unwrap();
    assert!(buf == page_with("A test string."));
}

#[test]
fn s1a_10_a_page_never_written_reads_as_zeros() {
    let dir = TempDir::new("s10b");
    let dm = new_dm(&dir);
    let mut buf = [0xFFu8; PS];
    dm.read_page(PageId(7), &mut buf).unwrap();
    assert!(buf == page_of(0));
}

#[test]
fn s1a_10_pages_dont_interfere() {
    let dir = TempDir::new("s10c");
    let dm = new_dm(&dir);
    for id in 0..10 {
        dm.write_page(PageId(id), &pattern(id as usize)).unwrap();
    }
    for id in (0..10).rev() {
        let mut buf = [0u8; PS];
        dm.read_page(PageId(id), &mut buf).unwrap();
        assert!(buf == pattern(id as usize), "page {id}");
    }
}

#[test]
fn s1a_10_reading_does_not_allocate() {
    let dir = TempDir::new("s10f");
    let dm = new_dm(&dir);
    let mut buf = [0u8; PS];
    for id in 0..5 {
        dm.read_page(PageId(id), &mut buf).unwrap();
    }
    assert_eq!(dm.slot_of(PageId(0)), None);
    assert_eq!(dm.allocate_slot().unwrap(), 0);
}

// ---- 1a-02 · growing the file ------------------------------------------------------------------------------------

#[test]
fn s1a_11_the_file_keeps_its_size_while_slots_fit() {
    let dir = TempDir::new("s11a");
    let dm = new_dm(&dir);
    for _ in 0..16 {
        dm.allocate_slot().unwrap();
    }
    assert_eq!(dm.get_db_file_size(), 17 * PS as u64);
}

#[test]
fn s1a_11_the_slot_that_doesnt_fit_doubles_the_capacity() {
    let dir = TempDir::new("s11b");
    let dm = new_dm(&dir);
    for _ in 0..16 {
        dm.allocate_slot().unwrap();
    }
    assert_eq!(dm.allocate_slot().unwrap(), 16);
    assert_eq!(dm.get_db_file_size(), 33 * PS as u64, "capacity 16 -> 32 pages, plus the spare page");
}

#[test]
fn s1a_11_it_doubles_again_and_again() {
    let dir = TempDir::new("s11c");
    let dm = new_dm(&dir);
    for _ in 0..33 {
        dm.allocate_slot().unwrap();
    }
    assert_eq!(dm.get_db_file_size(), 65 * PS as u64);
    for _ in 0..32 {
        dm.allocate_slot().unwrap();
    }
    assert_eq!(dm.get_db_file_size(), 129 * PS as u64);
}

#[test]
fn s1a_11_a_hundred_pages_leave_a_file_of_129_pages() {
    let dir = TempDir::new("s11d");
    let dm = new_dm(&dir);
    for id in 0..100 {
        dm.write_page(PageId(id), &pattern(id as usize)).unwrap();
    }
    assert_eq!(dm.get_db_file_size(), 129 * PS as u64);
}

#[test]
fn s1a_11_pages_survive_the_growth() {
    let dir = TempDir::new("s11e");
    let dm = new_dm(&dir);
    for id in 0..70 {
        dm.write_page(PageId(id), &pattern(id as usize)).unwrap();
    }
    for id in 0..70 {
        let mut buf = [0u8; PS];
        dm.read_page(PageId(id), &mut buf).unwrap();
        assert!(buf == pattern(id as usize), "page {id}");
    }
}

#[test]
fn s1a_11_the_size_is_always_a_power_of_two_of_pages_plus_one() {
    let dir = TempDir::new("s11f");
    let dm = new_dm(&dir);
    for n in 1..=200usize {
        dm.allocate_slot().unwrap();
        let capacity = n.next_power_of_two().max(16);
        assert_eq!(dm.get_db_file_size(), ((capacity + 1) * PS) as u64, "after {n} slots");
    }
}

// ---- 1a-02 · delete_page and the free list -----------------------------------------------------------------------

#[test]
fn s1a_12_a_deleted_page_reads_as_zeros_again() {
    let dir = TempDir::new("s12a");
    let dm = new_dm(&dir);
    dm.write_page(PageId(1), &page_of(9)).unwrap();
    dm.delete_page(PageId(1));
    let mut buf = [0xFFu8; PS];
    dm.read_page(PageId(1), &mut buf).unwrap();
    assert!(buf == page_of(0));
    assert_eq!(dm.slot_of(PageId(1)), None);
}

#[test]
fn s1a_12_the_newest_freed_slot_is_reused_first() {
    let dir = TempDir::new("s12b");
    let dm = new_dm(&dir);
    for id in [1, 2, 3] {
        dm.write_page(PageId(id), &page_of(id as u8)).unwrap();
    }
    assert_eq!((dm.slot_of(PageId(1)), dm.slot_of(PageId(2)), dm.slot_of(PageId(3))), (Some(0), Some(1), Some(2)));
    dm.delete_page(PageId(1)); // frees slot 0
    dm.delete_page(PageId(3)); // frees slot 2
    dm.write_page(PageId(10), &page_of(10)).unwrap();
    dm.write_page(PageId(11), &page_of(11)).unwrap();
    assert_eq!(dm.slot_of(PageId(10)), Some(2), "last freed, first reused");
    assert_eq!(dm.slot_of(PageId(11)), Some(0));
    assert_eq!(dm.allocate_slot().unwrap(), 3, "only now a fresh slot");
}

#[test]
fn s1a_12_reusing_a_slot_does_not_leave_the_old_pages_bytes() {
    let dir = TempDir::new("s12c");
    let dm = new_dm(&dir);
    dm.write_page(PageId(1), &page_of(1)).unwrap();
    dm.delete_page(PageId(1));
    dm.write_page(PageId(2), &page_of(2)).unwrap();
    let mut buf = [0u8; PS];
    dm.read_page(PageId(2), &mut buf).unwrap();
    assert!(buf == page_of(2));
    dm.read_page(PageId(1), &mut buf).unwrap();
    assert!(buf == page_of(0), "page 1 is gone");
}

#[test]
fn s1a_12_deleting_an_unknown_page_does_nothing() {
    let dir = TempDir::new("s12d");
    let dm = new_dm(&dir);
    dm.delete_page(PageId(77));
    assert_eq!(dm.allocate_slot().unwrap(), 0, "nothing was freed, so the next slot is a fresh one");
}

#[test]
fn s1a_12_deleting_twice_frees_the_slot_once() {
    let dir = TempDir::new("s12e");
    let dm = new_dm(&dir);
    dm.write_page(PageId(1), &page_of(1)).unwrap();
    dm.delete_page(PageId(1));
    dm.delete_page(PageId(1));
    let a = dm.allocate_slot().unwrap();
    let b = dm.allocate_slot().unwrap();
    assert_eq!((a, b), (0, 1), "a double free would hand slot 0 out twice");
}

#[test]
fn s1a_12_recycling_slots_keeps_the_file_from_growing() {
    let dir = TempDir::new("s12f");
    let dm = new_dm(&dir);
    for id in 0..40 {
        dm.write_page(PageId(id), &page_of(1)).unwrap();
    }
    let size = dm.get_db_file_size();
    for id in 0..40 {
        dm.delete_page(PageId(id));
    }
    for id in 100..140 {
        dm.write_page(PageId(id), &page_of(2)).unwrap();
    }
    assert_eq!(dm.get_db_file_size(), size);
}

// ---- 1a-03 · counters --------------------------------------------------------------------------------------------

#[test]
fn s1a_13_counters_start_at_zero() {
    let dir = TempDir::new("s13a");
    let dm = new_dm(&dir);
    assert_eq!((dm.get_num_writes(), dm.get_num_deletes(), dm.get_num_flushes()), (0, 0, 0));
}

#[test]
fn s1a_13_every_write_counts_including_rewrites() {
    let dir = TempDir::new("s13b");
    let dm = new_dm(&dir);
    dm.write_page(PageId(0), &page_of(1)).unwrap();
    dm.write_page(PageId(0), &page_of(2)).unwrap();
    dm.write_page(PageId(1), &page_of(3)).unwrap();
    assert_eq!(dm.get_num_writes(), 3);
}

#[test]
fn s1a_13_reads_dont_count() {
    let dir = TempDir::new("s13c");
    let dm = new_dm(&dir);
    dm.write_page(PageId(0), &page_of(1)).unwrap();
    let mut buf = [0u8; PS];
    dm.read_page(PageId(0), &mut buf).unwrap();
    dm.read_page(PageId(9), &mut buf).unwrap();
    assert_eq!(dm.get_num_writes(), 1);
}

#[test]
fn s1a_13_only_deletes_that_found_a_page_count() {
    let dir = TempDir::new("s13d");
    let dm = new_dm(&dir);
    dm.write_page(PageId(0), &page_of(1)).unwrap();
    dm.delete_page(PageId(0));
    dm.delete_page(PageId(0));
    dm.delete_page(PageId(99));
    assert_eq!(dm.get_num_deletes(), 1);
}

#[test]
fn s1a_13_counting_works_from_many_threads() {
    let dir = TempDir::new("s13e");
    let dm = Arc::new(new_dm(&dir));
    let handles: Vec<_> = (0..8)
        .map(|t| {
            let dm = Arc::clone(&dm);
            thread::spawn(move || {
                for i in 0..50 {
                    dm.write_page(PageId(t * 100 + i), &page_of(1)).unwrap();
                }
            })
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    assert_eq!(dm.get_num_writes(), 400);
}

// ---- 1a-03 · write_log -------------------------------------------------------------------------------------------

#[test]
fn s1a_14_an_empty_write_is_not_a_flush() {
    let dir = TempDir::new("s14f");
    let dm = new_dm(&dir);
    dm.write_log(b"").unwrap();
    assert_eq!(dm.get_num_flushes(), 0);
    dm.write_log(b"x").unwrap();
    dm.write_log(b"y").unwrap();
    assert_eq!(dm.get_num_flushes(), 2);
}

#[test]
fn s1a_14_records_are_appended_to_the_log_file() {
    let dir = TempDir::new("s14a");
    let dm = new_dm(&dir);
    dm.write_log(b"abc").unwrap();
    dm.write_log(b"def").unwrap();
    assert_eq!(std::fs::read(dir.path("test.log")).unwrap(), b"abcdef");
}

#[test]
fn s1a_14_every_non_empty_write_is_one_flush() {
    let dir = TempDir::new("s14b");
    let dm = new_dm(&dir);
    for i in 0..5 {
        dm.write_log(&[i]).unwrap();
    }
    assert_eq!(dm.get_num_flushes(), 5);
}

#[test]
fn s1a_14_appending_after_reopening_keeps_the_old_records() {
    let dir = TempDir::new("s14c");
    new_dm(&dir).write_log(b"one").unwrap();
    new_dm(&dir).write_log(b"two").unwrap();
    assert_eq!(std::fs::read(dir.path("test.log")).unwrap(), b"onetwo");
}

#[test]
fn s1a_14_the_log_is_its_own_file() {
    let dir = TempDir::new("s14h");
    let dm = new_dm(&dir);
    dm.write_log(b"log bytes").unwrap();
    assert_eq!(std::fs::read(dir.path("test.log")).unwrap(), b"log bytes");
    assert!(std::fs::read(dir.path("test.bustub")).unwrap().iter().all(|&b| b == 0), "the db file is untouched");
}

#[derive(Default)]
struct CountingDisk {
    reads: AtomicUsize,
    writes: AtomicUsize,
    deletes: AtomicUsize,
}

impl DiskIo for CountingDisk {
    fn read_page(&self, _: PageId, buf: &mut PageData) -> io::Result<()> {
        self.reads.fetch_add(1, Ordering::SeqCst);
        buf.fill(0x5A);
        Ok(())
    }
    fn write_page(&self, _: PageId, data: &PageData) -> io::Result<()> {
        assert!(*data == page_of(0x5A), "copy_page must write exactly what it read");
        self.writes.fetch_add(1, Ordering::SeqCst);
        Ok(())
    }
    fn delete_page(&self, _: PageId) {
        self.deletes.fetch_add(1, Ordering::SeqCst);
    }
}

// ---- 1a-03 · read_log --------------------------------------------------------------------------------------------

#[test]
fn s1a_15_a_log_record_reads_back() {
    let dir = TempDir::new("s15a");
    let dm = new_dm(&dir);
    dm.write_log(b"A test string.").unwrap();
    let mut buf = [0u8; 14];
    assert!(dm.read_log(&mut buf, 0).unwrap());
    assert_eq!(&buf, b"A test string.");
}

#[test]
fn s1a_15_records_are_appended_in_order() {
    let dir = TempDir::new("s15b");
    let dm = new_dm(&dir);
    dm.write_log(b"abc").unwrap();
    dm.write_log(b"def").unwrap();
    let mut all = [0u8; 6];
    assert!(dm.read_log(&mut all, 0).unwrap());
    assert_eq!(&all, b"abcdef");
    let mut tail = [0u8; 3];
    assert!(dm.read_log(&mut tail, 3).unwrap());
    assert_eq!(&tail, b"def");
}

#[test]
fn s1a_15_reading_an_empty_log_says_no_and_leaves_the_buffer() {
    let dir = TempDir::new("s15c");
    let dm = new_dm(&dir);
    let mut buf = [9u8; 4];
    assert!(!dm.read_log(&mut buf, 0).unwrap());
    assert_eq!(buf, [9; 4]);
}

#[test]
fn s1a_15_reading_at_or_past_the_end_says_no() {
    let dir = TempDir::new("s15d");
    let dm = new_dm(&dir);
    dm.write_log(b"abc").unwrap();
    let mut buf = [9u8; 2];
    assert!(!dm.read_log(&mut buf, 3).unwrap());
    assert!(!dm.read_log(&mut buf, 100).unwrap());
    assert_eq!(buf, [9; 2]);
}

#[test]
fn s1a_15_a_read_that_runs_off_the_end_is_zero_filled() {
    let dir = TempDir::new("s15e");
    let dm = new_dm(&dir);
    dm.write_log(b"hi").unwrap();
    let mut buf = [9u8; 8];
    assert!(dm.read_log(&mut buf, 0).unwrap());
    assert_eq!(&buf, b"hi\0\0\0\0\0\0");
}

#[test]
fn s1a_15_the_log_survives_reopening_and_keeps_appending() {
    let dir = TempDir::new("s15g");
    {
        let dm = new_dm(&dir);
        dm.write_log(b"one").unwrap();
    }
    let dm = new_dm(&dir);
    dm.write_log(b"two").unwrap();
    let mut buf = [0u8; 6];
    assert!(dm.read_log(&mut buf, 0).unwrap());
    assert_eq!(&buf, b"onetwo");
}

// ---- 1a-03 · the DiskIo trait ------------------------------------------------------------------------------------

#[test]
fn s1a_16_a_disk_manager_works_through_the_trait() {
    let dir = TempDir::new("s16a");
    let dm = new_dm(&dir);
    let disk: &dyn DiskIo = &dm;
    disk.write_page(PageId(4), &pattern(4)).unwrap();
    let mut buf = [0u8; PS];
    disk.read_page(PageId(4), &mut buf).unwrap();
    assert!(buf == pattern(4));
    disk.delete_page(PageId(4));
    disk.read_page(PageId(4), &mut buf).unwrap();
    assert!(buf == page_of(0));
    assert_eq!((dm.get_num_writes(), dm.get_num_deletes()), (1, 1), "the trait methods are the real ones, not copies");
}

#[test]
fn s1a_16_a_shared_trait_object_can_go_to_other_threads() {
    let dir = TempDir::new("s16b");
    let disk: Arc<dyn DiskIo> = Arc::new(new_dm(&dir));
    let handles: Vec<_> = (0..4)
        .map(|t| {
            let disk = Arc::clone(&disk);
            thread::spawn(move || disk.write_page(PageId(t), &pattern(t as usize)).unwrap())
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    for t in 0..4 {
        let mut buf = [0u8; PS];
        disk.read_page(PageId(t), &mut buf).unwrap();
        assert!(buf == pattern(t as usize));
    }
}

#[test]
fn s1a_16_copy_page_copies() {
    let dir = TempDir::new("s16c");
    let dm = new_dm(&dir);
    dm.write_page(PageId(1), &pattern(1)).unwrap();
    copy_page(&dm, PageId(1), PageId(2)).unwrap();
    let mut buf = [0u8; PS];
    dm.read_page(PageId(2), &mut buf).unwrap();
    assert!(buf == pattern(1));
    dm.read_page(PageId(1), &mut buf).unwrap();
    assert!(buf == pattern(1), "the source is unchanged");
}

#[test]
fn s1a_16_copying_a_page_that_was_never_written_writes_zeros() {
    let dir = TempDir::new("s16d");
    let dm = new_dm(&dir);
    dm.write_page(PageId(2), &page_of(7)).unwrap();
    copy_page(&dm, PageId(9), PageId(2)).unwrap();
    let mut buf = [1u8; PS];
    dm.read_page(PageId(2), &mut buf).unwrap();
    assert!(buf == page_of(0));
}

#[test]
fn s1a_16_copy_page_does_one_read_and_one_write() {
    let disk = CountingDisk::default();
    copy_page(&disk, PageId(1), PageId(2)).unwrap();
    assert_eq!((disk.reads.load(Ordering::SeqCst), disk.writes.load(Ordering::SeqCst)), (1, 1));
}

#[test]
fn s1a_18_copy_page_works_on_a_memory_disk() {
    let disk = DiskManagerUnlimitedMemory::new();
    disk.write_page(PageId(1), &pattern(3)).unwrap();
    copy_page(&disk, PageId(1), PageId(8)).unwrap();
    let mut buf = [0u8; PS];
    disk.read_page(PageId(8), &mut buf).unwrap();
    assert!(buf == pattern(3));
}

// ---- 1a-03 · DiskManagerMemory -----------------------------------------------------------------------------------

#[test]
fn s1a_17_pages_read_back() {
    let disk = DiskManagerMemory::new(8);
    disk.write_page(PageId(3), &pattern(3)).unwrap();
    let mut buf = [0u8; PS];
    disk.read_page(PageId(3), &mut buf).unwrap();
    assert!(buf == pattern(3));
}

#[test]
fn s1a_17_a_fresh_disk_is_zeroed() {
    let disk = DiskManagerMemory::new(4);
    let mut buf = [0xFFu8; PS];
    for id in 0..4 {
        disk.read_page(PageId(id), &mut buf).unwrap();
        assert!(buf == page_of(0), "page {id}");
    }
}

#[test]
fn s1a_17_pages_are_independent_and_all_fit() {
    let disk = DiskManagerMemory::new(16);
    for id in 0..16 {
        disk.write_page(PageId(id), &pattern(id as usize)).unwrap();
    }
    for id in 0..16 {
        let mut buf = [0u8; PS];
        disk.read_page(PageId(id), &mut buf).unwrap();
        assert!(buf == pattern(id as usize), "page {id}");
    }
    assert_eq!(disk.get_num_writes(), 16);
}

#[test]
#[should_panic(expected = "ran out of disk space")]
fn s1a_17_writing_past_the_capacity_panics() {
    let disk = DiskManagerMemory::new(4);
    let _ = disk.write_page(PageId(4), &page_of(1));
}

#[test]
#[should_panic(expected = "ran out of disk space")]
fn s1a_17_reading_past_the_capacity_panics() {
    let disk = DiskManagerMemory::new(4);
    let mut buf = [0u8; PS];
    let _ = disk.read_page(PageId(100), &mut buf);
}

#[test]
#[should_panic(expected = "ran out of disk space")]
fn s1a_17_a_negative_page_id_panics_too() {
    let disk = DiskManagerMemory::new(4);
    let mut buf = [0u8; PS];
    let _ = disk.read_page(PageId(-1), &mut buf);
}

#[test]
fn s1a_17_delete_changes_nothing() {
    let disk = DiskManagerMemory::new(4);
    disk.write_page(PageId(1), &page_of(8)).unwrap();
    disk.delete_page(PageId(1));
    let mut buf = [0u8; PS];
    disk.read_page(PageId(1), &mut buf).unwrap();
    assert!(buf == page_of(8));
}

#[test]
fn s1a_17_it_works_as_a_dyn_disk() {
    let disk: Arc<dyn DiskIo> = Arc::new(DiskManagerMemory::new(2));
    disk.write_page(PageId(1), &page_of(4)).unwrap();
    let mut buf = [0u8; PS];
    disk.read_page(PageId(1), &mut buf).unwrap();
    assert!(buf == page_of(4));
}

// ---- 1a-03 · DiskManagerUnlimitedMemory --------------------------------------------------------------------------

#[test]
fn s1a_18_pages_read_back_whatever_their_id() {
    let disk = DiskManagerUnlimitedMemory::new();
    for id in [0, 1, 500, 5000] {
        disk.write_page(PageId(id), &pattern(id as usize)).unwrap();
    }
    for id in [0, 1, 500, 5000] {
        let mut buf = [0u8; PS];
        disk.read_page(PageId(id), &mut buf).unwrap();
        assert!(buf == pattern(id as usize), "page {id}");
    }
}

#[test]
fn s1a_18_a_page_never_written_reads_as_zeros() {
    let disk = DiskManagerUnlimitedMemory::new();
    let mut buf = [0xFFu8; PS];
    disk.read_page(PageId(123), &mut buf).unwrap();
    assert!(buf == page_of(0));
    disk.write_page(PageId(200), &page_of(1)).unwrap();
    buf.fill(0xFF);
    disk.read_page(PageId(150), &mut buf).unwrap();
    assert!(buf == page_of(0), "a gap below a written page is zeros too");
}

#[test]
fn s1a_18_rewriting_replaces_the_page() {
    let disk = DiskManagerUnlimitedMemory::new();
    disk.write_page(PageId(2), &page_of(1)).unwrap();
    disk.write_page(PageId(2), &page_of(2)).unwrap();
    let mut buf = [0u8; PS];
    disk.read_page(PageId(2), &mut buf).unwrap();
    assert!(buf == page_of(2));
    assert_eq!(disk.get_num_writes(), 2);
}

#[test]
fn s1a_18_memory_usage_counts_only_pages_that_exist() {
    let disk = DiskManagerUnlimitedMemory::new();
    assert_eq!(disk.get_memory_usage(), 0);
    disk.write_page(PageId(3), &page_of(1)).unwrap();
    disk.write_page(PageId(4000), &page_of(1)).unwrap();
    assert_eq!(disk.get_memory_usage(), 2 * PS);
    disk.write_page(PageId(3), &page_of(2)).unwrap();
    assert_eq!(disk.get_memory_usage(), 2 * PS, "a rewrite is not a new page");
    let mut buf = [0u8; PS];
    disk.read_page(PageId(77), &mut buf).unwrap();
    assert_eq!(disk.get_memory_usage(), 2 * PS, "reading a missing page doesn't create it");
}

#[test]
fn s1a_18_delete_is_a_no_op() {
    let disk = DiskManagerUnlimitedMemory::new();
    disk.write_page(PageId(1), &page_of(6)).unwrap();
    disk.delete_page(PageId(1));
    let mut buf = [0u8; PS];
    disk.read_page(PageId(1), &mut buf).unwrap();
    assert!(buf == page_of(6));
}

#[test]
fn s1a_18_many_threads_write_their_own_pages() {
    let disk = Arc::new(DiskManagerUnlimitedMemory::new());
    let handles: Vec<_> = (0..8)
        .map(|t| {
            let disk = Arc::clone(&disk);
            thread::spawn(move || {
                for i in 0..25 {
                    let id = t * 25 + i;
                    disk.write_page(PageId(id), &pattern(id as usize)).unwrap();
                }
            })
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    assert_eq!(disk.get_num_writes(), 200);
    for id in 0..200 {
        let mut buf = [0u8; PS];
        disk.read_page(PageId(id), &mut buf).unwrap();
        assert!(buf == pattern(id as usize), "page {id}");
    }
}

#[test]
#[should_panic(expected = "invalid page id")]
fn s1a_18_the_invalid_page_id_panics() {
    let disk = DiskManagerUnlimitedMemory::new();
    let mut buf = [0u8; PS];
    let _ = disk.read_page(PageId::INVALID, &mut buf);
}

// ---- 1a-04 · shut_down -------------------------------------------------------------------------------------------

#[test]
fn s1a_19_shut_down_succeeds_and_the_data_is_still_there() {
    let dir = TempDir::new("s19a");
    let dm = new_dm(&dir);
    dm.write_page(PageId(0), &pattern(1)).unwrap();
    dm.write_log(b"record").unwrap();
    dm.shut_down().unwrap();
    assert!(std::fs::read(dir.path("test.bustub")).unwrap()[..PS] == pattern(1));
    assert_eq!(std::fs::read(dir.path("test.log")).unwrap(), b"record");
}

#[test]
fn s1a_19_shut_down_twice_is_fine() {
    let dir = TempDir::new("s19b");
    let dm = new_dm(&dir);
    dm.shut_down().unwrap();
    dm.shut_down().unwrap();
}
