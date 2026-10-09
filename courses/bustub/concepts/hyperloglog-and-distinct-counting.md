---
title: HyperLogLog: counting distinct items in a few kilobytes
summary: How the longest run of leading zeros in a hash estimates how many distinct values you have seen, why many registers and a harmonic mean make it accurate, and how Presto splits registers into dense and overflow parts.
minutes: 8
---
"How many **different** users visited today?" An exact answer needs to remember every user. **HyperLogLog** answers within a few percent using a few kilobytes, however many users there are, by watching something probabilistic about their hashes.

## The idea: rare patterns

Hash each item to 64 bits that look random. Half of the hashes start with `1`, a quarter with `01`, an eighth with `001`... A hash that starts with `r - 1` zeros and then a `1` has probability `2^-r`. If the longest such run you have seen is `r`, then you have probably looked at about `2^r` different values (the duplicates hash to the *same* bits, so they never add a new pattern). One estimate is noisy: a single lucky hash can claim a huge run.

## Many registers, a harmonic mean

Spread the items over `m = 2^b` **registers**. The first `b` bits of the hash choose the register; the position of the leftmost `1` in the other bits is the run length. Each register keeps the largest run it has seen. Every register is a tiny estimator for about `n/m` items. Combine them with a **harmonic mean**, which resists one huge outlier:

```text
estimate = constant × m² / Σ over registers of 2^(−register)
```

The relative error is about `1.04/√m`: 1024 registers (`b = 10`, 1 KB at one byte each, even less packed) give about 3%. An unseen register counts as 0, which contributes `2^0 = 1` to the sum, so an empty sketch estimates `constant × m`, a small bias the textbook corrects for small counts. The `constant` corrects a systematic bias in the harmonic-mean estimator; this course uses 0.79402 as BusTub does, which runs about 10% above the textbook value for large `m`.

```svg
caption: Four registers (b = 2). Each hash picks a register with its first two bits and updates it with the position of the first 1 in the rest. The sketch is just the four numbers.
<svg viewBox="0 0 760 150" role="img" aria-label="Hashes feeding four registers">
<text class="mid fg sm" x="130" y="30">hash 00|0001...  → register 0, position 4</text>
<text class="mid fg sm" x="130" y="58">hash 10|1...      → register 2, position 1</text>
<text class="mid fg sm" x="130" y="86">hash 10|00001...  → register 2, position 5</text>
<rect class="live" x="440" y="20" width="60" height="34"/><text class="mid fg" x="470" y="43">4</text>
<rect class="box" x="510" y="20" width="60" height="34"/><text class="mid dim" x="540" y="43">0</text>
<rect class="hot" x="580" y="20" width="60" height="34"/><text class="mid fg" x="610" y="43">5</text>
<rect class="box" x="650" y="20" width="60" height="34"/><text class="mid dim" x="680" y="43">0</text>
<text class="dim sm" x="470" y="70" style="text-anchor:middle">r0</text><text class="dim sm" x="540" y="70" style="text-anchor:middle">r1</text><text class="dim sm" x="610" y="70" style="text-anchor:middle">r2</text><text class="dim sm" x="680" y="70" style="text-anchor:middle">r3</text>
<text class="dim sm" x="380" y="130" style="text-anchor:middle">estimate = c·16 / (2^-4 + 2^0 + 2^-5 + 2^0)</text>
</svg>
```

## Presto's variant: dense and overflow buckets

Presto (the query engine) counts **trailing** zeros of the remaining bits instead, and stores each register in two parts: a 4-bit **dense** bucket holding the low four bits of the run length, and a sparse **overflow** map holding the higher bits (up to 3 bits) only for the registers that need them. Runs rarely exceed 15, so most registers need no overflow entry. The estimator is the same formula over the reassembled values. Because the run is counted as "number of trailing zeros" rather than "position of the first 1" (which is one more), its estimate is about half as large as the plain version's; it is a different, exactly specified design, which the course's tests pin down bit by bit.

## Thread safety and merging

