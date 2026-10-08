//! Port of `test/storage/b_plus_tree_sequential_scale_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University
//! Database Group). `std::shuffle` with a default engine becomes a Fisher-Yates shuffle with a fixed seed, so a failure repeats.

mod b_plus_tree_utils;

use std::sync::Arc;

use b_plus_tree_utils::*;
use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;

#[test]
fn basic_scale_test() {
    let bpm = BufferPoolManager::new(30, Arc::new(DiskManagerUnlimitedMemory::new()));
    let tree = new_tree(&bpm, 2, 3);

    let scale = 5000;
    let mut keys: Vec<i64> = (1..=scale).collect();

    // randomize the insertion order
    let mut state = 0x2545F4914F6CDD1Du64;
    for i in (1..keys.len()).rev() {
        state ^= state << 13;
        state ^= state >> 7;
        state ^= state << 17;
        keys.swap(i, (state % (i as u64 + 1)) as usize);
    }
    for &key in &keys {
        tree.insert(&index_key(key), &rid_of(key));
    }
    for &key in &keys {
        let rids = tree.get_value(&index_key(key));
        assert_eq!(rids.len(), 1);
        assert_eq!(rids[0].slot_num() as i64, key & 0xFFFF_FFFF);
    }
}
