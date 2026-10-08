**Where this fits.** The last bucket operation.

## The task

In `src/storage/page/extendible_htable_bucket_page.rs`:
- `remove_at(idx)`: panic ("past the bucket's size") for `idx >= size`; shift later entries down (keeping order) and count one fewer. (`PageArray::remove_at` does the shifting.)
- `remove(key, cmp) -> bool`: find the key, `remove_at` it, say whether it was there.

## Tests

- Remove takes a pair out; the rest keep their order; a missing key is `false`; removing twice finds nothing; `remove_at` by slot; a bucket can be emptied and refilled.

## Syntax and methods

```rust
self.entries_mut().remove_at(bucket_idx as usize, size as usize);
write_u32(self.page.as_mut(), SIZE_OFFSET, size - 1);
```

## Notes

BusTub's bucket doesn't promise to keep entries ordered, so a "swap with the last" removal (O(1)) is also valid; this port shifts (O(n)) because the shifting helper exists and a stable order makes tests and debugging simpler. For small `n` it doesn't matter.

## In BusTub

```cpp
auto Remove(const KeyType &key, const KeyComparator &cmp) -> bool;   void RemoveAt(uint32_t bucket_idx);
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::move(array_ + i + 1, array_ + size_, array_ + i); --size_;` | `copy_within` + `size - 1` |
| swap-with-last: `array_[i] = array_[size_ - 1]; --size_;` | the same, `Vec::swap_remove` |
| return `true`/`false` after `find` | `match`/`map` over the `Option<usize>` |

## Learn more
- [`Vec::swap_remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.swap_remove) vs [`Vec::remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.remove)
