//! Tests for module 0d: sketches and a CRDT: a count-min sketch, HyperLogLog and an observed-remove set.

use std::sync::Arc;

use bustub::primer::count_min_sketch::CountMinSketch;
use bustub::primer::hyperloglog::{HyperLogLog, HyperLogLogPresto};
use bustub::primer::orset::{ORSet, ORSetDriver};

fn cms<K: std::hash::Hash>(width: u32, depth: u32) -> CountMinSketch<K> {
    CountMinSketch::new(width, depth).unwrap()
}

// ---- 0d-01: count-min sketch: insert and count -----------------------------------------------------------------------------------------

#[test]
fn s0d_01_a_zero_dimension_is_an_error() {
    for i in [10u32, 20, 30, 40] {
        assert!(CountMinSketch::<i32>::new(0, i).is_err());
        assert!(CountMinSketch::<i32>::new(i * 5, 0).is_err());
    }
    assert!(CountMinSketch::<i32>::new(1, 1).is_ok());
}

#[test]
fn s0d_01_counts_of_strings() {
    let s: CountMinSketch<String> = cms(200, 12);
    let key = |x: &str| x.to_string();
    assert_eq!(s.count(&key("test")), 0);
    s.insert(&key("Welcome to CMU DB (15-445/645)"));
    assert_eq!(s.count(&key("Welcome to CMU DB (15-445/645)")), 1);
    let names = ["DJ-Cache", "Sirui", "Andy", "Melody", "William", "Saransh", "Song", "Ruiqi", "David"];
    for i in 0..10u32 {
        for n in names {
            s.insert(&key(n));
        }
        for n in names {
            assert_eq!(s.count(&key(n)), i + 1);
        }
    }
    assert_eq!(s.count(&key("NonExistent")), 0);
}

#[test]
fn s0d_01_counts_of_integers_including_negative_ones() {
    let s: CountMinSketch<i64> = cms(500, 20);
    assert_eq!(s.count(&0), 0);
    s.insert(&0);
    for i in 0..30u32 {
        for j in 0..4u32 {
            for k in [10i64, 122, 200, 911, 15445] {
                s.insert(&k);
            }
            for k in [10i64, 122, 200, 911, 15445] {
                assert_eq!(s.count(&k), i * 4 + j + 1);
            }
        }
        for j in 0..5u32 {
            for k in [-1i64, -2, -3, -15445] {
                s.insert(&k);
            }
            for k in [-1i64, -2, -3, -15445] {
                assert_eq!(s.count(&k), i * 5 + j + 1);
            }
        }
    }
    assert_eq!((s.count(&0), s.count(&10), s.count(&-1), s.count(&999999)), (1, 120, 150, 0));
}

#[test]
fn s0d_01_width_one_makes_every_item_collide_and_the_minimum_is_the_total() {
    let s: CountMinSketch<i64> = cms(1, 20);
    s.insert(&1);
    s.insert(&2);
    assert_eq!((s.count(&1), s.count(&2)), (2, 2));
    s.insert(&3);
    s.insert(&4);
    for k in 1..=4 {
        assert_eq!(s.count(&k), 4);
    }
    let one: CountMinSketch<i64> = cms(1, 1);
    for k in 0..5 {
        one.insert(&k);
    }
    assert_eq!((one.count(&0), one.count(&999), one.count(&-1)), (5, 5, 5), "even an item never inserted");
}

#[test]
fn s0d_01_the_estimate_is_never_below_the_truth_with_one_row() {
    let s: CountMinSketch<i64> = cms(50, 1);
    s.insert(&15445);
    s.insert(&(15445 + 4));
    s.insert(&15445);
    assert!(s.count(&15445) >= 2);
    assert!(s.count(&(15445 + 4)) >= 1);
}

