//! Tests for the B+ tree tombstone stages (2d-01 … 2d-03). A test named `s2d_02_…` belongs to stage 2d-02.
//! A leaf is shown as `[keys~tombstones]`: `[0,1,2,3~3,2]` has four pairs, of which 3 and 2 are deleted (3 is the older tombstone).

mod b_plus_tree_utils;

use std::collections::BTreeSet;
use std::sync::mpsc;
use std::sync::Arc;
use std::thread;
use std::time::Duration;

use b_plus_tree_utils::*;
use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::{PageId, BUSTUB_PAGE_SIZE};
use bustub::common::rid::Rid;
use bustub::storage::disk::disk_manager_memory::DiskManagerUnlimitedMemory;
use bustub::storage::index::generic_key::GenericComparator;
use bustub::storage::page::b_plus_tree_leaf_page::BPlusTreeLeafPage as Leaf;

struct Lcg(u64);
impl Lcg {
    fn next(&mut self, n: usize) -> usize {
        self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        ((self.0 >> 33) as usize) % n
    }
}

fn bpm(frames: usize) -> BufferPoolManager {
    BufferPoolManager::new(frames, Arc::new(DiskManagerUnlimitedMemory::new()))
}

fn assert_no_pins(bpm: &BufferPoolManager) {
    let next = bpm.new_page();
    for id in 0..next.0 {
        let pins = bpm.get_pin_count(PageId(id));
        assert!(matches!(pins, None | Some(0)), "page {id} is still pinned ({pins:?})");
    }
}

fn insert_all<const T: usize>(tree: &Tree<T>, keys: impl IntoIterator<Item = i64>) {
    for k in keys {
        assert!(insert(tree, k), "insert {k}");
    }
}

/// A leaf page with `max_size`, holding the pairs of `keys` (values made from the keys).
fn leaf_bytes<const T: usize>(max_size: u32, keys: &[i64]) -> [u8; BUSTUB_PAGE_SIZE] {
    let mut bytes = [0u8; BUSTUB_PAGE_SIZE];
    let mut leaf = Leaf::<_, Key, Rid, T>::new(&mut bytes[..]);
    leaf.init(max_size);
    for (i, &k) in keys.iter().enumerate() {
        leaf.set_entry_at(i as u32, &index_key(k), &rid_of(k));
    }
    leaf.set_size(keys.len() as u32);
    bytes
}

// ---- 2d-01 · The tombstone buffer in the leaf page ------------------------------------------------------------------------------

#[test]
fn s2d_01_the_buffer_takes_room_from_the_entries() {
    // leaf: 16-byte header, then (with tombstones) a 4-byte count and T 8-byte keys, then 16-byte pairs
    assert_eq!(Leaf::<&[u8], Key, Rid, 0>::capacity(), 511, "no tombstones: the layout of module 2c");
    assert_eq!(Leaf::<&[u8], Key, Rid, 1>::capacity(), (8192 - 16 - 4 - 8) / 16);
    assert_eq!(Leaf::<&[u8], Key, Rid, 2>::capacity(), 509);
    assert_eq!(Leaf::<&[u8], Key, Rid, 3>::capacity(), 509);
    assert_eq!(Leaf::<&[u8], Key, Rid, 4>::capacity(), 508);
}

#[test]
fn s2d_01_a_new_leaf_has_an_empty_buffer_even_on_a_recycled_page() {
    let mut bytes = [0xFFu8; BUSTUB_PAGE_SIZE]; // a page that held something else: garbage everywhere
    let mut leaf = Leaf::<_, Key, Rid, 2>::new(&mut bytes[..]);
    leaf.init(4);
    assert_eq!((leaf.size(), leaf.num_tombstones(), leaf.tombstones().len()), (0, 0, 0), "a new leaf has an empty buffer even on a recycled page");
    assert_eq!(leaf.next_page_id(), None, "a new leaf has an empty buffer even on a recycled page");
}

