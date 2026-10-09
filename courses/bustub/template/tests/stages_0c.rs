//! Tests for module 0c: a Robin Hood hash set.

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Barrier};

use bustub::primer::robin_hood_hash_set::{RobinHoodHash, RobinHoodHashSet};

fn set(capacity: usize) -> RobinHoodHashSet<i32> {
    RobinHoodHashSet::new(capacity).unwrap()
}

/// BusTub's `FindKeysWithHomeBucket`: the first `count` keys (from 0) whose home bucket is `home`.
fn keys_with_home(capacity: usize, home: usize, count: usize) -> Vec<i32> {
    let keys: Vec<i32> = (0..10000).filter(|k: &i32| k.robin_hood_hash() % capacity == home).take(count).collect();
    assert_eq!(keys.len(), count, "could not find enough colliding keys");
    keys
}

// ---- 0c-01: buckets -----------------------------------------------------------------------------------------------------------------------

#[test]
fn s0c_01_a_set_has_the_capacity_it_was_made_with() {
    let s = set(8);
    assert_eq!((s.capacity(), s.bucket_count(), s.size()), (8, 8, 0));
    assert_eq!(s.load_factor(), 0.0);
}

#[test]
fn s0c_01_capacity_zero_is_an_error() {
    assert!(RobinHoodHashSet::<i32>::new(0).is_err());
    assert!(RobinHoodHashSet::<i32>::new(1).is_ok());
}

#[test]
fn s0c_01_the_home_bucket_is_the_hash_modulo_the_capacity() {
    let s = set(8);
    for k in [0, 1, 7, 8, 12345, -5] {
        assert_eq!(s.home_bucket(&k), k.robin_hood_hash() % 8);
    }
    assert_eq!(keys_with_home(8, 3, 2).iter().map(|k| s.home_bucket(k)).collect::<Vec<_>>(), vec![3, 3]);
}

#[test]
fn s0c_01_the_probe_distance_counts_steps_forward_and_wraps() {
    let s = set(8);
    assert_eq!(s.probe_distance(3, 3), 0);
    assert_eq!(s.probe_distance(3, 5), 2);
    assert_eq!(s.probe_distance(6, 0), 2, "7, then 0");
    assert_eq!(s.probe_distance(7, 6), 7, "all the way round");
}

#[test]
fn s0c_01_the_int_hash_is_the_multiplicative_one_of_the_course() {
    assert_eq!(1i32.robin_hood_hash(), 0x9e37_79b9_7f4a_7c15u64 as usize);
    assert_eq!(2i64.robin_hood_hash(), 0x9e37_79b9_7f4a_7c15u64.wrapping_mul(2) as usize);
    assert_eq!(0i32.robin_hood_hash(), 0);
    let h = String::from("BusTub").robin_hood_hash();
    assert_eq!(h, String::from("BusTub").robin_hood_hash(), "deterministic");
    assert_ne!(h, String::from("CMU DB").robin_hood_hash());
}

// ---- 0c-02: insert and lookup --------------------------------------------------------------------------------------------------------------

#[test]
fn s0c_02_insert_duplicate_replace_lookup_and_statistics() {
    let s = set(8);
    assert!(!s.contains(&1));
    assert!(s.insert(&1));
    assert!(s.insert(&2));
    assert!(s.insert(&1), "an equal key is replaced and that is a success");
    assert!(s.contains(&1) && s.contains(&2));
    assert_eq!(s.size(), 2);
    assert_eq!(s.load_factor(), 0.25);
}

#[test]
fn s0c_02_strings_are_supported() {
    let s: RobinHoodHashSet<String> = RobinHoodHashSet::new(7).unwrap();
    for w in ["BusTub", "CMU DB", "15-445"] {
        assert!(s.insert(&w.to_string()));
    }
    assert!(s.contains(&"BusTub".to_string()) && s.contains(&"15-445".to_string()));
    assert!(!s.contains(&"missing".to_string()));
    assert_eq!(s.size(), 3);
}