#[test]
fn s0d_01_each_row_hashes_differently_but_always_the_same_way() {
    let s: CountMinSketch<i64> = cms(1000, 8);
    let columns: Vec<usize> = (0..8).map(|row| s.column(row, &12345)).collect();
    assert_eq!(columns, (0..8).map(|row| s.column(row, &12345)).collect::<Vec<_>>());
    assert!(columns.iter().all(|c| *c < 1000));
    let distinct: std::collections::BTreeSet<_> = columns.iter().collect();
    assert!(distinct.len() >= 5, "rows should not all pick the same column: {columns:?}");
}

// ---- 0d-02: clear, merge and top-k ------------------------------------------------------------------------------------------------------------

#[test]
fn s0d_02_clear_resets_every_count() {
    let s: CountMinSketch<i32> = cms(200, 10);
    for (item, times) in [(1, 15), (2, 10), (3, 8)] {
        for _ in 0..times {
            s.insert(&item);
        }
    }
    assert_eq!((s.count(&1), s.count(&2), s.count(&3)), (15, 10, 8));
    s.clear();
    assert_eq!((s.count(&1), s.count(&2), s.count(&3), s.count(&999)), (0, 0, 0, 0));
    s.insert(&1);
    assert_eq!(s.count(&1), 1);
}

#[test]
fn s0d_02_merge_adds_the_counts_of_two_sketches() {
    let (a, b): (CountMinSketch<String>, CountMinSketch<String>) = (cms(250, 8), cms(250, 8));
    let key = |x: &str| x.to_string();
    for (item, times) in [("055", 5), ("4987", 2), ("3125", 3), ("2256", 1)] {
        for _ in 0..times {
            a.insert(&key(item));
        }
    }
    for (item, times) in [("4739", 5), ("3125", 2), ("4987", 3), ("2256", 4)] {
        for _ in 0..times {
            b.insert(&key(item));
        }
    }
    a.merge(&b).unwrap();
    for item in ["055", "4987", "4739", "2256", "3125"] {
        assert_eq!(a.count(&key(item)), 5, "{item}");
    }
    assert_eq!((b.count(&key("4739")), b.count(&key("3125"))), (5, 2), "the other sketch is unchanged");
}

#[test]
fn s0d_02_merge_with_collisions_and_with_incompatible_sketches() {
    let (a, b): (CountMinSketch<i32>, CountMinSketch<i32>) = (cms(1, 20), cms(1, 20));
    for k in [1, 2, 5] {
        a.insert(&k);
    }
    for k in [3, 4] {
        b.insert(&k);
    }
    a.merge(&b).unwrap();
    assert_eq!((a.count(&1), a.count(&996)), (5, 5));
    let other: CountMinSketch<i32> = cms(2, 20);
    assert!(a.merge(&other).is_err());
    let other: CountMinSketch<i32> = cms(1, 19);
    assert!(a.merge(&other).is_err());
}

#[test]
fn s0d_02_top_k_orders_the_candidates_by_estimated_count() {
    for iter in 1..10u32 {
        let s: CountMinSketch<String> = cms(10, 3);
        for (item, times) in [("frequent", iter + 4), ("medium", iter + 2), ("rare", iter)] {
            for _ in 0..times {
                s.insert(&item.to_string());
            }
        }
        let candidates: Vec<String> = ["rare", "frequent", "medium"].iter().map(|s| s.to_string()).collect();
        let top = s.top_k(3, &candidates);
        assert_eq!(top, vec![("frequent".to_string(), iter + 4), ("medium".to_string(), iter + 2), ("rare".to_string(), iter)]);
    }
}

#[test]
fn s0d_02_top_k_keeps_at_most_k_and_at_most_the_candidates() {
    let s: CountMinSketch<i32> = cms(200, 15);
    for (item, times) in [(1, 1), (2, 5), (3, 3), (4, 9)] {
        for _ in 0..times {
            s.insert(&item);
        }
    }
    let top: Vec<i32> = s.top_k(3, &[1, 2, 3, 4]).into_iter().map(|p| p.0).collect();
    assert_eq!(top, vec![4, 2, 3]);
    assert_eq!(s.top_k(10, &[1, 2]).len(), 2);
    assert!(s.top_k(0, &[1, 2]).is_empty());
    assert_eq!(s.top_k(2, &[7, 8]).iter().map(|p| p.1).collect::<Vec<_>>(), vec![0, 0], "unseen candidates count 0 and keep their order");
}

