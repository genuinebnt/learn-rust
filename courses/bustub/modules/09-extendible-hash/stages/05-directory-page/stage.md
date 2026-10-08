**Where this fits.** The middle level. A directory has `2^global_depth` slots; slot `hash & mask` holds a bucket's page id, and each slot records the **local depth** of its bucket (how many hash bits that bucket actually distinguishes). Many slots can share a bucket: when a bucket has local depth `d` and the directory has global depth `g`, exactly `2^(g-d)` slots point at it.

## The task

In `src/storage/page/extendible_htable_directory_page.rs` (`| max_depth u32 | global_depth u32 | local_depths [u8; 512] | bucket_page_ids [i32; 512] |`), implement:
- `init(max_depth)`: panic ("does not fit") above 9; store the max depth, global depth 0, zero every local depth, set every bucket slot to `INVALID`;
- `get_max_depth`, `get_global_depth`, `size()` (`2^global`), `max_size()` (`2^max`);
- `get_bucket_page_id(idx)` / `set_bucket_page_id(idx, id)` and `get_local_depth(idx)`: panic ("out of range") for `idx >= max_size`.

## Tests

- A fresh directory: depths (max 3, global 0), size 1, max size 8, slot 0 `INVALID` with depth 0. Init overwrites garbage. Ids are stored per slot; the bytes match BusTub's layout (bucket ids from byte 520); out-of-range and over-deep panic.

## Syntax and methods

```rust
page[DIRECTORY_LOCAL_DEPTHS_OFFSET..DIRECTORY_LOCAL_DEPTHS_OFFSET + 512].fill(0);       // slice::fill
self.page.as_ref()[DIRECTORY_LOCAL_DEPTHS_OFFSET + bucket_idx as usize] as u32          // a u8 field
1u32 << self.get_global_depth()                                                         // size = 2^global
```

## Notes

The bounds check is against `max_size`, not `size`: slots beyond the current size are *reserved* (the directory will grow into them), and `set_bucket_page_id(5, ..)` on a depth-2 directory is a bug the page can't detect on its own. The table keeps to `size()`; the page guards its memory.

## In BusTub

```cpp
class ExtendibleHTableDirectoryPage { uint32_t max_depth_; uint32_t global_depth_; uint8_t local_depths_[512]; page_id_t bucket_page_ids_[512]; };
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `uint8_t local_depths_[512]` read as `local_depths_[i]` (an `int` promotion) | a byte at an offset, `as u32` |
| `(1 << global_depth_)` with `int`: overflows at 31 | `1u32 << depth` (depth ≤ 9 here) |
| `std::fill_n` / `memset` | `slice.fill(0)` |
| `assert(...)` compiled out by `NDEBUG` | `assert!` always on (`debug_assert!` for debug-only) |

## Learn more
- BusTub [extendible_htable_directory_page.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/page/extendible_htable_directory_page.h) · [`slice::fill`](https://doc.rust-lang.org/std/primitive.slice.html#method.fill) · [Extendible hashing](https://en.wikipedia.org/wiki/Extendible_hashing)
