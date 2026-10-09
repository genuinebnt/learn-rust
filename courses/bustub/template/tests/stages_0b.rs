//! Tests for module 0b: a skip list.

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

use std::collections::BTreeSet;

use bustub::primer::skiplist::SkipList;
use proptest::prelude::*;

fn list() -> SkipList<i32> {
    SkipList::new()
}

/// BusTub's `InstrumentedSkipList::CheckIntegrity`: the keys and heights are as expected and every level links exactly the nodes tall enough.
fn check_integrity(list: &SkipList<i32>, keys: &[i32], heights: &[usize]) {
    assert_eq!(list.size(), keys.len(), "in helper `check_integrity`");
    let nodes = list.nodes();
    assert_eq!(nodes.iter().map(|n| n.0).collect::<Vec<_>>(), keys, "in helper `check_integrity`");
    assert_eq!(nodes.iter().map(|n| n.1).collect::<Vec<_>>(), heights, "in helper `check_integrity`");
    for level in 0..*heights.iter().max().unwrap_or(&1) {
        let expected: Vec<i32> = keys.iter().zip(heights).filter(|(_, h)| **h > level).map(|(k, _)| *k).collect();
        assert_eq!(list.level(level), expected, "level {level}");
    }
}

// ---- 0b-01: insert and contains -------------------------------------------------------------------------------------------------------------

#[test]
fn s0b_01_a_new_list_is_empty() {
    let l = list();
    assert_eq!(l.size(), 0, "a new list is empty");
    assert!(l.is_empty(), "a new list is empty: expected `l.is_empty()`");
    assert!(!l.contains(&1), "a new list is empty: expected `!l.contains(&1)`");
}

#[test]
fn s0b_01_insert_adds_and_contains_finds() {
    let l = list();
    assert!(l.insert(&1), "insert adds and contains finds: expected `l.insert(&1)`");
    assert_eq!(l.size(), 1, "insert adds and contains finds");
    assert!(l.insert(&2), "insert adds and contains finds: expected `l.insert(&2)`");
    assert_eq!(l.size(), 2, "insert adds and contains finds");
    assert!(l.contains(&1) && l.contains(&2), "insert adds and contains finds: expected `l.contains(&1) && l.contains(&2)`");
    assert!(!l.contains(&3), "insert adds and contains finds: expected `!l.contains(&3)`");
    assert!(!l.is_empty(), "insert adds and contains finds: expected `!l.is_empty()`");
}

#[test]
fn s0b_01_a_duplicate_is_refused_and_changes_nothing() {
    let l = list();
    for i in 0..10 {
        assert!(l.insert(&i), "a duplicate is refused and changes nothing: expected `l.insert(&i)`");
    }
    for i in 0..10 {
        assert!(!l.insert(&i), "a duplicate is refused and changes nothing: expected `!l.insert(&i)`");
    }
    assert_eq!(l.size(), 10, "a duplicate is refused and changes nothing");
    assert_eq!(l.nodes().len(), 10, "a duplicate is refused and changes nothing");
}

#[test]
fn s0b_01_the_list_stays_sorted_whatever_the_insertion_order() {
    let l = list();
    for k in [12, 16, 2, 6, 15, 8, 13, 1, 11, 14, 0, 4, 19, 10, 9, 5, 7, 3, 17, 18] {
        l.insert(&k);
    }
    assert_eq!(l.nodes().iter().map(|n| n.0).collect::<Vec<_>>(), (0..20).collect::<Vec<_>>(), "the list stays sorted whatever the insertion order");
}

#[test]
fn s0b_01_a_comparison_function_decides_the_order() {
    let l: SkipList<i32> = SkipList::with_compare(|a: &i32, b: &i32| a > b);
    for k in [3, 1, 2] {
        l.insert(&k);
    }
    assert_eq!(l.nodes().iter().map(|n| n.0).collect::<Vec<_>>(), vec![3, 2, 1], "a comparison function decides the order");
    assert!(l.contains(&2), "a comparison function decides the order: expected `l.contains(&2)`");
}

