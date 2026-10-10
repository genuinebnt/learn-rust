//! Port of `test/storage/b_plus_tree_concurrent_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database
//! Group). `LaunchParallelTest` becomes `thread::scope`. The C++ tests run each case for a plain tree and for a tree with a tombstone
//! buffer (`Tombs = 3`); the tombstone buffer is module 2d, so here it is the plain tree.

mod b_plus_tree_utils;

use std::sync::Arc;
use std::thread;

use b_plus_tree_utils::*;
use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;

const NUM_ITERS: usize = 50;
const MIXTEST_NUM_ITERS: usize = 20;
const BPM_SIZE: usize = 50;

fn new_bpm() -> BufferPoolManager {
    BufferPoolManager::new(BPM_SIZE, Arc::new(DiskManagerUnlimitedMemory::new()))
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

fn insert_helper(tree: &Tree, keys: &[i64]) {
    for &key in keys {
        tree.insert(&index_key(key), &rid_of(key));
    }
}

/// Inserts only the keys whose value modulo `total_threads` is `thread_itr`.
fn insert_helper_split(tree: &Tree, keys: &[i64], total_threads: u64, thread_itr: u64) {
    for &key in keys {
        if key as u64 % total_threads == thread_itr {
            tree.insert(&index_key(key), &rid_of(key));
        }
    }
}

fn delete_helper(tree: &Tree, remove_keys: &[i64]) {
    for &key in remove_keys {
        tree.remove(&index_key(key));
    }
}

fn delete_helper_split(tree: &Tree, remove_keys: &[i64], total_threads: u64, thread_itr: u64) {
    for &key in remove_keys {
        if key as u64 % total_threads == thread_itr {
            tree.remove(&index_key(key));
        }
    }
}

fn lookup_helper(tree: &Tree, keys: &[i64]) {
    for &key in keys {
        let result = tree.get_value(&index_key(key));
        assert_eq!(result.len(), 1);
        assert_eq!(result[0], rid_of(key));
    }
}

#[test]
fn insert_test_1() {
    for _ in 0..NUM_ITERS {
        let bpm = new_bpm();
        let tree = new_tree(&bpm, 3, 5);

        // keys to insert
        let keys: Vec<i64> = (1..100).collect();
        launch_parallel_test(2, |_| insert_helper(&tree, &keys));

        for &key in &keys {
            let rids = tree.get_value(&index_key(key));
            assert_eq!(rids.len(), 1);
            assert_eq!(rids[0].slot_num() as i64, key & 0xFFFF_FFFF);
        }

        let mut current_key = 1;
        for (_, location) in tree.begin() {
            assert_eq!(location.page_id().0, 0);
            assert_eq!(location.slot_num() as i64, current_key);
            current_key += 1;
        }
        assert_eq!(current_key, keys.len() as i64 + 1);
    }
}

#[test]
fn insert_test_2() {
    for _ in 0..NUM_ITERS {
        let bpm = new_bpm();
        let tree = new_tree(&bpm, 3, 5);

        let keys: Vec<i64> = (1..1000).collect();
        launch_parallel_test(2, |thread_itr| insert_helper_split(&tree, &keys, 2, thread_itr));

        for &key in &keys {
            let rids = tree.get_value(&index_key(key));
            assert_eq!(rids.len(), 1);
            assert_eq!(rids[0].slot_num() as i64, key & 0xFFFF_FFFF);
        }

        let mut current_key = 1;
        for (_, location) in tree.begin() {
            assert_eq!(location.page_id().0, 0);
            assert_eq!(location.slot_num() as i64, current_key);
            current_key += 1;
        }
        assert_eq!(current_key, keys.len() as i64 + 1);
    }
}

#[test]
fn delete_test_1() {
    for _ in 0..NUM_ITERS {
        let bpm = new_bpm();
        let tree = new_tree(&bpm, 3, 5);

        // sequential insert
        insert_helper(&tree, &[1, 2, 3, 4, 5]);

        let remove_keys = [1, 5, 3, 4];
        launch_parallel_test(2, |_| delete_helper(&tree, &remove_keys));

        let mut current_key = 2;
        let mut size = 0;
        for (_, location) in tree.begin() {
            assert_eq!(location.page_id().0, 0);
            assert_eq!(location.slot_num() as i64, current_key);
            current_key += 1;
            size += 1;
        }
        assert_eq!(size, 1);
    }
}

#[test]
fn delete_test_2() {
    for _ in 0..NUM_ITERS {
        let bpm = new_bpm();
        let tree = new_tree(&bpm, 3, 5);

        // sequential insert
        insert_helper(&tree, &[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);

        let remove_keys = [1, 4, 3, 2, 5, 6];
        launch_parallel_test(2, |thread_itr| delete_helper_split(&tree, &remove_keys, 2, thread_itr));

        let mut current_key = 7;
        let mut size = 0;
        for (_, location) in tree.begin() {
            assert_eq!(location.page_id().0, 0);
            assert_eq!(location.slot_num() as i64, current_key);
            current_key += 1;
            size += 1;
        }
        assert_eq!(size, 4);
    }
}

#[test]
fn mix_test_1() {
    for _ in 0..MIXTEST_NUM_ITERS {
        let bpm = new_bpm();
        let tree = new_tree(&bpm, 3, 5);

        // first, populate the index
        let sieve = 2;
        let total_keys = 1000;
        let for_insert: Vec<i64> = (1..=total_keys).filter(|i| i % sieve == 0).collect();
        let for_delete: Vec<i64> = (1..=total_keys).filter(|i| i % sieve != 0).collect();
        // insert all the keys to delete
        insert_helper(&tree, &for_delete);

        let num_threads = 10;
        launch_parallel_test(num_threads, |tid| {
            if tid % 2 == 0 {
                insert_helper(&tree, &for_insert);
            } else {
                delete_helper(&tree, &for_delete);
            }
        });

        let mut size = 0;
        for (key, _) in tree.begin() {
            assert_eq!(key.get_as_integer(), for_insert[size]);
            size += 1;
        }
        assert_eq!(size, for_insert.len());
    }
}

#[test]
fn mix_test_2() {
    for _ in 0..MIXTEST_NUM_ITERS {
        let bpm = new_bpm();
        let tree = new_tree(&bpm, Tree::<0>::default_leaf_max_size(), Tree::<0>::default_internal_max_size());

        // add the preserved keys
        let total_keys = 1000;
        let sieve = 10;
        let preserved_keys: Vec<i64> = (1..=total_keys).filter(|i| i % sieve == 0).collect();
        let dynamic_keys: Vec<i64> = (1..=total_keys).filter(|i| i % sieve != 0).collect();
        insert_helper(&tree, &preserved_keys);

        let num_threads = 6;
        launch_parallel_test(num_threads, |tid| match tid % 3 {
            0 => insert_helper(&tree, &dynamic_keys),
            1 => delete_helper(&tree, &dynamic_keys),
            _ => lookup_helper(&tree, &preserved_keys),
        });

        // check that all the preserved keys exist
        let size = tree.begin().filter(|(key, _)| key.get_as_integer() % sieve == 0).count();
        assert_eq!(size, preserved_keys.len());
    }
}
