from _c import C
M0C, M0D = "26-robin-hood-hashing", "27-sketches-and-crdts"
CH = []

CH.append(C("0c-c1", M0C, "90-challenge-backward-shift-deletion", "build", "Challenge: backward-shift deletion", "medium", "stages_0c::s0c_c1",
  ["deleting from an open-addressing table without tombstones","keeping every key reachable from its home slot"],
  ["robin-hood-hashing-and-open-addressing","model-based-testing"],
  "`ShiftSet` in `src/primer/shift_set.rs`: a fixed-capacity hash set of `u64` using **linear probing** and **backward-shift deletion**: removing a key moves the following keys of its probe run back one slot, so no tombstones are ever needed and lookups never get slower after deletes. `insert` fails with `Full` when no slot is free.",
  "Tombstones keep a table correct and let it rot: after enough deletes every lookup probes through a graveyard. Backward-shift deletion repairs the run at the moment of the delete (the idea Robin Hood hashing makes cheap) so the table is always exactly as if the deleted key had never been inserted. The invariant to keep is reachability: a key must be findable from its home slot without crossing an empty one.",
  ["`new(capacity)`; `home(key)` is given. `insert(key)` returns `Ok(true)` if added, `Ok(false)` if present, `Err(Full)` when the table has no empty slot.","`contains`, `len`. `remove(key)` returns whether it was there and shifts later members of its run back so that every remaining key is still reachable.","`probe_len(key)` is the number of slots from the key's home to where it sits (0 when at home), `None` if absent."],
  ["Every stored key can be found by probing from its home slot without passing an empty slot.","`len()` equals the number of stored keys; there are no tombstones (a slot is empty or holds a key)."],
  ["The set of keys equals a `HashSet`'s after any inserts and removes.","After removing a key, the arrangement of the others equals the arrangement had it never been inserted *when it was inserted last* (checked through reachability).","A table filled and then emptied has every slot empty again."],
  ["capacity 8, keys with the same home h: insert a, b, c in order -> slots h, h+1, h+2; remove a -> b at h, c at h+1"],
  ["Insert, find, remove, full.","Wrap-around at the end of the table.","A property against a `HashSet`, checking reachability after every step."],
  src=("src/primer/shift_set.rs", '''
//! Linear probing with backward-shift deletion.

#[derive(Debug, PartialEq, Eq)]
pub struct Full;

pub struct ShiftSet {
    // @begin 0c-c1
    slots: Vec<Option<u64>>,
    len: usize,
    //~ _shift: (),
    // @end
}

/// The slot a key starts probing at.
pub fn home(key: u64, capacity: usize) -> usize {
    let mut x = key.wrapping_mul(0x9E37_79B9_7F4A_7C15);
    x ^= x >> 29;
    (x % capacity as u64) as usize
}

impl ShiftSet {
    pub fn new(capacity: usize) -> ShiftSet {
        // @begin 0c-c1
        ShiftSet { slots: vec![None; capacity.max(1)], len: 0 }
        //~ todo!("0c-c1: every slot empty")
        // @end
    }

    pub fn capacity(&self) -> usize {
        // @begin 0c-c1
        self.slots.len()
        //~ todo!("0c-c1: the number of slots")
        // @end
    }

    pub fn len(&self) -> usize {
        // @begin 0c-c1
        self.len
        //~ todo!("0c-c1: the number of keys")
        // @end
    }

    pub fn is_empty(&self) -> bool {
        self.len() == 0
    }

    // @begin 0c-c1
    fn find(&self, key: u64) -> Option<usize> {
        let n = self.slots.len();
        let h = home(key, n);
        for d in 0..n {
            let i = (h + d) % n;
            match self.slots[i] {
                None => return None,
                Some(k) if k == key => return Some(i),
                Some(_) => {}
            }
        }
        None
    }
    //~ // TODO(0c-c1): a probe helper of your own
    // @end

    pub fn contains(&self, key: u64) -> bool {
        // @begin 0c-c1
        self.find(key).is_some()
        //~ todo!("0c-c1: probe from the home slot until the key or an empty slot")
        // @end
    }

    pub fn probe_len(&self, key: u64) -> Option<usize> {
        // @begin 0c-c1
        let i = self.find(key)?;
        let n = self.slots.len();
        Some((i + n - home(key, n)) % n)
        //~ todo!("0c-c1: how far the key sits from its home slot")
        // @end
    }

    pub fn insert(&mut self, key: u64) -> Result<bool, Full> {
        // @begin 0c-c1
        if self.find(key).is_some() {
            return Ok(false);
        }
        if self.len == self.slots.len() {
            return Err(Full);
        }
        let n = self.slots.len();
        let mut i = home(key, n);
        while self.slots[i].is_some() {
            i = (i + 1) % n;
        }
        self.slots[i] = Some(key);
        self.len += 1;
        Ok(true)
        //~ todo!("0c-c1: the first empty slot at or after the home slot")
        // @end
    }

    pub fn remove(&mut self, key: u64) -> bool {
        // @begin 0c-c1
        let Some(mut hole) = self.find(key) else { return false };
        let n = self.slots.len();
        self.slots[hole] = None;
        self.len -= 1;
        // shift back every following key of the run that would otherwise become unreachable
        let mut j = (hole + 1) % n;
        while let Some(k) = self.slots[j] {
            let h = home(k, n);
            // k may move into the hole only if its home is not strictly between the hole and j (cyclically)
            let dist_home_to_j = (j + n - h) % n;
            let dist_hole_to_j = (j + n - hole) % n;
            if dist_home_to_j >= dist_hole_to_j {
                self.slots[hole] = Some(k);
                self.slots[j] = None;
                hole = j;
            }
            j = (j + 1) % n;
        }
        true
        //~ todo!("0c-c1: empty the slot, then move later keys of the run back into the hole when their home allows it")
        // @end
    }
}
'''),
  test=("tests/stages_0c.rs", '''
use bustub::primer::shift_set::{home, Full, ShiftSet};
use std::collections::HashSet;

/// Keys that all hash to the same home slot of a table of `cap` slots (found by search; tests do not depend on which).
fn same_home(cap: usize, target: usize, n: usize) -> Vec<u64> {
    (0u64..).filter(|&k| home(k, cap) == target).take(n).collect()
}

#[test]
fn s0c_c1_keys_with_one_home_form_a_run() {
    let mut s = ShiftSet::new(8);
    let ks = same_home(8, 2, 3);
    for &k in &ks {
        assert_eq!(s.insert(k), Ok(true));
    }
    assert_eq!(ks.iter().map(|&k| s.probe_len(k).unwrap()).collect::<Vec<_>>(), vec![0, 1, 2]);
}

#[test]
fn s0c_c1_removing_the_first_of_a_run_shifts_the_rest_back() {
    let mut s = ShiftSet::new(8);
    let ks = same_home(8, 2, 3);
    for &k in &ks {
        s.insert(k).unwrap();
    }
    assert!(s.remove(ks[0]));
    assert_eq!((s.probe_len(ks[1]), s.probe_len(ks[2])), (Some(0), Some(1)), "no hole left in the run");
    assert!(!s.contains(ks[0]));
    assert!(!s.remove(ks[0]));
}

#[test]
fn s0c_c1_a_key_whose_home_is_after_the_hole_stays_put() {
    let mut s = ShiftSet::new(8);
    let a = same_home(8, 2, 2);
    let b = same_home(8, 4, 1)[0];
    s.insert(a[0]).unwrap();
    s.insert(a[1]).unwrap(); // slot 3
    s.insert(b).unwrap(); // slot 4: its own home
    s.remove(a[0]);
    assert_eq!(s.probe_len(b), Some(0));
    assert_eq!(s.probe_len(a[1]), Some(0));
}

#[test]
fn s0c_c1_a_full_table_refuses_and_a_run_may_wrap_around_the_end() {
    let mut s = ShiftSet::new(4);
    let ks = same_home(4, 3, 4);
    for &k in &ks {
        assert_eq!(s.insert(k), Ok(true));
    }
    assert_eq!(s.insert(999_999), Err(Full));
    assert!(s.remove(ks[1]));
    assert!(ks.iter().filter(|&&k| k != ks[1]).all(|&k| s.contains(k)), "wrapping around the end must keep every key reachable");
    assert_eq!(s.insert(999_999), Ok(true));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against a `HashSet`; and after every step every stored key is found (reachable from its home without an empty slot).
    #[test]
    fn s0c_c1_property_a_shift_set_is_a_set_and_stays_reachable(cap in 2usize..14, ops in proptest::collection::vec((any::<bool>(), 0u64..40), 0..120)) {
        let mut s = ShiftSet::new(cap);
        let mut m: HashSet<u64> = HashSet::new();
        for (ins, k) in ops {
            if ins {
                let r = s.insert(k);
                if m.contains(&k) { prop_assert_eq!(r, Ok(false)); }
                else if m.len() == cap { prop_assert_eq!(r, Err(Full)); }
                else { prop_assert_eq!(r, Ok(true)); m.insert(k); }
            } else {
                prop_assert_eq!(s.remove(k), m.remove(&k));
            }
            prop_assert_eq!(s.len(), m.len());
            for &k in &m { prop_assert!(s.contains(k), "key {} lost", k); }
            for k in 0..40 { prop_assert_eq!(s.contains(k), m.contains(&k)); }
        }
    }
}
''')))