#[test]
fn s2d_01_tombstones_keep_the_order_they_were_added_in() {
    let mut bytes = leaf_bytes::<3>(10, &[1, 2, 3, 4, 5]);
    let mut leaf = Leaf::<_, Key, Rid, 3>::new(&mut bytes[..]);
    assert!(leaf.tombstones().is_empty(), "tombstones keep the order they were added in: expected `leaf.tombstones().is_empty()`");
    leaf.add_tombstone(&index_key(4));
    leaf.add_tombstone(&index_key(2));
    assert_eq!(leaf.num_tombstones(), 2, "tombstones keep the order they were added in");
    let as_ints = |leaf: &Leaf<&mut [u8], Key, Rid, 3>| leaf.tombstones().iter().map(|k| k.get_as_integer()).collect::<Vec<_>>();
    assert_eq!(as_ints(&leaf), vec![4, 2], "oldest first");
    leaf.add_tombstone(&index_key(5));
    assert_eq!(as_ints(&leaf), vec![4, 2, 5], "tombstones keep the order they were added in");
}

#[test]
#[should_panic]
fn s2d_01_a_full_buffer_does_not_take_another_tombstone() {
    let mut bytes = leaf_bytes::<2>(10, &[1, 2, 3]);
    let mut leaf = Leaf::<_, Key, Rid, 2>::new(&mut bytes[..]);
    leaf.add_tombstone(&index_key(1));
    leaf.add_tombstone(&index_key(2));
    leaf.add_tombstone(&index_key(3));
}

#[test]
fn s2d_01_a_tombstone_can_be_looked_up_by_key_or_by_slot_and_dropped() {
    let mut bytes = leaf_bytes::<3>(10, &[10, 20, 30, 40]);
    let cmp = GenericComparator::<8>;
    let mut leaf = Leaf::<_, Key, Rid, 3>::new(&mut bytes[..]);
    leaf.add_tombstone(&index_key(20));
    leaf.add_tombstone(&index_key(40));
    leaf.add_tombstone(&index_key(10));
    assert!(leaf.is_tombstoned(&index_key(20), &cmp) && !leaf.is_tombstoned(&index_key(30), &cmp), "a tombstone can be looked up by key or by slot and dropped: expected `leaf.is_tombstoned(&index_key(20), &cmp) && !leaf.is_tombstoned(&index_key(30), &cmp)`");
    assert_eq!((0..4).map(|i| leaf.is_deleted_at(i)).collect::<Vec<_>>(), vec![true, true, false, true], "a tombstone can be looked up by key or by slot and dropped");
    assert!(leaf.remove_tombstone(&index_key(40), &cmp), "a tombstone can be looked up by key or by slot and dropped: expected `leaf.remove_tombstone(&index_key(40), &cmp)`");
    assert!(!leaf.remove_tombstone(&index_key(40), &cmp), "already gone");
    assert!(!leaf.remove_tombstone(&index_key(30), &cmp), "never there");
    assert_eq!(leaf.tombstones().iter().map(|k| k.get_as_integer()).collect::<Vec<_>>(), vec![20, 10], "the others keep their order");
    assert_eq!(leaf.size(), 4, "a tombstone does not change the number of pairs");
}

#[test]
fn s2d_01_the_buffer_and_the_entries_do_not_overlap() {
    let keys: Vec<i64> = (100..140).collect();
    let mut bytes = leaf_bytes::<3>(50, &keys);
    let mut leaf = Leaf::<_, Key, Rid, 3>::new(&mut bytes[..]);
    leaf.add_tombstone(&index_key(139));
    leaf.add_tombstone(&index_key(100));
    leaf.add_tombstone(&index_key(120));
    leaf.set_next_page_id(Some(PageId(7)));
    for (i, &k) in keys.iter().enumerate() {
        assert_eq!(leaf.entry_at(i as u32), (index_key(k), rid_of(k)), "entry {i}");
    }
    assert_eq!(leaf.next_page_id(), Some(PageId(7)), "the buffer and the entries do not overlap");
    leaf.set_tombstones(&[]);
    assert_eq!(leaf.num_tombstones(), 0, "the buffer and the entries do not overlap");
    assert_eq!(leaf.key_at(0).get_as_integer(), 100, "clearing the buffer leaves the pairs alone");
}

