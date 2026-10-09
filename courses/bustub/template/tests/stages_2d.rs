//! Tests for module 2d, B+ tree tombstones. A test name starts with its stage: `s2d_02_…` belongs to stage 2d-02, and `anneal course test`
//! runs just those.
//!
//! A tree with `TOMBS > 0` deletes logically: a leaf keeps the pair where it is and remembers the key in a small buffer of tombstones.
//! The tests see the leaves only through the tree's observers (`leaf_keys`, `leaf_tombstones`, `leaf_sizes`, `depth`), written as text:
//! `[0,1][2,3~2,3][4,5~4]` is three leaves; the keys before a `~` are the pairs stored in the leaf, the keys after it its tombstones,
//! oldest first. Besides exact scenarios (the rules are in the stage page), random operations run against a `BTreeSet` and a checker
//! (`check_shape_t`) verifies from outside that every tombstone belongs to a pair in its leaf, no buffer overflows, leaf sizes and depth
//! are right, and a scan returns exactly the live keys.

mod b_plus_tree_utils;
mod common;

use std::collections::BTreeSet;
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

use b_plus_tree_utils::*;
use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::PageId;
#[path = "common/pool.rs"]
mod pool;
use pool::{pool_with, Policy};
use proptest::prelude::*;

struct Lcg(u64);
impl Lcg {
    fn next(&mut self, n: usize) -> usize {
        self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        ((self.0 >> 33) as usize) % n
    }
}

fn bpm(frames: usize) -> BufferPoolManager {
    pool_with(Policy::Fifo, frames).0
}

fn assert_no_pins(bpm: &BufferPoolManager) {
    for id in 0..2500 {
        assert!(matches!(bpm.get_pin_count(PageId(id)), None | Some(0)), "page {id} is still pinned: a guard was kept");
    }
}

fn insert_all<const T: usize>(tree: &Tree<T>, keys: impl IntoIterator<Item = i64>) {
    for k in keys {
        assert!(insert(tree, k), "insert {k}");
    }
}

// ---- 2d-01 · Deleting without moving anything ----------------------------------------------------------------------------

#[test]
fn s2d_01_remove_buffers_a_tombstone_instead_of_shifting_pairs() {
    let bpm = bpm(30);
    let tree = new_tree_t::<2>(&bpm, 4, 10);
    insert_all(&tree, 0..6);
    assert_eq!(leaves_t(&tree), "[0,1][2,3][4,5]");
    remove(&tree, 2);
    assert_eq!(leaves_t(&tree), "[0,1][2,3~2][4,5]", "the pair stays in its leaf; its key goes in the buffer");
    remove(&tree, 3);
    assert_eq!(leaves_t(&tree), "[0,1][2,3~2,3][4,5]", "tombstones keep the order they were added in");
    remove(&tree, 4);
    assert_eq!(leaves_t(&tree), "[0,1][2,3~2,3][4,5~4]");
    for k in [2, 3, 4, 9, -1] {
        remove(&tree, k); // already deleted, or not there at all
    }
    assert_eq!(leaves_t(&tree), "[0,1][2,3~2,3][4,5~4]", "removing a deleted or a missing key changes nothing");
    assert_no_pins(&bpm);
}

#[test]
fn s2d_01_deleted_pairs_are_not_found_and_not_scanned() {
    let bpm = bpm(30);
    let tree = new_tree_t::<2>(&bpm, 4, 10);
    insert_all(&tree, 0..8);
    for k in [1, 5] {
        remove(&tree, k);
    }
    for k in 0..8 {
        assert_eq!(get(&tree, k).len(), usize::from(k != 1 && k != 5), "key {k}");
    }
    assert_eq!(keys_by_scan(&tree), vec![0, 2, 3, 4, 6, 7]);
    let from = |k: i64| tree.begin_at(&index_key(k)).map(|(k, _)| k.get_as_integer()).collect::<Vec<_>>();
    assert_eq!(from(1), vec![2, 3, 4, 6, 7], "a scan starting at a deleted key starts at the next live one");
    assert_eq!(from(5), vec![6, 7]);
    assert_eq!(from(7), vec![7]);
    assert!(tree.begin_at(&index_key(8)).is_end());
}