CH.append(C("0c-c2", M0C, "91-challenge-probe-statistics", "extend", "Challenge: probe statistics", "easy", "stages_0c::s0c_c2",
  ["measuring how far keys sit from home in your table","what Robin Hood hashing does to the spread of probe distances"],
  ["robin-hood-hashing-and-open-addressing","performance-tests-and-measuring"],
  "`probe_histogram` and `mean_probe` in `src/primer/probe_stats.rs`: using the public view of **your** `RobinHoodHashSet<i32>` (`home_bucket`, `get_bucket`, `probe_distance`), compute how far each of a list of keys sits from its home bucket: `probe_histogram(set, keys)[d]` is the number of keys at distance `d`, and `mean_probe` the average.",
  "The point of Robin Hood hashing is a table where the *worst* probe distance stays small: rich keys give way to poor ones, so the variance of distances is low. You cannot see that from the answers (they are the same as any set's); you see it by measuring. A histogram of distances is the standard tool, and it is also how you find a bad hash function.",
  ["`probe_histogram(set, keys)`: for each key found in the set, its distance; the result has one entry per distance from 0 to the maximum, and counts the keys (absent keys are skipped).","`mean_probe(set, keys)`: the mean distance of the found keys (0.0 if none)."],
  ["The counts sum to the number of found keys.","The largest index with a non-zero count is at most `max_probe_distance()` of the set."],
  ["On a table at most half full, most keys are at distance 0 or 1.","Removing keys never raises the maximum distance of the remaining ones (Robin Hood property, tested on your implementation).","The histogram of a key list with duplicates counts each occurrence."],
  ["capacity 16, keys 1..8: histogram sums to 8"],
  ["Counts and mean on a small table.","Absent keys.","Your table's maximum distance against the histogram."],
  src=("src/primer/probe_stats.rs", '''
//! Probe-distance statistics over your Robin Hood hash set.

use crate::primer::robin_hood_hash_set::RobinHoodHashSet;

/// `h[d]` = how many of `keys` that are in `set` sit `d` buckets after their home bucket.
pub fn probe_histogram(set: &RobinHoodHashSet<i32>, keys: &[i32]) -> Vec<usize> {
    // @begin 0c-c2
    let mut h: Vec<usize> = Vec::new();
    for k in keys {
        if set.contains(k) {
            let d = set.probe_distance(set.home_bucket(k), set.get_bucket(k));
            if h.len() <= d {
                h.resize(d + 1, 0);
            }
            h[d] += 1;
        }
    }
    h
    //~ todo!("0c-c2: for each found key, the distance from its home bucket to the bucket it is in")
    // @end
}

/// The mean distance of the found keys.
pub fn mean_probe(set: &RobinHoodHashSet<i32>, keys: &[i32]) -> f64 {
    // @begin 0c-c2
    let h = probe_histogram(set, keys);
    let n: usize = h.iter().sum();
    if n == 0 {
        return 0.0;
    }
    h.iter().enumerate().map(|(d, c)| d * c).sum::<usize>() as f64 / n as f64
    //~ todo!("0c-c2: the weighted average of the histogram")
    // @end
}
'''),
  test=("tests/stages_0c.rs", '''
use bustub::primer::probe_stats::{mean_probe, probe_histogram};
use bustub::primer::robin_hood_hash_set::RobinHoodHashSet;

fn filled(cap: usize, keys: &[i32]) -> RobinHoodHashSet<i32> {
    let s = RobinHoodHashSet::new(cap).unwrap();
    for k in keys {
        s.insert(k);
    }
    s
}

#[test]
fn s0c_c2_the_histogram_counts_every_found_key_once() {
    let keys: Vec<i32> = (1..=8).collect();
    let s = filled(16, &keys);
    let h = probe_histogram(&s, &keys);
    assert_eq!(h.iter().sum::<usize>(), 8);
    assert!(!h.is_empty());
}

#[test]
fn s0c_c2_absent_keys_are_skipped_and_an_empty_input_gives_an_empty_histogram() {
    let s = filled(16, &[1, 2, 3]);
    assert_eq!(probe_histogram(&s, &[100, 200]), Vec::<usize>::new());
    assert_eq!(mean_probe(&s, &[]), 0.0);
    assert_eq!(probe_histogram(&s, &[1, 1]).iter().sum::<usize>(), 2, "each occurrence counts");
}

#[test]
fn s0c_c2_a_nearly_empty_table_has_everything_at_home() {
    let keys = [3, 4];
    let s = filled(64, &keys);
    let h = probe_histogram(&s, &keys);
    assert_eq!(h[0], 2);
    assert!(mean_probe(&s, &keys) < 1.0);
}

#[test]
fn s0c_c2_the_histogram_agrees_with_the_tables_own_maximum() {
    let keys: Vec<i32> = (0..40).collect();
    let s = filled(64, &keys);
    let h = probe_histogram(&s, &keys);
    assert_eq!(h.len() - 1, s.max_probe_distance(), "the largest distance of any key is the table's maximum");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 64, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: removing keys never raises the maximum distance of the others; mean lies between 0 and the maximum.
    #[test]
    fn s0c_c2_property_removal_does_not_raise_distances(keys in proptest::collection::btree_set(0i32..200, 1..30), remove in proptest::collection::vec(0i32..200, 0..15)) {
        let keys: Vec<i32> = keys.into_iter().collect();
        let s = filled(64, &keys);
        let before = probe_histogram(&s, &keys);
        let max_before = before.len().saturating_sub(1);
        for r in &remove { s.remove(r); }
        let after = probe_histogram(&s, &keys);
        prop_assert!(after.len().saturating_sub(1) <= max_before);
        let mean = mean_probe(&s, &keys);
        prop_assert!(mean >= 0.0 && mean <= after.len().saturating_sub(1) as f64);
    }
}
''')))

