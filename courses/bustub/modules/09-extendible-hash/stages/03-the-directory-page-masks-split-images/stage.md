The directory page is the middle level: it maps the **low `global_depth` bits** of a hash to a bucket page, and records each bucket's **local depth**. This stage builds its accessors and its three pieces of bit arithmetic: the global and local **masks**, `hash_to_bucket_index`, and the **split image** of a slot (the slot that differs only in the bit a split would add).

It is the first place the table's invariants appear in code: local depth never exceeds global depth, and two slots that share a bucket share its depth.

## Part 1 · The directory page: init and accessors

**Where this fits.** The middle level. A directory has `2^global_depth` slots; slot `hash & mask` holds a bucket's page id, and each slot records the **local depth** of its bucket (how many hash bits that bucket actually distinguishes). Many slots can share a bucket: when a bucket has local depth `d` and the directory has global depth `g`, exactly `2^(g-d)` slots point at it.

### The task

In `src/storage/page/extendible_htable_directory_page.rs` (`| max_depth u32 | global_depth u32 | local_depths [u8; 512] | bucket_page_ids [i32; 512] |`), implement:
- `init(max_depth)`: panic ("does not fit") above 9; store the max depth, global depth 0, zero every local depth, set every bucket slot to `INVALID`;
- `get_max_depth`, `get_global_depth`, `size()` (`2^global`), `max_size()` (`2^max`);
- `get_bucket_page_id(idx)` / `set_bucket_page_id(idx, id)` and `get_local_depth(idx)`: panic ("out of range") for `idx >= max_size`.

### Tests

- A fresh directory: depths (max 3, global 0), size 1, max size 8, slot 0 `INVALID` with depth 0. Init overwrites garbage. Ids are stored per slot; the bytes match BusTub's layout (bucket ids from byte 520); out-of-range and over-deep panic.

### Syntax and methods

```rust
page[DIRECTORY_LOCAL_DEPTHS_OFFSET..DIRECTORY_LOCAL_DEPTHS_OFFSET + 512].fill(0);       // slice::fill
self.page.as_ref()[DIRECTORY_LOCAL_DEPTHS_OFFSET + bucket_idx as usize] as u32          // a u8 field
1u32 << self.get_global_depth()                                                         // size = 2^global
```

### Notes

The bounds check is against `max_size`, not `size`: slots beyond the current size are *reserved* (the directory will grow into them), and `set_bucket_page_id(5, ..)` on a depth-2 directory is a bug the page can't detect on its own. The table keeps to `size()`; the page guards its memory.

### In BusTub