#[test]
fn s2d_01_without_tombstones_the_buffer_does_not_exist() {
    let mut bytes = leaf_bytes::<0>(10, &[1, 2, 3]);
    let leaf = Leaf::<_, Key, Rid, 0>::new(&mut bytes[..]);
    assert_eq!((leaf.num_tombstones(), leaf.tombstones().len()), (0, 0), "without tombstones the buffer does not exist");
    assert!(!leaf.is_deleted_at(1), "without tombstones the buffer does not exist: expected `!leaf.is_deleted_at(1)`");
    assert_eq!(leaf.entry_at(0), (index_key(1), rid_of(1)), "the pairs start right after the 16-byte header");
}

// ---- 2d-02 · Logical delete -----------------------------------------------------------------------------------------------------

#[test]
fn s2d_02_a_leaf_deletes_logically_and_a_full_buffer_removes_the_oldest_pair() {
    let cmp = GenericComparator::<8>;
    let mut bytes = leaf_bytes::<2>(10, &[1, 2, 3, 4, 5]);
    let mut leaf = Leaf::<_, Key, Rid, 2>::new(&mut bytes[..]);
    assert!(leaf.remove_logically(&index_key(2), &cmp), "a leaf deletes logically and a full buffer removes the oldest pair: expected `leaf.remove_logically(&index_key(2), &cmp)`");
    assert!(leaf.remove_logically(&index_key(4), &cmp), "a leaf deletes logically and a full buffer removes the oldest pair: expected `leaf.remove_logically(&index_key(4), &cmp)`");
    assert_eq!((leaf.size(), leaf.num_tombstones()), (5, 2), "the pairs are still there");
    assert!(!leaf.remove_logically(&index_key(2), &cmp), "already deleted");
    assert!(!leaf.remove_logically(&index_key(9), &cmp), "never there");
    assert!(leaf.remove_logically(&index_key(1), &cmp), "a leaf deletes logically and a full buffer removes the oldest pair: expected `leaf.remove_logically(&index_key(1), &cmp)`");
    // the buffer was full: the oldest tombstoned pair (2) went for real, 1 is the newest tombstone
    assert_eq!(leaf.size(), 4, "a leaf deletes logically and a full buffer removes the oldest pair");
    assert_eq!(leaf.tombstones().iter().map(|k| k.get_as_integer()).collect::<Vec<_>>(), vec![4, 1], "a leaf deletes logically and a full buffer removes the oldest pair");
    assert_eq!((0..4).map(|i| leaf.key_at(i).get_as_integer()).collect::<Vec<_>>(), vec![1, 3, 4, 5], "a leaf deletes logically and a full buffer removes the oldest pair");
    assert_eq!(leaf.lookup(&index_key(1), &cmp), None, "a deleted pair is not found");
    assert_eq!(leaf.lookup(&index_key(3), &cmp), Some(rid_of(3)), "a leaf deletes logically and a full buffer removes the oldest pair");
    assert_eq!(leaf.find(&index_key(1), &cmp), Some(0), "but it is still in the page");
}

#[test]
fn s2d_02_a_leaf_insert_brings_a_tombstoned_pair_back_with_the_new_value() {
    let cmp = GenericComparator::<8>;
    let mut bytes = leaf_bytes::<2>(10, &[1, 2, 3]);
    let mut leaf = Leaf::<_, Key, Rid, 2>::new(&mut bytes[..]);
    leaf.remove_logically(&index_key(2), &cmp);
    assert!(!leaf.insert(&index_key(3), &rid_of(99), &cmp), "a live duplicate is still refused");
    assert!(leaf.insert(&index_key(2), &rid_of(200), &cmp), "a deleted pair comes back");
    assert_eq!((leaf.size(), leaf.num_tombstones()), (3, 0), "no new slot, no tombstone");
    assert_eq!(leaf.lookup(&index_key(2), &cmp), Some(rid_of(200)), "a leaf insert brings a tombstoned pair back with the new value");
}