CH.append(C("0c-c3", M0C, "92-challenge-the-distance-that-wraps", "debug", "Challenge: the distance that wraps", "easy", "stages_0c::s0c_c3",
  ["finding a modular-distance bug that only shows when a probe run wraps around the end of the table"],
  ["robin-hood-hashing-and-open-addressing","overflow-and-checked-arithmetic","property-testing-and-fuzzing"],
  "`probe_distance` in `src/primer/probe_dist.rs` is how many slots forward from a key's home slot to where it sits, in a circular table. It is right for every key that does not wrap around the end of the table and wrong for those that do. Find the bug and fix it.",
  "Almost every key in a half-empty table sits before the end, so the code works in every small test and then, one key in `capacity / run-length`, a probe run crosses the end and the distance comes out huge or panics. Circular arithmetic is where `a - b` stops being the distance, and the cure is to add the modulus before subtracting.",
  ["`probe_distance(home, slot, capacity)` is the number of steps forward (wrapping from `capacity - 1` to 0) to get from `home` to `slot`; both are below `capacity`.","The result is in `0..capacity`."],
  ["`(home + probe_distance) % capacity == slot`.","`probe_distance(h, h, c) == 0`."],
  ["Distances of consecutive slots from one home increase by one until the wrap, then continue.","Distance from `h` to `s` plus distance from `s` to `h` is `capacity` (for `h != s`).","A key at its home has distance 0 whatever the capacity."],
  ["capacity 8: home 6, slot 1 -> 3","home 2, slot 5 -> 3","home 4, slot 4 -> 0"],
  ["Distances before and after the wrap.","All pairs for small capacities.","A property: stepping forward from home reaches the slot after exactly that many steps."],
  src=("src/primer/probe_dist.rs", '''
//! Distance along a circular probe sequence.

pub fn probe_distance(home: usize, slot: usize, capacity: usize) -> usize {
    // @begin 0c-c3
    (slot + capacity - home) % capacity
    //~ if slot >= home { slot - home } else { home - slot }
    // @end
}
'''),
  test=("tests/stages_0c.rs", '''
use bustub::primer::probe_dist::probe_distance;

#[test]
fn s0c_c3_distances_that_do_not_wrap() {
    assert_eq!(probe_distance(2, 5, 8), 3);
    assert_eq!(probe_distance(4, 4, 8), 0);
}

#[test]
fn s0c_c3_distances_that_wrap_around_the_end() {
    assert_eq!(probe_distance(6, 1, 8), 3, "6, 7, 0, 1");
    assert_eq!(probe_distance(7, 0, 8), 1);
    assert_eq!(probe_distance(5, 4, 8), 7, "all the way around but one");
}

#[test]
fn s0c_c3_forward_and_back_make_a_full_circle() {
    for c in 2..10 {
        for h in 0..c {
            for s in 0..c {
                if h != s {
                    assert_eq!(probe_distance(h, s, c) + probe_distance(s, h, c), c, "capacity {c}, {h} <-> {s}");
                }
            }
        }
    }
}

#[test]
fn s0c_c3_shifting_both_slots_by_the_same_amount_changes_nothing() {
    for c in 3..9 {
        for h in 0..c {
            for s in 0..c {
                for k in 0..c {
                    assert_eq!(probe_distance((h + k) % c, (s + k) % c, c), probe_distance(h, s, c));
                }
            }
        }
    }
}

#[test]
fn s0c_c3_shifting_both_slots_by_the_same_amount_changes_nothing() {
    for c in 3..9 {
        for h in 0..c {
            for s in 0..c {
                for k in 0..c {
                    assert_eq!(probe_distance((h + k) % c, (s + k) % c, c), probe_distance(h, s, c));
                }
            }
        }
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: stepping forward from home exactly `distance` times lands on the slot, and the distance is below the capacity.
    #[test]
    fn s0c_c3_property_walking_the_distance_lands_on_the_slot(c in 1usize..20, h in 0usize..20, s in 0usize..20) {
        let (h, s) = (h % c, s % c);
        let d = probe_distance(h, s, c);
        prop_assert!(d < c);
        let mut at = h;
        for _ in 0..d { at = (at + 1) % c; }
        prop_assert_eq!(at, s);
    }
}
''')))

CH.append(C("0c-c4", M0C, "93-challenge-multiply-shift-range-reduction", "build", "Challenge: range reduction without division", "easy", "stages_0c::s0c_c4",
  ["mapping a hash onto `0..n` with a multiply and a shift","the property a bucket function must have: in range, monotone, and nearly uniform"],
  ["hash-functions-and-murmur3","shifts-masks-and-bit-tricks"],
  "`reduce` in `src/primer/range_reduce.rs`: map a 32-bit hash `h` onto `0..n` as `(h * n) >> 32` (done in 64 bits), the \"fastrange\" reduction. It needs no division, works for any `n` (not just powers of two), and is monotone in `h`.",
  "`hash % n` is a division (slow on the critical path of every probe) and uses the **low** bits of the hash, which are the weakest bits of many hash functions. Multiplying and keeping the high bits is faster and uses the strongest bits. The trade-off to understand: results are *buckets of consecutive hash values*, so a bad hash that clusters in value clusters in buckets.",
  ["`reduce(h, n)` returns a value `< n` for `n >= 1`; `n == 0` returns 0.","It is `((h as u64 * n as u64) >> 32) as u32`.","`reduce_pow2(h, bits)` takes the top `bits` bits (`h >> (32 - bits)`) and equals `reduce(h, 1 << bits)`."],
  ["The result is always below `n`.","`reduce` is non-decreasing in `h`."],
  ["`reduce(h, 1)` is 0 and `reduce(u32::MAX, n)` is `n - 1`.","Each bucket receives a number of consecutive hash values that differs by at most one from the others.","`reduce(h, n)` for `n` a power of two equals the top bits of `h`."],
  ["reduce(0, 10) = 0; reduce(u32::MAX, 10) = 9; reduce(2^31, 10) = 5"],
  ["Range and monotonicity.","Even sharing between buckets.","Power-of-two equivalence."],
  src=("src/primer/range_reduce.rs", '''
//! Mapping a hash onto a range without a division.

/// A value in `0..n` (0 when `n == 0`), non-decreasing in `h`.
pub fn reduce(h: u32, n: u32) -> u32 {
    // @begin 0c-c4
    ((h as u64 * n as u64) >> 32) as u32
    //~ todo!("0c-c4: multiply in 64 bits and keep the high half")
    // @end
}

/// The top `bits` bits of `h` (`bits` in `0..=32`).
pub fn reduce_pow2(h: u32, bits: u32) -> u32 {
    // @begin 0c-c4
    if bits == 0 {
        0
    } else {
        h >> (32 - bits)
    }
    //~ todo!("0c-c4: shift the low bits away")
    // @end
}
'''),
  test=("tests/stages_0c.rs", '''
use bustub::primer::range_reduce::{reduce, reduce_pow2};

#[test]
fn s0c_c4_the_ends_and_the_middle() {
    assert_eq!(reduce(0, 10), 0);
    assert_eq!(reduce(u32::MAX, 10), 9);
    assert_eq!(reduce(1 << 31, 10), 5);
    assert_eq!(reduce(12345, 1), 0);
    assert_eq!(reduce(12345, 0), 0);
}

#[test]
fn s0c_c4_powers_of_two_are_the_top_bits() {
    for bits in 0..=10 {
        for h in [0u32, 1, 0x8000_0000, 0xDEAD_BEEF, u32::MAX, 0x1234_5678] {
            assert_eq!(reduce(h, 1 << bits), reduce_pow2(h, bits), "h {h:#x}, {bits} bits");
        }
    }
}

#[test]
fn s0c_c4_every_bucket_gets_nearly_the_same_share_of_hash_values() {
    // sample the hash space evenly: each of 7 buckets should receive within one sample of the average (1000)
    let n = 7u32;
    let samples = 7 * 1000;
    let mut counts = vec![0usize; n as usize];
    for i in 0..samples {
        let h = ((i as u64 * (1u64 << 32)) / samples as u64) as u32;
        counts[reduce(h, n) as usize] += 1;
    }
    assert!(counts.iter().all(|&c| (999..=1001).contains(&c)), "{counts:?}");
}

#[test]
fn s0c_c4_halving_a_fine_bucket_gives_the_coarse_one() {
    for h in [0u32, 1, 12345, 0x8000_0000, 0xDEAD_BEEF, u32::MAX] {
        assert_eq!(reduce(h, 20) / 2, reduce(h, 10), "h {h:#x}");
        assert!(reduce(h, 10) <= reduce(h, 20));
    }
}

#[test]
fn s0c_c4_halving_a_fine_bucket_gives_the_coarse_one() {
    for h in [0u32, 1, 12345, 0x8000_0000, 0xDEAD_BEEF, u32::MAX] {
        assert_eq!(reduce(h, 20) / 2, reduce(h, 10), "h {h:#x}");
        assert!(reduce(h, 10) <= reduce(h, 20));
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: below `n`, and non-decreasing in the hash.
    #[test]
    fn s0c_c4_property_in_range_and_monotone(a in any::<u32>(), b in any::<u32>(), n in 1u32..100_000) {
        prop_assert!(reduce(a, n) < n);
        let (lo, hi) = (a.min(b), a.max(b));
        prop_assert!(reduce(lo, n) <= reduce(hi, n));
    }
}
''')))

