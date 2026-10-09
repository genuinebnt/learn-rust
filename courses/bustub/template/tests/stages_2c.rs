//! Tests for module 2c, the B+ tree. A test name starts with its stage: `s2c_02_…` belongs to stage 2c-02, and `anneal course test` runs
//! just those.
//!
//! The tests use only the tree's public API, `BPlusTree::new`, `insert`, `get_value`, `remove`, `begin`, `begin_at`, `end`, and its three
//! read-only observers: `depth`, `leaf_sizes` (and, in module 2d, `leaf_tombstones`). Pages are yours. The rules of a B+ tree are checked
//! from outside by `check_shape` (see `b_plus_tree_utils`): the leaves hold exactly the keys, a leaf is neither overfull nor underfull, the
//! depth fits the number of leaves, every lookup latches the same number of pages (so every leaf is at one depth), and a scan is sorted.
//! Operations are compared with a `BTreeMap`/`BTreeSet` model on random sequences. Anything that could hang waits with a timeout.

mod b_plus_tree_utils;
mod common;

use std::collections::{BTreeMap, BTreeSet};
use std::sync::mpsc;
use std::thread;
use std::time::Duration;

use b_plus_tree_utils::*;
use bustub::buffer::buffer_pool_manager::BufferPoolManager;
use bustub::common::config::PageId;
use bustub::storage::index::b_plus_tree::BPlusTree;
use bustub::storage::index::generic_key::GenericComparator;
use common::pool::{pool_with, Policy};
use proptest::prelude::*;

struct Lcg(u64);
impl Lcg {
    fn next(&mut self, n: usize) -> usize {
        self.0 = self.0.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407);
        ((self.0 >> 33) as usize) % n
    }
}

fn config() -> ProptestConfig {
    ProptestConfig { cases: 24, max_shrink_iters: 2000, ..ProptestConfig::default() }
}

fn new_pool(frames: usize) -> BufferPoolManager {
    pool_with(Policy::Fifo, frames).0
}

/// Runs `work` on a thread; fails the test if it does not finish in time (a deadlock must fail, not hang).
fn within<T: Send + 'static>(what: &str, work: impl FnOnce() -> T + Send + 'static) -> T {
    let (tx, rx) = mpsc::channel();
    thread::spawn(move || {
        let _ = tx.send(work());
    });
    rx.recv_timeout(Duration::from_secs(60)).unwrap_or_else(|_| panic!("timed out: {what} (a latch that is never released?)"))
}

fn assert_nothing_pinned(bpm: &BufferPoolManager) {
    for id in 0..2500 {
        assert!(matches!(bpm.get_pin_count(PageId(id)), None | Some(0)), "page {id} is still pinned between operations: a guard was kept");
    }
}

// ---- 2c-01 · One leaf is a tree -----------------------------------------------------------------------------------------

#[test]
fn s2c_01_a_new_tree_is_empty() {
    let bpm = new_pool(10);
    let tree = new_tree(&bpm, 4, 4);
    assert!(tree.is_empty());
    assert_eq!(tree.get_root_page_id(), PageId::INVALID);
    assert_eq!((tree.depth(), tree.leaf_sizes()), (0, vec![]));
    assert!(get(&tree, 7).is_empty());
    assert_eq!(tree.index_name(), "foo_pk");
}

#[test]
fn s2c_01_the_first_key_makes_a_root_leaf() {
    let bpm = new_pool(10);
    let tree = new_tree(&bpm, 4, 4);
    assert!(insert(&tree, 42));
    assert!(!tree.is_empty());
    assert!(tree.get_root_page_id().is_valid());
    assert_eq!((tree.depth(), tree.leaf_sizes()), (1, vec![1]));
    assert_eq!(get(&tree, 42), vec![rid_of(42)]);
    assert!(get(&tree, 41).is_empty());
}

#[test]
fn s2c_01_a_duplicate_key_is_refused_and_keeps_its_value() {
    let bpm = new_pool(10);
    let tree = new_tree(&bpm, 8, 4);
    assert!(insert(&tree, 5));
    assert!(!tree.insert(&index_key(5), &rid_of(999)), "keys are unique");
    assert_eq!(get(&tree, 5), vec![rid_of(5)], "the first value stays");
    assert_eq!(tree.leaf_sizes(), vec![1]);
}