#[test]
fn s0b_01_node_heights_come_from_the_seeded_generator() {
    // BusTub's IntegrityCheckTest: the seed is fixed, so the heights are too (listed here by key, 0 to 19)
    let l = list();
    for k in [12, 16, 2, 6, 15, 8, 13, 1, 11, 14, 0, 4, 19, 10, 9, 5, 7, 3, 17, 18] {
        l.insert(&k);
    }
    let keys: Vec<i32> = (0..20).collect();
    let heights = [2, 1, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 3, 1, 1, 2, 1, 1, 2, 3];
    check_integrity(&l, &keys, &heights);
}

#[test]
fn s0b_01_strings_work_too() {
    let l: SkipList<String> = SkipList::new();
    for w in ["pear", "apple", "fig"] {
        l.insert(&w.to_string());
    }
    assert!(l.contains(&"fig".to_string()), "strings work too: expected `l.contains(&\"fig\".to_string())`");
    assert_eq!(l.nodes().iter().map(|n| n.0.clone()).collect::<Vec<_>>(), vec!["apple", "fig", "pear"], "strings work too");
}

// ---- 0b-02: erase and clear ---------------------------------------------------------------------------------------------------------------

#[test]
fn s0b_02_erase_removes_the_key() {
    let l = list();
    for i in 0..5 {
        assert!(l.insert(&i), "erase removes the key: expected `l.insert(&i)`");
    }
    for i in 0..5 {
        assert!(l.contains(&i), "erase removes the key: expected `l.contains(&i)`");
        assert!(l.erase(&i), "erase removes the key: expected `l.erase(&i)`");
        assert!(!l.contains(&i), "erase removes the key: expected `!l.contains(&i)`");
        assert_eq!(l.size(), 5 - i as usize - 1, "erase removes the key");
    }
    assert!(l.is_empty(), "erase removes the key: expected `l.is_empty()`");
}

#[test]
fn s0b_02_erasing_a_missing_key_changes_nothing() {
    let l = list();
    for i in 0..5 {
        l.insert(&i);
    }
    assert!(!l.erase(&10), "erasing a missing key changes nothing: expected `!l.erase(&10)`");
    assert!(!l.erase(&-1), "erasing a missing key changes nothing: expected `!l.erase(&-1)`");
    assert_eq!(l.size(), 5, "erasing a missing key changes nothing");
}

#[test]
fn s0b_02_every_level_forgets_the_erased_node() {
    let l = list();
    for i in 0..200 {
        l.insert(&i);
    }
    for i in (0..200).step_by(3) {
        assert!(l.erase(&i), "every level forgets the erased node: expected `l.erase(&i)`");
    }
    let expected: Vec<i32> = (0..200).filter(|i| i % 3 != 0).collect();
    assert_eq!(l.nodes().iter().map(|n| n.0).collect::<Vec<_>>(), expected, "every level forgets the erased node");
    for level in 1..14 {
        let keys = l.level(level);
        assert!(keys.windows(2).all(|w| w[0] < w[1]), "level {level} is sorted");
        assert!(keys.iter().all(|k| k % 3 != 0), "level {level} still links an erased node");
    }
}

#[test]
fn s0b_02_erased_slots_are_reused_and_the_list_still_works() {
    let l = list();
    for round in 0..5 {
        for i in 0..100 {
            assert!(l.insert(&i), "round {round}");
        }
        for i in 0..100 {
            assert!(l.erase(&i), "erased slots are reused and the list still works: expected `l.erase(&i)`");
        }
        assert!(l.is_empty(), "erased slots are reused and the list still works: expected `l.is_empty()`");
    }
}