CH.append(C("0c-c5", M0C, "94-challenge-comparing-eight-bytes-at-once", "build", "Challenge: eight comparisons at once", "medium", "stages_0c::s0c_c5",
  ["a SWAR (SIMD within a register) byte comparison","how Swiss tables and SIMD hash probes test a group of control bytes"],
  ["shifts-masks-and-bit-tricks","performance-tests-and-measuring"],
  "`match_byte` and `first_match` in `src/primer/swar.rs`: given 8 control bytes packed in a `u64`, `match_byte(group, byte)` returns a mask with the **high bit of each matching byte set** (and no other bit), computed with a handful of arithmetic operations and no loop over bytes. `first_match(mask)` is the index (0..8) of the lowest matching byte, or `None`.",
  "Modern hash tables (Swiss tables, F14) keep one control byte per slot and compare a whole group of them with one instruction to decide which slots to inspect. With no SIMD available, the same idea works inside one 64-bit register. It is the cleanest example of why bit tricks are not decoration: the loop over eight bytes disappears.",
  ["Bytes are numbered from the least significant (byte 0).","`match_byte(group, b)`: bit `8 * i + 7` is set exactly for the bytes `i` equal to `b`; no other bit is set. No false positives for any input.","`first_match(mask)`: the index of the first (lowest) set byte, `None` for 0."],
  ["The mask only ever has bits at positions 7, 15, 23, ... 63.","`first_match(match_byte(g, b))` is the position of the first byte of `g` equal to `b`."],
  ["`match_byte(g, b)` has as many bits as `g` has bytes equal to `b`.","`match_byte(g, b) == 0` when `b` does not occur.","Replacing a byte of `g` by `b` sets exactly its flag."],
  ["g = bytes [1, 7, 7, 0, 255, 7, 2, 9]: match_byte(g, 7) flags bytes 1, 2, 5; first_match -> 1"],
  ["Matches and non-matches.","The classic false-positive cases (0x01 next to the target, 0x80, 0xFF).","A property against a per-byte comparison."],
  src=("src/primer/swar.rs", '''
//! Comparing the eight bytes of a u64 at once.

const LOW7: u64 = 0x7F7F_7F7F_7F7F_7F7F;
const HIGH: u64 = 0x8080_8080_8080_8080;

/// The high bit of each byte of `group` that equals `byte`, and no other bit.
pub fn match_byte(group: u64, byte: u8) -> u64 {
    // @begin 0c-c5
    // x has a zero byte exactly where `group` equals `byte`; detect zero bytes exactly (no false positives):
    let x = group ^ (u64::from(byte) * 0x0101_0101_0101_0101);
    !(((x & LOW7).wrapping_add(LOW7)) | x | LOW7) & HIGH
    //~ todo!("0c-c5: xor with the byte repeated eight times, then find the zero bytes of the result with arithmetic only")
    // @end
}

/// The index of the lowest flagged byte.
pub fn first_match(mask: u64) -> Option<usize> {
    // @begin 0c-c5
    if mask == 0 {
        None
    } else {
        Some(mask.trailing_zeros() as usize / 8)
    }
    //~ todo!("0c-c5: the position of the lowest set bit, divided by eight")
    // @end
}
'''),
  test=("tests/stages_0c.rs", '''
use bustub::primer::swar::{first_match, match_byte};

fn pack(bytes: [u8; 8]) -> u64 {
    u64::from_le_bytes(bytes)
}

#[test]
fn s0c_c5_flags_the_matching_bytes_and_only_them() {
    let g = pack([1, 7, 7, 0, 255, 7, 2, 9]);
    let m = match_byte(g, 7);
    assert_eq!(m, (1u64 << 15) | (1u64 << 23) | (1u64 << 47));
    assert_eq!(first_match(m), Some(1));
    assert_eq!(match_byte(g, 8), 0);
    assert_eq!(first_match(0), None);
}

#[test]
fn s0c_c5_neighbours_of_the_target_do_not_cause_false_positives() {
    // classic traps: a byte one above the target (borrow propagation) and the high-bit patterns
    let g = pack([0x01, 0x00, 0x80, 0xFF, 0x7F, 0x81, 0xFE, 0x02]);
    for (b, want) in [(0x00u8, vec![1usize]), (0x01, vec![0]), (0x80, vec![2]), (0xFF, vec![3]), (0x7F, vec![4]), (0x02, vec![7])] {
        let m = match_byte(g, b);
        let idx: Vec<usize> = (0..8).filter(|i| m >> (8 * i + 7) & 1 == 1).collect();
        assert_eq!(idx, want, "byte {b:#x}");
        assert_eq!(m & !0x8080_8080_8080_8080, 0);
    }
}

#[test]
fn s0c_c5_all_equal_and_none_equal() {
    assert_eq!(match_byte(u64::MAX, 0xFF), 0x8080_8080_8080_8080);
    assert_eq!(match_byte(0, 0), 0x8080_8080_8080_8080);
    assert_eq!(match_byte(0, 1), 0);
}

#[test]
fn s0c_c5_replacing_one_byte_flags_exactly_its_position() {
    for i in 0..8 {
        let mut bytes = [0xAAu8; 8];
        bytes[i] = 0x17;
        assert_eq!(match_byte(pack(bytes), 0x17), 1u64 << (8 * i + 7));
        assert_eq!(first_match(match_byte(pack(bytes), 0x17)), Some(i));
    }
}

#[test]
fn s0c_c5_replacing_one_byte_flags_exactly_its_position() {
    for i in 0..8 {
        let mut bytes = [0xAAu8; 8];
        bytes[i] = 0x17;
        assert_eq!(match_byte(pack(bytes), 0x17), 1u64 << (8 * i + 7));
        assert_eq!(first_match(match_byte(pack(bytes), 0x17)), Some(i));
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 1024, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: exactly the bytes equal to the target are flagged, whatever the group.
    #[test]
    fn s0c_c5_property_matches_a_per_byte_comparison(bytes in proptest::array::uniform8(prop_oneof![0u8..4, any::<u8>()]), b in prop_oneof![0u8..4, any::<u8>()]) {
        let g = pack(bytes);
        let m = match_byte(g, b);
        let mut want = 0u64;
        for (i, &x) in bytes.iter().enumerate() { if x == b { want |= 1 << (8 * i + 7); } }
        prop_assert_eq!(m, want);
        prop_assert_eq!(first_match(m), bytes.iter().position(|&x| x == b));
    }
}
''')))