```cpp
class ExtendibleHTableDirectoryPage { uint32_t max_depth_; uint32_t global_depth_; uint8_t local_depths_[512]; page_id_t bucket_page_ids_[512]; };
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `uint8_t local_depths_[512]` read as `local_depths_[i]` (an `int` promotion) | a byte at an offset, `as u32` |
| `(1 << global_depth_)` with `int`: overflows at 31 | `1u32 << depth` (depth ≤ 9 here) |
| `std::fill_n` / `memset` | `slice.fill(0)` |
| `assert(...)` compiled out by `NDEBUG` | `assert!` always on (`debug_assert!` for debug-only) |

### Learn more
- BusTub [extendible_htable_directory_page.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/page/extendible_htable_directory_page.h) · [`slice::fill`](https://doc.rust-lang.org/std/primitive.slice.html#method.fill) · [Extendible hashing](https://en.wikipedia.org/wiki/Extendible_hashing)

## Part 2 · Masks, hash_to_bucket_index and the split image

**Where this fits.** How a hash picks a slot, and which slot is a bucket's sibling.

### The task

In `src/storage/page/extendible_htable_directory_page.rs`:
- `get_global_depth_mask()`: `global_depth` one-bits from the low end (`0b111` for depth 3); `get_local_depth_mask(idx)`: the same for slot `idx`'s local depth;
- `hash_to_bucket_index(hash)`: `hash & global_depth_mask`;
- `get_split_image_index(idx)`: the slot of the bucket this one splits from / merges with: flip bit `local_depth - 1` of `idx`. A bucket of local depth 0 has no sibling: return `idx` itself.

### Tests

- Depth 3: mask `0b111`; a slot of local depth 2: mask `0b11`; depth 0: mask 0 and every hash maps to slot 0.
- Global depth 2 maps `h` to `h % 4`. Split images: depth-1 slots 0 and 1 are each other's; depth-2 slot 5 (`101`) pairs with `111` = 7; depth-3 slot 3 pairs with 7; depth 0 is its own image.

### Syntax and methods

```rust
(1u32 << depth) - 1                                    // `depth` one-bits (fine for depth < 32)
bucket_idx ^ (1 << (depth - 1))                        // XOR flips one bit
```

### Notes

**Why flip bit `d - 1`?** A bucket of local depth `d` is identified by the low `d` bits of its slots' indexes. It came into being when a depth-`d-1` bucket split on bit `d - 1` (counting from 0), so its sibling is the slot that agrees on the lower `d - 1` bits and differs in bit `d - 1`: `idx ^ (1 << (d - 1))`. Draw the depth-2 directory (slots 00, 01, 10, 11) once and the rule is obvious: slot 01 and slot 11 are siblings at depth 2; if those two later merge into one depth-1 bucket, slot 1's sibling is slot 0.

### In BusTub

"GetGlobalDepthMask - returns a mask of global_depth 1's and the rest 0's ... DirectoryIndex = Hash(key) & GLOBAL_DEPTH_MASK". (`GetSplitImageIndex` has no comment: you derive it.)

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `(1 << depth) - 1` with `int`: `1 << 31` is UB in C++ before C++20, and `depth == 32` is UB | `1u32 << depth` is fine below 32; a shift of 32 panics in debug builds |
| `~(~0u << depth)` mask idiom | `(1u32 << depth) - 1`, or `u32::MAX >> (32 - depth)` (careful at depth 0) |
| `hash & mask` | the same |
| `x ^ (1u << k)` flip a bit | the same; `x ^= 1 << k` |

### Learn more
- [Bit manipulation in Rust's integer docs](https://doc.rust-lang.org/std/primitive.u32.html) (`count_ones`, `leading_zeros`, `trailing_zeros`, `rotate_left`) · CMU 15-445 "Hash Tables" (extendible hashing: the directory)

## Part 3 · Local depths: set, incr, decr

**Where this fits.** A bucket's local depth changes when it splits (+1) or merges (-1).

### The task

In `src/storage/page/extendible_htable_directory_page.rs`:
- `set_local_depth(idx, depth)`: panic ("out of range") for a slot at or past `max_size`, and panic ("max depth") for a depth above the directory's max depth; store the byte;
- `incr_local_depth(idx)`: +1, panic ("max depth") if already at the max depth;
- `decr_local_depth(idx)`: -1, panic ("already 0") at 0.

### Tests

- Set and read at slots 3 and 15; incr/decr move one step and leave other slots alone; the three panics.

### Syntax and methods

```rust
self.page.as_mut()[DIRECTORY_LOCAL_DEPTHS_OFFSET + idx as usize] = local_depth;
```

### Notes

The directory page does not know *which bucket* a slot's depth belongs to, and so `incr_local_depth(5)` changes slot 5 only; if slots 1, 3, 5 share a bucket, the **table** must update all three. That bookkeeping is stage 18 (split) and 20 (merge): the page is deliberately dumb.

### In BusTub

```cpp
void IncrLocalDepth(uint32_t bucket_idx);  void DecrLocalDepth(uint32_t bucket_idx);  void SetLocalDepth(uint32_t bucket_idx, uint8_t local_depth);
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `uint8_t depth = ...; depth - 1` promotes to `int` (so `0 - 1 == -1`, then narrowed back to 255 on store) | `u8` arithmetic overflows loudly; the asserts catch the 0 case first |
| `BUSTUB_ASSERT(local_depths_[idx] > 0, ...)` | `assert!(depth > 0, "local depth is already 0")` |
| `static_cast<uint8_t>(x)` | `x as u8` (truncating, so check range first) |

### Learn more
- [Integer overflow](https://doc.rust-lang.org/book/ch03-02-data-types.html#integer-overflow) · BusTub [extendible_htable_directory_page.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/page/extendible_htable_directory_page.h)

## Performance

All operations are O(1) bit arithmetic on integers read from the page: a mask is `(1 << k) - 1`, an index is `hash & mask`, a split image is one xor. The cost to be aware of is **page size**, not instructions: a directory page holds 512 bucket ids (2 KiB) plus 512 depth bytes (512 B), about 2.5 KiB of the 8 KiB page. That is the **ceiling of the table**: global depth 9 means 512 buckets per directory, and `header_max_depth` directories multiply it.

Reading a directory is one page read; the bucket id lookup is an array index, so the whole directory level of a lookup is a few nanoseconds once the page is in memory.

**Measure it.** Print the number of keys one directory can address at depth 9 with a bucket of 511 entries (8-byte keys and `Rid` values: 512 x 511 = 261 632) and with 512 header slots (about 134 million). Time 100 million `hash_to_bucket_index` calls and confirm it is a mask and a load.

## Hints

### Which bits does a bucket of local depth d actually look at?

The **low `d` bits** of the hash. A bucket pointed to by several directory slots (because its local depth is below the global depth) is the same bucket for every slot that agrees on those `d` bits; the other `global - d` bits are *don't care*. Write the masks as functions of the depths and test the table of cases: global 3 and local 1 means slots 000, 010, 100 and 110 share a bucket.

### The split image is not "the next slot"

The bucket you would merge with is the one that differs in exactly **bit `d - 1`** of the index (where `d` is the local depth), so `i ^ (1 << (d - 1))`. At local depth 0 there is no such bit: the bucket has no sibling and is its own image (a shift of `-1` would underflow). Hand-check three cases on paper: slots 0 and 1 at depth 1, slots 1 and 3 at depth 2, slots 5 and 1 at depth 3.

### `set_local_depth` is not free-form

A local depth above the global depth, or above the maximum, breaks the structure the directory describes. Decide whether the *setter* enforces that (a panic with a message) or whether the *caller* must (and `verify_integrity` later catches a violation); in either case the failing message should name the slot and both depths. The next stage's growth and shrink rely on these being right.
