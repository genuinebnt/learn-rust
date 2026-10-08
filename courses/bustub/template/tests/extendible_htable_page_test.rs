//! Port of `test/storage/extendible_htable_page_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database
//! Group). `guard.AsMut<Page>()` becomes a typed view over the guard's bytes; `Init`, `Insert`, ... keep their names in snake_case.

use std::sync::Arc;

use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::PageId;
use bustub::common::rid::Rid;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;
use bustub::storage::index::generic_key::{GenericComparator, GenericKey};
use bustub::storage::page::extendible_htable_bucket_page::ExtendibleHTableBucketPage;
use bustub::storage::page::extendible_htable_directory_page::ExtendibleHTableDirectoryPage;
use bustub::storage::page::extendible_htable_header_page::ExtendibleHTableHeaderPage;

type Bucket<'a> = ExtendibleHTableBucketPage<&'a mut [u8], GenericKey<8>, Rid>;

fn new_bpm() -> BufferPoolManager {
    BufferPoolManager::new(5, Arc::new(DiskManagerUnlimitedMemory::new()))
}

fn generic_key(n: i64) -> GenericKey<8> {
    let mut k = GenericKey::<8>::default();
    k.set_from_integer(n);
    k
}

#[test]
fn bucket_page_sample_test() {
    let bpm = new_bpm();

    let bucket_page_id = bpm.new_page();
    let mut guard = bpm.write_page(bucket_page_id);
    let mut bucket_page = Bucket::new(&mut guard.get_data_mut()[..]);
    bucket_page.init(10);

    let comparator = GenericComparator::<8>;

    // insert a few (key, value) pairs
    for i in 0..10i64 {
        let rid = Rid::new(PageId(i as i32), i as u32);
        assert!(bucket_page.insert(&generic_key(i), &rid, &comparator));
    }

    let index_key = generic_key(11);
    let rid = Rid::new(PageId(11), 11);
    assert!(bucket_page.is_full());
    assert!(!bucket_page.insert(&index_key, &rid, &comparator));

    // check for the inserted pairs
    for i in 0..10i64 {
        assert_eq!(bucket_page.lookup(&generic_key(i), &comparator), Some(Rid::new(PageId(i as i32), i as u32)));
    }

    // remove a few pairs
    for i in 0..10i64 {
        if i % 2 == 1 {
            assert!(bucket_page.remove(&generic_key(i), &comparator));
        }
    }

    for i in 0..10i64 {
        if i % 2 == 1 {
            // remove the same pairs again
            assert!(!bucket_page.remove(&generic_key(i), &comparator));
        } else {
            assert!(bucket_page.remove(&generic_key(i), &comparator));
        }
    }

    assert!(bucket_page.is_empty());
    // page guard dropped
}