CH.append(C("0d-c1", M0D, "90-challenge-a-bloom-filter", "build", "Challenge: a Bloom filter", "medium", "stages_0d::s0d_c1",
  ["a set that may answer yes wrongly but never no wrongly","choosing the number of bits and hashes for a target error rate"],
  ["count-min-sketch-and-frequency-estimation","hash-functions-and-murmur3","property-testing-and-fuzzing"],
  "`BloomFilter` in `src/primer/bloom.rs`: a bit array of `m` bits and `k` hash functions (derived from two base hashes by double hashing, `h1 + i * h2`). `insert(key)` sets `k` bits; `contains(key)` is true only if all `k` bits are set. There are **no false negatives**; false positives happen with a probability that depends on `m`, `k` and the number of keys. `union(other)` of two filters of the same shape contains everything either contained.",
  "A Bloom filter is the smallest useful probabilistic structure: a few bits per key buy \"definitely not here\" answers that save a disk read (LSM trees check one per SSTable) or a network round trip. The part to get right is the one-sided error, and the part to understand is the cost: `m / n` bits per key buys an error rate you can compute.",
  ["`new(m_bits, k)`; `insert(&u64)`, `contains(&u64)`; `bits_set()` counts set bits; `union(&other) -> Option<BloomFilter>` (`None` if `m` or `k` differ).","`positions(key)` (given) lists the `k` bit indexes of a key."],
  ["Every inserted key is contained, always.","`bits_set() <= k * inserted_keys` and never more than `m`."],
  ["Inserting a key twice changes nothing.","`union(a, b)` contains everything `a` or `b` contained, and its bits are the bitwise or.","With 10 bits per key and 7 hashes, the false-positive rate on 1000 keys is below 3%."],
  ["m 1000, k 3: insert 1..100 -> all contained; false positives among 1000..2000 are a few percent at most"],
  ["No false negatives; duplicates.","Union and its shape check.","The measured false-positive rate against the theory."],
  src=("src/primer/bloom.rs", '''
//! A Bloom filter over u64 keys.

fn mix(mut x: u64, seed: u64) -> u64 {
    x ^= seed;
    x = (x ^ (x >> 33)).wrapping_mul(0xff51_afd7_ed55_8ccd);
    x = (x ^ (x >> 33)).wrapping_mul(0xc4ce_b9fe_1a85_ec53);
    x ^ (x >> 33)
}

pub struct BloomFilter {
    // @begin 0d-c1
    bits: Vec<u64>,
    m: usize,
    k: u32,
    //~ _bloom: (),
    // @end
}

impl BloomFilter {
    pub fn new(m_bits: usize, k: u32) -> BloomFilter {
        // @begin 0d-c1
        let m = m_bits.max(1);
        BloomFilter { bits: vec![0; m.div_ceil(64)], m, k: k.max(1) }
        //~ todo!("0d-c1: m cleared bits")
        // @end
    }

    /// The `k` bit positions of a key (double hashing).
    pub fn positions(&self, key: u64) -> Vec<usize> {
        // @begin 0d-c1
        let (h1, h2) = (mix(key, 0x9E37_79B9), mix(key, 0x7F4A_7C15) | 1);
        (0..self.k as u64).map(|i| (h1.wrapping_add(i.wrapping_mul(h2)) % self.m as u64) as usize).collect()
        //~ todo!("0d-c1: h1 + i * h2 modulo m, for i in 0..k")
        // @end
    }

    pub fn insert(&mut self, key: u64) {
        // @begin 0d-c1
        for p in self.positions(key) {
            self.bits[p / 64] |= 1 << (p % 64);
        }
        //~ todo!("0d-c1: set the k bits")
        // @end
    }

    pub fn contains(&self, key: u64) -> bool {
        // @begin 0d-c1
        self.positions(key).into_iter().all(|p| self.bits[p / 64] >> (p % 64) & 1 == 1)
        //~ todo!("0d-c1: all k bits set")
        // @end
    }

    pub fn bits_set(&self) -> usize {
        // @begin 0d-c1
        self.bits.iter().map(|w| w.count_ones() as usize).sum()
        //~ todo!("0d-c1: how many bits are set")
        // @end
    }

    pub fn union(&self, other: &BloomFilter) -> Option<BloomFilter> {
        // @begin 0d-c1
        if self.m != other.m || self.k != other.k {
            return None;
        }
        Some(BloomFilter { bits: self.bits.iter().zip(&other.bits).map(|(a, b)| a | b).collect(), m: self.m, k: self.k })
        //~ todo!("0d-c1: the bitwise or, for filters of the same shape")
        // @end
    }
}
'''),
  test=("tests/stages_0d.rs", '''
use bustub::primer::bloom::BloomFilter;

#[test]
fn s0d_c1_there_are_no_false_negatives() {
    let mut f = BloomFilter::new(2000, 5);
    for k in 0..200u64 {
        f.insert(k * 7919);
    }
    assert!((0..200u64).all(|k| f.contains(k * 7919)));
}

#[test]
fn s0d_c1_an_empty_filter_contains_nothing_and_inserting_twice_changes_nothing() {
    let mut f = BloomFilter::new(512, 3);
    assert!(!f.contains(1) && f.bits_set() == 0);
    f.insert(1);
    let once = f.bits_set();
    f.insert(1);
    assert_eq!(f.bits_set(), once);
    assert!(once <= 3);
}

#[test]
fn s0d_c1_the_false_positive_rate_matches_the_theory() {
    // 10 bits per key and 7 hashes: about 0.8% in theory; accept up to 3%
    let mut f = BloomFilter::new(10_000, 7);
    for k in 0..1000u64 {
        f.insert(k);
    }
    let fp = (1_000_000u64..1_005_000).filter(|&k| f.contains(k)).count();
    assert!(fp < 150, "{fp} false positives in 5000 probes");
}

#[test]
fn s0d_c1_union_contains_everything_either_contained_and_checks_the_shape() {
    let (mut a, mut b) = (BloomFilter::new(1024, 4), BloomFilter::new(1024, 4));
    for k in 0..50u64 { a.insert(k); }
    for k in 100..150u64 { b.insert(k); }
    let u = a.union(&b).unwrap();
    assert!((0..50u64).chain(100..150).all(|k| u.contains(k)));
    assert_eq!(u.bits_set() , {
        let mut both = BloomFilter::new(1024, 4);
        for k in (0..50u64).chain(100..150) { both.insert(k); }
        both.bits_set()
    });
    assert!(a.union(&BloomFilter::new(512, 4)).is_none());
    assert!(a.union(&BloomFilter::new(1024, 5)).is_none());
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 64, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: whatever is inserted is contained, and the number of set bits is at most `k` per key.
    #[test]
    fn s0d_c1_property_inserted_keys_are_always_found(keys in proptest::collection::vec(any::<u64>(), 0..80), m in 64usize..4000, k in 1u32..8) {
        let mut f = BloomFilter::new(m, k);
        for &x in &keys { f.insert(x); }
        for &x in &keys { prop_assert!(f.contains(x)); }
        prop_assert!(f.bits_set() <= (k as usize * keys.len()).min(m));
    }
}
''')))