#[test]
fn s2c_01_creating_a_tree_formats_its_header_page_whatever_it_held() {
    let bpm = new_pool(10);
    let header = bpm.new_page();
    bpm.write_page(header).get_data_mut().fill(0xFF); // a recycled page full of garbage
    let tree: Tree = BPlusTree::new("t", header, &bpm, GenericComparator::<8>, 4, 4);
    assert!(tree.is_empty(), "a new tree on a dirty page is still empty");
    assert!(!tree.get_root_page_id().is_valid());
    assert!(insert(&tree, 1));
    // a second tree on another header page is independent
    let other = new_tree(&bpm, 4, 4);
    assert!(other.is_empty());
    assert!(get(&other, 1).is_empty());
}

#[test]
fn s2c_01_sizes_that_cannot_work_are_a_bug_in_the_caller_and_panic() {
    let bpm = new_pool(10);
    let header = bpm.new_page();
    let make = |leaf: u32, internal: u32| {
        let bpm = &bpm;
        std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let _t: Tree = BPlusTree::new("t", header, bpm, GenericComparator::<8>, leaf, internal);
        }))
        .is_ok()
    };
    assert!(make(2, 3), "the smallest legal tree: 2 pairs per leaf, 3 children per internal page");
    assert!(!make(1, 3), "a leaf must hold at least 2 pairs");
    assert!(!make(4, 2), "an internal page must hold at least 3 children");
    assert!(!make(100_000, 3), "more pairs than fit in a page");
    assert!(!make(4, 100_000), "more children than fit in a page");
}

#[test]
fn s2c_01_the_default_sizes_are_what_a_page_holds() {
    let leaf = Tree::<0>::default_leaf_max_size();
    let internal = Tree::<0>::default_internal_max_size();
    assert!((100..=1100).contains(&leaf), "a leaf of (8-byte key, 8-byte rid) pairs holds hundreds in 8 KiB, not {leaf}");
    assert!((100..=1100).contains(&internal), "an internal page holds hundreds of children, not {internal}");
}

proptest! {
    #![proptest_config(config())]

    /// With the default sizes nothing splits for a few hundred keys: the tree is one leaf and behaves like a map.
    #[test]
    fn s2c_01_a_tree_that_never_splits_behaves_like_a_map(ops in prop::collection::vec((0i64..400, any::<bool>()), 1..250)) {
        let bpm = new_pool(6);
        let tree = new_tree(&bpm, Tree::<0>::default_leaf_max_size(), Tree::<0>::default_internal_max_size());
        let mut model: BTreeMap<i64, i64> = BTreeMap::new();
        for (k, is_insert) in ops {
            if is_insert {
                let v = k * 3 + model.len() as i64;
                let fresh = !model.contains_key(&k);
                prop_assert_eq!(tree.insert(&index_key(k), &rid_of(v)), fresh, "insert({})", k);
                if fresh { model.insert(k, v); }
            } else {
                prop_assert_eq!(get(&tree, k), model.get(&k).map(|&v| vec![rid_of(v)]).unwrap_or_default(), "get({})", k);
            }
        }
        prop_assert_eq!(tree.depth(), usize::from(!model.is_empty()));
        prop_assert_eq!(tree.leaf_sizes(), if model.is_empty() { vec![] } else { vec![model.len()] });
        assert_nothing_pinned(&bpm);
    }
}

// ---- 2c-02 · Splits ------------------------------------------------------------------------------------------------------

#[test]
fn s2c_02_a_leaf_that_reaches_max_size_splits_in_two() {
    let bpm = new_pool(20);
    let tree = new_tree(&bpm, 4, 3);
    for k in 1..=3 {
        assert!(insert(&tree, k));
    }
    assert_eq!((tree.depth(), tree.leaf_sizes()), (1, vec![3]), "three pairs fit in a leaf of max size 4");
    assert!(insert(&tree, 4));
    assert_eq!(tree.depth(), 2, "the fourth pair fills the leaf, which splits under a new root");
    assert_eq!(tree.leaf_sizes(), vec![2, 2], "a split gives half of the pairs to each leaf");
    for k in 1..=4 {
        assert_eq!(get(&tree, k), vec![rid_of(k)]);
    }
}

