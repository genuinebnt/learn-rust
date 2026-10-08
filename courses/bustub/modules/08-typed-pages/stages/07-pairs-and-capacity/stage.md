**Where this fits.** A bucket page holds `(key, value)` pairs after a small header. How many fit?

## The task

In `src/storage/index/fixed_size.rs`:
- `FixedSize for (A, B)`: `SIZE = A::SIZE + B::SIZE`; `encode` writes `A` then `B`; `decode` reads them back. (`split_at_mut` / `split_at` give you both halves.)
- `const fn array_size(metadata_size, entry_size) -> usize`: how many entries fit in a page after `metadata_size` bytes of header: `(BUSTUB_PAGE_SIZE - metadata_size) / entry_size`. BusTub's `HTableBucketArraySize`.

## Tests

- `(i32, i32)` is 8 bytes, `(GenericKey<8>, Rid)` 16, `(GenericKey<64>, PageId)` 68. Pairs lay the first value first and nest: `((i32, i32), i64)`.
- `array_size(8, 16) == 511`, `array_size(8, 8) == 1023`, and it works **in a `const` context** (`const N: usize = array_size(8, 16);`, and as an array length).

## Syntax and methods

```rust
impl<A: FixedSize, B: FixedSize> FixedSize for (A, B) {
    const SIZE: usize = A::SIZE + B::SIZE;          // computed at compile time from the two types
    fn encode(&self, out: &mut [u8]) { let (first, second) = out.split_at_mut(A::SIZE); self.0.encode(first); self.1.encode(second); }
}
pub const fn array_size(metadata_size: usize, entry_size: usize) -> usize { ... }   // callable at compile time
```

## Notes

`split_at_mut` is how you hand out two non-overlapping `&mut` into one slice: the borrow checker allows it because the function *proves* they don't overlap. Writing `out[..n]` and `out[n..]` as two simultaneous `&mut` borrows is rejected; this is the standard way round it.

**`const fn`** runs at compile time when used where a constant is needed: `[0u8; array_size(8, 1024)]` is legal. BusTub's C++ equivalent is `constexpr`, used the same way for the bucket array's length.

## In BusTub

```cpp
static constexpr uint64_t HTABLE_BUCKET_PAGE_METADATA_SIZE = sizeof(uint32_t) * 2;
constexpr auto HTableBucketArraySize(uint64_t mapping_type_size) -> uint64_t { return (BUSTUB_PAGE_SIZE - HTABLE_BUCKET_PAGE_METADATA_SIZE) / mapping_type_size; };
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::pair<K, V>` / `std::tuple` (layout unspecified, may contain padding) | `(K, V)` here is encoded field by field: no padding |
| `sizeof(std::pair<GenericKey<8>, RID>)` may be 16 or 24 depending on alignment | `<(GenericKey<8>, Rid)>::SIZE` is 16 by construction |
| `constexpr` function | `const fn` |
| `static_assert(HTableBucketArraySize(sizeof(MappingType)) > 0)` | `const _: () = assert!(array_size(8, 16) > 0);` |
| integer division of `uint64_t` (silently rounds down) | `usize` division (rounds down; division by zero panics, in `const` it fails the build) |

**Port rule:** C++ code that depends on `sizeof` of a struct matching the on-disk size is fragile (padding, alignment, compiler flags); the Rust version states the on-disk size separately and tests it.

## Learn more
- [`split_at_mut`](https://doc.rust-lang.org/std/primitive.slice.html#method.split_at_mut) · The Reference: [const functions](https://doc.rust-lang.org/reference/items/functions.html#const-functions) · [tuple trait impls](https://doc.rust-lang.org/book/ch10-02-traits.html#implementing-a-trait-on-a-type)