CH.append(C("0d-c2", M0D, "91-challenge-reservoir-sampling", "build", "Challenge: reservoir sampling", "medium", "stages_0d::s0d_c2",
  ["a uniform sample of a stream of unknown length in constant memory","a proof-by-test that each item has the same chance"],
  ["property-testing-and-fuzzing","hyperloglog-and-distinct-counting"],
  "`Reservoir` in `src/primer/reservoir.rs`: keep a uniform random sample of `k` items from a stream you see once and whose length you do not know (Algorithm R). The first `k` items fill the reservoir; item number `i` (1-based) after that replaces a uniformly random slot with probability `k / i`. A seeded generator (given) makes runs reproducible.",
  "`ORDER BY random() LIMIT k` sorts everything; reservoir sampling reads the data once and holds `k` items, which is how `TABLESAMPLE`, statistics collection (`ANALYZE`) and log sampling work. The remarkable part is the claim that every item ends up in the sample with the *same* probability `k / n`: a statement a test can check by repetition.",
  ["`Reservoir::new(k, seed)`; `offer(item)`; `sample()` returns the current items (any order); `seen()` is the number offered.","The reservoir never holds more than `k` items, and holds `min(k, seen)`.","Item `i > k` replaces slot `rng % i` if that is below `k` (Algorithm R); the generator is `XorShift` (given)."],
  ["`sample().len() == min(k, seen())`.","Every sampled item was offered, and an item appears at most as many times as it was offered."],
  ["A stream no longer than `k` is returned whole.","The same seed and stream give the same sample.","Across many runs, each of `n` items is in the sample about `k / n` of the time."],
  ["k 3, stream 1..=3 -> {1,2,3}","k 1, 10 items, 20 000 runs: each item about 2 000 times"],
  ["Small streams, size bounds, determinism.","Uniformity over many seeded runs.","A property over streams."],
  src=("src/primer/reservoir.rs", '''
//! Reservoir sampling (Algorithm R).

/// A small seeded xorshift generator (given).
pub struct XorShift(u64);

impl XorShift {
    pub fn new(seed: u64) -> XorShift {
        XorShift(seed.wrapping_mul(0x9E37_79B9_7F4A_7C15).max(1))
    }

    pub fn next_u64(&mut self) -> u64 {
        let mut x = self.0;
        x ^= x << 13;
        x ^= x >> 7;
        x ^= x << 17;
        self.0 = x;
        x
    }
}

pub struct Reservoir<T> {
    // @begin 0d-c2
    k: usize,
    items: Vec<T>,
    seen: u64,
    rng: XorShift,
    //~ _res: std::marker::PhantomData<T>,
    // @end
}

impl<T> Reservoir<T> {
    pub fn new(k: usize, seed: u64) -> Reservoir<T> {
        // @begin 0d-c2
        Reservoir { k, items: Vec::with_capacity(k), seen: 0, rng: XorShift::new(seed) }
        //~ todo!("0d-c2: an empty reservoir for `k` items")
        // @end
    }

    pub fn offer(&mut self, item: T) {
        // @begin 0d-c2
        self.seen += 1;
        if self.items.len() < self.k {
            self.items.push(item);
        } else if self.k > 0 {
            let j = (self.rng.next_u64() % self.seen) as usize;
            if j < self.k {
                self.items[j] = item;
            }
        }
        //~ todo!("0d-c2: fill the reservoir, then replace a random slot with probability k / seen")
        // @end
    }

    pub fn sample(&self) -> &[T] {
        // @begin 0d-c2
        &self.items
        //~ todo!("0d-c2: the items held")
        // @end
    }

    pub fn seen(&self) -> u64 {
        // @begin 0d-c2
        self.seen
        //~ todo!("0d-c2: how many items were offered")
        // @end
    }
}
'''),
  test=("tests/stages_0d.rs", '''
use bustub::primer::reservoir::Reservoir;

#[test]
fn s0d_c2_a_short_stream_is_kept_whole() {
    let mut r = Reservoir::new(5, 1);
    for i in 0..3 {
        r.offer(i);
    }
    let mut s = r.sample().to_vec();
    s.sort();
    assert_eq!((s, r.seen()), (vec![0, 1, 2], 3));
}

#[test]
fn s0d_c2_the_sample_never_exceeds_k() {
    let mut r = Reservoir::new(4, 9);
    for i in 0..1000 {
        r.offer(i);
        assert!(r.sample().len() <= 4);
    }
    assert_eq!((r.sample().len(), r.seen()), (4, 1000));
}

#[test]
fn s0d_c2_a_reservoir_of_zero_holds_nothing() {
    let mut r = Reservoir::new(0, 3);
    for i in 0..10 {
        r.offer(i);
    }
    assert_eq!((r.sample().len(), r.seen()), (0, 10));
}

#[test]
fn s0d_c2_the_same_seed_gives_the_same_sample() {
    let run = |seed| {
        let mut r = Reservoir::new(5, seed);
        for i in 0..500 {
            r.offer(i);
        }
        r.sample().to_vec()
    };
    assert_eq!(run(7), run(7));
    assert_ne!(run(7), run(8));
}

#[test]
fn s0d_c2_every_item_is_equally_likely_to_be_sampled() {
    // 10 items, k = 3: each should be sampled in about 30% of 20 000 runs
    let n = 10usize;
    let runs = 20_000;
    let mut hits = vec![0usize; n];
    for seed in 0..runs {
        let mut r = Reservoir::new(3, seed as u64 + 1);
        for i in 0..n {
            r.offer(i);
        }
        for &i in r.sample() {
            hits[i] += 1;
        }
    }
    for (i, &h) in hits.iter().enumerate() {
        let p = h as f64 / runs as f64;
        assert!((p - 0.3).abs() < 0.03, "item {i} was sampled with frequency {p}, expected 0.3 (all: {hits:?})");
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the sample is a sub-multiset of the stream with `min(k, n)` items.
    #[test]
    fn s0d_c2_property_the_sample_comes_from_the_stream(stream in proptest::collection::vec(0u32..6, 0..40), k in 0usize..8, seed in any::<u64>()) {
        let mut r = Reservoir::new(k, seed);
        for &x in &stream { r.offer(x); }
        prop_assert_eq!(r.sample().len(), k.min(stream.len()));
        let mut pool = stream.clone();
        for x in r.sample() {
            let at = pool.iter().position(|y| y == x);
            prop_assert!(at.is_some(), "{} sampled more often than offered", x);
            pool.remove(at.unwrap());
        }
    }
}
''')))

CH.append(C("0d-c3", M0D, "92-challenge-a-merkle-tree", "build", "Challenge: a Merkle tree", "medium", "stages_0d::s0d_c3",
  ["a hash tree whose root commits to every leaf","an inclusion proof that a verifier checks without the other leaves"],
  ["hashing-values-and-keys","property-testing-and-fuzzing"],
  "`MerkleTree` in `src/primer/merkle.rs`: build a hash tree over a list of byte-string leaves: the hash of a leaf is `leaf_hash(data)`; an inner node is `node_hash(left, right)`; an odd node at the end of a level is paired with itself. `root()` commits to every leaf; `proof(i)` returns the sibling hashes from leaf `i` up to the root; `verify(root, leaf, index, proof)` recomputes the root from the leaf and the proof.",
  "Anti-entropy in replicated stores (Dynamo, Cassandra), certificate transparency, git and blockchains all compare large data by comparing roots, and prove one item belongs with a logarithmic-size proof. The structure is the same everywhere; the details to get right are the odd node at the end of a level and that a proof is only valid for one index.",
  ["`leaf_hash` and `node_hash` are given (64-bit FNV-1a based, with domain separation: a leaf and an inner hash never collide by construction of the inputs).","`root()` of an empty tree is `0`; of one leaf, that leaf's hash.","`proof(i)` is a list of `(sibling_hash, sibling_is_right)` from the bottom up; `None` for an index out of range.","`verify(root, leaf, proof)` folds the leaf hash with the proof and compares it with `root`."],
  ["`verify(root, leaves[i], proof(i))` is true for every `i`.","Changing any leaf changes the root."],
  ["A proof for leaf `i` does not verify a different leaf (with overwhelming likelihood: for the leaves tested, never).","Appending a leaf changes the root; the root of the same leaves is always the same.","Proof length is `ceil(log2(n))`."],
  ["4 leaves: proof(2) has 2 siblings; changing leaf 1 changes the root but not proof(2)'s first sibling hash... except that its second sibling (the hash of leaves 0-1) changes"],
  ["Roots of 0, 1, 2, 3 and 4 leaves.","Proof sizes and verification for every leaf.","Tampering with a leaf, a sibling or the order."],
  src=("src/primer/merkle.rs", '''
//! A Merkle tree over byte strings.

fn fnv(data: &[u8], seed: u64) -> u64 {
    let mut h = 0xcbf2_9ce4_8422_2325u64 ^ seed;
    for &b in data {
        h ^= b as u64;
        h = h.wrapping_mul(0x100_0000_01b3);
    }
    h
}

/// The hash of a leaf.
pub fn leaf_hash(data: &[u8]) -> u64 {
    fnv(data, 0x00)
}

/// The hash of an inner node from its children.
pub fn node_hash(left: u64, right: u64) -> u64 {
    let mut buf = [0u8; 16];
    buf[..8].copy_from_slice(&left.to_le_bytes());
    buf[8..].copy_from_slice(&right.to_le_bytes());
    fnv(&buf, 0x01)
}

pub struct MerkleTree {
    // @begin 0d-c3
    /// levels[0] are the leaf hashes; the last level has one entry (the root); empty for no leaves.
    levels: Vec<Vec<u64>>,
    //~ _merkle: (),
    // @end
}

impl MerkleTree {
    pub fn new(leaves: &[Vec<u8>]) -> MerkleTree {
        // @begin 0d-c3
        if leaves.is_empty() {
            return MerkleTree { levels: Vec::new() };
        }
        let mut levels = vec![leaves.iter().map(|l| leaf_hash(l)).collect::<Vec<u64>>()];
        while levels.last().unwrap().len() > 1 {
            let prev = levels.last().unwrap();
            let next: Vec<u64> = prev.chunks(2).map(|c| node_hash(c[0], *c.get(1).unwrap_or(&c[0]))).collect();
            levels.push(next);
        }
        MerkleTree { levels }
        //~ todo!("0d-c3: hash the leaves, then pair neighbours level by level; an odd one out is paired with itself")
        // @end
    }

    pub fn root(&self) -> u64 {
        // @begin 0d-c3
        self.levels.last().map_or(0, |l| l[0])
        //~ todo!("0d-c3: the single hash at the top (0 for no leaves)")
        // @end
    }

    pub fn leaves(&self) -> usize {
        // @begin 0d-c3
        self.levels.first().map_or(0, Vec::len)
        //~ todo!("0d-c3: how many leaves")
        // @end
    }

    /// `(sibling hash, sibling is on the right)` from the leaf up to (not including) the root.
    pub fn proof(&self, index: usize) -> Option<Vec<(u64, bool)>> {
        // @begin 0d-c3
        if index >= self.leaves() {
            return None;
        }
        let mut i = index;
        let mut out = Vec::new();
        for level in &self.levels[..self.levels.len() - 1] {
            let sib = if i % 2 == 0 { (*level.get(i + 1).unwrap_or(&level[i]), true) } else { (level[i - 1], false) };
            out.push(sib);
            i /= 2;
        }
        Some(out)
        //~ todo!("0d-c3: at each level the neighbour of the current node, and which side it is on")
        // @end
    }
}

/// Does `leaf` with `proof` lead to `root`?
pub fn verify(root: u64, leaf: &[u8], proof: &[(u64, bool)]) -> bool {
    // @begin 0d-c3
    let mut h = leaf_hash(leaf);
    for &(sib, on_right) in proof {
        h = if on_right { node_hash(h, sib) } else { node_hash(sib, h) };
    }
    h == root
    //~ todo!("0d-c3: fold the leaf hash with each sibling in order")
    // @end
}
'''),
  test=("tests/stages_0d.rs", '''
use bustub::primer::merkle::{leaf_hash, node_hash, verify, MerkleTree};

fn leaves(n: usize) -> Vec<Vec<u8>> {
    (0..n).map(|i| format!("leaf-{i}").into_bytes()).collect()
}

#[test]
fn s0d_c3_roots_of_small_trees_by_hand() {
    assert_eq!(MerkleTree::new(&[]).root(), 0);
    let one = leaves(1);
    assert_eq!(MerkleTree::new(&one).root(), leaf_hash(&one[0]));
    let two = leaves(2);
    assert_eq!(MerkleTree::new(&two).root(), node_hash(leaf_hash(&two[0]), leaf_hash(&two[1])));
    let three = leaves(3);
    let (a, b, c) = (leaf_hash(&three[0]), leaf_hash(&three[1]), leaf_hash(&three[2]));
    assert_eq!(MerkleTree::new(&three).root(), node_hash(node_hash(a, b), node_hash(c, c)), "an odd node is paired with itself");
}

#[test]
fn s0d_c3_every_leaf_has_a_proof_that_verifies() {
    for n in 1..=9 {
        let ls = leaves(n);
        let t = MerkleTree::new(&ls);
        for (i, l) in ls.iter().enumerate() {
            let p = t.proof(i).unwrap();
            assert!(verify(t.root(), l, &p), "n {n}, leaf {i}");
            assert_eq!(p.len(), (n as f64).log2().ceil() as usize);
        }
        assert!(t.proof(n).is_none());
    }
}

#[test]
fn s0d_c3_a_wrong_leaf_or_a_tampered_proof_fails() {
    let ls = leaves(6);
    let t = MerkleTree::new(&ls);
    let p = t.proof(2).unwrap();
    assert!(!verify(t.root(), b"leaf-3", &p), "a proof is for one leaf");
    let mut bad = p.clone();
    bad[0].0 ^= 1;
    assert!(!verify(t.root(), &ls[2], &bad));
    let mut flipped = p.clone();
    flipped[1].1 = !flipped[1].1;
    assert!(!verify(t.root(), &ls[2], &flipped));
}

#[test]
fn s0d_c3_changing_any_leaf_or_the_order_changes_the_root() {
    let ls = leaves(5);
    let root = MerkleTree::new(&ls).root();
    for i in 0..5 {
        let mut m = ls.clone();
        m[i].push(b'!');
        assert_ne!(MerkleTree::new(&m).root(), root, "leaf {i}");
    }
    let mut swapped = ls.clone();
    swapped.swap(0, 4);
    assert_ne!(MerkleTree::new(&swapped).root(), root);
    assert_eq!(MerkleTree::new(&ls).root(), root, "the root is a function of the leaves");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: every leaf's proof verifies against the root and against nothing else.
    #[test]
    fn s0d_c3_property_proofs_verify_exactly_their_leaf(ls in proptest::collection::vec(proptest::collection::vec(any::<u8>(), 0..6), 1..12)) {
        let t = MerkleTree::new(&ls);
        for (i, l) in ls.iter().enumerate() {
            let p = t.proof(i).unwrap();
            prop_assert!(verify(t.root(), l, &p));
            let mut other = l.clone();
            other.push(0);
            prop_assert!(!verify(t.root(), &other, &p));
        }
    }
}
''')))

