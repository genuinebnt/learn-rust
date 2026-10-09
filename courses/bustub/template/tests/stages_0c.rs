//! Tests for module 0c: a Robin Hood hash set.

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Barrier};

use std::collections::HashSet;

use bustub::primer::robin_hood_hash_set::{RobinHoodHash, RobinHoodHashSet};
use proptest::prelude::*;

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
    assert_eq!((s.capacity(), s.bucket_count(), s.size()), (8, 8, 0), "a set has the capacity it was made with");
    assert_eq!(s.load_factor(), 0.0, "a set has the capacity it was made with");
}

#[test]
fn s0c_01_capacity_zero_is_an_error() {
    assert!(RobinHoodHashSet::<i32>::new(0).is_err(), "capacity zero is an error: expected `RobinHoodHashSet::<i32>::new(0).is_err()`");
    assert!(RobinHoodHashSet::<i32>::new(1).is_ok(), "capacity zero is an error: expected `RobinHoodHashSet::<i32>::new(1).is_ok()`");
}

#[test]
fn s0c_01_the_home_bucket_is_the_hash_modulo_the_capacity() {
    let s = set(8);
    for k in [0, 1, 7, 8, 12345, -5] {
        assert_eq!(s.home_bucket(&k), k.robin_hood_hash() % 8, "the home bucket is the hash modulo the capacity");
    }
    assert_eq!(keys_with_home(8, 3, 2).iter().map(|k| s.home_bucket(k)).collect::<Vec<_>>(), vec![3, 3], "the home bucket is the hash modulo the capacity");
}

#[test]
fn s0c_01_the_probe_distance_counts_steps_forward_and_wraps() {
    let s = set(8);
    assert_eq!(s.probe_distance(3, 3), 0, "the probe distance counts steps forward and wraps");
    assert_eq!(s.probe_distance(3, 5), 2, "the probe distance counts steps forward and wraps");
    assert_eq!(s.probe_distance(6, 0), 2, "7, then 0");
    assert_eq!(s.probe_distance(7, 6), 7, "all the way round");
}

#[test]
fn s0c_01_the_int_hash_is_the_multiplicative_one_of_the_course() {
    assert_eq!(1i32.robin_hood_hash(), 0x9e37_79b9_7f4a_7c15u64 as usize, "the int hash is the multiplicative one of the course");
    assert_eq!(2i64.robin_hood_hash(), 0x9e37_79b9_7f4a_7c15u64.wrapping_mul(2) as usize, "the int hash is the multiplicative one of the course");
    assert_eq!(0i32.robin_hood_hash(), 0, "the int hash is the multiplicative one of the course");
    let h = String::from("BusTub").robin_hood_hash();
    assert_eq!(h, String::from("BusTub").robin_hood_hash(), "deterministic");
    assert_ne!(h, String::from("CMU DB").robin_hood_hash(), "the int hash is the multiplicative one of the course");
}

// ---- 0c-02: insert and lookup --------------------------------------------------------------------------------------------------------------

#[test]
fn s0c_02_insert_duplicate_replace_lookup_and_statistics() {
    let s = set(8);
    assert!(!s.contains(&1), "insert duplicate replace lookup and statistics: expected `!s.contains(&1)`");
    assert!(s.insert(&1), "insert duplicate replace lookup and statistics: expected `s.insert(&1)`");
    assert!(s.insert(&2), "insert duplicate replace lookup and statistics: expected `s.insert(&2)`");
    assert!(s.insert(&1), "an equal key is replaced and that is a success");
    assert!(s.contains(&1) && s.contains(&2), "insert duplicate replace lookup and statistics: expected `s.contains(&1) && s.contains(&2)`");
    assert_eq!(s.size(), 2, "insert duplicate replace lookup and statistics");
    assert_eq!(s.load_factor(), 0.25, "insert duplicate replace lookup and statistics");
}

