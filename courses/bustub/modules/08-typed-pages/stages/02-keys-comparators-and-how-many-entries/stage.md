Two more things an index page needs from its entries. A **key** is an opaque array of `N` bytes (`GenericKey<N>`), compared by a **comparator** that knows how to interpret them, not by `memcmp`: signed integers compare differently from their bytes. And the capacity of a page is computed from the sizes: how many `(key, value)` pairs fit in 8 KiB after the metadata.

The skill is separating *storing* a key from *ordering* it, which is what lets one B+ tree serve integers, strings and composite keys.

## Part 1 · GenericKey: an index key of N opaque bytes

**Where this fits.** BusTub's indexes are generic over the key: an `int`, a `GenericKey<8>`, `GenericKey<64>`. A `GenericKey<N>` is `N` bytes; what they mean is the comparator's business.

### The task

`GenericKey<const KEY_SIZE: usize>` in `src/storage/index/generic_key.rs` has a public `data: [u8; KEY_SIZE]` and `Default` (all zeros). Implement:
- `set_from_integer(i64)`: zero the key, then store the integer little-endian in the first 8 bytes (BusTub: "for test purpose only");
- `get_as_integer()`: the first 8 bytes as an `i64`;
- `FixedSize for GenericKey<N>`: `SIZE = N`, `encode`/`decode` copy the bytes.

### Tests

- `set_from_integer(42)` / `-7` read back; setting a key that held `0xFF…` clears the bytes after the integer.
- Encoding gives the little-endian bytes; sizes 8, 32, 64 all work; the default is zero.

### Syntax and methods

```rust
pub struct GenericKey<const KEY_SIZE: usize> { pub data: [u8; KEY_SIZE] }     // a const generic parameter: the size is part of the type
impl<const KEY_SIZE: usize> GenericKey<KEY_SIZE> { ... }
self.data[..8].copy_from_slice(&key.to_le_bytes());
```

### Notes

**Const generics.** `GenericKey<8>` and `GenericKey<64>` are different types, and the array length is checked by the compiler: you can't pass a 64-byte key where an 8-byte one is expected. C++'s `template <size_t KeySize>` is the same idea. `[u8; KEY_SIZE]` lives inline in the struct (no heap), so a page full of keys is one contiguous run of bytes, which is the whole point of a fixed-size key.

### In BusTub