#[test]
fn s0c_02_a_single_bucket_table_holds_one_key() {
    let s = set(1);
    assert!(s.insert(&1));
    assert!(s.insert(&1));
    assert!(!s.insert(&2));
    assert_eq!(s.size(), 1);
    assert_eq!(s.load_factor(), 1.0);
}

#[test]
fn s0c_02_a_key_further_from_home_takes_the_bucket_of_a_closer_one() {
    let s = set(4);
    let colliding = keys_with_home(4, 0, 3);
    let next = keys_with_home(4, 1, 1)[0];
    assert!(s.insert(&colliding[0]));
    assert!(s.insert(&colliding[1]));
    assert!(s.insert(&next));
    assert!(s.insert(&colliding[2]));
    // the last insert displaces the key whose home is 1
    assert_eq!(s.get_bucket(&colliding[2]), 2);
    assert_eq!(s.get_bucket(&next), 3);
    assert_eq!(s.get_bucket(&99), s.bucket_count(), "absent");
    for k in [colliding[0], colliding[1], next, colliding[2]] {
        assert!(s.contains(&k));
    }
    assert_eq!(s.size(), 4);
}

#[test]
fn s0c_02_insert_fails_only_when_every_bucket_is_taken() {
    let s = set(4);
    for k in [0, 4, 1, 8] {
        assert!(s.insert(&k));
    }
    assert!(!s.insert(&12));
    assert_eq!(s.size(), 4);
    for k in [0, 4, 1, 8] {
        assert!(s.contains(&k));
    }
    assert!(!s.contains(&12));
}

#[test]
fn s0c_02_probing_wraps_around_the_end_of_the_table() {
    let s = set(8);
    let keys = keys_with_home(8, 6, 3);
    for k in &keys {
        assert!(s.insert(k));
    }
    assert_eq!([s.get_bucket(&keys[0]), s.get_bucket(&keys[1]), s.get_bucket(&keys[2])], [6, 7, 0]);
    assert!(s.contains(&keys[2]));
}

#[test]
fn s0c_02_an_absent_key_is_reported_absent_in_a_crowded_table() {
    let s = set(16);
    for k in 0..15 {
        assert!(s.insert(&k));
    }
    for k in 100..200 {
        assert!(!s.contains(&k));
        assert_eq!(s.get_bucket(&k), 16);
    }
    for k in 0..15 {
        assert!(s.contains(&k));
    }
}

#[test]
fn s0c_02_every_key_is_found_after_many_displacements() {
    let s = set(64);
    for k in 0..60 {
        assert!(s.insert(&(k * 7)));
    }
    for k in 0..60 {
        assert!(s.contains(&(k * 7)), "{}", k * 7);
        assert!(s.get_bucket(&(k * 7)) < 64);
    }
    let buckets: std::collections::BTreeSet<usize> = (0..60).map(|k| s.get_bucket(&(k * 7))).collect();
    assert_eq!(buckets.len(), 60, "every key has a bucket of its own");
}

// ---- 0c-03: remove, clear and tombstones --------------------------------------------------------------------------------------------------

#[test]
fn s0c_03_remove_reports_whether_the_key_was_there() {
    let s = set(8);
    s.insert(&1);
    s.insert(&9);
    assert!(s.remove(&1));
    assert!(!s.remove(&1));
    assert!(!s.remove(&77));
    assert!(!s.contains(&1));
    assert!(s.contains(&9));
    assert_eq!(s.size(), 1);
}

#[test]
fn s0c_03_a_lookup_continues_past_a_tombstone() {
    let s = set(8);
    let keys = keys_with_home(8, 6, 3);
    for k in &keys {
        s.insert(k);
    }
    assert_eq!(s.get_bucket(&keys[2]), 0);
    assert!(s.remove(&keys[1]));
    assert!(!s.contains(&keys[1]));
    assert!(s.contains(&keys[2]), "bucket 7 holds a tombstone, bucket 0 the key");
    assert!(!s.remove(&keys[1]));
    assert_eq!(s.size(), 2);
}