#[test]
fn s2d_01_a_full_buffer_makes_room_by_really_removing_the_oldest() {
    let bpm = bpm(30);
    let tree = new_tree_t::<2>(&bpm, 6, 10);
    insert_all(&tree, 0..5);
    assert_eq!(leaves_t(&tree), "[0,1,2,3,4]");
    remove(&tree, 1);
    remove(&tree, 2);
    remove(&tree, 3); // the buffer is full: 1 goes for real, 3 is the newest tombstone
    assert_eq!(leaves_t(&tree), "[0,2,3,4~2,3]");
    assert!(get(&tree, 1).is_empty());
    assert_eq!(keys_by_scan(&tree), vec![0, 4]);
}

#[test]
fn s2d_01_inserting_a_deleted_key_again_brings_it_back_with_the_new_value() {
    let bpm = bpm(30);
    let tree = new_tree_t::<3>(&bpm, 5, 10);
    insert_all(&tree, 0..4);
    remove(&tree, 2);
    assert!(tree.insert(&index_key(2), &rid_of(2000)), "a deleted key can be inserted again");
    assert_eq!(leaves_t(&tree), "[0,1,2,3]", "it takes its old slot and its tombstone goes");
    assert_eq!(get(&tree, 2), vec![rid_of(2000)]);
    assert!(!tree.insert(&index_key(2), &rid_of(1)), "now it is live again: a duplicate");
}

#[test]
fn s2d_01_a_tree_with_every_pair_deleted_is_empty_to_a_scan_but_still_has_its_page() {
    let bpm = bpm(30);
    let tree = new_tree_t::<4>(&bpm, 6, 10);
    insert_all(&tree, 0..3);
    for k in 0..3 {
        remove(&tree, k);
    }
    assert!(tree.begin().is_end());
    assert!(get(&tree, 1).is_empty());
    assert!(tree.get_root_page_id().is_valid(), "the leaf is still there, holding three tombstones");
    assert_eq!(leaves_t(&tree), "[0,1,2~0,1,2]");
    assert!(insert(&tree, 1));
    assert_eq!(keys_by_scan(&tree), vec![1]);
}

#[test]
fn s2d_01_a_delete_that_fits_still_write_latches_only_the_leaf() {
    let bpm = bpm(30);
    let tree = new_tree_t::<2>(&bpm, 4, 10);
    insert_all(&tree, 0..6);
    let (reads, writes) = (tree.bpm.get_reads(), tree.bpm.get_writes());
    remove(&tree, 2);
    assert!(tree.bpm.get_reads() > reads);
    assert_eq!(tree.bpm.get_writes() - writes, 1);
    let writes = tree.bpm.get_writes();
    assert!(insert(&tree, 2), "bringing a pair back is also a single-leaf write");
    assert_eq!(tree.bpm.get_writes() - writes, 1);
}

#[test]
fn s2d_01_a_tree_without_tombstones_has_none_to_report() {
    let bpm = bpm(30);
    let tree = new_tree(&bpm, 4, 4);
    insert_all(&tree, 0..10);
    remove(&tree, 3);
    assert!(tree.leaf_tombstones().iter().all(|t| t.is_empty()), "with TOMBS = 0 a delete is physical");
    assert_eq!(tree.leaf_keys().concat().len(), 9);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 24, max_shrink_iters: 2000, failure_persistence: None, ..ProptestConfig::default() })]

    /// On one big leaf (nothing splits) any operations agree with a set, and a leaf holds at most `T` tombstones.
    #[test]
    fn s2d_01_logical_deletes_agree_with_a_set(t in 1usize..4, ops in prop::collection::vec((0i64..30, any::<bool>()), 1..120)) {
        fn run<const T: usize>(ops: &[(i64, bool)]) -> Result<(), String> {
            let bpm = bpm(10);
            let tree = new_tree_t::<T>(&bpm, 60, 4);
            let mut live = BTreeSet::new();
            for &(k, is_insert) in ops {
                if is_insert {
                    if insert(&tree, k) != live.insert(k) { return Err(format!("insert({k}) answered wrongly")); }
                } else {
                    remove(&tree, k);
                    live.remove(&k);
                }
                check_shape_t::<T>(&tree, &live, 60, 4, true)?;
            }
            Ok(())
        }
        let r = match t { 1 => run::<1>(&ops), 2 => run::<2>(&ops), _ => run::<3>(&ops) };
        prop_assert!(r.is_ok(), "{:?}", r);
    }
}