```cpp
template <size_t KeySize> class GenericKey {
  inline void SetFromInteger(int64_t key) { memset(data_, 0, KeySize); memcpy(data_, &key, sizeof(int64_t)); }
  inline auto GetAsInteger() const -> int64_t { int64_t out; memcpy(&out, data_, sizeof(int64_t)); return out; }
  char data_[KeySize];
};
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `template <size_t KeySize>` | `<const KEY_SIZE: usize>` |
| `char data_[KeySize]` (signedness of `char` is implementation-defined) | `[u8; KEY_SIZE]` (always unsigned) |
| `memset(data_, 0, KeySize); memcpy(data_, &key, 8)` | `self.data = [0; KEY_SIZE]; self.data[..8].copy_from_slice(&key.to_le_bytes())` |
| `memcpy(&out, data_, sizeof(int64_t))` into an uninitialised local | `i64::from_le_bytes(self.data[..8].try_into().unwrap())`: no uninitialised memory exists |
| `reinterpret_cast<int64_t *>(data_)` in `ToString()`: strict-aliasing UB | the safe read above |

### Learn more
- The Rust Reference: [const generics](https://doc.rust-lang.org/reference/items/generics.html#const-generics) · [`[T; N]` arrays](https://doc.rust-lang.org/std/primitive.array.html)
- BusTub [generic_key.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/index/generic_key.h)

## Part 2 · KeyComparator: ordering keys

**Where this fits.** An index needs to sort keys. The ordering lives in a comparator object, because the same bytes can mean different things.

### The task

`trait KeyComparator<K> { fn compare(&self, lhs: &K, rhs: &K) -> Ordering; }` is given in `src/storage/index/generic_key.rs`. Implement it for:
- `IntComparator` over `i32` (`src/storage/index/int_comparator.rs`): the numeric order;
- `GenericComparator<N>` over `GenericKey<N>`: compare the **signed integers** in their first 8 bytes.

### Tests

- `1 < 2`, `2 == 2`, `3 > -3`, `i32::MIN < i32::MAX`. Keys 5 < 9, 9 == 9, 10 > 9; **negative numbers sort first** (`-1 < 0`, `-100 < -2`), and `256 > 1` even though 256's first byte is 0.
- A comparator drives `sort_by` correctly.

### Syntax and methods

```rust
use std::cmp::Ordering;                 // Less | Equal | Greater
lhs.get_as_integer().cmp(&rhs.get_as_integer())     // Ord::cmp
keys.sort_by(|a, b| cmp.compare(a, b));
```

### Notes

**Comparing the bytes is a different question.** `[u8; 8]` compares lexicographically as unsigned bytes: for a little-endian integer that is neither numeric order nor signed order. A comparator exists to say what the bytes *mean*. (BusTub's real `GenericComparator` interprets the bytes through the index's schema: integer columns, varchars, ... You will build that in the Tuples module; this one covers the tests that put one integer in a key.)

**`Ordering` instead of -1/0/1.** BusTub's comparators return an `int`; callers write `cmp(a, b) < 0`. `Ordering` is an enum (`Less`, `Equal`, `Greater`) with methods (`is_lt`, `then`, `reverse`) and works with `sort_by`, `binary_search_by`, `max_by`...

### In BusTub

```cpp
class IntComparator { public: inline auto operator()(const int lhs, const int rhs) const -> int { if (lhs < rhs) return -1; if (lhs > rhs) return 1; return 0; } };
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| a function object with `operator()(a, b) -> int` (-1/0/1) | `trait KeyComparator<K>` with `compare(&self, a, b) -> Ordering` |
| `std::less<K>`, `std::function<bool(K, K)>`, `qsort`'s `int (*)(const void *, const void *)` | `Ord`, `Fn(&K, &K) -> Ordering`, `sort_by` |
| comparator passed as a template parameter `typename KeyComparator` | a generic `C: KeyComparator<K>` |
| `memcmp(a, b, n)` for byte keys (unsigned lexicographic order) | `a.cmp(b)` on `[u8; N]` (the same order) |
| `<=>` (C++20 three-way comparison) | `Ord::cmp` / `PartialOrd::partial_cmp` |

**Port rule:** a C++ comparator template parameter is a trait bound with a `compare` method returning `Ordering`; if it is a plain function, accept `impl Fn(&K, &K) -> Ordering`.

