//! Port of `test/container/disk/hash/extendible_htable_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University
//! Database Group). `GetValue(key, &result)` returning a bool and filling a vector becomes `get_value(&key) -> Vec<V>`.
//!
//! `InsertTest1` is in the stage tests (`s2b_18_*`), adapted: with BusTub's MurmurHash3 the keys 0..8 do not spread two to a
//! bucket (0, 2, 4 and 6 share their low bits), so the original's "8 keys fit" cannot hold for any correct table.

use std::sync::Arc;

use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::container::disk::hash::disk_extendible_hash_table::DiskExtendibleHashTable;
use bustub::container::hash::hash_function::HashFunction;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;
use bustub::storage::index::int_comparator::IntComparator;

fn new_bpm() -> BufferPoolManager {
    BufferPoolManager::new(50, Arc::new(DiskManagerUnlimitedMemory::new()))
}

#[test]
fn insert_test_2() {
    let bpm = new_bpm();
    let ht = DiskExtendibleHashTable::<i32, i32, IntComparator>::new("blah", &bpm, IntComparator, HashFunction::new(), 2, 3, 2);

    let num_keys = 5;

    // insert some values
    for i in 0..num_keys {
        let inserted = ht.insert(&i, &i);
        assert!(inserted);
        let res = ht.get_value(&i);
        assert_eq!(1, res.len());
        assert_eq!(i, res[0]);
    }

    ht.verify_integrity();

    // check that they were actually inserted
    for i in 0..num_keys {
        let res = ht.get_value(&i);
        let got_value = !res.is_empty();
        assert!(got_value);
        assert_eq!(1, res.len());
        assert_eq!(i, res[0]);
    }

    ht.verify_integrity();

    // try to get some keys that don't exist/were not inserted
    for i in num_keys..2 * num_keys {
        let res = ht.get_value(&i);
        assert!(res.is_empty());
    }

    ht.verify_integrity();
}

#[test]
fn remove_test_1() {
    let bpm = new_bpm();
    let ht = DiskExtendibleHashTable::<i32, i32, IntComparator>::new("blah", &bpm, IntComparator, HashFunction::new(), 2, 3, 2);

    let num_keys = 5;

    // insert some values
    for i in 0..num_keys {
        let inserted = ht.insert(&i, &i);
        assert!(inserted);
        let res = ht.get_value(&i);
        assert_eq!(1, res.len());
        assert_eq!(i, res[0]);
    }

    ht.verify_integrity();

    // check that they were actually inserted
    for i in 0..num_keys {
        let res = ht.get_value(&i);
        assert!(!res.is_empty());
        assert_eq!(1, res.len());
        assert_eq!(i, res[0]);
    }

    ht.verify_integrity();

    // try to get some keys that don't exist/were not inserted
    for i in num_keys..2 * num_keys {
        let res = ht.get_value(&i);
        assert!(res.is_empty());
    }

    ht.verify_integrity();

    // remove the keys we inserted
    for i in 0..num_keys {
        let removed = ht.remove(&i);
        assert!(removed);
        let res = ht.get_value(&i);
        assert_eq!(0, res.len());
    }

    ht.verify_integrity();

    // try to remove some keys that don't exist/were not inserted
    for i in num_keys..2 * num_keys {
        let removed = ht.remove(&i);
        assert!(!removed);
        let res = ht.get_value(&i);
        assert!(res.is_empty());
        assert_eq!(0, res.len());
    }

    ht.verify_integrity();
}
