**Where this fits.** A bucket's local depth changes when it splits (+1) or merges (-1).

## The task

In `src/storage/page/extendible_htable_directory_page.rs`:
- `set_local_depth(idx, depth)`: panic ("out of range") for a slot at or past `max_size`, and panic ("max depth") for a depth above the directory's max depth; store the byte;
- `incr_local_depth(idx)`: +1, panic ("max depth") if already at the max depth;
- `decr_local_depth(idx)`: -1, panic ("already 0") at 0.

## Tests

- Set and read at slots 3 and 15; incr/decr move one step and leave other slots alone; the three panics.

## Syntax and methods

```rust
self.page.as_mut()[DIRECTORY_LOCAL_DEPTHS_OFFSET + idx as usize] = local_depth;
```

## Notes

The directory page does not know *which bucket* a slot's depth belongs to, and so `incr_local_depth(5)` changes slot 5 only; if slots 1, 3, 5 share a bucket, the **table** must update all three. That bookkeeping is stage 18 (split) and 20 (merge): the page is deliberately dumb.

## In BusTub

```cpp
void IncrLocalDepth(uint32_t bucket_idx);  void DecrLocalDepth(uint32_t bucket_idx);  void SetLocalDepth(uint32_t bucket_idx, uint8_t local_depth);
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `uint8_t depth = ...; depth - 1` promotes to `int` (so `0 - 1 == -1`, then narrowed back to 255 on store) | `u8` arithmetic overflows loudly; the asserts catch the 0 case first |
| `BUSTUB_ASSERT(local_depths_[idx] > 0, ...)` | `assert!(depth > 0, "local depth is already 0")` |
| `static_cast<uint8_t>(x)` | `x as u8` (truncating, so check range first) |

## Learn more
- [Integer overflow](https://doc.rust-lang.org/book/ch03-02-data-types.html#integer-overflow) · BusTub [extendible_htable_directory_page.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/page/extendible_htable_directory_page.h)