### Learn more
- [`Ordering`](https://doc.rust-lang.org/std/cmp/enum.Ordering.html) · [`Ord`](https://doc.rust-lang.org/std/cmp/trait.Ord.html) · [`sort_by`](https://doc.rust-lang.org/std/primitive.slice.html#method.sort_by)
- BusTub [int_comparator.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/index/int_comparator.h)

## Part 3 · Pairs, and how many entries fit in a page

**Where this fits.** A bucket page holds `(key, value)` pairs after a small header. How many fit?

### The task

In `src/storage/index/fixed_size.rs`:
- `FixedSize for (A, B)`: `SIZE = A::SIZE + B::SIZE`; `encode` writes `A` then `B`; `decode` reads them back. (`split_at_mut` / `split_at` give you both halves.)
- `const fn array_size(metadata_size, entry_size) -> usize`: how many entries fit in a page after `metadata_size` bytes of header: `(BUSTUB_PAGE_SIZE - metadata_size) / entry_size`. BusTub's `HTableBucketArraySize`.

### Tests

- `(i32, i32)` is 8 bytes, `(GenericKey<8>, Rid)` 16, `(GenericKey<64>, PageId)` 68. Pairs lay the first value first and nest: `((i32, i32), i64)`.
- `array_size(8, 16) == 511`, `array_size(8, 8) == 1023`, and it works **in a `const` context** (`const N: usize = array_size(8, 16);`, and as an array length).

### Syntax and methods

```rust
impl<A: FixedSize, B: FixedSize> FixedSize for (A, B) {
    const SIZE: usize = A::SIZE + B::SIZE;          // computed at compile time from the two types
    fn encode(&self, out: &mut [u8]) { let (first, second) = out.split_at_mut(A::SIZE); self.0.encode(first); self.1.encode(second); }
}
pub const fn array_size(metadata_size: usize, entry_size: usize) -> usize { ... }   // callable at compile time
```

### Notes

`split_at_mut` is how you hand out two non-overlapping `&mut` into one slice: the borrow checker allows it because the function *proves* they don't overlap. Writing `out[..n]` and `out[n..]` as two simultaneous `&mut` borrows is rejected; this is the standard way round it.

**`const fn`** runs at compile time when used where a constant is needed: `[0u8; array_size(8, 1024)]` is legal. BusTub's C++ equivalent is `constexpr`, used the same way for the bucket array's length.

### In BusTub

```cpp
static constexpr uint64_t HTABLE_BUCKET_PAGE_METADATA_SIZE = sizeof(uint32_t) * 2;
constexpr auto HTableBucketArraySize(uint64_t mapping_type_size) -> uint64_t { return (BUSTUB_PAGE_SIZE - HTABLE_BUCKET_PAGE_METADATA_SIZE) / mapping_type_size; };
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::pair<K, V>` / `std::tuple` (layout unspecified, may contain padding) | `(K, V)` here is encoded field by field: no padding |
| `sizeof(std::pair<GenericKey<8>, RID>)` may be 16 or 24 depending on alignment | `<(GenericKey<8>, Rid)>::SIZE` is 16 by construction |
| `constexpr` function | `const fn` |
| `static_assert(HTableBucketArraySize(sizeof(MappingType)) > 0)` | `const _: () = assert!(array_size(8, 16) > 0);` |
| integer division of `uint64_t` (silently rounds down) | `usize` division (rounds down; division by zero panics, in `const` it fails the build) |

**Port rule:** C++ code that depends on `sizeof` of a struct matching the on-disk size is fragile (padding, alignment, compiler flags); the Rust version states the on-disk size separately and tests it.

### Learn more
- [`split_at_mut`](https://doc.rust-lang.org/std/primitive.slice.html#method.split_at_mut) · The Reference: [const functions](https://doc.rust-lang.org/reference/items/functions.html#const-functions) · [tuple trait impls](https://doc.rust-lang.org/book/ch10-02-traits.html#implementing-a-trait-on-a-type)

## Performance

`GenericKey<N>` is a plain `[u8; N]`: copying it is a `memcpy` of `N` bytes, comparing integer keys is one decode and one integer compare (decode inlines to a load), and nothing allocates. Compared with a `String` key it avoids heap and pointer-chasing at the price of a fixed width.

The capacity formula `(8192 - metadata) / entry_size` is evaluated by the compiler (`const fn`): zero run-time cost, and a wrong layout becomes a **compile error** instead of a runtime page overflow. The trade-off to understand is fixed-width keys: every entry occupies `N` bytes even when the actual key is shorter, so `GenericKey<64>` for 8-byte integers wastes 56 bytes per entry and a page holds a fifth as many.

**Measure it.** Print how many entries fit in a bucket page for `GenericKey<4>`, `<8>`, `<16>` and `<64>` with an 8-byte `Rid`; then insert 100 000 random keys into a sorted `Vec<(GenericKey<N>, Rid)>` for each `N` and time lookups, to see the cache effect of wider entries.

## Hints

### Compare values, not bytes

A little-endian `i64` -2 is `fe ff ff ff ff ff ff ff` and +1 is `01 00 ...`: compared as bytes, -2 is *greater* than +1. The comparator must **decode** both keys to the type they represent and compare those. This is why the comparator is a separate object from the key: the same eight bytes can be an integer, two `u32`s or a string prefix, and only the schema knows.

### `Ordering` over -1/0/1

BusTub's comparator returns an `int` (negative, zero, positive); Rust's `Ordering` is an enum with exactly three values, which makes "forgot the equal case" a non-exhaustive `match` error rather than a silent bug. Implement the comparator trait to return `Ordering` and let `lower_bound` and the B+ tree use `match`; test it for transitivity on a handful of triples, since a comparator that is not a total order corrupts every structure built on it.

### Make the page layout a compile-time fact

`array_size(metadata, entry)` is a `const fn`. Use it for a `const` and add `const _: () = assert!(...)` that the metadata plus capacity times entry size is at most the page size. Then changing a key width in one place either still fits, or fails to build: the failure moves from a corrupted page at run time to a red build at your desk.