#[test]
fn s0d_02_top_k_tracks_a_sketch_that_keeps_counting() {
    // BusTub's TopKDynamicTest: the same sketch gets more and more inserts
    let cases: [[u32; 4]; 6] = [[1, 2, 3, 4], [7, 5, 3, 1], [2, 2, 5, 7], [6, 6, 2, 2], [1, 3, 6, 6], [400, 200, 300, 100]];
    let expected: [[i32; 3]; 6] = [[4, 3, 2], [1, 2, 3], [4, 3, 1], [1, 2, 4], [4, 3, 2], [1, 3, 2]];
    let s: CountMinSketch<i32> = cms(200, 15);
    for (case, want) in cases.iter().zip(expected) {
        for (i, times) in case.iter().enumerate() {
            for _ in 0..*times {
                s.insert(&(i as i32 + 1));
            }
        }
        let got: Vec<i32> = s.top_k(3, &[1, 2, 3, 4]).into_iter().map(|p| p.0).collect();
        assert_eq!(got, want);
    }
}

// ---- 0d-03: HyperLogLog: registers ---------------------------------------------------------------------------------------------------------

#[test]
fn s0d_03_the_register_is_the_top_bits_of_the_hash() {
    let h: HyperLogLog<i64> = HyperLogLog::new(3);
    assert_eq!(h.register_index(0), 0);
    assert_eq!(h.register_index(u64::MAX), 7);
    assert_eq!(h.register_index(0b101 << 61), 5);
    assert_eq!(h.register_index(0b101 << 61 | 12345), 5);
    let one: HyperLogLog<i64> = HyperLogLog::new(0);
    assert_eq!(one.register_index(u64::MAX), 0);
}

#[test]
fn s0d_03_the_run_length_is_the_position_of_the_leftmost_one_after_the_register_bits() {
    let h: HyperLogLog<i64> = HyperLogLog::new(3);
    // 3 register bits, then 61 bits
    assert_eq!(h.position_of_leftmost_one(0b000_1 << 60), 1);
    assert_eq!(h.position_of_leftmost_one(0b111_01 << 59), 2);
    assert_eq!(h.position_of_leftmost_one(0b010_0001 << 57), 4);
    assert_eq!(h.position_of_leftmost_one(0b101 << 61), 62, "all zeros after the register bits: 64 - 3 + 1");
    assert_eq!(h.position_of_leftmost_one(1), 61, "the last bit");
}

#[test]
fn s0d_03_with_no_register_bits_all_64_bits_count() {
    let h: HyperLogLog<i64> = HyperLogLog::new(0);
    assert_eq!(h.position_of_leftmost_one(1 << 63), 1);
    assert_eq!(h.position_of_leftmost_one(1), 64);
    assert_eq!(h.position_of_leftmost_one(0), 65);
}

#[test]
fn s0d_03_adding_a_value_raises_exactly_one_register_to_its_rank() {
    let h: HyperLogLog<i64> = HyperLogLog::new(4);
    assert!(h.registers().iter().all(|r| *r == 0));
    h.add_elem(&42);
    let regs = h.registers();
    assert_eq!(regs.iter().filter(|r| **r > 0).count(), 1);
    assert!(*regs.iter().max().unwrap() >= 1);
}

#[test]
fn s0d_03_adding_the_same_value_twice_changes_nothing() {
    let h: HyperLogLog<i64> = HyperLogLog::new(4);
    h.add_elem(&42);
    let once = h.registers();
    for _ in 0..100 {
        h.add_elem(&42);
    }
    assert_eq!(h.registers(), once);
}

#[test]
fn s0d_03_a_register_only_ever_grows() {
    let h: HyperLogLog<i64> = HyperLogLog::new(2);
    let mut before = h.registers();
    for i in 0..500 {
        h.add_elem(&i);
        let after = h.registers();
        assert!(before.iter().zip(&after).all(|(b, a)| a >= b));
        before = after;
    }
    assert!(before.iter().all(|r| *r > 0), "500 values reach all 4 registers");
}