#[test]
fn s2d_02_physically_removing_a_pair_drops_its_tombstone() {
    let cmp = GenericComparator::<8>;
    let mut bytes = leaf_bytes::<3>(10, &[1, 2, 3, 4]);
    let mut leaf = Leaf::<_, Key, Rid, 3>::new(&mut bytes[..]);
    leaf.remove_logically(&index_key(2), &cmp);
    leaf.remove_logically(&index_key(3), &cmp);
    leaf.remove_at(1); // the pair for key 2, for real
    assert_eq!(leaf.tombstones().iter().map(|k| k.get_as_integer()).collect::<Vec<_>>(), vec![3], "physically removing a pair drops its tombstone");
    assert!(leaf.remove(&index_key(3), &cmp), "physically removing a pair drops its tombstone: expected `leaf.remove(&index_key(3), &cmp)`");
    assert_eq!((leaf.size(), leaf.num_tombstones()), (2, 0), "physically removing a pair drops its tombstone");
}

#[test]
fn s2d_02_remove_buffers_a_tombstone_instead_of_shifting_pairs() {
    let bpm = bpm(30);
    let tree = new_tree_t::<2>(&bpm, 4, 10);
    insert_all(&tree, 0..6);
    assert_eq!(shape_t::<2>(&bpm, tree.get_root_page_id()), "{2,4 [0,1] [2,3] [4,5]}", "remove buffers a tombstone instead of shifting pairs");
    remove(&tree, 2);
    assert_eq!(shape_t::<2>(&bpm, tree.get_root_page_id()), "{2,4 [0,1] [2,3~2] [4,5]}", "remove buffers a tombstone instead of shifting pairs");
    remove(&tree, 3);
    assert_eq!(shape_t::<2>(&bpm, tree.get_root_page_id()), "{2,4 [0,1] [2,3~2,3] [4,5]}", "remove buffers a tombstone instead of shifting pairs");
    remove(&tree, 4);
    assert_eq!(shape_t::<2>(&bpm, tree.get_root_page_id()), "{2,4 [0,1] [2,3~2,3] [4,5~4]}", "remove buffers a tombstone instead of shifting pairs");
    // removing a deleted or a missing key changes nothing
    for k in [2, 3, 4, 9, -1] {
        remove(&tree, k);
    }
    assert_eq!(shape_t::<2>(&bpm, tree.get_root_page_id()), "{2,4 [0,1] [2,3~2,3] [4,5~4]}", "remove buffers a tombstone instead of shifting pairs");
    assert_no_pins(&bpm);
}

#[test]
fn s2d_02_deleted_pairs_are_not_found_and_not_scanned() {
    let bpm = bpm(30);
    let tree = new_tree_t::<2>(&bpm, 4, 10);
    insert_all(&tree, 0..8);
    for k in [1, 5] {
        remove(&tree, k);
    }
    for k in 0..8 {
        assert_eq!(get(&tree, k).len(), (k != 1 && k != 5) as usize, "key {k}");
    }
    assert_eq!(keys_by_scan(&tree), vec![0, 2, 3, 4, 6, 7], "deleted pairs are not found and not scanned");
    let from = |k: i64| tree.begin_at(&index_key(k)).map(|(k, _)| k.get_as_integer()).collect::<Vec<_>>();
    assert_eq!(from(1), vec![2, 3, 4, 6, 7], "a scan starting at a deleted key starts at the next live one");
    assert_eq!(from(5), vec![6, 7], "deleted pairs are not found and not scanned");
    assert_eq!(from(7), vec![7], "deleted pairs are not found and not scanned");
    assert!(tree.begin_at(&index_key(8)).is_end(), "deleted pairs are not found and not scanned: expected `tree.begin_at(&index_key(8)).is_end()`");
}

