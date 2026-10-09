//! Port of `src/include/primer/hyperloglog.h` / `hyperloglog_presto.h` and their `.cpp` files: **HyperLogLog** estimates how many
//! *distinct* items a stream contains, in a few kilobytes. Hash every item to 64 bits. The first `b` bits pick one of `m = 2^b`
//! registers; in the other bits, the run of zeros ahead of the first (or after the last) 1 bit is rare: a run of `r` happens with
//! probability `2^-r`, so seeing run length `r` suggests about `2^r` distinct items went by. Each register keeps the longest run it has
//! seen, and the registers' estimates are combined with a harmonic mean, which resists one lucky register.

use std::collections::hash_map::DefaultHasher;
use std::collections::HashMap;
use std::hash::{Hash, Hasher};
use std::marker::PhantomData;
use std::sync::Mutex;

/// The bias correction of the estimator used by the course.
const CONSTANT: f64 = 0.79402;

/// A 64-bit hash with well-mixed bits (given): `DefaultHasher`, then a final avalanche so that every bit position is usable.
fn hash64<K: Hash>(val: &K) -> u64 {
    let mut hasher = DefaultHasher::new();
    val.hash(&mut hasher);
    let mut h = hasher.finish();
    h ^= h >> 30;
    h = h.wrapping_mul(0xbf58_476d_1ce4_e5b9);
    h ^= h >> 27;
    h = h.wrapping_mul(0x94d0_49bb_1331_11eb);
    h ^ (h >> 31)
}

/// The estimate from the registers: `CONSTANT * m^2 / sum(2^-register)`, rounded down. No registers: 0.
fn estimate(registers: impl Iterator<Item = u32>, m: usize) -> u64 {
    if m == 0 {
        return 0;
    }
    let sum: f64 = registers.map(|r| 2f64.powi(-(r as i32))).sum();
    (CONSTANT * (m as f64) * (m as f64) / sum) as u64
}

pub struct HyperLogLog<K> {
    n_bits: i16,
    registers: Mutex<Vec<u8>>,
    cardinality: Mutex<u64>,
    _key: PhantomData<fn(&K)>,
}

impl<K: Hash> HyperLogLog<K> {
    /// A sketch with `2^n_bits` registers. A negative `n_bits` gives no registers (cardinality 0 forever).
    pub fn new(n_bits: i16) -> HyperLogLog<K> {
        let m = if n_bits < 0 { 0 } else { 1usize << n_bits };
        HyperLogLog { n_bits, registers: Mutex::new(vec![0; m]), cardinality: Mutex::new(0), _key: PhantomData }
    }

    /// The last estimate (see `compute_cardinality`).
    pub fn cardinality(&self) -> u64 {
        *self.cardinality.lock().unwrap()
    }

    /// The registers (given; for tests): the longest run seen in each.
    pub fn registers(&self) -> Vec<u8> {
        self.registers.lock().unwrap().clone()
    }

    /// The register a hash belongs to: its first `n_bits` bits.
    pub fn register_index(&self, hash: u64) -> usize {
        todo!("0d-03: the top n_bits bits of the hash as a number (0 when n_bits is 0)")
    }

    /// The run length of the hash: the **position of the leftmost 1** among the 64 - n_bits bits after the register bits, counted from 1.
    /// All zeros: `64 - n_bits + 1`.
    pub fn position_of_leftmost_one(&self, hash: u64) -> u8 {
        todo!("0d-03: drop the first n_bits bits (shift left), count the leading zeros of what is left (at most 64 - n_bits), plus one")
    }

    /// Takes `val` into account.
    pub fn add_elem(&self, val: &K) {
        todo!("0d-03: hash the value; the register is register_index; keep the larger of its value and position_of_leftmost_one (under the lock; do nothing if there are no registers)")
    }

    /// Recomputes the estimate from the registers and stores it.
    pub fn compute_cardinality(&self) {
        todo!("0d-04: CONSTANT * m * m / the sum of 2^-register over the registers, rounded down; 0 with no registers; store it")
    }
}

/// HyperLogLog as Presto stores it: the run length is the number of **trailing** zeros of the bits after the register bits, and a
/// register keeps its low 4 bits in a dense array and the rest (up to 3 bits) in a sparse overflow map, since most registers stay small.
pub struct HyperLogLogPresto<K> {
    n_leading_bits: i16,
    /// Low 4 bits of each register.
    dense: Mutex<Vec<u8>>,
    /// Bits 4 to 6 of the registers that need them.
    overflow: Mutex<HashMap<u16, u8>>,
    cardinality: Mutex<u64>,
    _key: PhantomData<fn(&K)>,
}

/// The hash Presto's sketch uses for a key (given): integers hash to themselves, so tests can pick the bits; anything else is hashed.
pub trait PrestoHash {
    fn presto_hash(&self) -> u64;
}

impl PrestoHash for i64 {
    fn presto_hash(&self) -> u64 {
        *self as u64
    }
}

impl PrestoHash for String {
    fn presto_hash(&self) -> u64 {
        hash64(self)
    }
}

impl<K: PrestoHash> HyperLogLogPresto<K> {
    pub fn new(n_leading_bits: i16) -> HyperLogLogPresto<K> {
        let m = if n_leading_bits < 0 { 0 } else { 1usize << n_leading_bits };
        HyperLogLogPresto { n_leading_bits, dense: Mutex::new(vec![0; m]), overflow: Mutex::new(HashMap::new()), cardinality: Mutex::new(0), _key: PhantomData }
    }

    pub fn cardinality(&self) -> u64 {
        *self.cardinality.lock().unwrap()
    }

    /// The dense array: the low 4 bits of every register.
    pub fn dense_bucket(&self) -> Vec<u8> {
        self.dense.lock().unwrap().clone()
    }

    /// The overflow bits (bits 4 to 6) of register `idx`; 0 if it has none.
    pub fn overflow_bucket_of(&self, idx: u16) -> u8 {
        self.overflow.lock().unwrap().get(&idx).copied().unwrap_or(0)
    }

    /// The whole value of register `idx`: dense bits plus overflow bits shifted in above them.
    fn register(&self, idx: usize) -> u32 {
        (self.dense.lock().unwrap()[idx] as u32) | ((self.overflow_bucket_of(idx as u16) as u32) << 4)
    }

    pub fn add_elem(&self, val: &K) {
        todo!("0d-05: the register is the top n bits of the hash; its run is the trailing zeros of the other 64 - n bits (all zero: 64 - n); if larger than the register's value store the low 4 bits densely and bits 4 to 6 in the overflow map")
    }

    pub fn compute_cardinality(&self) {
        todo!("0d-05: the same estimate as HyperLogLog, over the registers rebuilt from dense and overflow bits")
    }
}