#[test]
fn s0d_03_a_negative_size_has_no_registers_and_ignores_everything() {
    let none: HyperLogLog<i64> = HyperLogLog::new(-2);
    none.add_elem(&1);
    assert!(none.registers().is_empty());
}

#[test]
fn s0d_03_adding_is_thread_safe() {
    let h: Arc<HyperLogLog<i64>> = Arc::new(HyperLogLog::new(3));
    let handles: Vec<_> = (0..8)
        .map(|t| {
            let h = h.clone();
            std::thread::spawn(move || (0..2000).for_each(|i| h.add_elem(&(t * 2000 + i))))
        })
        .collect();
    handles.into_iter().for_each(|t| t.join().unwrap());
    let sequential: HyperLogLog<i64> = HyperLogLog::new(3);
    (0..16000).for_each(|i| sequential.add_elem(&i));
    assert_eq!(h.registers(), sequential.registers(), "taking the maximum is order independent, so threads lose nothing");
}

// ---- 0d-04: HyperLogLog: the estimate --------------------------------------------------------------------------------------------------

#[test]
fn s0d_04_an_empty_sketch_estimates_the_formula_on_all_zero_registers() {
    let h: HyperLogLog<i64> = HyperLogLog::new(3);
    assert_eq!(h.cardinality(), 0, "nothing computed yet");
    h.compute_cardinality();
    // CONSTANT * m^2 / m = 0.79402 * 8
    assert_eq!(h.cardinality(), 6);
}

#[test]
fn s0d_04_zero_register_bits_is_one_register() {
    let h: HyperLogLog<i64> = HyperLogLog::new(0);
    h.compute_cardinality();
    assert_eq!(h.cardinality(), 0, "0.79402 rounded down");
    h.add_elem(&1);
    h.compute_cardinality();
    let one = h.cardinality();
    assert!(one >= 1);
    h.add_elem(&-1);
    h.compute_cardinality();
    assert!(h.cardinality() >= one, "a second value can only raise the single register");
}

#[test]
fn s0d_04_a_negative_size_has_cardinality_zero() {
    let h: HyperLogLog<i64> = HyperLogLog::new(-2);
    h.compute_cardinality();
    assert_eq!(h.cardinality(), 0);
}

#[test]
fn s0d_04_the_estimate_is_close_for_many_distinct_values() {
    let h: HyperLogLog<i64> = HyperLogLog::new(10); // 1024 registers: about 3% standard error
    for i in 0..100_000i64 {
        h.add_elem(&i);
        h.add_elem(&i); // repeats do not count
    }
    h.compute_cardinality();
    // the course's constant 0.79402 is about 10% above the textbook 0.7213 for this many registers, so the estimate runs high
    let ratio = h.cardinality() as f64 / 100_000.0;
    assert!((0.95..1.3).contains(&ratio), "estimate / truth = {ratio}");
}

#[test]
fn s0d_04_strings_and_a_small_set_give_a_plausible_estimate() {
    let h: HyperLogLog<String> = HyperLogLog::new(8);
    for i in 0..2000 {
        h.add_elem(&format!("user-{i}"));
    }
    h.compute_cardinality();
    let ratio = h.cardinality() as f64 / 2000.0;
    assert!((0.8..1.4).contains(&ratio), "estimate / truth = {ratio}");
}

// ---- 0d-05: HyperLogLog, Presto-style ---------------------------------------------------------------------------------------------------

#[test]
fn s0d_05_a_run_of_18_trailing_zeros_is_split_into_dense_and_overflow_bits() {
    // BusTub's PrestoCase1: two register bits would be 1; 262144 = 2^18 has top bit 0 (register 0) and 18 trailing zeros
    let h: HyperLogLogPresto<i64> = HyperLogLogPresto::new(1);
    assert_eq!(h.cardinality(), 0);
    h.add_elem(&262144);
    h.compute_cardinality();
    assert_eq!(h.cardinality(), 3);
    assert_eq!(h.dense_bucket()[0], 2, "18 = 0b1_0010: the low four bits");
    assert_eq!(h.overflow_bucket_of(0), 1, "and the bit above them");
}

