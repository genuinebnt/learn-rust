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