#[test]
fn s2d_02_a_full_buffer_makes_room_by_really_removing_the_oldest() {
    let bpm = bpm(30);
    let tree = new_tree_t::<2>(&bpm, 6, 10);
    insert_all(&tree, 0..5);
    assert_eq!(shape_t::<2>(&bpm, tree.get_root_page_id()), "[0,1,2,3,4]", "a full buffer makes room by really removing the oldest");
    remove(&tree, 1);
    remove(&tree, 2);
    remove(&tree, 3); // the buffer is full: 1 really goes, 3 is the newest tombstone
    assert_eq!(shape_t::<2>(&bpm, tree.get_root_page_id()), "[0,2,3,4~2,3]", "a full buffer makes room by really removing the oldest");
    assert!(get(&tree, 1).is_empty(), "a full buffer makes room by really removing the oldest: expected `get(&tree, 1).is_empty()`");
    assert_eq!(keys_by_scan(&tree), vec![0, 4], "a full buffer makes room by really removing the oldest");
}

#[test]
fn s2d_02_inserting_a_deleted_key_again_replaces_its_value() {
    let bpm = bpm(30);
    let tree = new_tree_t::<3>(&bpm, 5, 10);
    insert_all(&tree, 0..4);
    remove(&tree, 2);
    assert!(tree.insert(&index_key(2), &rid_of(2000)), "inserting a deleted key again replaces its value: expected `tree.insert(&index_key(2), &rid_of(2000))`");
    assert_eq!(shape_t::<3>(&bpm, tree.get_root_page_id()), "[0,1,2,3]", "inserting a deleted key again replaces its value");
    assert_eq!(get(&tree, 2), vec![rid_of(2000)], "inserting a deleted key again replaces its value");
    assert!(!tree.insert(&index_key(2), &rid_of(1)), "now it is live again: a duplicate");
}

#[test]
fn s2d_02_a_tree_with_every_pair_deleted_is_empty_to_a_scan_but_still_has_its_pages() {
    let bpm = bpm(30);
    let tree = new_tree_t::<4>(&bpm, 6, 10);
    insert_all(&tree, 0..3);
    for k in 0..3 {
        remove(&tree, k);
    }
    assert!(tree.begin().is_end(), "a tree with every pair deleted is empty to a scan but still has its pages: expected `tree.begin().is_end()`");
    assert!(get(&tree, 1).is_empty(), "a tree with every pair deleted is empty to a scan but still has its pages: expected `get(&tree, 1).is_empty()`");
    assert!(tree.get_root_page_id().is_valid(), "the leaf is still there, holding three tombstones");
    assert_eq!(shape_t::<4>(&bpm, tree.get_root_page_id()), "[0,1,2~0,1,2]", "a tree with every pair deleted is empty to a scan but still has its pages");
    assert!(insert(&tree, 1), "a tree with every pair deleted is empty to a scan but still has its pages: expected `insert(&tree, 1)`");
    assert_eq!(keys_by_scan(&tree), vec![1], "a tree with every pair deleted is empty to a scan but still has its pages");
}

#[test]
fn s2d_02_a_delete_that_fits_still_write_latches_only_the_leaf() {
    let bpm = bpm(30);
    let tree = new_tree_t::<2>(&bpm, 4, 10);
    insert_all(&tree, 0..6);
    let (reads, writes) = (tree.bpm.get_reads(), tree.bpm.get_writes());
    remove(&tree, 2);
    assert!(tree.bpm.get_reads() - reads > 0, "a delete that fits still write latches only the leaf: expected `tree.bpm.get_reads() - reads > 0`");
    assert_eq!(tree.bpm.get_writes() - writes, 1, "a delete that fits still write latches only the leaf");
    let writes = tree.bpm.get_writes();
    assert!(insert(&tree, 2), "bringing a pair back is also a single-leaf write");
    assert_eq!(tree.bpm.get_writes() - writes, 1, "a delete that fits still write latches only the leaf");
}