// ---- 2d-02 · Tombstones through splits, borrows and merges ---------------------------------------------------------------

#[test]
fn s2d_02_a_split_sends_each_tombstone_with_its_pair() {
    let bpm = bpm(30);
    let tree = new_tree_t::<3>(&bpm, 5, 4);
    insert_all(&tree, 0..4);
    for k in [3, 2, 0] {
        remove(&tree, k);
    }
    assert_eq!(leaves_t(&tree), "[0,1,2,3~3,2,0]");
    insert(&tree, 4); // the leaf reaches max_size 5: split
    assert_eq!(leaves_t(&tree), "[0,1,2~2,0][3,4~3]", "the buffer is divided by key; the order is kept");
}

#[test]
fn s2d_02_a_short_leaf_purges_its_own_tombstones_and_merges() {
    // BusTub's TombstoneBorrowTest scenario: the left leaf is at min_size, so the third remove makes it short
    let bpm = bpm(30);
    let tree = new_tree_t::<1>(&bpm, 4, 4);
    insert_all(&tree, 0..5);
    assert_eq!(leaves_t(&tree), "[0,1][2,3,4]");
    remove(&tree, 2); // the right leaf buffers 2
    remove(&tree, 1); // the left leaf buffers 1
    assert_eq!(leaves_t(&tree), "[0,1~1][2,3,4~2]");
    remove(&tree, 0); // the buffer is full: 1 goes for real; the leaf (now [0], below min 2) purges 0 as well, then must merge
    assert_eq!(leaves_t(&tree), "[2,3,4~2]", "one leaf: the right leaf's tombstone survived, the short leaf's did not");
    assert_eq!(keys_by_scan(&tree), vec![3, 4]);
}

#[test]
fn s2d_02_a_merge_keeps_the_tombstones_of_the_page_that_stays() {
    // BusTub's TombstoneCoalesceTest scenario
    let bpm = bpm(30);
    let tree = new_tree_t::<2>(&bpm, 6, 6);
    insert_all(&tree, 0..7);
    assert_eq!(leaves_t(&tree), "[0,1,2][3,4,5,6]");
    for k in [3, 0, 4, 1, 5, 2] {
        remove(&tree, k);
    }
    assert_eq!(leaves_t(&tree), "[4,5,6~4,5]");
    assert_eq!(keys_by_scan(&tree), vec![6]);
}

#[test]
fn s2d_02_a_leaf_that_borrows_a_deleted_pair_takes_its_tombstone_along() {
    let bpm = bpm(30);
    let tree = new_tree_t::<1>(&bpm, 6, 10);
    insert_all(&tree, 0..7);
    assert_eq!(leaves_t(&tree), "[0,1,2][3,4,5,6]");
    remove(&tree, 3); // the right leaf buffers 3: a deleted pair at its front
    remove(&tree, 1); // the left leaf, at min_size 3, buffers 1
    assert_eq!(leaves_t(&tree), "[0,1,2~1][3,4,5,6~3]");
    remove(&tree, 0); // the buffer is full: 1 goes for real; [0,2] is short, purges 0 too, and borrows 3 (deleted) and its tombstone
    assert_eq!(leaves_t(&tree), "[2,3,4,5,6~3]", "the left leaf is still short, the right has nothing more to spare: they merge");
    assert_eq!(keys_by_scan(&tree), vec![2, 4, 5, 6]);
}

#[test]
fn s2d_02_deletes_that_the_buffers_can_hold_never_change_the_shape_of_the_tree() {
    let bpm = bpm(60);
    let tree = new_tree_t::<2>(&bpm, 4, 3);
    insert_all(&tree, 0..100); // leaves of two pairs each: a leaf can never be asked for a third tombstone
    let (depth, leaves) = (tree.depth(), tree.leaf_sizes());
    for k in 0..99 {
        remove(&tree, k);
    }
    assert_eq!(keys_by_scan(&tree), vec![99]);
    assert_eq!((tree.depth(), tree.leaf_sizes()), (depth, leaves), "every delete fitted in a buffer, so no pair moved and no page merged");
    assert_eq!(tree.leaf_tombstones().concat().len(), 99);
    assert_no_pins(&bpm);
}