#[test]
fn s0d_05_zero_has_all_the_remaining_bits_as_trailing_zeros() {
    let h: HyperLogLogPresto<i64> = HyperLogLogPresto::new(1);
    h.add_elem(&262144);
    h.add_elem(&0);
    h.compute_cardinality();
    assert_eq!(h.cardinality(), 3);
    assert_eq!(h.dense_bucket()[0], 15, "63 = 0b11_1111");
    assert_eq!(h.overflow_bucket_of(0), 3);
}

#[test]
fn s0d_05_a_second_register_and_the_estimate_for_long_runs() {
    let h: HyperLogLogPresto<i64> = HyperLogLogPresto::new(1);
    h.add_elem(&262144);
    h.add_elem(&0);
    h.add_elem(&-9151314442816847872); // top bit 1 (register 1), then bit 56
    h.compute_cardinality();
    assert_eq!(h.cardinality(), 227086569448168320);
    assert_eq!(h.dense_bucket()[1], 8, "56 = 0b11_1000");
    assert_eq!(h.overflow_bucket_of(0), 3);
    h.add_elem(&-1);
    h.compute_cardinality();
    assert_eq!(h.cardinality(), 227086569448168320, "a value with no trailing zeros changes nothing");
    h.add_elem(&i64::MIN);
    h.compute_cardinality();
    assert_eq!(h.cardinality(), 14647083729406857216);
    assert_eq!(h.dense_bucket()[1], 15);
}

#[test]
fn s0d_05_one_register_uses_all_64_bits() {
    let h: HyperLogLogPresto<i64> = HyperLogLogPresto::new(0);
    h.add_elem(&65536);
    assert_eq!(h.dense_bucket()[0], 0);
    assert_eq!(h.overflow_bucket_of(0), 1);
    h.add_elem(&i64::MIN);
    h.compute_cardinality();
    assert_eq!((h.dense_bucket()[0], h.overflow_bucket_of(0)), (15, 3));
    h.add_elem(&0);
    h.compute_cardinality();
    assert_eq!(h.cardinality(), 14647083729406857216);
    assert_eq!((h.dense_bucket()[0], h.overflow_bucket_of(0)), (0, 4), "64 = 0b100_0000: dense 0, overflow 4");
}

#[test]
fn s0d_05_negative_size_and_strings() {
    let h: HyperLogLogPresto<i64> = HyperLogLogPresto::new(-2);
    h.compute_cardinality();
    assert_eq!(h.cardinality(), 0);
    let s: HyperLogLogPresto<String> = HyperLogLogPresto::new(8);
    for i in 0..2000 {
        s.add_elem(&format!("user-{i}"));
    }
    s.compute_cardinality();
    // counting trailing zeros instead of the position of the first 1 halves every register's weight: about half of the plain estimate
    let ratio = s.cardinality() as f64 / 2000.0;
    assert!((0.35..0.8).contains(&ratio), "estimate / truth = {ratio}");
}

// ---- 0d-06: the observed-remove set ---------------------------------------------------------------------------------------------------

#[test]
fn s0d_06_add_and_remove_on_one_replica() {
    let mut s: ORSet<i32> = ORSet::new();
    for i in 0..10 {
        assert!(!s.contains(&i));
    }
    for i in 0..10 {
        s.add(&i, i as i64);
        assert!(s.contains(&i));
    }
    for i in 0..10 {
        s.remove(&i);
        assert!(!s.contains(&i));
    }
}

#[test]
fn s0d_06_adding_an_element_twice_with_two_ids_needs_one_remove() {
    let mut s: ORSet<String> = ORSet::new();
    s.add(&"a".to_string(), 1);
    s.add(&"a".to_string(), 2);
    s.remove(&"a".to_string());
    assert!(!s.contains(&"a".to_string()), "a remove kills every add it has seen");
}