#[test]
fn s0b_02_clear_empties_the_list_and_it_can_be_filled_again() {
    let l = list();
    for i in 0..20 {
        l.insert(&i);
    }
    l.clear();
    assert_eq!(l.size(), 0, "clear empties the list and it can be filled again");
    assert!(l.is_empty(), "clear empties the list and it can be filled again: expected `l.is_empty()`");
    for i in 0..30 {
        assert!(!l.contains(&i), "clear empties the list and it can be filled again: expected `!l.contains(&i)`");
    }
    assert!(l.insert(&5), "clear empties the list and it can be filled again: expected `l.insert(&5)`");
    assert_eq!(l.nodes().len(), 1, "clear empties the list and it can be filled again");
}

#[test]
fn s0b_02_erasing_the_tallest_node_lowers_the_height_of_the_list() {
    let l = list();
    for i in 0..500 {
        l.insert(&i);
    }
    let tallest = l.nodes().iter().map(|n| n.1).max().unwrap();
    assert!(tallest > 2, "erasing the tallest node lowers the height of the list: expected `tallest > 2`");
    for (k, _) in l.nodes() {
        l.erase(&k);
    }
    // a list that was once tall and is now empty searches on one level again: it still works
    l.insert(&1);
    assert!(l.contains(&1), "erasing the tallest node lowers the height of the list: expected `l.contains(&1)`");
    assert!(l.level(1).is_empty() || l.level(1) == vec![1], "erasing the tallest node lowers the height of the list: expected `l.level(1).is_empty() || l.level(1) == vec![1]`");
}

// ---- 0b-03: BusTub's tests --------------------------------------------------------------------------------------------------------------------

#[test]
fn s0b_03_insert_contains_clear() {
    let l = list();
    for i in 0..10 {
        assert!(l.insert(&i), "insert contains clear: expected `l.insert(&i)`");
    }
    for i in 0..10 {
        assert!(l.contains(&i), "insert contains clear: expected `l.contains(&i)`");
    }
    for i in 10..20 {
        assert!(!l.contains(&i), "insert contains clear: expected `!l.contains(&i)`");
    }
    for i in 0..10 {
        assert!(!l.insert(&i), "insert contains clear: expected `!l.insert(&i)`");
    }
    assert_eq!(l.size(), 10, "insert contains clear");
    for i in 10..20 {
        assert!(l.insert(&i), "insert contains clear: expected `l.insert(&i)`");
    }
    assert_eq!(l.size(), 20, "insert contains clear");
    l.clear();
    assert!(l.is_empty(), "insert contains clear: expected `l.is_empty()`");
    for i in 0..30 {
        assert!(!l.contains(&i), "insert contains clear: expected `!l.contains(&i)`");
    }
}

#[test]
fn s0b_03_concurrent_insert() {
    let l = Arc::new(list());
    let ok = Arc::new(AtomicUsize::new(0));
    let handles: Vec<_> = (0..10)
        .map(|t| {
            let (l, ok) = (l.clone(), ok.clone());
            std::thread::spawn(move || {
                for i in t * 100..t * 100 + 100 {
                    if l.insert(&i) {
                        ok.fetch_add(1, Ordering::SeqCst);
                    }
                }
            })
        })
        .collect();
    handles.into_iter().for_each(|h| h.join().unwrap());
    assert_eq!(ok.load(Ordering::SeqCst), 1000, "concurrent insert");
    assert!((0..1000).all(|i| l.contains(&i)), "concurrent insert: expected `(0..1000).all(|i| l.contains(&i))`");
    assert_eq!(l.nodes().iter().map(|n| n.0).collect::<Vec<_>>(), (0..1000).collect::<Vec<_>>(), "concurrent insert");
}