The register update is "keep the maximum", which is why HyperLogLog sketches **merge** by taking the element-wise maximum, and why two threads updating the same register must not lose the larger value (a lock around the update, or a compare-and-swap loop).

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::bitset<64>` and a loop to find the leftmost one | a `u64`, `leading_zeros()` and `trailing_zeros()`, which compile to one instruction |
| `std::vector<std::bitset<4>>` | `Vec<u8>` holding values 0 to 15 |
| `std::unordered_map<uint16_t, std::bitset<3>>` | `HashMap<u16, u8>` |

**Port rule:** bit tricks on a `bitset` are integer operations; `leading_zeros` is the position of the leftmost one.

## In real code

### Using it: the register update and the estimate

```rust test
const CONSTANT: f64 = 0.79402;

struct Hll {
    bits: u32,
    registers: Vec<u8>,
}

impl Hll {
    fn new(bits: u32) -> Hll {
        Hll { bits, registers: vec![0; 1 << bits] }
    }
    fn add_hash(&mut self, hash: u64) {
        let index = if self.bits == 0 { 0 } else { (hash >> (64 - self.bits)) as usize };
        let rest = hash << self.bits;
        let rank = (rest.leading_zeros().min(64 - self.bits) + 1) as u8;
        self.registers[index] = self.registers[index].max(rank);
    }
    fn estimate(&self) -> u64 {
        let m = self.registers.len() as f64;
        let sum: f64 = self.registers.iter().map(|r| 2f64.powi(-(*r as i32))).sum();
        (CONSTANT * m * m / sum) as u64
    }
}

fn mix(mut x: u64) -> u64 {
    x ^= x >> 30;
    x = x.wrapping_mul(0xbf58476d1ce4e5b9);
    x ^= x >> 27;
    x = x.wrapping_mul(0x94d049bb133111eb);
    x ^ (x >> 31)
}

#[test]
fn repeated_values_do_not_move_the_estimate() {
    let mut h = Hll::new(6);
    for i in 0..1000u64 {
        h.add_hash(mix(i));
    }
    let once = h.estimate();
    for i in 0..1000u64 {
        h.add_hash(mix(i));
    }
    assert_eq!(h.estimate(), once);
}

#[test]
fn the_estimate_tracks_the_number_of_distinct_values() {
    let mut h = Hll::new(10);
    for i in 0..50_000u64 {
        h.add_hash(mix(i));
    }
    let ratio = h.estimate() as f64 / 50_000.0;
    assert!((0.95..1.3).contains(&ratio), "{ratio}");
}
```

### Using it: dense and overflow parts

```rust test
use std::collections::HashMap;

/// Stores run lengths up to 127: the low 4 bits densely, bits 4 to 6 only where nonzero.
struct Packed {
    dense: Vec<u8>,
    overflow: HashMap<usize, u8>,
}

impl Packed {
    fn new(n: usize) -> Packed {
        Packed { dense: vec![0; n], overflow: HashMap::new() }
    }
    fn set(&mut self, i: usize, v: u32) {
        self.dense[i] = (v & 0xF) as u8;
        match ((v >> 4) & 0x7) as u8 {
            0 => {
                self.overflow.remove(&i);
            }
            high => {
                self.overflow.insert(i, high);
            }
        }
    }
    fn get(&self, i: usize) -> u32 {
        self.dense[i] as u32 | ((self.overflow.get(&i).copied().unwrap_or(0) as u32) << 4)
    }
}

#[test]
fn small_values_need_no_overflow_entry() {
    let mut p = Packed::new(4);
    p.set(0, 9);
    assert_eq!((p.get(0), p.overflow.len()), (9, 0));
}

#[test]
fn big_values_split_in_two_and_come_back_whole() {
    let mut p = Packed::new(4);
    for v in [16, 18, 56, 63, 64] {
        p.set(1, v);
        assert_eq!(p.get(1), v);
    }
    p.set(1, 18);
    assert_eq!((p.dense[1], p.overflow[&1]), (2, 1));
}
```

### In the exercises

- **0d-02:** the register index and the position of the leftmost one; `add_elem`.
- **0d-02:** the estimate.
- **0d-03:** the Presto layout with trailing zeros, dense and overflow buckets.

### Where it is used

- **Redis** `PFADD` / `PFCOUNT`, **PostgreSQL** (the `postgresql-hll` extension), **BigQuery** `APPROX_COUNT_DISTINCT`, **Presto/Trino** `approx_distinct`, **Spark** `approx_count_distinct`.
- **Flajolet, Fusy, Gandouet, Meunier**, "HyperLogLog: the analysis of a near-optimal cardinality estimation algorithm" (2007); Google's HyperLogLog++ (2013) adds bias correction.