#[test]
fn s2c_02_the_tree_grows_taller_only_at_the_root_and_by_one_level_at_a_time() {
    let bpm = new_pool(40);
    let tree = new_tree(&bpm, 2, 3);
    let mut last = 0;
    for k in 0..300 {
        assert!(insert(&tree, k * 13 % 301));
        let d = tree.depth();
        assert!(d == last || d == last + 1, "inserting key {k} took the depth from {last} to {d}");
        last = d;
    }
    assert!(last >= 5, "300 keys with 2 pairs per leaf and 3 children per page need at least 5 levels, got {last}");
}

#[test]
fn s2c_02_ascending_inserts_keep_every_rule() {
    let bpm = new_pool(50);
    let tree = new_tree(&bpm, 4, 4);
    let mut live = BTreeSet::new();
    for k in 0..200 {
        assert!(insert(&tree, k));
        live.insert(k);
        check_shape(&tree, &live, 4, 4, false).unwrap_or_else(|e| panic!("after inserting {k}: {e}"));
    }
}

#[test]
fn s2c_02_descending_inserts_keep_every_rule() {
    let bpm = new_pool(50);
    let tree = new_tree(&bpm, 5, 3);
    let mut live = BTreeSet::new();
    for k in (0..200).rev() {
        assert!(insert(&tree, k));
        live.insert(k);
        check_shape(&tree, &live, 5, 3, false).unwrap_or_else(|e| panic!("after inserting {k}: {e}"));
    }
}

#[test]
fn s2c_02_a_refused_duplicate_changes_nothing() {
    let bpm = new_pool(30);
    let tree = new_tree(&bpm, 3, 3);
    for k in 0..50 {
        insert(&tree, k);
    }
    let (depth, sizes) = (tree.depth(), tree.leaf_sizes());
    for k in (0..50).step_by(3) {
        assert!(!tree.insert(&index_key(k), &rid_of(-1)));
    }
    assert_eq!((tree.depth(), tree.leaf_sizes()), (depth, sizes));
    for k in 0..50 {
        assert_eq!(get(&tree, k), vec![rid_of(k)], "key {k} keeps its first value");
    }
}

#[test]
fn s2c_02_every_guard_is_released_after_a_big_build() {
    let bpm = new_pool(40);
    let tree = new_tree(&bpm, 3, 4);
    for k in 0..500 {
        insert(&tree, (k * 37) % 503);
    }
    assert_nothing_pinned(&bpm);
}

proptest! {
    #![proptest_config(config())]

    /// Random keys in random order on trees of random shape: after every insert the shape rules hold and every key is found.
    #[test]
    fn s2c_02_random_inserts_keep_every_rule(leaf_max in 2u32..9, internal_max in 3u32..7, keys in prop::collection::vec(-300i64..300, 1..70)) {
        let bpm = new_pool(60);
        let tree = new_tree(&bpm, leaf_max, internal_max);
        let mut live = BTreeSet::new();
        for k in keys {
            let fresh = live.insert(k);
            prop_assert_eq!(insert(&tree, k), fresh, "insert({})", k);
            if let Err(e) = check_shape(&tree, &live, leaf_max, internal_max, false) {
                return Err(TestCaseError::fail(format!("after inserting {k} (leaf {leaf_max}, internal {internal_max}): {e}")));
            }
        }
        for &k in &live {
            prop_assert_eq!(get(&tree, k), vec![rid_of(k)]);
        }
        assert_nothing_pinned(&bpm);
    }
}

// ---- 2c-03 · The iterator ------------------------------------------------------------------------------------------------

fn filled<'a>(bpm: &'a BufferPoolManager, leaf_max: u32, internal_max: u32, keys: &[i64]) -> Tree<'a> {
    let tree = new_tree(bpm, leaf_max, internal_max);
    for &k in keys {
        insert(&tree, k);
    }
    tree
}