#[test]
fn s0b_03_concurrent_erase() {
    let l = Arc::new(list());
    for i in 0..100 {
        l.insert(&i);
    }
    let ok = Arc::new(AtomicUsize::new(0));
    let handles: Vec<_> = (0..10)
        .map(|t| {
            let (l, ok) = (l.clone(), ok.clone());
            std::thread::spawn(move || {
                for i in t * 10..t * 10 + 10 {
                    if l.erase(&i) {
                        ok.fetch_add(1, Ordering::SeqCst);
                    }
                }
            })
        })
        .collect();
    handles.into_iter().for_each(|h| h.join().unwrap());
    assert_eq!(ok.load(Ordering::SeqCst), 100, "concurrent erase");
    assert!(l.is_empty(), "concurrent erase: expected `l.is_empty()`");
}

#[test]
fn s0b_03_concurrent_insert_and_erase() {
    let l = Arc::new(list());
    for i in 0..100 {
        l.insert(&i);
    }
    let (ins, era) = (Arc::new(AtomicUsize::new(0)), Arc::new(AtomicUsize::new(0)));
    let handles: Vec<_> = (0..10)
        .map(|t| {
            let (l, ins, era) = (l.clone(), ins.clone(), era.clone());
            std::thread::spawn(move || {
                for i in t * 10..t * 10 + 10 {
                    if !l.contains(&i) {
                        l.insert(&i);
                    }
                    if l.insert(&(i + 100)) {
                        ins.fetch_add(1, Ordering::SeqCst);
                    }
                    if l.erase(&i) {
                        era.fetch_add(1, Ordering::SeqCst);
                    }
                }
            })
        })
        .collect();
    handles.into_iter().for_each(|h| h.join().unwrap());
    assert_eq!((ins.load(Ordering::SeqCst), era.load(Ordering::SeqCst)), (100, 100), "concurrent insert and erase");
    assert!((100..200).all(|i| l.contains(&i)), "concurrent insert and erase: expected `(100..200).all(|i| l.contains(&i))`");
    assert!((0..100).all(|i| !l.contains(&i)), "concurrent insert and erase: expected `(0..100).all(|i| !l.contains(&i))`");
}

#[test]
fn s0b_03_readers_share_the_list() {
    // 8 readers of a list of 80 000 keys: they must be able to read at the same time (a plain mutex makes them take turns)
    let l = Arc::new(list());
    for i in 0..80_000 {
        l.insert(&i);
    }
    let handles: Vec<_> = (0..8)
        .map(|_| {
            let l = l.clone();
            std::thread::spawn(move || (0..80_000).filter(|i| l.contains(i)).count())
        })
        .collect();
    for h in handles {
        assert_eq!(h.join().unwrap(), 80_000, "readers share the list");
    }
}

#[test]
fn s0b_03_a_big_list_is_dropped_without_overflowing_the_stack() {
    // C++ links nodes with pointers and must free them in a loop; an arena is freed in one go
    let l = list();
    for i in 0..200_000 {
        l.insert(&i);
    }
    drop(l);
}

// ---- properties: the skip list against a set --------------------------------------------------------------------------------------

fn pconfig() -> ProptestConfig {
    ProptestConfig { cases: 64, max_shrink_iters: 2000, failure_persistence: None, ..ProptestConfig::default() }
}

/// What every skip list must look like, whatever was done to it: the keys in order, size right, every height between 1 and 14, level 0
/// holds all keys, each higher level is a sorted **sub-list** of the one below (exactly the nodes tall enough), and the top level in use is
/// the height of the tallest node.
fn well_formed(list: &SkipList<i32>, model: &BTreeSet<i32>) -> Result<(), TestCaseError> {
    let nodes = list.nodes();
    prop_assert_eq!(nodes.iter().map(|n| n.0).collect::<Vec<_>>(), model.iter().copied().collect::<Vec<_>>(), "the keys in order");
    prop_assert_eq!(list.size(), model.len());
    prop_assert_eq!(list.is_empty(), model.is_empty());
    prop_assert!(nodes.iter().all(|(_, h)| (1..=14).contains(h)), "heights are between 1 and MAX_HEIGHT");
    let tallest = nodes.iter().map(|n| n.1).max().unwrap_or(0);
    for level in 0..tallest {
        let expected: Vec<i32> = nodes.iter().filter(|(_, h)| *h > level).map(|(k, _)| *k).collect();
        prop_assert_eq!(list.level(level), expected, "level {} links exactly the nodes tall enough", level);
    }
    prop_assert!(list.level(tallest).is_empty(), "nothing is linked above the tallest node");
    Ok(())
}