CH.append(C("0d-c4", M0D, "93-challenge-a-counter-that-merges", "build", "Challenge: a counter that merges", "easy", "stages_0d::s0d_c4",
  ["a CRDT counter that supports decrements","the three laws that make merging order-independent"],
  ["crdts-and-observed-remove-sets","property-testing-and-fuzzing"],
  "`PnCounter` in `src/primer/pn_counter.rs`: a counter that many replicas can increment **and decrement** without coordination. Each replica keeps, per node, how much it has added and how much it has taken away; `value()` is total added minus total taken; `merge(&other)` combines two replicas by taking, for each node, the **larger** of the two counts on each side.",
  "A plain counter shared by replicas loses updates (two replicas read 5 and both write 6). A grow-only counter per node cannot lose them but cannot decrement; a pair of them can. The reason merging works is three algebraic laws, and each is a test: merge in any order, any grouping, any number of times, and the replicas converge.",
  ["`PnCounter::new()`; `inc(node, n)`, `dec(node, n)` update that node's own counts; `value() -> i64`.","`merge(&other)`: for every node, `p = max(p, other.p)` and `n = max(n, other.n)`.","Nodes are `u32`."],
  ["For each node, the added and removed counts only ever grow.","`value()` equals the sum of all added counts minus the sum of all removed counts."],
  ["Commutative: `a.merge(b)` and `b.merge(a)` give equal counters.","Associative: merging in either grouping gives the same counter.","Idempotent: merging a counter into itself, or merging twice, changes nothing."],
  ["a: node 1 +5; b: node 2 +3, node 2 -1; merged value = 7; merged again = 7"],
  ["Increments and decrements.","Each law on examples.","A property for random replicas."],
  src=("src/primer/pn_counter.rs", '''
//! A positive-negative counter CRDT.

use std::collections::BTreeMap;

#[derive(Clone, Debug, Default, PartialEq, Eq)]
pub struct PnCounter {
    // @begin 0d-c4
    added: BTreeMap<u32, u64>,
    removed: BTreeMap<u32, u64>,
    //~ _pn: (),
    // @end
}

impl PnCounter {
    pub fn new() -> PnCounter {
        // @begin 0d-c4
        PnCounter::default()
        //~ todo!("0d-c4: a counter nobody has changed")
        // @end
    }

    pub fn inc(&mut self, node: u32, n: u64) {
        // @begin 0d-c4
        *self.added.entry(node).or_insert(0) += n;
        //~ todo!("0d-c4: this node added n")
        // @end
    }

    pub fn dec(&mut self, node: u32, n: u64) {
        // @begin 0d-c4
        *self.removed.entry(node).or_insert(0) += n;
        //~ todo!("0d-c4: this node took n away")
        // @end
    }

    pub fn value(&self) -> i64 {
        // @begin 0d-c4
        self.added.values().sum::<u64>() as i64 - self.removed.values().sum::<u64>() as i64
        //~ todo!("0d-c4: all added minus all removed")
        // @end
    }

    pub fn merge(&mut self, other: &PnCounter) {
        // @begin 0d-c4
        for (&n, &v) in &other.added {
            let e = self.added.entry(n).or_insert(0);
            *e = (*e).max(v);
        }
        for (&n, &v) in &other.removed {
            let e = self.removed.entry(n).or_insert(0);
            *e = (*e).max(v);
        }
        //~ todo!("0d-c4: for each node the larger count, separately for added and removed")
        // @end
    }
}
'''),
  test=("tests/stages_0d.rs", '''
use bustub::primer::pn_counter::PnCounter;

fn counter(ops: &[(u32, bool, u64)]) -> PnCounter {
    let mut c = PnCounter::new();
    for &(n, up, v) in ops {
        if up { c.inc(n, v) } else { c.dec(n, v) }
    }
    c
}

#[test]
fn s0d_c4_values_add_and_subtract() {
    let c = counter(&[(1, true, 5), (1, false, 2), (2, true, 10)]);
    assert_eq!(c.value(), 13);
    assert_eq!(PnCounter::new().value(), 0);
    assert_eq!(counter(&[(1, false, 4)]).value(), -4);
}

#[test]
fn s0d_c4_merging_two_replicas_combines_their_updates() {
    let mut a = counter(&[(1, true, 5)]);
    let b = counter(&[(2, true, 3), (2, false, 1)]);
    a.merge(&b);
    assert_eq!(a.value(), 7);
    a.merge(&b);
    assert_eq!(a.value(), 7, "merging again changes nothing");
}

#[test]
fn s0d_c4_two_replicas_that_each_saw_a_newer_state_of_the_same_node_keep_the_larger() {
    let old = counter(&[(1, true, 3)]);
    let new = counter(&[(1, true, 8)]);
    let mut m = old.clone();
    m.merge(&new);
    assert_eq!(m.value(), 8, "not 11: the counts of one node are not added together");
}

#[test]
fn s0d_c4_updates_made_after_a_merge_are_not_lost_by_the_next_one() {
    let mut a = counter(&[(1, true, 2)]);
    let mut b = a.clone();
    b.inc(2, 4);
    a.inc(1, 1);
    a.merge(&b);
    b.merge(&a);
    assert_eq!((a.value(), b.value()), (7, 7));
    assert_eq!(a, b);
}

#[test]
fn s0d_c4_updates_made_after_a_merge_are_not_lost_by_the_next_one() {
    let mut a = counter(&[(1, true, 2)]);
    let mut b = a.clone();
    b.inc(2, 4);
    a.inc(1, 1);
    a.merge(&b);
    b.merge(&a);
    assert_eq!((a.value(), b.value()), (7, 7));
    assert_eq!(a, b);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: merge is commutative, associative and idempotent, and replicas that exchange everything agree.
    #[test]
    fn s0d_c4_property_the_three_laws(a in proptest::collection::vec((0u32..3, any::<bool>(), 0u64..9), 0..8), b in proptest::collection::vec((0u32..3, any::<bool>(), 0u64..9), 0..8), c in proptest::collection::vec((0u32..3, any::<bool>(), 0u64..9), 0..8)) {
        let (a, b, c) = (counter(&a), counter(&b), counter(&c));
        let merged = |x: &PnCounter, y: &PnCounter| { let mut m = x.clone(); m.merge(y); m };
        prop_assert_eq!(merged(&a, &b), merged(&b, &a));
        prop_assert_eq!(merged(&merged(&a, &b), &c), merged(&a, &merged(&b, &c)));
        prop_assert_eq!(merged(&a, &a), a.clone());
        let all = merged(&merged(&a, &b), &c);
        prop_assert_eq!(merged(&all, &a), all);
    }
}
''')))