#[test]
fn s2c_03_an_empty_tree_begins_where_it_ends() {
    let bpm = new_pool(10);
    let tree = new_tree(&bpm, 4, 4);
    assert!(tree.begin().is_end());
    assert!(tree.begin() == tree.end());
    assert_eq!(tree.begin().next(), None);
    assert!(tree.begin_at(&index_key(3)).is_end());
}

#[test]
fn s2c_03_a_scan_visits_every_key_once_in_order_across_leaves() {
    let bpm = new_pool(60);
    let keys: Vec<i64> = (0..400).map(|i| (i * 211) % 401).collect();
    let tree = filled(&bpm, 3, 4, &keys);
    assert!(tree.leaf_sizes().len() > 50, "the scan has to cross many leaves");
    let scanned: Vec<(i64, _)> = tree.begin().map(|(k, v)| (k.get_as_integer(), v)).collect();
    let mut want: Vec<i64> = keys.clone();
    want.sort();
    assert_eq!(scanned.iter().map(|p| p.0).collect::<Vec<_>>(), want);
    assert!(scanned.iter().all(|(k, v)| *v == rid_of(*k)), "each key comes with its own value");
}

#[test]
fn s2c_03_begin_at_starts_at_the_first_key_not_less_than_the_argument() {
    let bpm = new_pool(40);
    let tree = filled(&bpm, 3, 3, &(0..100).map(|i| i * 2).collect::<Vec<_>>());
    let from = |k: i64| tree.begin_at(&index_key(k)).map(|(k, _)| k.get_as_integer()).collect::<Vec<_>>();
    assert_eq!(from(40).first(), Some(&40), "a key that is present");
    assert_eq!(from(41).first(), Some(&42), "a key that is absent: the next one");
    assert_eq!(from(-5).len(), 100, "below every key: everything");
    assert!(tree.begin_at(&index_key(199)).is_end(), "above every key: the end");
    assert_eq!(from(196), vec![196, 198]);
}

#[test]
fn s2c_03_iterators_compare_by_position_and_the_end_is_reached_exactly_once() {
    let bpm = new_pool(30);
    let tree = filled(&bpm, 3, 3, &[1, 2, 3, 4, 5, 6, 7]);
    assert!(tree.begin() == tree.begin());
    assert!(tree.begin() != tree.end());
    assert!(tree.begin_at(&index_key(4)) == { let mut it = tree.begin(); for _ in 0..3 { it.next(); } it });
    let mut it = tree.begin();
    for _ in 0..7 {
        assert!(!it.is_end());
        it.next();
    }
    assert!(it.is_end() && it == tree.end() && it.next().is_none());
}

#[test]
fn s2c_03_an_iterator_keeps_no_page_latched_or_pinned() {
    // five frames, ten live iterators: if an iterator pinned a page, the pool would run out
    let bpm = new_pool(5);
    let tree = filled(&bpm, 4, 4, &(0..20).collect::<Vec<_>>());
    let mut iterators: Vec<_> = (0..10).map(|i| tree.begin_at(&index_key(i))).collect();
    for it in iterators.iter_mut() {
        it.next();
    }
    // and the tree can still be changed while they exist
    assert!(insert(&tree, 100));
    assert_nothing_pinned(&bpm);
}

proptest! {
    #![proptest_config(config())]

    /// A scan equals the sorted model, and `begin_at(k)` equals the model's `range(k..)`.
    #[test]
    fn s2c_03_scans_equal_the_sorted_model(leaf_max in 2u32..8, internal_max in 3u32..6, keys in prop::collection::vec(-200i64..200, 0..90), probes in prop::collection::vec(-210i64..210, 1..8)) {
        let bpm = new_pool(60);
        let tree = filled(&bpm, leaf_max, internal_max, &keys);
        let model: BTreeSet<i64> = keys.iter().copied().collect();
        prop_assert_eq!(keys_by_scan(&tree), model.iter().copied().collect::<Vec<_>>());
        for p in probes {
            let got: Vec<i64> = tree.begin_at(&index_key(p)).map(|(k, _)| k.get_as_integer()).collect();
            prop_assert_eq!(got, model.range(p..).copied().collect::<Vec<_>>(), "begin_at({})", p);
        }
    }
}