#[test]
fn s0d_06_adding_back_after_a_remove_works() {
    let mut s: ORSet<i32> = ORSet::new();
    s.add(&1, 0);
    s.remove(&1);
    s.add(&1, 1);
    assert!(s.contains(&1), "the new add has a new id that the remove never saw");
}

#[test]
fn s0d_06_removing_an_absent_element_is_harmless() {
    let mut s: ORSet<i32> = ORSet::new();
    s.remove(&7);
    s.add(&7, 0);
    assert!(s.contains(&7), "a remove of something not yet seen does not block a later add");
}

#[test]
fn s0d_06_other_elements_are_not_affected() {
    let mut s: ORSet<i32> = ORSet::new();
    s.add(&1, 0);
    s.add(&2, 1);
    s.remove(&1);
    assert!(!s.contains(&1) && s.contains(&2));
}

// ---- 0d-07: merging, and a network of replicas ---------------------------------------------------------------------------------------------

#[test]
fn s0d_07_merge_brings_in_adds_and_removes() {
    let (mut a, mut b): (ORSet<i32>, ORSet<i32>) = (ORSet::new(), ORSet::new());
    a.add(&1, 0);
    b.add(&2, 1);
    b.remove(&2);
    a.merge(&b);
    assert!(a.contains(&1) && !a.contains(&2));
    assert!(!b.contains(&1));
    b.merge(&a);
    assert!(b.contains(&1));
    b.add(&2, 2);
    assert!(b.contains(&2));
}

#[test]
fn s0d_07_add_wins_over_a_concurrent_remove() {
    let (mut a, mut b): (ORSet<String>, ORSet<String>) = (ORSet::new(), ORSet::new());
    let c = "15-445".to_string();
    a.add(&c, 0);
    a.remove(&c);
    b.add(&c, 1);
    let (copy_a, copy_b) = (a.clone(), b.clone());
    a.merge(&copy_b);
    b.merge(&copy_a);
    assert!(a.contains(&c) && b.contains(&c));
}

#[test]
fn s0d_07_merging_twice_changes_nothing() {
    let (mut a, mut b): (ORSet<String>, ORSet<String>) = (ORSet::new(), ORSet::new());
    let s = |x: &str| x.to_string();
    a.add(&s("15-410"), 0);
    a.remove(&s("15-410"));
    b.add(&s("15-410"), 1);
    b.add(&s("15-721"), 2);
    let (copy_a, copy_b) = (a.clone(), b.clone());
    a.merge(&copy_b);
    b.merge(&copy_a);
    for set in [&a, &b] {
        assert!(set.contains(&s("15-410")) && set.contains(&s("15-721")));
    }
    a.merge(&copy_b);
    b.merge(&copy_a);
    assert_eq!(a.to_string(), b.to_string());
}

#[test]
fn s0d_07_elements_lists_each_element_once_and_to_string_sorts_them() {
    let mut s: ORSet<i32> = ORSet::new();
    s.add(&3, 0);
    s.add(&1, 1);
    s.add(&3, 2);
    s.add(&2, 3);
    s.remove(&2);
    let mut e = s.elements();
    e.sort();
    assert_eq!(e, vec![1, 3]);
    assert_eq!(s.to_string(), "{1, 3}");
    assert_eq!(ORSet::<i32>::new().to_string(), "{}");
}

#[test]
fn s0d_07_merge_order_does_not_matter() {
    let mut replicas: Vec<ORSet<i32>> = (0..3).map(|_| ORSet::new()).collect();
    let mut uid = 0;
    for step in 0..30 {
        let r = step % 3;
        let elem = (step * 7 % 5) as i32;
        if step % 4 == 3 {
            replicas[r].remove(&elem);
        } else {
            replicas[r].add(&elem, uid);
            uid += 1;
        }
    }
    let mut left = replicas[0].clone();
    left.merge(&replicas[1]);
    left.merge(&replicas[2]);
    let mut right = replicas[2].clone();
    right.merge(&replicas[1]);
    right.merge(&replicas[0]);
    assert_eq!(left.to_string(), right.to_string());
}