#[test]
fn header_directory_page_sample_test() {
    let bpm = new_bpm();

    /************************ HEADER PAGE TEST ************************/
    let header_page_id = bpm.new_page();
    let mut header_guard = bpm.write_page(header_page_id);
    let mut header_page = ExtendibleHTableHeaderPage::new(&mut header_guard.get_data_mut()[..]);
    header_page.init(2);

    /* Test hashes for header page
    00000000000000001000000000000000 - 32768
    01000000000000001000000000000000 - 1073774592
    10000000000000001000000000000000 - 2147516416
    11000000000000001000000000000000 - 3221258240
    */

    // ensure we are hashing into proper bucket based on upper 2 bits
    let hashes: [u32; 4] = [32768, 1073774592, 2147516416, 3221258240];
    for (i, hash) in hashes.iter().enumerate() {
        assert_eq!(header_page.hash_to_directory_index(*hash), i as u32);
    }

    drop(header_guard);

    /************************ DIRECTORY PAGE TEST ************************/
    let directory_page_id = bpm.new_page();
    let mut directory_guard = bpm.write_page(directory_page_id);
    let mut directory_page = ExtendibleHTableDirectoryPage::new(&mut directory_guard.get_data_mut()[..]);
    directory_page.init(3);

    let bucket_page_id_1 = bpm.new_page();
    let mut bucket_guard_1 = bpm.write_page(bucket_page_id_1);
    Bucket::new(&mut bucket_guard_1.get_data_mut()[..]).init(10);

    let bucket_page_id_2 = bpm.new_page();
    let mut bucket_guard_2 = bpm.write_page(bucket_page_id_2);
    Bucket::new(&mut bucket_guard_2.get_data_mut()[..]).init(10);

    let bucket_page_id_3 = bpm.new_page();
    let mut bucket_guard_3 = bpm.write_page(bucket_page_id_3);
    Bucket::new(&mut bucket_guard_3.get_data_mut()[..]).init(10);

    let bucket_page_id_4 = bpm.new_page();
    let mut bucket_guard_4 = bpm.write_page(bucket_page_id_4);
    Bucket::new(&mut bucket_guard_4.get_data_mut()[..]).init(10);

    directory_page.set_bucket_page_id(0, bucket_page_id_1);

    /*
    ======== DIRECTORY (global_depth_: 0) ========
    | bucket_idx | page_id | local_depth |
    |    0    |    2    |    0    |
    ================ END DIRECTORY ================
    */

    directory_page.verify_integrity();
    assert_eq!(directory_page.size(), 1);
    assert_eq!(directory_page.get_bucket_page_id(0), bucket_page_id_1);

    // grow the directory, local depths should change!
    directory_page.set_local_depth(0, 1);
    directory_page.incr_global_depth();
    directory_page.set_bucket_page_id(1, bucket_page_id_2);
    directory_page.set_local_depth(1, 1);

    /*
    ======== DIRECTORY (global_depth_: 1) ========
    | bucket_idx | page_id | local_depth |
    |    0    |    2    |    1    |
    |    1    |    3    |    1    |
    ================ END DIRECTORY ================
    */

    directory_page.verify_integrity();
    assert_eq!(directory_page.size(), 2);
    assert_eq!(directory_page.get_bucket_page_id(0), bucket_page_id_1);
    assert_eq!(directory_page.get_bucket_page_id(1), bucket_page_id_2);

    for i in 0..100u32 {
        assert_eq!(directory_page.hash_to_bucket_index(i), i % 2);
    }

    directory_page.set_local_depth(0, 2);
    directory_page.incr_global_depth();
    directory_page.set_bucket_page_id(2, bucket_page_id_3);

    /*
    ======== DIRECTORY (global_depth_: 2) ========
    | bucket_idx | page_id | local_depth |
    |    0    |    2    |    2    |
    |    1    |    3    |    1    |
    |    2    |    4    |    2    |
    |    3    |    3    |    1    |
    ================ END DIRECTORY ================
    */

    directory_page.verify_integrity();
    assert_eq!(directory_page.size(), 4);
    assert_eq!(directory_page.get_bucket_page_id(0), bucket_page_id_1);
    assert_eq!(directory_page.get_bucket_page_id(1), bucket_page_id_2);
    assert_eq!(directory_page.get_bucket_page_id(2), bucket_page_id_3);
    assert_eq!(directory_page.get_bucket_page_id(3), bucket_page_id_2);

    for i in 0..100u32 {
        assert_eq!(directory_page.hash_to_bucket_index(i), i % 4);
    }

    directory_page.set_local_depth(0, 3);
    directory_page.incr_global_depth();
    directory_page.set_bucket_page_id(4, bucket_page_id_4);

    /*
    ======== DIRECTORY (global_depth_: 3) ========
    | bucket_idx | page_id | local_depth |
    |    0    |    2    |    3    |
    |    1    |    3    |    1    |
    |    2    |    4    |    2    |
    |    3    |    3    |    1    |
    |    4    |    5    |    3    |
    |    5    |    3    |    1    |
    |    6    |    4    |    2    |
    |    7    |    3    |    1    |
    ================ END DIRECTORY ================
    */
    directory_page.verify_integrity();
    assert_eq!(directory_page.size(), 8);
    assert_eq!(directory_page.get_bucket_page_id(0), bucket_page_id_1);
    assert_eq!(directory_page.get_bucket_page_id(1), bucket_page_id_2);
    assert_eq!(directory_page.get_bucket_page_id(2), bucket_page_id_3);
    assert_eq!(directory_page.get_bucket_page_id(3), bucket_page_id_2);
    assert_eq!(directory_page.get_bucket_page_id(4), bucket_page_id_4);
    assert_eq!(directory_page.get_bucket_page_id(5), bucket_page_id_2);
    assert_eq!(directory_page.get_bucket_page_id(6), bucket_page_id_3);
    assert_eq!(directory_page.get_bucket_page_id(7), bucket_page_id_2);

    for i in 0..100u32 {
        assert_eq!(directory_page.hash_to_bucket_index(i), i % 8);
    }

    // (BusTub: uncommenting `directory_page->IncrGlobalDepth();` here "should cause an Assertion failed since this would be
    // exceeding the max depth we initialized"; in Rust that is a panic, covered by a should_panic test in the stage tests.)

    // at this time, we cannot shrink the directory since we have ld = gd = 3
    assert!(!directory_page.can_shrink());

    directory_page.set_local_depth(0, 2);
    directory_page.set_local_depth(4, 2);
    directory_page.set_bucket_page_id(0, bucket_page_id_4);

    /*
    ======== DIRECTORY (global_depth_: 3) ========
    | bucket_idx | page_id | local_depth |
    |    0    |    5    |    2    |
    |    1    |    3    |    1    |
    |    2    |    4    |    2    |
    |    3    |    3    |    1    |
    |    4    |    5    |    2    |
    |    5    |    3    |    1    |
    |    6    |    4    |    2    |
    |    7    |    3    |    1    |
    ================ END DIRECTORY ================
    */

    assert!(directory_page.can_shrink());
    directory_page.decr_global_depth();

    /*
    ======== DIRECTORY (global_depth_: 2) ========
    | bucket_idx | page_id | local_depth |
    |    0    |    5    |    2    |
    |    1    |    3    |    1    |
    |    2    |    4    |    2    |
    |    3    |    3    |    1    |
    ================ END DIRECTORY ================
    */

    directory_page.verify_integrity();
    assert_eq!(directory_page.size(), 4);
    assert!(!directory_page.can_shrink());
    // page guard dropped
}
