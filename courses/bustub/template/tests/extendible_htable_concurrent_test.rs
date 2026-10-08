//! Port of `test/container/disk/hash/extendible_htable_concurrent_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon
//! University Database Group). `LaunchParallelTest` becomes `thread::scope`.

use std::sync::Arc;
use std::thread;

use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::PageId;
use bustub::common::rid::Rid;
use bustub::container::disk::hash::disk_extendible_hash_table::DiskExtendibleHashTable;
use bustub::container::hash::hash_function::HashFunction;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;
use bustub::storage::index::generic_key::{GenericComparator, GenericKey};

type Table<'a> = DiskExtendibleHashTable<'a, GenericKey<8>, Rid, GenericComparator<8>>;

fn new_bpm() -> BufferPoolManager {
    BufferPoolManager::new(50, Arc::new(DiskManagerUnlimitedMemory::new()))
}

fn new_table(bpm: &BufferPoolManager) -> Table<'_> {
    DiskExtendibleHashTable::new("blah", bpm, GenericComparator::<8>, HashFunction::new(), 9, 9, Table::default_bucket_max_size())
}

fn index_key(key: i64) -> GenericKey<8> {
    let mut k = GenericKey::<8>::default();
    k.set_from_integer(key);
    k
}

fn rid_of(key: i64) -> Rid {
    let value = key & 0xFFFF_FFFF;
    Rid::new(PageId((key >> 32) as i32), value as u32)
}

/// Runs `f(thread_itr)` on `num_threads` threads and waits for them (BusTub's `LaunchParallelTest`).
fn launch_parallel_test(num_threads: u64, f: impl Fn(u64) + Sync) {
    thread::scope(|scope| {
        for thread_itr in 0..num_threads {
            let f = &f;
            scope.spawn(move || f(thread_itr));
        }
    });
}

// helper function to insert
fn insert_helper(ht: &Table<'_>, keys: &[i64]) {
    for &key in keys {
        ht.insert(&index_key(key), &rid_of(key));
    }
}

// helper function to separate insert
fn insert_helper_split(ht: &Table<'_>, keys: &[i64], total_threads: u64, thread_itr: u64) {
    for &key in keys {
        if key as u64 % total_threads == thread_itr {
            ht.insert(&index_key(key), &rid_of(key));
        }
    }
}

// helper function to delete
fn delete_helper(ht: &Table<'_>, remove_keys: &[i64]) {
    for &key in remove_keys {
        ht.remove(&index_key(key));
    }
}

// helper function to separate delete
fn delete_helper_split(ht: &Table<'_>, remove_keys: &[i64], total_threads: u64, thread_itr: u64) {
    for &key in remove_keys {
        if key as u64 % total_threads == thread_itr {
            ht.remove(&index_key(key));
        }
    }
}

fn lookup_helper(ht: &Table<'_>, keys: &[i64]) {
    for &key in keys {
        let result = ht.get_value(&index_key(key));
        assert_eq!(result.len(), 1, "key {key}");
        assert_eq!(result[0], rid_of(key));
    }
}

#[test]
fn insert_test_1() {
    let bpm = new_bpm();
    let ht = new_table(&bpm);

    // keys to Insert
    let keys: Vec<i64> = (1..100).collect();
    launch_parallel_test(2, |_| insert_helper(&ht, &keys));

    for &key in &keys {
        let rids = ht.get_value(&index_key(key));
        assert_eq!(rids.len(), 1);
        assert_eq!(rids[0].slot_num() as i64, key & 0xFFFF_FFFF);
    }
}

#[test]
fn insert_test_2() {
    let bpm = new_bpm();
    let ht = new_table(&bpm);

    let keys: Vec<i64> = (1..100).collect();
    launch_parallel_test(2, |t| insert_helper_split(&ht, &keys, 2, t));

    for &key in &keys {
        let rids = ht.get_value(&index_key(key));
        assert_eq!(rids.len(), 1);
        assert_eq!(rids[0].slot_num() as i64, key & 0xFFFF_FFFF);
    }
}

#[test]
fn delete_test_1() {
    let bpm = new_bpm();
    let ht = new_table(&bpm);

    // sequential insert
    let keys = vec![1, 2, 3, 4, 5];
    insert_helper(&ht, &keys);

    let remove_keys = vec![1, 5, 3, 4];
    launch_parallel_test(2, |_| delete_helper(&ht, &remove_keys));

    for &key in &keys {
        let rids = ht.get_value(&index_key(key));
        if key != 2 {
            assert_eq!(rids.len(), 0);
            continue;
        }
        assert_eq!(rids.len(), 1);
        assert_eq!(rids[0].slot_num() as i64, key & 0xFFFF_FFFF);
    }
}

#[test]
fn delete_test_2() {
    let bpm = new_bpm();
    let ht = new_table(&bpm);

    // sequential insert
    let keys = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
    insert_helper(&ht, &keys);

    let remove_keys = vec![1, 4, 3, 2, 5, 6];
    launch_parallel_test(2, |t| delete_helper_split(&ht, &remove_keys, 2, t));

    for &key in &keys {
        let rids = ht.get_value(&index_key(key));
        if key <= 6 {
            assert_eq!(rids.len(), 0);
            continue;
        }
        assert_eq!(rids.len(), 1);
        assert_eq!(rids[0].slot_num() as i64, key & 0xFFFF_FFFF);
    }
}

#[test]
fn mix_test_1() {
    let bpm = new_bpm();
    let ht = new_table(&bpm);

    // first, populate index
    insert_helper(&ht, &[1, 2, 3, 4, 5]);

    // concurrent insert
    let keys: Vec<i64> = (6..=10).collect();
    launch_parallel_test(1, |_| insert_helper(&ht, &keys));
    // concurrent delete
    let remove_keys = vec![1, 4, 3, 5, 6];
    launch_parallel_test(1, |_| delete_helper(&ht, &remove_keys));

    let valid_keys = [2, 7, 8, 9, 10];
    let invalid_keys = [1, 3, 4, 5, 6];

    for key in valid_keys {
        let rids = ht.get_value(&index_key(key));
        assert_eq!(rids.len(), 1);
        assert_eq!(rids[0].slot_num() as i64, key & 0xFFFF_FFFF);
    }
    for key in invalid_keys {
        assert_eq!(ht.get_value(&index_key(key)).len(), 0);
    }
}

#[test]
fn mix_test_2() {
    let bpm = new_bpm();
    let ht = new_table(&bpm);

    // Add preserved_keys
    let (mut preserved_keys, mut dynamic_keys) = (Vec::new(), Vec::new());
    let (total_keys, sieve) = (50i64, 5i64);
    for i in 1..=total_keys {
        if i % sieve == 0 {
            preserved_keys.push(i);
        } else {
            dynamic_keys.push(i);
        }
    }
    insert_helper(&ht, &preserved_keys);

    let num_threads = 6;
    launch_parallel_test(num_threads, |i| match i % 3 {
        0 => insert_helper(&ht, &dynamic_keys),
        1 => delete_helper(&ht, &dynamic_keys),
        _ => lookup_helper(&ht, &preserved_keys),
    });

    // Check all preserved keys exist
    for &key in &preserved_keys {
        let rids = ht.get_value(&index_key(key));
        assert_eq!(rids.len(), 1);
        assert_eq!(rids[0].slot_num() as i64, key & 0xFFFF_FFFF);
    }
}