// ---- 0d-08: BusTub's driver tests -------------------------------------------------------------------------------------------------------

#[test]
fn s0d_08_add_remove_and_sync_across_three_nodes() {
    let mut d: ORSetDriver<i32> = ORSetDriver::new(3);
    for i in 0..10usize {
        d.add(i % 3, &(i as i32));
        assert!(d.contains(i % 3, &(i as i32)));
        assert!(!d.contains((i + 1) % 3, &(i as i32)) && !d.contains((i + 2) % 3, &(i as i32)));
        d.sync();
        assert!((0..3).all(|n| d.contains(n, &(i as i32))));
    }
    for i in 0..10usize {
        d.remove(i % 3, &(i as i32));
        assert!(!d.contains(i % 3, &(i as i32)));
        assert!(d.contains((i + 1) % 3, &(i as i32)) && d.contains((i + 2) % 3, &(i as i32)));
        d.sync();
        assert!((0..3).all(|n| !d.contains(n, &(i as i32))));
    }
}

#[test]
fn s0d_08_merge_test_two_nodes_agree_after_sync() {
    let mut d: ORSetDriver<i32> = ORSetDriver::new(2);
    d.add(0, &1);
    d.add(1, &1);
    d.remove(0, &1);
    d.sync();
    assert!(d.contains(0, &1));
    assert_eq!(d.contains(0, &1), d.contains(1, &1));
    d.add(1, &2);
    d.sync();
    d.remove(0, &2);
    d.add(0, &1);
    d.sync();
    d.remove(1, &1);
    d.sync();
    assert_eq!(d.contains(0, &1), d.contains(1, &1));
    assert_eq!(d.contains(0, &2), d.contains(1, &2));
}

#[test]
fn s0d_08_removing_everything_and_adding_it_back() {
    let mut d: ORSetDriver<i32> = ORSetDriver::new(3);
    for i in 0..10usize {
        d.add(i % 3, &(i as i32));
    }
    d.sync();
    for i in 0..10usize {
        assert!((0..3).all(|n| d.contains(n, &(i as i32))));
        d.remove(i % 3, &(i as i32));
    }
    d.sync();
    for i in 0..10 {
        assert!((0..3).all(|n| !d.contains(n, &i)));
    }
    for i in 0..10usize {
        d.add(i % 3, &(i as i32));
    }
    d.sync();
    for i in 0..10 {
        assert!((0..3).all(|n| d.contains(n, &i)));
    }
}

#[test]
fn s0d_08_adds_win_a_lot() {
    let mut d: ORSetDriver<i32> = ORSetDriver::new(3);
    for i in 0..10 {
        for n in 0..3 {
            d.add(n, &i);
        }
    }
    for i in 0..10usize {
        d.remove(i % 3, &(i as i32));
        assert!(!d.contains(i % 3, &(i as i32)));
    }
    d.sync();
    for i in 0..10 {
        assert!((0..3).all(|n| d.contains(n, &i)), "the other replicas' adds survive the remove");
    }
}

#[test]
fn s0d_08_a_lost_network_still_converges_later() {
    let mut d: ORSetDriver<i32> = ORSetDriver::new(3);
    for i in 0..10 {
        d.add((i % 2) as usize, &i);
    }
    for i in 0..20 {
        d.add(2, &i);
    }
    d.save(0);
    d.save(1);
    d.load(0);
    d.load(1);
    for i in 0..10 {
        assert!(d.contains(0, &i) && d.contains(1, &i) && d.contains(2, &i));
    }
    for i in 10..20 {
        assert!(!d.contains(0, &i) && !d.contains(1, &i) && d.contains(2, &i));
        d.remove(0, &i);
    }
    for i in 10..20 {
        d.add(0, &i);
        d.remove(2, &i);
    }
    d.sync();
    for i in 10..20 {
        assert!((0..3).all(|n| d.contains(n, &i)), "node 0's fresh add beats node 2's remove of the old one");
    }
}