// ---- 2c-04 · Remove: borrow, merge, shrink ---------------------------------------------------------------------------------

#[test]
fn s2c_04_removing_a_key_that_is_not_there_changes_nothing() {
    let bpm = new_pool(30);
    let tree = filled(&bpm, 3, 3, &(0..30).collect::<Vec<_>>());
    let before = (tree.depth(), tree.leaf_sizes());
    remove(&tree, 100);
    remove(&tree, -1);
    assert_eq!((tree.depth(), tree.leaf_sizes()), before);
    let empty = new_tree(&bpm, 3, 3);
    remove(&empty, 1); // from an empty tree
    assert!(empty.is_empty());
}

#[test]
fn s2c_04_removing_the_last_key_empties_the_tree_and_it_can_be_used_again() {
    let bpm = new_pool(30);
    let tree = new_tree(&bpm, 3, 3);
    insert(&tree, 2);
    remove(&tree, 2);
    assert!(tree.is_empty());
    assert_eq!(tree.get_root_page_id(), PageId::INVALID);
    assert_eq!((tree.depth(), tree.leaf_sizes()), (0, vec![]));
    assert!(get(&tree, 2).is_empty());
    assert!(insert(&tree, 9));
    assert_eq!(keys_by_scan(&tree), vec![9]);
}

#[test]
fn s2c_04_removing_everything_in_any_order_keeps_every_rule_all_the_way_down() {
    for (name, order) in [("ascending", (0..120).collect::<Vec<i64>>()), ("descending", (0..120).rev().collect()), ("scattered", (0..120).map(|i| (i * 53) % 120).collect())] {
        let bpm = new_pool(60);
        let tree = filled(&bpm, 4, 3, &(0..120).collect::<Vec<_>>());
        let mut live: BTreeSet<i64> = (0..120).collect();
        for k in order {
            remove(&tree, k);
            live.remove(&k);
            check_shape(&tree, &live, 4, 3, true).unwrap_or_else(|e| panic!("{name}: after removing {k}: {e}"));
        }
        assert!(tree.is_empty());
        assert_nothing_pinned(&bpm);
    }
}

#[test]
fn s2c_04_the_tree_gets_shorter_when_its_keys_go() {
    let bpm = new_pool(60);
    let tree = filled(&bpm, 4, 3, &(0..200).collect::<Vec<_>>());
    let tall = tree.depth();
    for k in 0..198 {
        remove(&tree, k);
    }
    assert_eq!(keys_by_scan(&tree), vec![198, 199]);
    assert_eq!((tree.depth(), tree.leaf_sizes()), (1, vec![2]), "two keys fit in one leaf: the tree is back to a single root leaf (it was {tall} levels)");
}

#[test]
fn s2c_04_pages_that_are_no_longer_part_of_the_tree_are_given_back() {
    let (bpm, disk) = pool_with(Policy::Fifo, 60);
    let tree = filled(&bpm, 3, 3, &(0..150).collect::<Vec<_>>());
    let peak_leaves = tree.leaf_sizes().len();
    for k in 0..150 {
        remove(&tree, k);
    }
    let freed = disk.deletes.lock().unwrap().len();
    assert!(freed >= peak_leaves, "the tree had {peak_leaves} leaves and is empty again, but only {freed} pages were deleted from the pool");
}

proptest! {
    #![proptest_config(config())]

    /// Random inserts and removes on trees of random shape: after every operation the rules hold and the scan equals the model.
    #[test]
    fn s2c_04_random_inserts_and_removes_keep_every_rule(leaf_max in 2u32..9, internal_max in 3u32..7, ops in prop::collection::vec((-60i64..60, any::<bool>()), 1..160)) {
        let bpm = new_pool(60);
        let tree = new_tree(&bpm, leaf_max, internal_max);
        let mut live = BTreeSet::new();
        for (k, is_insert) in ops {
            if is_insert {
                prop_assert_eq!(insert(&tree, k), live.insert(k), "insert({})", k);
            } else {
                remove(&tree, k);
                live.remove(&k);
            }
            if let Err(e) = check_shape(&tree, &live, leaf_max, internal_max, true) {
                return Err(TestCaseError::fail(format!("after {}({k}) (leaf {leaf_max}, internal {internal_max}): {e}", if is_insert { "insert" } else { "remove" })));
            }
        }
        assert_nothing_pinned(&bpm);
    }
}