#[test]
fn s0c_03_an_insert_reuses_a_tombstone() {
    let s = set(8);
    let keys = keys_with_home(8, 6, 4);
    for k in &keys[..3] {
        s.insert(k);
    }
    assert!(s.remove(&keys[1]));
    assert!(s.insert(&keys[3]));
    assert_eq!(s.get_bucket(&keys[3]), 7);
    assert!(s.contains(&keys[3]) && s.contains(&keys[2]));
    assert_eq!(s.size(), 3);
}

#[test]
fn s0c_03_the_max_probe_distance_ignores_tombstones() {
    let s = set(4);
    let keys = keys_with_home(4, 0, 3);
    assert_eq!(s.max_probe_distance(), 0);
    for k in &keys {
        s.insert(k);
    }
    assert_eq!([s.get_bucket(&keys[0]), s.get_bucket(&keys[1]), s.get_bucket(&keys[2])], [0, 1, 2]);
    assert_eq!(s.max_probe_distance(), 2);
    assert!(s.remove(&keys[2]));
    assert_eq!(s.max_probe_distance(), 1);
}

#[test]
fn s0c_03_a_key_stays_reachable_when_a_tombstone_in_front_of_it_is_reused() {
    // the reason a lookup must not stop at a key that is closer to home than the sought one
    let s = set(8);
    let ks = keys_with_home(8, 2, 3);
    let other = keys_with_home(8, 3, 2);
    // two keys with home 2 fill buckets 2 and 3; a key with home 3 is pushed to 4; ...
    assert!(s.insert(&ks[0]) && s.insert(&ks[1]) && s.insert(&other[0]));
    assert!(s.insert(&ks[2]));
    assert!(s.remove(&ks[1]));
    assert!(s.insert(&other[1]));
    for k in [ks[0], ks[2], other[0], other[1]] {
        assert!(s.contains(&k), "{k} was lost");
    }
}

#[test]
fn s0c_03_random_inserts_and_removes_agree_with_a_hash_set() {
    use std::collections::HashSet;
    let s = set(97);
    let mut model = HashSet::new();
    let mut x = 12345u64;
    for _ in 0..20_000 {
        x ^= x << 13;
        x ^= x >> 7;
        x ^= x << 17;
        let key = (x % 150) as i32;
        if x % 3 == 0 {
            assert_eq!(s.remove(&key), model.remove(&key));
        } else if model.len() < 97 || model.contains(&key) {
            assert!(s.insert(&key));
            model.insert(key);
        } else {
            assert!(!s.insert(&key));
        }
        assert_eq!(s.size(), model.len());
    }
    for key in 0..150 {
        assert_eq!(s.contains(&key), model.contains(&key), "{key}");
    }
}

#[test]
fn s0c_03_clear_empties_the_table_but_keeps_the_capacity() {
    let s = set(8);
    s.insert(&1);
    s.insert(&9);
    s.remove(&1);
    s.clear();
    assert_eq!((s.capacity(), s.size()), (8, 0));
    assert_eq!(s.load_factor(), 0.0);
    assert!(!s.contains(&1) && !s.contains(&9));
    assert!(s.insert(&17) && s.contains(&17));
}

#[test]
fn s0c_03_a_table_full_of_tombstones_accepts_inserts_again() {
    let s = set(4);
    for round in 0..10 {
        for k in 0..4 {
            assert!(s.insert(&(round * 4 + k)), "round {round}");
        }
        for k in 0..4 {
            assert!(s.remove(&(round * 4 + k)));
        }
    }
    assert_eq!(s.size(), 0);
}

// ---- 0c-04: BusTub's concurrent tests ---------------------------------------------------------------------------------------------------------