#[derive(Clone, Debug)]
enum SetOp {
    Insert(i32),
    Erase(i32),
    Contains(i32),
    Clear,
}

proptest! {
    #![proptest_config(pconfig())]

    /// Any sequence of inserts, erases, lookups and clears: the list answers as a `BTreeSet` does and is well formed after every step.
    #[test]
    fn s0b_02_the_list_behaves_like_a_sorted_set(ops in prop::collection::vec(prop_oneof![
        6 => (-30..30i32).prop_map(SetOp::Insert),
        4 => (-30..30i32).prop_map(SetOp::Erase),
        3 => (-30..30i32).prop_map(SetOp::Contains),
        1 => Just(SetOp::Clear),
    ], 1..120)) {
        let l = list();
        let mut model = BTreeSet::new();
        for op in ops {
            match op {
                SetOp::Insert(k) => prop_assert_eq!(l.insert(&k), model.insert(k)),
                SetOp::Erase(k) => prop_assert_eq!(l.erase(&k), model.remove(&k)),
                SetOp::Contains(k) => prop_assert_eq!(l.contains(&k), model.contains(&k)),
                SetOp::Clear => { l.clear(); model.clear(); }
            }
            well_formed(&l, &model)?;
        }
    }

    /// A list ordered by a different comparison (reverse order, or by absolute value with equal absolute values being the same key)
    /// keeps its keys in that order and treats keys that neither precede the other as equal.
    #[test]
    fn s0b_01_a_comparison_function_decides_what_is_in_order_and_what_is_equal(keys in prop::collection::vec(-20..20i32, 0..40)) {
        let by_abs: SkipList<i32> = SkipList::with_compare(|a: &i32, b: &i32| a.abs() < b.abs());
        let mut seen: BTreeSet<i32> = BTreeSet::new();
        for k in &keys {
            let fresh = seen.insert(k.abs());
            prop_assert_eq!(by_abs.insert(k), fresh, "{} and {} are the same key", k, -k);
        }
        let order: Vec<i32> = by_abs.nodes().iter().map(|n| n.0.abs()).collect();
        prop_assert_eq!(order, seen.iter().copied().collect::<Vec<_>>());
        for k in -20..20i32 {
            prop_assert_eq!(by_abs.contains(&k), seen.contains(&k.abs()));
        }
        let reverse: SkipList<i32> = SkipList::with_compare(|a: &i32, b: &i32| a > b);
        for k in &keys { reverse.insert(k); }
        let mut want: Vec<i32> = keys.iter().copied().collect::<BTreeSet<_>>().into_iter().collect();
        want.reverse();
        prop_assert_eq!(reverse.nodes().iter().map(|n| n.0).collect::<Vec<_>>(), want);
    }
}

#[test]
fn s0b_03_threads_inserting_and_erasing_overlapping_keys_leave_a_well_formed_list() {
    let l = Arc::new(list());
    let workers: Vec<_> = (0..4)
        .map(|t| {
            let l = l.clone();
            std::thread::spawn(move || {
                for i in 0..500 {
                    let k = (i * 7 + t * 13) % 300;
                    if (i + t) % 3 == 0 { l.erase(&k); } else { l.insert(&k); }
                    assert!(l.size() <= 300);
                }
            })
        })
        .collect();
    for w in workers {
        w.join().unwrap();
    }
    let keys: Vec<i32> = l.nodes().iter().map(|n| n.0).collect();
    assert!(keys.windows(2).all(|w| w[0] < w[1]), "the keys are strictly increasing");
    assert_eq!(keys.len(), l.size());
    for k in &keys {
        assert!(l.contains(k));
    }
}