// ---- 2c-05 · Latching ------------------------------------------------------------------------------------------------------

/// A tree of 40 even keys (leaf size 4): returns it and a key that lands in a leaf with room for one more pair.
#[test]
fn s2c_05_an_insert_into_a_leaf_with_room_write_latches_only_that_leaf() {
    let bpm = new_pool(60);
    let tree = filled(&bpm, 4, 3, &(0..40).map(|i| i * 2).collect::<Vec<_>>());
    let firsts = leaf_first_keys(&tree);
    let roomy = tree.leaf_sizes().iter().position(|&s| (s as u32) + 1 < 4).expect("a leaf with room");
    let (r0, w0) = (tree.bpm.get_reads(), tree.bpm.get_writes());
    assert!(insert(&tree, firsts[roomy] + 1));
    assert!(tree.bpm.get_reads() > r0, "the descent read-latches the path");
    assert_eq!(tree.bpm.get_writes() - w0, 1, "only the leaf is write-latched when it cannot split");
}

#[test]
fn s2c_05_a_remove_from_a_leaf_above_its_minimum_write_latches_only_that_leaf() {
    let bpm = new_pool(60);
    let tree = filled(&bpm, 4, 3, &(0..40).map(|i| i * 2).collect::<Vec<_>>());
    for k in [1, 3, 5] {
        insert(&tree, k); // fill some leaves above their minimum of 2
    }
    let firsts = leaf_first_keys(&tree);
    let fat = tree.leaf_sizes().iter().position(|&s| (s as u32) > 4 / 2).expect("a leaf above its minimum");
    let w0 = tree.bpm.get_writes();
    remove(&tree, firsts[fat]);
    assert_eq!(tree.bpm.get_writes() - w0, 1, "only the leaf is write-latched when it cannot underflow");
}

#[test]
fn s2c_05_an_insert_that_splits_holds_more_than_the_leaf() {
    let bpm = new_pool(60);
    let tree = filled(&bpm, 4, 3, &[1, 2, 3, 4, 5, 6, 7, 8]);
    let w0 = tree.bpm.get_writes();
    // the tree is in the middle of its life: some insert must split a leaf
    let mut splits = 0;
    for k in 100..110 {
        let before = tree.leaf_sizes().len();
        let w = tree.bpm.get_writes();
        insert(&tree, k);
        if tree.leaf_sizes().len() > before {
            assert!(tree.bpm.get_writes() - w >= 2, "a split changes the leaf and its parent: at least two write latches");
            splits += 1;
        }
    }
    assert!(splits > 0 && tree.bpm.get_writes() > w0);
}

#[test]
fn s2c_05_lookups_and_scans_take_no_write_latch() {
    let bpm = new_pool(60);
    let tree = filled(&bpm, 4, 3, &(0..60).collect::<Vec<_>>());
    let w0 = tree.bpm.get_writes();
    for k in 0..60 {
        get(&tree, k);
    }
    assert_eq!(keys_by_scan(&tree).len(), 60);
    assert_eq!(tree.bpm.get_writes(), w0, "reads must not write-latch");
}

#[test]
fn s2c_05_threads_inserting_disjoint_ranges_lose_nothing() {
    within("4 inserting threads", || {
        let bpm = new_pool(80);
        let tree = new_tree(&bpm, 3, 4);
        thread::scope(|scope| {
            for t in 0..4i64 {
                let tree = &tree;
                scope.spawn(move || {
                    for i in 0..250 {
                        assert!(insert(tree, i * 4 + t), "thread {t}: insert {}", i * 4 + t);
                    }
                });
            }
        });
        let live: BTreeSet<i64> = (0..1000).collect();
        check_shape(&tree, &live, 3, 4, true).unwrap_or_else(|e| panic!("{e}"));
        assert_nothing_pinned(&bpm);
    });
}