#[test]
fn s0c_04_sixteen_threads_insert_the_same_key() {
    let s = Arc::new(set(64));
    let gate = Arc::new(Barrier::new(16));
    let ok = Arc::new(AtomicUsize::new(0));
    let handles: Vec<_> = (0..16)
        .map(|_| {
            let (s, gate, ok) = (s.clone(), gate.clone(), ok.clone());
            std::thread::spawn(move || {
                gate.wait();
                if s.insert(&42) {
                    ok.fetch_add(1, Ordering::SeqCst);
                }
            })
        })
        .collect();
    handles.into_iter().for_each(|h| h.join().unwrap());
    assert_eq!(ok.load(Ordering::SeqCst), 16);
    assert_eq!(s.size(), 1);
    assert!(s.contains(&42));
}

#[test]
fn s0c_04_writers_and_readers_do_not_lose_keys() {
    let s = Arc::new(set(512));
    let gate = Arc::new(Barrier::new(8));
    let ok = Arc::new(AtomicUsize::new(0));
    let mut handles = vec![];
    for w in 0..4 {
        let (s, gate, ok) = (s.clone(), gate.clone(), ok.clone());
        handles.push(std::thread::spawn(move || {
            gate.wait();
            for i in 0..64 {
                if s.insert(&(w * 64 + i)) {
                    ok.fetch_add(1, Ordering::SeqCst);
                }
            }
        }));
    }
    for r in 0..4 {
        let (s, gate) = (s.clone(), gate.clone());
        handles.push(std::thread::spawn(move || {
            gate.wait();
            for i in 0..256 {
                let _ = s.contains(&((i + r) % 256));
            }
        }));
    }
    handles.into_iter().for_each(|h| h.join().unwrap());
    assert_eq!(ok.load(Ordering::SeqCst), 256);
    assert_eq!(s.size(), 256);
    assert!((0..256).all(|i| s.contains(&i)));
}

#[test]
fn s0c_04_each_key_is_removed_exactly_once_whoever_races() {
    let s = Arc::new(set(128));
    for k in 0..64 {
        assert!(s.insert(&k));
    }
    let gate = Arc::new(Barrier::new(8));
    let ok = Arc::new(AtomicUsize::new(0));
    let handles: Vec<_> = (0..8)
        .map(|_| {
            let (s, gate, ok) = (s.clone(), gate.clone(), ok.clone());
            std::thread::spawn(move || {
                gate.wait();
                for k in 0..64 {
                    if s.remove(&k) {
                        ok.fetch_add(1, Ordering::SeqCst);
                    }
                }
            })
        })
        .collect();
    handles.into_iter().for_each(|h| h.join().unwrap());
    assert_eq!(ok.load(Ordering::SeqCst), 64);
    assert_eq!(s.size(), 0);
    assert!((0..64).all(|k| !s.contains(&k)));
}

#[test]
fn s0c_04_overlapping_inserts_lookups_and_removes_finish_and_keep_the_size_sane() {
    let s = Arc::new(set(64));
    let gate = Arc::new(Barrier::new(8));
    let handles: Vec<_> = (0..8)
        .map(|t| {
            let (s, gate) = (s.clone(), gate.clone());
            std::thread::spawn(move || {
                gate.wait();
                for i in 0..500 {
                    let key = (t * 17 + i) % 96;
                    let _ = s.insert(&key);
                    let _ = s.contains(&((key + 1) % 96));
                    let _ = s.remove(&((key + 32) % 96));
                }
            })
        })
        .collect();
    handles.into_iter().for_each(|h| h.join().unwrap());
    assert!(s.size() <= s.capacity());
    let present = (0..96).filter(|k| s.contains(k)).count();
    assert_eq!(present, s.size(), "the count agrees with what a lookup finds");
}

#[test]
fn s0c_04_a_big_table_takes_two_hundred_thousand_inserts() {
    let s = set(262_144);
    for k in 0..200_000 {
        assert!(s.insert(&k));
    }
    assert_eq!(s.size(), 200_000);
    assert!(s.max_probe_distance() < 200, "probe distances stay short at load factor 0.76: {}", s.max_probe_distance());
}
