//! Port of `test/storage/b_plus_tree_tombstone_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database
//! Group). `BPlusTree<..., NumTombs>` is `BPlusTree<..., TOMBS>` here (a const generic). The C++ tests read the leaf pages one by one
//! (`IndexLeaves`, `GetTombstones()`, `KeyAt`); the pages are the learner's here, so the tree's observers `leaf_keys` and
//! `leaf_tombstones` stand in: the keys stored in each leaf (tombstoned ones included) and the keys in each leaf's buffer, oldest first.

mod b_plus_tree_utils;

use std::sync::Arc;

use b_plus_tree_utils::*;
use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::PageId;
use bustub::common::rid::Rid;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;

fn new_bpm() -> BufferPoolManager {
    BufferPoolManager::new(50, Arc::new(DiskManagerUnlimitedMemory::new()))
}

fn rid_with_slot(i: i64, value: i64) -> Rid {
    Rid::new(PageId((i >> 32) as i32), (value & 0xFFFF_FFFF) as u32)
}

/// The keys of each leaf, as integers.
fn keys_of<const T: usize>(tree: &Tree<T>) -> Vec<Vec<i64>> {
    tree.leaf_keys().into_iter().map(|l| l.iter().map(|k| k.get_as_integer()).collect()).collect()
}

/// The tombstones of each leaf, as integers, each leaf's oldest first.
fn tombs_of<const T: usize>(tree: &Tree<T>) -> Vec<Vec<i64>> {
    tree.leaf_tombstones().into_iter().map(|l| l.iter().map(|k| k.get_as_integer()).collect()).collect()
}

fn all_tombstones<const T: usize>(tree: &Tree<T>) -> Vec<i64> {
    tombs_of(tree).concat()
}

#[test]
fn tombstone_basic_test() {
    let bpm = new_bpm();
    let tree = new_tree_t::<2>(&bpm, 4, 4);

    let num_keys = 17;
    let mut expected: Vec<i64> = vec![];
    for i in 0..num_keys {
        tree.insert(&index_key(i), &rid_with_slot(i, i));
        expected.push(i);
    }

    // Test tombstones are being used / affect the index iterator correctly

    let mut to_delete = vec![1, 5, 9];
    for &i in &to_delete {
        tree.remove(&index_key(i));
        expected.retain(|&k| k != i);
    }

    for (i, (key, _)) in tree.begin().enumerate() {
        assert_eq!(key.get_as_integer(), expected[i]);
    }

    let tombstones = all_tombstones(&tree);
    assert_eq!(tombstones.len(), to_delete.len());
    for i in 0..tombstones.len() {
        assert_eq!(tombstones[i], to_delete[i]);
    }

    // Test insertions interact correctly with tombstones

    for &i in &to_delete {
        tree.insert(&index_key(i), &rid_with_slot(i, 2 * i));
    }

    for leaf in tombs_of(&tree) {
        assert_eq!(leaf.len(), 0);
    }

    for &i in &to_delete {
        let rids = tree.get_value(&index_key(i));
        assert_eq!(rids.len(), 1);
        assert_eq!(rids[0].slot_num() as i64, (2 * i) & 0xFFFF_FFFF);
    }

    // Test tombstones are processed in the correct order

    to_delete.clear();
    let min_size = 4 / 2;
    for keys in keys_of(&tree) {
        if keys.len() > min_size {
            for i in 0..min_size + 1 {
                to_delete.push(keys[i]);
            }
            break;
        }
    }
    assert_eq!(to_delete.len(), min_size + 1, "a leaf above its minimum size");

    for &i in &to_delete {
        tree.remove(&index_key(i));
    }

    let tombstones = all_tombstones(&tree);
    assert_eq!(tombstones.len(), to_delete.len() - 1);
    for i in 0..tombstones.len() {
        assert_eq!(tombstones[i], to_delete[i + 1]);
    }

    let rids = tree.get_value(&index_key(to_delete[0]));
    assert_eq!(rids.len(), 0);

    // Test index iterator stays valid for "empty" tree (and that tree isn't fully physically deleted)

    for i in 0..num_keys {
        tree.remove(&index_key(i));
    }

    let tot_tombs = all_tombstones(&tree).len();

    // Worst case: all keys are in full leaf nodes and so only 2 entries are tombed per.
    assert!(tot_tombs > ((num_keys as usize - 1) / 4) * 2);
    assert!(tot_tombs < num_keys as usize);
    assert!(tree.begin().is_end());
}