#[test]
fn s0c_02_strings_are_supported() {
    let s: RobinHoodHashSet<String> = RobinHoodHashSet::new(7).unwrap();
    for w in ["BusTub", "CMU DB", "15-445"] {
        assert!(s.insert(&w.to_string()), "strings are supported: expected `s.insert(&w.to_string())`");
    }
    assert!(s.contains(&"BusTub".to_string()) && s.contains(&"15-445".to_string()), "strings are supported: expected `s.contains(&\"BusTub\".to_string()) && s.contains(&\"15-445\".to_string())`");
    assert!(!s.contains(&"missing".to_string()), "strings are supported: expected `!s.contains(&\"missing\".to_string())`");
    assert_eq!(s.size(), 3, "strings are supported");
}

#[test]
fn s0c_02_a_single_bucket_table_holds_one_key() {
    let s = set(1);
    assert!(s.insert(&1), "a single bucket table holds one key: expected `s.insert(&1)`");
    assert!(s.insert(&1), "a single bucket table holds one key: expected `s.insert(&1)`");
    assert!(!s.insert(&2), "a single bucket table holds one key: expected `!s.insert(&2)`");
    assert_eq!(s.size(), 1, "a single bucket table holds one key");
    assert_eq!(s.load_factor(), 1.0, "a single bucket table holds one key");
}

#[test]
fn s0c_02_a_key_further_from_home_takes_the_bucket_of_a_closer_one() {
    let s = set(4);
    let colliding = keys_with_home(4, 0, 3);
    let next = keys_with_home(4, 1, 1)[0];
    assert!(s.insert(&colliding[0]), "a key further from home takes the bucket of a closer one: expected `s.insert(&colliding[0])`");
    assert!(s.insert(&colliding[1]), "a key further from home takes the bucket of a closer one: expected `s.insert(&colliding[1])`");
    assert!(s.insert(&next), "a key further from home takes the bucket of a closer one: expected `s.insert(&next)`");
    assert!(s.insert(&colliding[2]), "a key further from home takes the bucket of a closer one: expected `s.insert(&colliding[2])`");
    // the last insert displaces the key whose home is 1
    assert_eq!(s.get_bucket(&colliding[2]), 2, "a key further from home takes the bucket of a closer one");
    assert_eq!(s.get_bucket(&next), 3, "a key further from home takes the bucket of a closer one");
    assert_eq!(s.get_bucket(&99), s.bucket_count(), "absent");
    for k in [colliding[0], colliding[1], next, colliding[2]] {
        assert!(s.contains(&k), "a key further from home takes the bucket of a closer one: expected `s.contains(&k)`");
    }
    assert_eq!(s.size(), 4, "a key further from home takes the bucket of a closer one");
}

#[test]
fn s0c_02_insert_fails_only_when_every_bucket_is_taken() {
    let s = set(4);
    for k in [0, 4, 1, 8] {
        assert!(s.insert(&k), "insert fails only when every bucket is taken: expected `s.insert(&k)`");
    }
    assert!(!s.insert(&12), "insert fails only when every bucket is taken: expected `!s.insert(&12)`");
    assert_eq!(s.size(), 4, "insert fails only when every bucket is taken");
    for k in [0, 4, 1, 8] {
        assert!(s.contains(&k), "insert fails only when every bucket is taken: expected `s.contains(&k)`");
    }
    assert!(!s.contains(&12), "insert fails only when every bucket is taken: expected `!s.contains(&12)`");
}

#[test]
fn s0c_02_probing_wraps_around_the_end_of_the_table() {
    let s = set(8);
    let keys = keys_with_home(8, 6, 3);
    for k in &keys {
        assert!(s.insert(k), "probing wraps around the end of the table: expected `s.insert(k)`");
    }
    assert_eq!([s.get_bucket(&keys[0]), s.get_bucket(&keys[1]), s.get_bucket(&keys[2])], [6, 7, 0], "probing wraps around the end of the table");
    assert!(s.contains(&keys[2]), "probing wraps around the end of the table: expected `s.contains(&keys[2])`");
}

#[test]
fn s0c_02_an_absent_key_is_reported_absent_in_a_crowded_table() {
    let s = set(16);
    for k in 0..15 {
        assert!(s.insert(&k), "an absent key is reported absent in a crowded table: expected `s.insert(&k)`");
    }
    for k in 100..200 {
        assert!(!s.contains(&k), "an absent key is reported absent in a crowded table: expected `!s.contains(&k)`");
        assert_eq!(s.get_bucket(&k), 16, "an absent key is reported absent in a crowded table");
    }
    for k in 0..15 {
        assert!(s.contains(&k), "an absent key is reported absent in a crowded table: expected `s.contains(&k)`");
    }
}