#[test]
fn s2d_02_once_the_buffers_overflow_the_dead_pairs_go_for_real_and_leaves_merge_away() {
    let bpm = bpm(60);
    let tree = new_tree_t::<1>(&bpm, 6, 3);
    insert_all(&tree, 0..100);
    let leaves = tree.leaf_sizes().len();
    for k in 0..99 {
        remove(&tree, k);
    }
    assert_eq!(keys_by_scan(&tree), vec![99]);
    assert!(tree.leaf_sizes().len() < leaves / 3, "one tombstone per leaf cannot hold 99 deletes: {} of {leaves} leaves are left", tree.leaf_sizes().len());
    assert!(tree.leaf_tombstones().concat().len() <= tree.leaf_sizes().len());
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 24, max_shrink_iters: 2000, failure_persistence: None, ..ProptestConfig::default() })]

    /// Trees of random shape and buffer size, random inserts and removes: after every step the structure rules of `check_shape_t` hold.
    #[test]
    fn s2d_02_random_operations_keep_every_rule_for_every_buffer_size(t in 1usize..4, leaf_max in 2u32..8, internal_max in 3u32..6, ops in prop::collection::vec((-40i64..40, any::<bool>()), 1..140)) {
        fn run<const T: usize>(leaf_max: u32, internal_max: u32, ops: &[(i64, bool)]) -> Result<(), String> {
            let bpm = bpm(60);
            let tree = new_tree_t::<T>(&bpm, leaf_max, internal_max);
            let mut live = BTreeSet::new();
            for (i, &(k, is_insert)) in ops.iter().enumerate() {
                if is_insert {
                    if insert(&tree, k) != live.insert(k) { return Err(format!("step {i}: insert({k}) answered wrongly")); }
                } else {
                    remove(&tree, k);
                    live.remove(&k);
                }
                check_shape_t::<T>(&tree, &live, leaf_max, internal_max, true).map_err(|e| format!("step {i}, {}({k}), T={T} leaf {leaf_max} internal {internal_max}: {e}\n{}", if is_insert { "insert" } else { "remove" }, leaves_t(&tree)))?;
            }
            assert_no_pins(&bpm);
            Ok(())
        }
        let r = match t { 1 => run::<1>(leaf_max, internal_max, &ops), 2 => run::<2>(leaf_max, internal_max, &ops), _ => run::<3>(leaf_max, internal_max, &ops) };
        prop_assert!(r.is_ok(), "{:?}", r);
    }
}

// ---- 2d-03 · Boss ----------------------------------------------------------------------------------------------------------

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
            let scanned: BTreeSet<i64> = keys_by_scan(&tree).into_iter().collect();
            assert!(preserved.iter().all(|k| scanned.contains(k)), "a preserved key is missing from the scan");
            // whatever the dynamic keys ended as, the structure must be sound for the keys that are live
            check_shape_t::<3>(&tree, &scanned, 4, 5, true).unwrap_or_else(|e| panic!("{e}"));
            assert_no_pins(&bpm);
        }
        tx.send(()).unwrap();
    });
    assert!(rx.recv_timeout(Duration::from_secs(90)).is_ok(), "the workload did not finish: a deadlock?");
    handle.join().unwrap();
}

#[test]
fn s2d_03_long_runs_for_every_buffer_size_agree_with_a_set() {
    fn run<const T: usize>(leaf: u32, internal: u32, seed: u64) {
        let bpm = bpm(60);
        let tree = new_tree_t::<T>(&bpm, leaf, internal);
        let mut live = BTreeSet::new();
        let mut rng = Lcg(seed);
        for step in 0..1500 {
            let key = rng.next(80) as i64;
            if rng.next(5) < 3 {
                assert_eq!(insert(&tree, key), live.insert(key), "T={T} ({leaf},{internal}) seed {seed} step {step}: insert {key}");
            } else {
                live.remove(&key);
                remove(&tree, key);
            }
            if step % 25 == 0 {
                check_shape_t::<T>(&tree, &live, leaf, internal, true).unwrap_or_else(|e| panic!("T={T} ({leaf},{internal}) seed {seed} step {step}: {e}\n{}", leaves_t(&tree)));
            }
        }
    }
    for (leaf, internal) in [(2, 3), (3, 3), (4, 4), (5, 4), (6, 7)] {
        for seed in 0..3 {
            run::<1>(leaf, internal, seed);
            run::<2>(leaf, internal, seed + 10);
            run::<3>(leaf, internal, seed + 20);
        }
    }
}
