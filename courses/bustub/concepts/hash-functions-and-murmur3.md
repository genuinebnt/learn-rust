---
title: Hash functions and MurmurHash3
summary: What a good hash must do, how a 128-bit multiply-rotate-xor hash like MurmurHash3 achieves it, why you port it against golden values from the C++, and the wrapping arithmetic that makes the port exact.
minutes: 10
---
An extendible hash table is only as good as its hash: if it sends many keys to the same low bits, one bucket overflows and the directory doubles for nothing. BusTub uses **MurmurHash3** (Austin Appleby, public domain), and this course asks you to port it bit for bit.

## What a hash function must do

| property | meaning | why the table needs it |
|---|---|---|
| **deterministic** | the same bytes always give the same hash | the key must be found where it was put |
| **uniform** | outputs spread evenly over the range | buckets fill evenly |
| **avalanche** | flipping one input bit flips about half the output bits | similar keys (1, 2, 3, ...) must not land in neighbouring buckets |
| **fast** | a few cycles per byte | it runs on every operation |
| *not* cryptographic | no need to resist attackers | but then do not use it on untrusted keys without a seed (hash-flooding) |

The identity "hash" (`hash(k) = k`) is deterministic and fast and **fails uniformity and avalanche** for sequential keys: with the low bits as the directory index, keys 0 to 511 fill 512 distinct slots in order, and a stride-512 key pattern lands all in slot 0.

## The shape of MurmurHash3 (x64, 128-bit)

The input is processed in **16-byte blocks**; each block is mixed into two 64-bit lanes `h1`, `h2` with the same three moves:

1. **multiply** by a large odd constant (spreads each bit's influence upward),
2. **rotate** left (moves the high bits, which multiplication cannot reach downward, back to the bottom),
3. **xor** into the running state, then mix the two lanes together.

A final **`fmix64`** step (xor-shift-multiply, twice) forces the avalanche: every input bit affects every output bit. The last partial block (the *tail*, 1 to 15 bytes) is folded in byte by byte through a `match` on its length. BusTub takes **the first 64 bits** of the 128-bit result as the hash, then the table uses 32 of them.

```rust
h1 ^= k1.wrapping_mul(C1).rotate_left(31).wrapping_mul(C2);     // mix a block's first lane
h1 = h1.rotate_left(27).wrapping_add(h2).wrapping_mul(5).wrapping_add(0x52dce729);
```

## Porting traps

- **Wrapping arithmetic.** The algorithm is defined modulo 2<sup>64</sup>. In C unsigned overflow wraps silently; in Rust a plain `*` or `+` **panics in debug**. Every multiply and add in the port must be `wrapping_mul` / `wrapping_add`, or the first input long enough to overflow aborts your test.
- **Rotations**: `rotate_left(r)` exists; C writes `(x << r) | (x >> (64 - r))`, which is undefined for `r = 0` (a shift of 64): another face of the full-width edge.
- **Reading a block**: `u64::from_le_bytes(chunk.try_into().unwrap())`. The C reads through a `uint64_t*` cast: on a big-endian machine the hash would differ, so a *portable* hash fixes the byte order, as the port does.
- **The tail**: C uses a `switch` with deliberate fall-through; Rust's `match` has none, so the tail is built by `for` over the remaining bytes, shifting each into place.

## Test against the original

A ported hash that is *almost* right is useless: it still hashes, still distributes, and silently disagrees with every file the C++ wrote. The only convincing test is **golden values**: compile the C++ `MurmurHash3_x64_128`, hash a set of inputs (empty, 1 byte, 15, 16, 17 bytes, a long string, several seeds), and put the outputs in the test. The stage's tests do exactly that.

| input length | exercises |
|---|---|
| 0 | the finalisation only |
| 1 to 15 | each case of the tail `match` |
| 16 | exactly one block, no tail |
| 17 and more | a block then a tail |

> [!WHY] Why not use `std`'s hasher?
> `HashMap`'s default `RandomState` is seeded randomly per process, and `DefaultHasher` makes no promise to stay the same between Rust versions: a key's hash could change between runs, so a page written yesterday could not be read today. A hash that determines **on-disk placement** must be stable across runs, machines and versions of your code: it is part of the file format.

## In real code

### The API you will use

| call | what it does | when |
|---|---|---|
| `x.wrapping_mul(c)` / `wrapping_add` | arithmetic modulo 2<sup>64</sup> | every step of a hash |
| `x.rotate_left(r)` | rotate | mixing bits |
| `x ^ (x >> 33)` | xor-shift | finalisation (`fmix64`) |
| `u64::from_le_bytes(chunk.try_into().unwrap())` | read a block | the input loop |
| `bytes.chunks_exact(16)` / `.remainder()` | full 16-byte blocks and the leftover tail | block/tail split |
| `std::hash::{Hash, Hasher}` | the trait for hashing any type (and `DefaultHasher`: SipHash, not stable across Rust versions) | in-memory maps only |
| a golden-value test | `assert_eq!(hash(b"abc"), 0x...)` from the C++ | proving a port |

```rust test
const C1: u64 = 0x87c3_7b91_1142_53d5;
const C2: u64 = 0x4cf5_ad43_2745_937f;

fn fmix64(mut k: u64) -> u64 {
    k ^= k >> 33;
    k = k.wrapping_mul(0xff51_afd7_ed55_8ccd);
    k ^= k >> 33;
    k = k.wrapping_mul(0xc4ce_b9fe_1a85_ec53);
    k ^ (k >> 33)
}

/// The shape of MurmurHash3's block loop for one 16-byte block (the real function adds the tail and the final mix of two lanes).
fn mix_block(h1: u64, h2: u64, block: &[u8; 16]) -> (u64, u64) {
    let k1 = u64::from_le_bytes(block[..8].try_into().unwrap());
    let k2 = u64::from_le_bytes(block[8..].try_into().unwrap());
    let h1 = (h1 ^ k1.wrapping_mul(C1).rotate_left(31).wrapping_mul(C2)).rotate_left(27).wrapping_add(h2).wrapping_mul(5).wrapping_add(0x52dc_e729);
    let h2 = (h2 ^ k2.wrapping_mul(C2).rotate_left(33).wrapping_mul(C1)).rotate_left(31).wrapping_add(h1).wrapping_mul(5).wrapping_add(0x3849_5ab5);
    (h1, h2)
}

#[test]
fn avalanche_flipping_one_input_bit_changes_about_half_the_output() {
    let base = fmix64(0x1234_5678);
    let mut total = 0;
    for bit in 0..32 {
        total += (base ^ fmix64(0x1234_5678 ^ (1 << bit))).count_ones();
    }
    let avg = total as f64 / 32.0;
    assert!(avg > 24.0 && avg < 40.0, "average flipped output bits: {avg}");      // 32 of 64 is the ideal
}

#[test]
fn blocks_and_tails() {
    let data = [7u8; 37];
    let chunks = data.chunks_exact(16);
    assert_eq!(chunks.len(), 2);                                 // two full blocks...
    assert_eq!(chunks.remainder().len(), 5);                      // ...and a 5-byte tail
    let (a, b) = mix_block(0, 0, data[..16].try_into().unwrap());
    assert_ne!((a, b), (0, 0));
}
```

```rust test
const BUCKETS: usize = 64;

fn fmix64(mut k: u64) -> u64 {
    k ^= k >> 33; k = k.wrapping_mul(0xff51_afd7_ed55_8ccd); k ^= k >> 33; k = k.wrapping_mul(0xc4ce_b9fe_1a85_ec53); k ^ (k >> 33)
}

#[test]
fn sequential_keys_spread_over_the_low_bits() {
    let mut counts = [0usize; BUCKETS];
    for key in 0..64_000u64 {
        counts[(fmix64(key) as usize) & (BUCKETS - 1)] += 1;      // the directory index: the LOW bits of the hash
    }
    let (min, max) = (counts.iter().min().unwrap(), counts.iter().max().unwrap());
    assert!(*max < 1100 && *min > 900, "min {min}, max {max} (ideal 1000)");

    // The identity "hash" does not:
    let mut ident = [0usize; BUCKETS];
    for key in (0..64_000u64).step_by(64) {
        ident[(key as usize) & (BUCKETS - 1)] += 1;               // stride-64 keys all land in bucket 0
    }
    assert_eq!(ident[0], 1000);
}
```

### In the exercises

- **2b-01:** port `MurmurHash3_x64_128` completely: the block loop (`chunks_exact(16)`), the tail (a loop over `remainder()`), and the finalisation with `fmix64`. Every `*` and `+` is `wrapping_*`. The stage's golden values come from compiling the C++; test lengths 0, 1, 15, 16, 17 and a long input.
- **2b-02:** `HashFunction::get_hash(&key)` encodes the key to bytes (`FixedSize::encode`) and takes the first 64-bit lane of the 128-bit result.

### Where it is used

- **Hash tables and partitioning**: Cassandra (`Murmur3Partitioner`) and Kafka's default partitioner (the murmur2 variant) place keys with MurmurHash; PostgreSQL uses its own `hash_bytes` (Bob Jenkins' lookup3).
- **Bloom filters and sketches**: two Murmur hashes generate all `k` filter positions (double hashing).
- **Why not SipHash or SHA-256?** SipHash resists hash-flooding of untrusted keys (Rust's default); SHA is cryptographic and far slower. A database hashing its own keys wants speed and a **stable** result: placement is on disk.