#[test]
fn s0c_02_every_key_is_found_after_many_displacements() {
    let s = set(64);
    for k in 0..60 {
        assert!(s.insert(&(k * 7)), "every key is found after many displacements: expected `s.insert(&(k * 7))`");
    }
    for k in 0..60 {
        assert!(s.contains(&(k * 7)), "{}", k * 7);
        assert!(s.get_bucket(&(k * 7)) < 64, "every key is found after many displacements: expected `s.get_bucket(&(k * 7)) < 64`");
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
    assert!(s.remove(&1), "remove reports whether the key was there: expected `s.remove(&1)`");
    assert!(!s.remove(&1), "remove reports whether the key was there: expected `!s.remove(&1)`");
    assert!(!s.remove(&77), "remove reports whether the key was there: expected `!s.remove(&77)`");
    assert!(!s.contains(&1), "remove reports whether the key was there: expected `!s.contains(&1)`");
    assert!(s.contains(&9), "remove reports whether the key was there: expected `s.contains(&9)`");
    assert_eq!(s.size(), 1, "remove reports whether the key was there");
}

#[test]
fn s0c_03_a_lookup_continues_past_a_tombstone() {
    let s = set(8);
    let keys = keys_with_home(8, 6, 3);
    for k in &keys {
        s.insert(k);
    }
    assert_eq!(s.get_bucket(&keys[2]), 0, "a lookup continues past a tombstone");
    assert!(s.remove(&keys[1]), "a lookup continues past a tombstone: expected `s.remove(&keys[1])`");
    assert!(!s.contains(&keys[1]), "a lookup continues past a tombstone: expected `!s.contains(&keys[1])`");
    assert!(s.contains(&keys[2]), "bucket 7 holds a tombstone, bucket 0 the key");
    assert!(!s.remove(&keys[1]), "a lookup continues past a tombstone: expected `!s.remove(&keys[1])`");
    assert_eq!(s.size(), 2, "a lookup continues past a tombstone");
}

#[test]
fn s0c_03_an_insert_reuses_a_tombstone() {
    let s = set(8);
    let keys = keys_with_home(8, 6, 4);
    for k in &keys[..3] {
        s.insert(k);
    }
    assert!(s.remove(&keys[1]), "an insert reuses a tombstone: expected `s.remove(&keys[1])`");
    assert!(s.insert(&keys[3]), "an insert reuses a tombstone: expected `s.insert(&keys[3])`");
    assert_eq!(s.get_bucket(&keys[3]), 7, "an insert reuses a tombstone");
    assert!(s.contains(&keys[3]) && s.contains(&keys[2]), "an insert reuses a tombstone: expected `s.contains(&keys[3]) && s.contains(&keys[2])`");
    assert_eq!(s.size(), 3, "an insert reuses a tombstone");
}

#[test]
fn s0c_03_the_max_probe_distance_ignores_tombstones() {
    let s = set(4);
    let keys = keys_with_home(4, 0, 3);
    assert_eq!(s.max_probe_distance(), 0, "the max probe distance ignores tombstones");
    for k in &keys {
        s.insert(k);
    }
    assert_eq!([s.get_bucket(&keys[0]), s.get_bucket(&keys[1]), s.get_bucket(&keys[2])], [0, 1, 2], "the max probe distance ignores tombstones");
    assert_eq!(s.max_probe_distance(), 2, "the max probe distance ignores tombstones");
    assert!(s.remove(&keys[2]), "the max probe distance ignores tombstones: expected `s.remove(&keys[2])`");
    assert_eq!(s.max_probe_distance(), 1, "the max probe distance ignores tombstones");
}

#[test]
fn s0c_03_a_key_stays_reachable_when_a_tombstone_in_front_of_it_is_reused() {
    // the reason a lookup must not stop at a key that is closer to home than the sought one
    let s = set(8);
    let ks = keys_with_home(8, 2, 3);
    let other = keys_with_home(8, 3, 2);
    // two keys with home 2 fill buckets 2 and 3; a key with home 3 is pushed to 4; ...
    assert!(s.insert(&ks[0]) && s.insert(&ks[1]) && s.insert(&other[0]), "a key stays reachable when a tombstone in front of it is reused: expected `s.insert(&ks[0]) && s.insert(&ks[1]) && s.insert(&other[0])`");
    assert!(s.insert(&ks[2]), "a key stays reachable when a tombstone in front of it is reused: expected `s.insert(&ks[2])`");
    assert!(s.remove(&ks[1]), "a key stays reachable when a tombstone in front of it is reused: expected `s.remove(&ks[1])`");
    assert!(s.insert(&other[1]), "a key stays reachable when a tombstone in front of it is reused: expected `s.insert(&other[1])`");
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
            assert_eq!(s.remove(&key), model.remove(&key), "random inserts and removes agree with a hash set");
        } else if model.len() < 97 || model.contains(&key) {
            assert!(s.insert(&key), "random inserts and removes agree with a hash set: expected `s.insert(&key)`");
            model.insert(key);
        } else {
            assert!(!s.insert(&key), "random inserts and removes agree with a hash set: expected `!s.insert(&key)`");
        }
        assert_eq!(s.size(), model.len(), "random inserts and removes agree with a hash set");
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
    assert_eq!((s.capacity(), s.size()), (8, 0), "clear empties the table but keeps the capacity");
    assert_eq!(s.load_factor(), 0.0, "clear empties the table but keeps the capacity");
    assert!(!s.contains(&1) && !s.contains(&9), "clear empties the table but keeps the capacity: expected `!s.contains(&1) && !s.contains(&9)`");
    assert!(s.insert(&17) && s.contains(&17), "clear empties the table but keeps the capacity: expected `s.insert(&17) && s.contains(&17)`");
}

