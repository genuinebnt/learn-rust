**Where this fits.** How a hash picks a slot, and which slot is a bucket's sibling.

## The task

In `src/storage/page/extendible_htable_directory_page.rs`:
- `get_global_depth_mask()`: `global_depth` one-bits from the low end (`0b111` for depth 3); `get_local_depth_mask(idx)`: the same for slot `idx`'s local depth;
- `hash_to_bucket_index(hash)`: `hash & global_depth_mask`;
- `get_split_image_index(idx)`: the slot of the bucket this one splits from / merges with: flip bit `local_depth - 1` of `idx`. A bucket of local depth 0 has no sibling: return `idx` itself.

## Tests

- Depth 3: mask `0b111`; a slot of local depth 2: mask `0b11`; depth 0: mask 0 and every hash maps to slot 0.
- Global depth 2 maps `h` to `h % 4`. Split images: depth-1 slots 0 and 1 are each other's; depth-2 slot 5 (`101`) pairs with `111` = 7; depth-3 slot 3 pairs with 7; depth 0 is its own image.

## Syntax and methods

```rust
(1u32 << depth) - 1                                    // `depth` one-bits (fine for depth < 32)
bucket_idx ^ (1 << (depth - 1))                        // XOR flips one bit
```

## Notes

**Why flip bit `d - 1`?** A bucket of local depth `d` is identified by the low `d` bits of its slots' indexes. It came into being when a depth-`d-1` bucket split on bit `d - 1` (counting from 0), so its sibling is the slot that agrees on the lower `d - 1` bits and differs in bit `d - 1`: `idx ^ (1 << (d - 1))`. Draw the depth-2 directory (slots 00, 01, 10, 11) once and the rule is obvious: slot 01 and slot 11 are siblings at depth 2; if those two later merge into one depth-1 bucket, slot 1's sibling is slot 0.

## In BusTub

"GetGlobalDepthMask - returns a mask of global_depth 1's and the rest 0's ... DirectoryIndex = Hash(key) & GLOBAL_DEPTH_MASK". (`GetSplitImageIndex` has no comment: you derive it.)

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `(1 << depth) - 1` with `int`: `1 << 31` is UB in C++ before C++20, and `depth == 32` is UB | `1u32 << depth` is fine below 32; a shift of 32 panics in debug builds |
| `~(~0u << depth)` mask idiom | `(1u32 << depth) - 1`, or `u32::MAX >> (32 - depth)` (careful at depth 0) |
| `hash & mask` | the same |
| `x ^ (1u << k)` flip a bit | the same; `x ^= 1 << k` |

## Learn more
- [Bit manipulation in Rust's integer docs](https://doc.rust-lang.org/std/primitive.u32.html) (`count_ones`, `leading_zeros`, `trailing_zeros`, `rotate_left`) · CMU 15-445 "Hash Tables" (extendible hashing: the directory)