// ---- 2d-03 · Tombstones through splits, borrows and merges ----------------------------------------------------------------------

#[test]
fn s2d_03_a_split_sends_each_tombstone_with_its_pair() {
    let bpm = bpm(30);
    let tree = new_tree_t::<3>(&bpm, 5, 4);
    insert_all(&tree, 0..4);
    for k in [3, 2, 0] {
        remove(&tree, k);
    }
    assert_eq!(shape_t::<3>(&bpm, tree.get_root_page_id()), "[0,1,2,3~3,2,0]", "a split sends each tombstone with its pair");
    insert(&tree, 4); // the leaf reaches max_size 5: split
    assert_eq!(shape_t::<3>(&bpm, tree.get_root_page_id()), "{3 [0,1,2~2,0] [3,4~3]}", "the buffer is divided by key; the order is kept");
    check_structure_t::<3>(&bpm, tree.get_root_page_id()).unwrap();
}

#[test]
fn s2d_03_a_short_leaf_purges_its_own_tombstones_and_merges() {
    // BusTub's TombstoneBorrowTest scenario: the left leaf is at min_size, so the third remove makes it short
    let bpm = bpm(30);
    let tree = new_tree_t::<1>(&bpm, 4, 4);
    insert_all(&tree, 0..5);
    assert_eq!(shape_t::<1>(&bpm, tree.get_root_page_id()), "{2 [0,1] [2,3,4]}", "a short leaf purges its own tombstones and merges");
    remove(&tree, 2); // the right leaf buffers 2
    remove(&tree, 1); // the left leaf buffers 1
    assert_eq!(shape_t::<1>(&bpm, tree.get_root_page_id()), "{2 [0,1~1] [2,3,4~2]}", "a short leaf purges its own tombstones and merges");
    remove(&tree, 0); // the buffer is full: 1 goes for real; the leaf (now [0], 1 pair < min 2) purges 0 as well, then must merge
    assert_eq!(shape_t::<1>(&bpm, tree.get_root_page_id()), "[2,3,4~2]", "one leaf: the right leaf's tombstone survived, the short leaf's did not");
    assert_eq!(keys_by_scan(&tree), vec![3, 4], "a short leaf purges its own tombstones and merges");
}

#[test]
fn s2d_03_a_merge_keeps_the_tombstones_of_the_page_that_stays() {
    // BusTub's TombstoneCoalesceTest scenario
    let bpm = bpm(30);
    let tree = new_tree_t::<2>(&bpm, 6, 6);
    insert_all(&tree, 0..7);
    assert_eq!(shape_t::<2>(&bpm, tree.get_root_page_id()), "{3 [0,1,2] [3,4,5,6]}", "a merge keeps the tombstones of the page that stays");
    for k in [3, 0, 4, 1, 5, 2] {
        remove(&tree, k);
    }
    assert_eq!(shape_t::<2>(&bpm, tree.get_root_page_id()), "[4,5,6~4,5]", "a merge keeps the tombstones of the page that stays");
    assert_eq!(keys_by_scan(&tree), vec![6], "a merge keeps the tombstones of the page that stays");
    check_structure_t::<2>(&bpm, tree.get_root_page_id()).unwrap();
}