#[test]
fn s0c_03_a_table_full_of_tombstones_accepts_inserts_again() {
    let s = set(4);
    for round in 0..10 {
        for k in 0..4 {
            assert!(s.insert(&(round * 4 + k)), "round {round}");
        }
        for k in 0..4 {
            assert!(s.remove(&(round * 4 + k)), "a table full of tombstones accepts inserts again: expected `s.remove(&(round * 4 + k))`");
        }
    }
    assert_eq!(s.size(), 0, "a table full of tombstones accepts inserts again");
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
    assert_eq!(ok.load(Ordering::SeqCst), 16, "sixteen threads insert the same key");
    assert_eq!(s.size(), 1, "sixteen threads insert the same key");
    assert!(s.contains(&42), "sixteen threads insert the same key: expected `s.contains(&42)`");
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
    assert_eq!(ok.load(Ordering::SeqCst), 256, "writers and readers do not lose keys");
    assert_eq!(s.size(), 256, "writers and readers do not lose keys");
    assert!((0..256).all(|i| s.contains(&i)), "writers and readers do not lose keys: expected `(0..256).all(|i| s.contains(&i))`");
}

#[test]
fn s0c_04_each_key_is_removed_exactly_once_whoever_races() {
    let s = Arc::new(set(128));
    for k in 0..64 {
        assert!(s.insert(&k), "each key is removed exactly once whoever races: expected `s.insert(&k)`");
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
    assert_eq!(ok.load(Ordering::SeqCst), 64, "each key is removed exactly once whoever races");
    assert_eq!(s.size(), 0, "each key is removed exactly once whoever races");
    assert!((0..64).all(|k| !s.contains(&k)), "each key is removed exactly once whoever races: expected `(0..64).all(|k| !s.contains(&k))`");
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
    assert!(s.size() <= s.capacity(), "overlapping inserts lookups and removes finish and keep the size sane: expected `s.size() <= s.capacity()`");
    let present = (0..96).filter(|k| s.contains(k)).count();
    assert_eq!(present, s.size(), "the count agrees with what a lookup finds");
}

#[test]
fn s0c_04_a_big_table_takes_two_hundred_thousand_inserts() {
    let s = set(262_144);
    for k in 0..200_000 {
        assert!(s.insert(&k), "a big table takes two hundred thousand inserts: expected `s.insert(&k)`");
    }
    assert_eq!(s.size(), 200_000, "a big table takes two hundred thousand inserts");
    assert!(s.max_probe_distance() < 200, "probe distances stay short at load factor 0.76: {}", s.max_probe_distance());
}

// ---- properties: the set against a hash set, and the Robin Hood invariants --------------------------------------------------------------

fn pconfig() -> ProptestConfig {
    ProptestConfig { cases: 64, max_shrink_iters: 2000, failure_persistence: None, ..ProptestConfig::default() }
}

#[derive(Clone, Debug)]
enum HashOp {
    Insert(i32),
    Remove(i32),
    Contains(i32),
    Clear,
}

fn hash_op() -> impl Strategy<Value = HashOp> {
    prop_oneof![
        6 => (0..40i32).prop_map(HashOp::Insert),
        3 => (0..40i32).prop_map(HashOp::Remove),
        3 => (0..40i32).prop_map(HashOp::Contains),
        1 => Just(HashOp::Clear),
    ]
}

proptest! {
    #![proptest_config(pconfig())]

    /// Any inserts, removes, lookups and clears on a small table (so it fills up and tombstones pile up): the set answers as a `HashSet`
    /// does, an insert fails exactly when the table is full of other keys, and every key found is reported at a bucket within the table.
    #[test]
    fn s0c_03_the_set_behaves_like_a_hash_set_with_a_capacity(capacity in 1usize..24, ops in prop::collection::vec(hash_op(), 1..150)) {
        let s = set(capacity);
        let mut model: HashSet<i32> = HashSet::new();
        for op in ops {
            match op {
                HashOp::Insert(k) => {
                    let expected = model.contains(&k) || model.len() < capacity;
                    prop_assert_eq!(s.insert(&k), expected, "insert {} with {} of {} buckets live", k, model.len(), capacity);
                    if expected { model.insert(k); }
                }
                HashOp::Remove(k) => prop_assert_eq!(s.remove(&k), model.remove(&k)),
                HashOp::Contains(k) => prop_assert_eq!(s.contains(&k), model.contains(&k)),
                HashOp::Clear => { s.clear(); model.clear(); }
            }
            prop_assert_eq!(s.size(), model.len());
            prop_assert_eq!(s.load_factor(), model.len() as f64 / capacity as f64);
            for k in 0..40 {
                prop_assert_eq!(s.contains(&k), model.contains(&k), "key {}", k);
                let b = s.get_bucket(&k);
                prop_assert_eq!(b < capacity, model.contains(&k), "the bucket of {} is {}", k, b);
            }
        }
    }

    /// With inserts only (no tombstones yet) the table is a proper **Robin Hood** table: a key sits at a distinct bucket; every bucket
    /// between its home and its place is taken (no gaps in a probe sequence); and walking along a run of taken buckets, a key is never
    /// more than one step further from its home than the key before it (richer keys never sit behind poorer ones).
    #[test]
    fn s0c_02_inserts_alone_leave_a_robin_hood_table(capacity in 2usize..40, keys in prop::collection::vec(0..400i32, 0..60)) {
        let s = set(capacity);
        let mut live: Vec<i32> = vec![];
        for k in keys {
            if s.insert(&k) && !live.contains(&k) { live.push(k); }
        }
        let mut at: Vec<Option<i32>> = vec![None; capacity];
        for k in &live {
            let b = s.get_bucket(k);
            prop_assert!(b < capacity);
            prop_assert!(at[b].is_none(), "two keys in bucket {}", b);
            at[b] = Some(*k);
        }
        let dist = |k: &i32, b: usize| s.probe_distance(s.home_bucket(k), b);
        for k in &live {
            let b = s.get_bucket(k);
            for d in 0..dist(k, b) {
                let between = (s.home_bucket(k) + d) % capacity;
                prop_assert!(at[between].is_some(), "a gap at bucket {} on the way to {}", between, k);
            }
        }
        for b in 0..capacity {
            let next = (b + 1) % capacity;
            if let (Some(x), Some(y)) = (&at[b], &at[next]) {
                // wrapping the end of the table starts a new run only if the first key sits at its home; the rule holds across it too
                prop_assert!(dist(y, next) <= dist(x, b) + 1, "{} at {} is {} from home, but {} behind it is {}", x, b, dist(x, b), y, dist(y, next));
            }
        }
    }
}
