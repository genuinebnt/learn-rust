//! Port of `test/storage/b_plus_tree_tombstone_test.cpp` (BusTub, MIT, Copyright (c) 2015-2025 Carnegie Mellon University Database
//! Group). `BPlusTree<..., NumTombs>` is `BPlusTree<..., TOMBS>` here (a const generic); `GetTombstones()` is `tombstones()`.

mod b_plus_tree_utils;

use std::sync::Arc;

use b_plus_tree_utils::*;
use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::PageId;
use bustub::common::rid::Rid;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;
use bustub::storage::page::b_plus_tree_leaf_page::BPlusTreeLeafPage as LeafPage;

fn new_bpm() -> BufferPoolManager {
    BufferPoolManager::new(50, Arc::new(DiskManagerUnlimitedMemory::new()))
}

fn rid_with_slot(i: i64, value: i64) -> Rid {
    Rid::new(PageId((i >> 32) as i32), (value & 0xFFFF_FFFF) as u32)
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

    let mut tombstones: Vec<i64> = vec![];
    let mut leaf = IndexLeaves::<2>::with_tombstones(tree.get_root_page_id(), &bpm);
    while leaf.valid() {
        tombstones.extend(leaf.leaf().tombstones().iter().map(|t| t.get_as_integer()));
        leaf.advance();
    }
    drop(leaf);

    assert_eq!(tombstones.len(), to_delete.len());
    for i in 0..tombstones.len() {
        assert_eq!(tombstones[i], to_delete[i]);
    }

    // Test insertions interact correctly with tombstones

    for &i in &to_delete {
        tree.insert(&index_key(i), &rid_with_slot(i, 2 * i));
    }

    let mut leaf = IndexLeaves::<2>::with_tombstones(tree.get_root_page_id(), &bpm);
    while leaf.valid() {
        assert_eq!(leaf.leaf().tombstones().len(), 0);
        leaf.advance();
    }
    drop(leaf);

    for &i in &to_delete {
        let rids = tree.get_value(&index_key(i));
        assert_eq!(rids.len(), 1);
        assert_eq!(rids[0].slot_num() as i64, (2 * i) & 0xFFFF_FFFF);
    }

    // Test tombstones are processed in the correct order

    to_delete.clear();
    {
        let mut leaf = IndexLeaves::<2>::with_tombstones(tree.get_root_page_id(), &bpm);
        while leaf.valid() {
            assert_eq!(2, leaf.leaf().min_size());
            if leaf.leaf().size() > leaf.leaf().min_size() {
                for i in 0..leaf.leaf().min_size() + 1 {
                    to_delete.push(leaf.leaf().key_at(i).get_as_integer());
                }
                break;
            }
            leaf.advance();
        }
    }

    for &i in &to_delete {
        tree.remove(&index_key(i));
    }

    tombstones.clear();
    let mut leaf = IndexLeaves::<2>::with_tombstones(tree.get_root_page_id(), &bpm);
    while leaf.valid() {
        tombstones.extend(leaf.leaf().tombstones().iter().map(|t| t.get_as_integer()));
        leaf.advance();
    }
    drop(leaf);
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

    let mut leaf = IndexLeaves::<2>::with_tombstones(tree.get_root_page_id(), &bpm);
    let mut tot_tombs = 0;
    while leaf.valid() {
        tot_tombs += leaf.leaf().tombstones().len();
        leaf.advance();
    }
    drop(leaf);

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
    while get_num_leaves(&tree, &bpm) < 2 && i < 6 {
        tree.insert(&index_key(i), &rid_with_slot(i, i));
        i += 1;
    }

    let mut leaf = IndexLeaves::<3>::with_tombstones(tree.get_root_page_id(), &bpm);
    while leaf.valid() {
        let mut expected: Vec<i64> = vec![];
        for i in 0..leaf.leaf().size() {
            let key = leaf.leaf().key_at(i).get_as_integer();
            if key == 0 || key == 2 || key == 3 {
                expected.push(key);
            }
        }
        expected.sort_by(|a, b| b.cmp(a));
        let tombstones = leaf.leaf().tombstones();
        assert_eq!(tombstones.len(), expected.len());
        for i in 0..tombstones.len() {
            assert_eq!(tombstones[i].get_as_integer(), expected[i]);
        }
        leaf.advance();
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

    let left_pid = get_leftmost_leaf_page_id(tree.get_root_page_id(), &bpm);
    let to_remove: Vec<i64> = {
        let left_guard = bpm.read_page(left_pid);
        let left_page = LeafPage::<_, Key, Rid, 1>::new(&left_guard[..]);
        let next = left_page.next_page_id();
        assert!(next.is_some());
        let right_guard = bpm.read_page(next.unwrap());
        let right_page = LeafPage::<_, Key, Rid, 1>::new(&right_guard[..]);
        if left_page.size() == left_page.min_size() {
            vec![right_page.key_at(0), left_page.key_at(1), left_page.key_at(0)]
        } else {
            vec![left_page.key_at(0), right_page.key_at(1), right_page.key_at(0)]
        }
        .into_iter()
        .map(|k| k.get_as_integer())
        .collect()
    };

    for &k in &to_remove {
        tree.remove(&index_key(k));
    }

    let mut tombstones: Vec<i64> = vec![];
    let mut leaf = IndexLeaves::<1>::with_tombstones(tree.get_root_page_id(), &bpm);
    while leaf.valid() {
        assert!(leaf.leaf().size() >= leaf.leaf().min_size());
        tombstones.extend(leaf.leaf().tombstones().iter().map(|t| t.get_as_integer()));
        leaf.advance();
    }

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
    let mut larger_pid = PageId::INVALID;
    let mut smaller_pid = PageId::INVALID;
    {
        let mut leaf = IndexLeaves::<2>::with_tombstones(tree.get_root_page_id(), &bpm);
        let mut pid = get_leftmost_leaf_page_id(tree.get_root_page_id(), &bpm);
        while leaf.valid() {
            if leaf.leaf().size() == 4 {
                larger_pid = pid;
            } else {
                smaller_pid = pid;
            }
            match leaf.leaf().next_page_id() {
                Some(next) => pid = next,
                None => {}
            }
            leaf.advance();
        }
    }
    assert_ne!(larger_pid, PageId::INVALID);
    assert_ne!(smaller_pid, PageId::INVALID);

    // figure out keys to delete from the larger and smaller pages
    let (to_del_from_larger_page, to_del_from_smaller_page): (Vec<i64>, Vec<i64>) = {
        let larger_guard = bpm.read_page(larger_pid);
        let smaller_guard = bpm.read_page(smaller_pid);
        let larger_page = LeafPage::<_, Key, Rid, 2>::new(&larger_guard[..]);
        let smaller_page = LeafPage::<_, Key, Rid, 2>::new(&smaller_guard[..]);
        (
            (0..3).map(|i| larger_page.key_at(i).get_as_integer()).collect(),
            (0..3).map(|i| smaller_page.key_at(i).get_as_integer()).collect(),
        )
    };

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

    // ensure index is still correct
    let mut leaves: Vec<PageId> = vec![];
    {
        let mut pid = Some(get_leftmost_leaf_page_id(tree.get_root_page_id(), &bpm));
        while let Some(id) = pid {
            leaves.push(id);
            pid = LeafPage::<_, Key, Rid, 2>::new(&bpm.read_page(id)[..]).next_page_id();
        }
    }
    assert_eq!(leaves, vec![tree.get_root_page_id()]);

    // get the only leaf page in the b+ tree
    let root_guard = bpm.read_page(tree.get_root_page_id());
    let root_page = LeafPage::<_, Key, Rid, 2>::new(&root_guard[..]);
    assert!(bpm.read_page(tree.get_root_page_id())[..4] == 1u32.to_le_bytes());

    let tombstones = root_page.tombstones();
    assert_eq!(tombstones.len(), 2);

    // final set of tombstones should either be the last two keys logically deleted from the smaller page or the last two keys
    // logically deleted from the larger page.
    let mut eq_to_smaller_page = true;
    let mut eq_to_larger_page = true;
    for i in 0..2 {
        eq_to_smaller_page &= tombstones[i].get_as_integer() == to_del_from_smaller_page[1 + i];
        eq_to_larger_page &= tombstones[i].get_as_integer() == to_del_from_larger_page[1 + i];
    }

    assert!(!eq_to_smaller_page || !eq_to_larger_page);
    assert!(eq_to_smaller_page || eq_to_larger_page);
}