CH.append(C("0d-c5", M0D, "94-challenge-merging-registers", "debug", "Challenge: merging registers", "easy", "stages_0d::s0d_c5",
  ["finding a merge that adds where it should take the maximum","testing the CRDT laws to catch it"],
  ["hyperloglog-and-distinct-counting","crdts-and-observed-remove-sets","property-testing-and-fuzzing"],
  "`src/primer/hll_registers.rs` holds the registers of a HyperLogLog sketch and merges two sketches built over different parts of a stream, so that the merged sketch estimates the union. It looks right, and merging a sketch with itself changes it. Find the bug and fix it.",
  "A sketch you can merge is a CRDT: the merged value must be the same however the data was split and however often the parts are combined. That holds only if the merge is **idempotent**, and the one-word difference between \"take the larger register\" and \"add the registers\" is the difference between a sketch of the union and a number that grows every time two replicas talk.",
  ["`update(hash)` sets the register chosen by the top `bits` bits of the hash to `max(register, rank)` where `rank` is one more than the number of leading zeros of the remaining bits.","`merge(&other)`: register-wise **maximum**, for sketches of the same size (else `Err`)."],
  ["Every register is the largest rank ever seen for it.","Registers never decrease."],
  ["`merge(a, a) == a` (idempotent).","`merge(a, b) == merge(b, a)` and `merge(merge(a, b), c) == merge(a, merge(b, c))`.","The sketch of a stream equals the merge of the sketches of any split of it."],
  ["a registers [1,0,3,0], b [0,2,3,0] -> merged [1,2,3,0]"],
  ["Register-wise maximum.","The three laws.","Split-stream equality."],
  src=("src/primer/hll_registers.rs", '''
//! The registers of a HyperLogLog sketch, and merging them.

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Registers {
    bits: u32,
    regs: Vec<u8>,
}

#[derive(Debug, PartialEq, Eq)]
pub struct SizeMismatch;

impl Registers {
    /// `2^bits` registers, `bits` in `1..=16`.
    pub fn new(bits: u32) -> Registers {
        let bits = bits.clamp(1, 16);
        Registers { bits, regs: vec![0; 1 << bits] }
    }

    /// Records one hashed element.
    pub fn update(&mut self, hash: u64) {
        let idx = (hash >> (64 - self.bits)) as usize;
        let rest = hash << self.bits;
        let rank = (rest.leading_zeros().min(64 - self.bits) + 1) as u8;
        self.regs[idx] = self.regs[idx].max(rank);
    }

    pub fn registers(&self) -> &[u8] {
        &self.regs
    }

    /// Absorbs another sketch of the same size.
    pub fn merge(&mut self, other: &Registers) -> Result<(), SizeMismatch> {
        if self.bits != other.bits {
            return Err(SizeMismatch);
        }
        for (a, b) in self.regs.iter_mut().zip(&other.regs) {
            // @begin 0d-c5
            *a = (*a).max(*b);
            //~ *a = a.saturating_add(*b);
            // @end
        }
        Ok(())
    }
}
'''),
  test=("tests/stages_0d.rs", '''
use bustub::primer::hll_registers::{Registers, SizeMismatch};

fn sketch(hashes: &[u64]) -> Registers {
    let mut r = Registers::new(4);
    for &h in hashes {
        r.update(h);
    }
    r
}

fn mix(i: u64) -> u64 {
    let mut x = i.wrapping_mul(0x9E37_79B9_7F4A_7C15);
    x ^= x >> 29;
    x = x.wrapping_mul(0xBF58_476D_1CE4_E5B9);
    x ^ (x >> 32)
}

#[test]
fn s0d_c5_merging_takes_the_larger_register_not_the_sum() {
    let a = sketch(&[mix(1), mix(2), mix(3)]);
    let mut b = a.clone();
    b.merge(&a).unwrap();
    assert_eq!(b, a, "merging a sketch with itself changes nothing");
}

#[test]
fn s0d_c5_registers_of_two_sketches_combine_by_maximum() {
    let a = sketch(&(0..20).map(mix).collect::<Vec<_>>());
    let b = sketch(&(10..40).map(mix).collect::<Vec<_>>());
    let mut m = a.clone();
    m.merge(&b).unwrap();
    for i in 0..16 {
        assert_eq!(m.registers()[i], a.registers()[i].max(b.registers()[i]));
    }
}

#[test]
fn s0d_c5_the_sketch_of_a_stream_is_the_merge_of_the_sketches_of_its_parts() {
    let all: Vec<u64> = (0..200).map(mix).collect();
    let whole = sketch(&all);
    let mut parts = sketch(&all[..70]);
    parts.merge(&sketch(&all[70..])).unwrap();
    assert_eq!(parts, whole);
    let mut again = parts.clone();
    again.merge(&sketch(&all[..70])).unwrap();
    assert_eq!(again, whole, "merging in a part that was already included changes nothing");
}

#[test]
fn s0d_c5_sketches_of_different_sizes_do_not_merge() {
    let mut a = Registers::new(4);
    assert_eq!(a.merge(&Registers::new(5)), Err(SizeMismatch));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the three laws, and the split-stream equality, for arbitrary hashes.
    #[test]
    fn s0d_c5_property_merge_is_a_semilattice(a in proptest::collection::vec(any::<u64>(), 0..30), b in proptest::collection::vec(any::<u64>(), 0..30), c in proptest::collection::vec(any::<u64>(), 0..30)) {
        let (sa, sb, sc) = (sketch(&a), sketch(&b), sketch(&c));
        let m = |x: &Registers, y: &Registers| { let mut r = x.clone(); r.merge(y).unwrap(); r };
        prop_assert_eq!(m(&sa, &sb), m(&sb, &sa));
        prop_assert_eq!(m(&m(&sa, &sb), &sc), m(&sa, &m(&sb, &sc)));
        prop_assert_eq!(m(&sa, &sa), sa.clone());
        let mut joined = a.clone();
        joined.extend(&b);
        prop_assert_eq!(m(&sa, &sb), sketch(&joined));
    }
}
''')))