#[test]
fn s2c_05_threads_that_insert_remove_and_read_at_once_agree_with_their_models() {
    within("mixed threads", || {
        let bpm = new_pool(80);
        let tree = new_tree(&bpm, 3, 4);
        for k in 10_000..10_150 {
            assert!(insert(&tree, k)); // stable keys the readers expect throughout
        }
        let models: Vec<BTreeSet<i64>> = thread::scope(|scope| {
            let writers: Vec<_> = (0..3i64)
                .map(|t| {
                    let tree = &tree;
                    scope.spawn(move || {
                        let mut model = BTreeSet::new();
                        let mut rng = Lcg(11 + t as u64);
                        for _ in 0..1200 {
                            let k = t * 1000 + rng.next(150) as i64;
                            if rng.next(2) == 0 {
                                assert_eq!(insert(tree, k), model.insert(k), "thread {t}: insert {k}");
                            } else {
                                remove(tree, k);
                                model.remove(&k);
                            }
                        }
                        model
                    })
                })
                .collect();
            for _ in 0..2 {
                let tree = &tree;
                scope.spawn(move || {
                    for round in 0..15 {
                        for k in 10_000..10_150 {
                            assert_eq!(get(tree, k).len(), 1, "reader, round {round}: the stable key {k} must always be found");
                        }
                    }
                });
            }
            writers.into_iter().map(|w| w.join().unwrap()).collect()
        });
        let mut live: BTreeSet<i64> = (10_000..10_150).collect();
        for m in models {
            live.extend(m);
        }
        check_shape(&tree, &live, 3, 4, true).unwrap_or_else(|e| panic!("{e}"));
        assert_nothing_pinned(&bpm);
    });
}

#[test]
fn s2c_05_a_scan_that_runs_while_writers_work_stays_sorted_and_loses_the_stable_keys_never() {
    within("scan and writers", || {
        let bpm = new_pool(80);
        let tree = new_tree(&bpm, 3, 4);
        for k in (0..600).step_by(3) {
            insert(&tree, k); // the stable keys: multiples of 3
        }
        thread::scope(|scope| {
            for t in 0..2i64 {
                let tree = &tree;
                scope.spawn(move || {
                    for i in 0..300 {
                        let k = (i * 3 + 1 + t) % 600; // never a multiple of 3
                        if i % 2 == 0 { insert(tree, k); } else { remove(tree, k); }
                    }
                });
            }
            let tree = &tree;
            scope.spawn(move || {
                for _ in 0..20 {
                    let keys = keys_by_scan(tree);
                    assert!(keys.windows(2).all(|w| w[0] < w[1]), "a scan must stay sorted while the tree changes");
                    assert!((0..600).step_by(3).all(|k| keys.binary_search(&k).is_ok()), "a scan lost a key that was never removed");
                }
            });
        });
    });
}

// ---- 2c-06 · Boss --------------------------------------------------------------------------------------------------------

#[test]
fn s2c_06_a_long_run_of_inserts_removes_scans_and_lookups_agrees_with_a_btreemap() {
    for (leaf_max, internal_max) in [(2, 3), (3, 4), (5, 5), (8, 3)] {
        let bpm = new_pool(80);
        let tree = new_tree(&bpm, leaf_max, internal_max);
        let mut live = BTreeSet::new();
        let mut rng = Lcg(2025 + leaf_max as u64);
        for step in 0..6000 {
            let k = rng.next(400) as i64 - 100;
            match rng.next(10) {
                0..=4 => assert_eq!(insert(&tree, k), live.insert(k), "({leaf_max},{internal_max}) step {step}: insert {k}"),
                5..=7 => {
                    remove(&tree, k);
                    live.remove(&k);
                }
                _ => assert_eq!(get(&tree, k).len(), usize::from(live.contains(&k)), "({leaf_max},{internal_max}) step {step}: get {k}"),
            }
            if step % 500 == 0 {
                check_shape(&tree, &live, leaf_max, internal_max, true).unwrap_or_else(|e| panic!("({leaf_max},{internal_max}) step {step}: {e}"));
            }
        }
        check_shape(&tree, &live, leaf_max, internal_max, true).unwrap_or_else(|e| panic!("({leaf_max},{internal_max}) at the end: {e}"));
        assert_nothing_pinned(&bpm);
    }
}
