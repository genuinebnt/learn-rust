**Where this fits.** The inverse of the last stage.

## The task

Implement `remove_at(index, len)` in `src/storage/page/page_array.rs`: the array holds `len` entries; shift entries `index + 1..len` **one entry to the left** over entry `index`. Panic with a message containing "no entry" if `index >= len`.

## Tests

- Remove the middle, the first, the last (index `len - 1`: nothing to shift), the only entry.
- Past `len` panics; insert-then-remove restores the array; a model test of 500 random inserts and removes agrees with a `Vec`.

## Syntax and methods

```rust
self.bytes.as_mut().copy_within((index + 1) * size..len * size, index * size);
```

## Notes

Removing doesn't clear the freed last slot: the bytes after `len` are stale. **The length lives outside the array** (in the page header), and every operation takes it as an argument: the array never reads entries at or after `len`. This is a recurring design in database pages: the header is the source of truth, the bytes beyond it are garbage (test `lower_bound` next with exactly that).

## In BusTub

```cpp
void ExtendibleHTableBucketPage::RemoveAt(uint32_t bucket_idx) { /* shift left, then --size_ */ }
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::copy(first + 1, last, first)` (left shift: the forward direction is safe) | `copy_within(index + 1..len, index)` |
| `std::vector::erase(it)` | `Vec::remove(index)` |
| the size field maintained by hand next to the shifts (`--size_`) | the caller keeps the length (as the page header does) |
| stale bytes after the logical end: harmless in C++ too, until a bug reads them | the model test compares only `0..len` and a stale-bytes test checks nothing reads past it |

## Learn more
- [`Vec::remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.remove) · C++ [`std::vector::erase`](https://en.cppreference.com/w/cpp/container/vector/erase)
