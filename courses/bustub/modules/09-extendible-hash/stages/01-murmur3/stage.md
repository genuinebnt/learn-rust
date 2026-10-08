**Where this fits.** A hash table is only as good as its hash. BusTub hashes every index key with **MurmurHash3**, and its tests are written against that function's output: to run them, you need the same function bit for bit. This stage is a small, classic C-to-Rust port: integer arithmetic that wraps, rotations, a loop over 16-byte blocks, and a `switch` that falls through.

## The task

In `src/container/hash/murmur3.rs` implement `murmur_hash3_x64_128(data: &[u8], seed: u32) -> [u64; 2]` (`fmix64` is given). The algorithm, from BusTub's `third_party/murmur3/MurmurHash3.cpp`:

```cpp
h1 = seed; h2 = seed;  c1 = 0x87c37b91114253d5;  c2 = 0x4cf5ad432745937f;
for each 16-byte block (k1 = first 8 bytes, k2 = next 8, little-endian):
    k1 *= c1; k1 = rotl64(k1,31); k1 *= c2; h1 ^= k1;
    h1 = rotl64(h1,27); h1 += h2; h1 = h1*5 + 0x52dce729;
    k2 *= c2; k2 = rotl64(k2,33); k2 *= c1; h2 ^= k2;
    h2 = rotl64(h2,31); h2 += h1; h2 = h2*5 + 0x38495ab5;
tail = the remaining len % 16 bytes;  k1 = k2 = 0;
switch (len & 15)  // each case FALLS THROUGH to the next lower one
    case 15..9: k2 ^= tail[i] << (8*(i-8));   then (after case 9)  k2 *= c2; k2 = rotl64(k2,33); k2 *= c1; h2 ^= k2;
    case 8..1:  k1 ^= tail[i] << (8*i);       then (after case 1)  k1 *= c1; k1 = rotl64(k1,31); k1 *= c2; h1 ^= k1;
h1 ^= len; h2 ^= len;  h1 += h2; h2 += h1;  h1 = fmix(h1); h2 = fmix(h2);  h1 += h2; h2 += h1;
return {h1, h2};
```

## Tests

- The empty input hashes to `[0, 0]`. Inputs of 1..15 bytes (tail only), 16..40 bytes (blocks and tail), seeds 1, 42 and `u32::MAX`, and five well-known strings. **Every expected value was produced by compiling BusTub's own `MurmurHash3.cpp`** and printing its output: this is a *golden-value* test.

## Syntax and methods

```rust
k1 = k1.wrapping_mul(C1).rotate_left(31).wrapping_mul(C2);        // C's unsigned multiplication wraps; in Rust you must say so
for block in data.chunks_exact(16) { let k1 = u64::from_le_bytes(block[..8].try_into().unwrap()); .. }
let tail = data.chunks_exact(16).remainder();                     // the last len % 16 bytes
for (i, &byte) in tail.iter().enumerate().take(8) { k1 ^= (byte as u64) << (8 * i); }   // the fall-through switch is just "OR in each byte"
```

## Notes

**Fall-through `switch` becomes a loop.** The C code ORs tail byte `i` into `k1` (or `k2`) at shift `8*i` for every byte that exists, because case 15 falls through 14, 13, ...; the `switch` is only a way to run the right number of those statements. A loop over the tail bytes does the same, then the single multiply-rotate-multiply-XOR step that follows the last case runs *if the tail had any bytes for that half* (`k2` step: more than 8 tail bytes; `k1` step: at least one).

**Wrapping arithmetic.** In C, unsigned overflow wraps by definition. In Rust, `a * b` on `u64` panics on overflow in debug builds, so every hash step uses `wrapping_mul` / `wrapping_add`. This is the single most common bug when porting hash functions and PRNGs.

**Why test against the original.** A hash function can be "almost right" and still pass its own test. Compiling the C++ you are porting and recording its outputs is the strongest check there is. It is also how real migrations (a database, a codec, a protocol) are verified.

## In BusTub

`HashFunction<K>::GetHash` calls `murmur3::MurmurHash3_x64_128(&key, sizeof(KeyType), 0, &hash)` and returns `hash[0]`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `uint64_t x = a * b;` wraps silently | `a.wrapping_mul(b)` (or `*` and a debug-build panic if it overflows) |
| `(x << r) \| (x >> (64 - r))` (`rotl64`, also `_rotl64`, `std::rotl` in C++20) | `x.rotate_left(r)` |
| `const uint64_t *blocks = (const uint64_t *)data; blocks[i]`: unaligned and aliasing UB | `u64::from_le_bytes(block[..8].try_into().unwrap())` |
| `switch` with `// fallthrough` comments | a loop, or `match` arms that call a shared helper |
| `h1 ^= len;` mixing a `size_t`/`int` into a `uint64_t` | `h1 ^= len as u64;` |
| `memcpy(out, hash, 16)` of two `uint64_t` | return `[u64; 2]` |

**Port rule:** when you port a numeric algorithm, replace every `+ - *` on unsigned types by the `wrapping_*` method (the algorithm *relies* on wrap-around), and verify with golden values produced by the original.

## Learn more
- [`u64::rotate_left`](https://doc.rust-lang.org/std/primitive.u64.html#method.rotate_left) · [`wrapping_mul`](https://doc.rust-lang.org/std/primitive.u64.html#method.wrapping_mul) · [`chunks_exact`](https://doc.rust-lang.org/std/primitive.slice.html#method.chunks_exact) and [`remainder`](https://doc.rust-lang.org/std/slice/struct.ChunksExact.html#method.remainder)
- Austin Appleby's [MurmurHash3 notes](https://github.com/aappleby/smhasher/wiki/MurmurHash3) and [source](https://github.com/aappleby/smhasher/blob/master/src/MurmurHash3.cpp) · [`murmur3` crate](https://docs.rs/murmur3) · C++ [`[[fallthrough]]`](https://en.cppreference.com/w/cpp/language/attributes/fallthrough)