#[test]
fn s2d_03_a_leaf_that_borrows_a_deleted_pair_takes_its_tombstone_along() {
    let bpm = bpm(30);
    let tree = new_tree_t::<1>(&bpm, 6, 10);
    insert_all(&tree, 0..7);
    assert_eq!(shape_t::<1>(&bpm, tree.get_root_page_id()), "{3 [0,1,2] [3,4,5,6]}", "a leaf that borrows a deleted pair takes its tombstone along");
    remove(&tree, 3); // the right leaf buffers 3: a deleted pair at its front
    remove(&tree, 1); // the left leaf, at min_size 3, buffers 1
    assert_eq!(shape_t::<1>(&bpm, tree.get_root_page_id()), "{3 [0,1,2~1] [3,4,5,6~3]}", "a leaf that borrows a deleted pair takes its tombstone along");
    remove(&tree, 0); // the buffer is full: 1 goes for real; [0,2] is short, purges 0 too, and borrows 3 (deleted) and its tombstone
    // the left leaf is [2,3~3] (2 pairs, still short) and the right [4,5,6] has nothing more to spare: they merge
    assert_eq!(shape_t::<1>(&bpm, tree.get_root_page_id()), "[2,3,4,5,6~3]", "a leaf that borrows a deleted pair takes its tombstone along");
    assert_eq!(keys_by_scan(&tree), vec![2, 4, 5, 6], "a leaf that borrows a deleted pair takes its tombstone along");
}

#[test]
fn s2d_03_random_operations_agree_with_a_model_for_every_buffer_size() {
    fn run<const T: usize>(leaf: u32, internal: u32, seed: u64) {
        let bpm = bpm(40);
        let tree = new_tree_t::<T>(&bpm, leaf, internal);
        let mut model = BTreeSet::new();
        let mut rng = Lcg(seed);
        for step in 0..500 {
            let key = rng.next(60) as i64;
            if rng.next(5) < 3 {
                assert_eq!(insert(&tree, key), model.insert(key), "T={T} ({leaf},{internal}) seed {seed} step {step}: insert {key}");
            } else {
                model.remove(&key);
                remove(&tree, key);
            }
            check_structure_t::<T>(&bpm, tree.get_root_page_id()).unwrap_or_else(|e| panic!("T={T} ({leaf},{internal}) seed {seed} step {step}: {e}\n{}", shape_t::<T>(&bpm, tree.get_root_page_id())));
        }
        assert_eq!(keys_by_scan(&tree), model.iter().copied().collect::<Vec<_>>(), "T={T} ({leaf},{internal}) seed {seed}");
        assert_no_pins(&bpm);
    }
    for (leaf, internal) in [(2, 3), (3, 3), (4, 4), (5, 4), (6, 7)] {
        for seed in 0..2 {
            run::<1>(leaf, internal, seed);
            run::<2>(leaf, internal, seed + 10);
            run::<3>(leaf, internal, seed + 20);
        }
    }
}

#[test]
fn s2d_03_threads_deleting_and_inserting_keep_every_live_key() {
    let (tx, rx) = mpsc::channel();
    let handle = thread::spawn(move || {
        for _ in 0..5 {
            let bpm = bpm(50);
            let tree = new_tree_t::<3>(&bpm, 4, 5);
            let preserved: Vec<i64> = (1..=400).filter(|k| k % 10 == 0).collect();
            let dynamic: Vec<i64> = (1..=400).filter(|k| k % 10 != 0).collect();
            insert_all(&tree, preserved.iter().copied());
            thread::scope(|scope| {
                for tid in 0..6 {
                    let (tree, preserved, dynamic) = (&tree, &preserved, &dynamic);
                    scope.spawn(move || match tid % 3 {
                        0 => dynamic.iter().for_each(|&k| {
                            insert(tree, k);
                        }),
                        1 => dynamic.iter().for_each(|&k| remove(tree, k)),
                        _ => {
                            for &k in preserved {
                                assert_eq!(get(tree, k), vec![rid_of(k)], "preserved key {k} went missing");
                            }
                        }
                    });
                }
            });
            check_structure_t::<3>(&bpm, tree.get_root_page_id()).unwrap();
            assert_eq!(tree.begin().filter(|(k, _)| k.get_as_integer() % 10 == 0).count(), preserved.len(), "threads deleting and inserting keep every live key");
            assert_no_pins(&bpm);
        }
        tx.send(()).unwrap();
    });
    assert!(rx.recv_timeout(Duration::from_secs(90)).is_ok(), "the workload did not finish: a deadlock?");
    handle.join().unwrap();
}