#[test]
fn tombstone_split_test() {
    let bpm = new_bpm();
    let tree = new_tree_t::<3>(&bpm, 5, 4);

    for i in 0..4 {
        tree.insert(&index_key(i), &rid_with_slot(i, i));
    }

    tree.remove(&index_key(3));
    tree.remove(&index_key(2));
    tree.remove(&index_key(0));

    let mut i = 4;
    while tree.leaf_sizes().len() < 2 && i < 6 {
        tree.insert(&index_key(i), &rid_with_slot(i, i));
        i += 1;
    }

    for (keys, tombstones) in keys_of(&tree).into_iter().zip(tombs_of(&tree)) {
        let mut expected: Vec<i64> = keys.iter().copied().filter(|k| *k == 0 || *k == 2 || *k == 3).collect();
        expected.sort_by(|a, b| b.cmp(a));
        assert_eq!(tombstones.len(), expected.len());
        for i in 0..tombstones.len() {
            assert_eq!(tombstones[i], expected[i]);
        }
    }
}

#[test]
fn tombstone_borrow_test() {
    let bpm = new_bpm();
    let tree = new_tree_t::<1>(&bpm, 4, 4);

    let num_keys = 5;
    for i in 0..num_keys {
        tree.insert(&index_key(i), &rid_with_slot(i, i));
    }

    let leaves = keys_of(&tree);
    assert!(leaves.len() >= 2);
    let (left, right) = (&leaves[0], &leaves[1]);
    let min_size = 4 / 2;
    let to_remove: Vec<i64> = if left.len() == min_size { vec![right[0], left[1], left[0]] } else { vec![left[0], right[1], right[0]] };

    for &k in &to_remove {
        tree.remove(&index_key(k));
    }

    for keys in keys_of(&tree) {
        assert!(keys.len() >= min_size);
    }
    let tombstones = all_tombstones(&tree);
    assert_eq!(tombstones.len(), 1);
    assert_eq!(tombstones[0], to_remove[0]);
}

#[test]
fn tombstone_coalesce_test() {
    let bpm = new_bpm();
    let tree = new_tree_t::<2>(&bpm, 6, 6);

    // insert 0, 1, 2, 3, 4, 5, 6 into the b+ tree
    let num_keys = 7;
    for i in 0..num_keys {
        tree.insert(&index_key(i), &rid_with_slot(i, i));
    }

    // there should be a larger leaf page and a smaller leaf page
    let leaves = keys_of(&tree);
    let larger = leaves.iter().find(|l| l.len() == 4).expect("a larger leaf").clone();
    let smaller = leaves.iter().find(|l| l.len() != 4).expect("a smaller leaf").clone();

    // figure out keys to delete from the larger and smaller pages
    let to_del_from_larger_page: Vec<i64> = larger[..3].to_vec();
    let to_del_from_smaller_page: Vec<i64> = smaller[..3].to_vec();

    // delete keys alternating between the larger and smaller pages.
    // The final delete from the smaller page should force a coalesce.
    let to_del = [
        to_del_from_larger_page[0],
        to_del_from_smaller_page[0],
        to_del_from_larger_page[1],
        to_del_from_smaller_page[1],
        to_del_from_larger_page[2],
        to_del_from_smaller_page[2],
    ];
    for k in to_del {
        tree.remove(&index_key(k));
    }

    // ensure index is still correct: one leaf, which is the root
    assert_eq!(tree.leaf_sizes().len(), 1);
    assert_eq!(tree.depth(), 1);

    let tombstones = tombs_of(&tree).concat();
    assert_eq!(tombstones.len(), 2);

    // final set of tombstones should either be the last two keys logically deleted from the smaller page or the last two keys
    // logically deleted from the larger page.
    let mut eq_to_smaller_page = true;
    let mut eq_to_larger_page = true;
    for i in 0..2 {
        eq_to_smaller_page &= tombstones[i] == to_del_from_smaller_page[1 + i];
        eq_to_larger_page &= tombstones[i] == to_del_from_larger_page[1 + i];
    }

    assert!(!eq_to_smaller_page || !eq_to_larger_page);
    assert!(eq_to_smaller_page || eq_to_larger_page);
}
