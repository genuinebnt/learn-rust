This stage has 7 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · Read and write integers at an offset

**Where this fits.** Every index in BusTub lives inside 8 KiB pages. A page is just bytes; the index code needs to read "the 4-byte count at byte 0" and "the 8-byte value at byte 4096". This module builds the small toolkit for that, in safe Rust, before the hash table and the B+ tree use it.

### The idea

BusTub casts the page's `char *` to a pointer to a struct (`reinterpret_cast<ExtendibleHTableDirectoryPage *>(data)`) and reads fields as members. That is undefined behaviour in C++ unless the alignment and the aliasing rules happen to hold, and it silently depends on the machine's byte order. The safe version reads the bytes it wants: **which bytes** (an offset), **how many** (4 for a `u32`), **in which order** (little-endian, stated).

### The task

In `src/storage/page/page_bytes.rs`: `read_u32`, `write_u32`, `read_u64`, `write_u64` (page, offset, [value]). Little-endian. Any offset, aligned or not. They must **panic** (not read garbage) if the range is past the end of the slice.

### Tests

- `0x12345678` is stored as bytes `78 56 34 12`; a `u64` likewise.
- Values read back at offsets 0, 1, 2, 3, 5, 100, and at the very end; a write changes only its own bytes; extremes (`u32::MAX`, `u64::MAX`).
- Reading or writing past the end panics.

### Syntax and methods

```rust
u32::from_le_bytes(page[offset..offset + 4].try_into().expect("a 4-byte slice"))   // &[u8] (len 4) -> [u8; 4] -> u32
page[offset..offset + 4].copy_from_slice(&value.to_le_bytes());                    // [u8; 4] -> the page
```

`page[a..b]` panics if the range is out of bounds: Rust's replacement for "undefined behaviour on a bad offset".

### Notes

**Endianness.** A `u32` is four bytes; which byte comes first is a convention. x86 and ARM run little-endian, network protocols are big-endian, files are whatever their format says. A page written on one machine must read the same on another, so *pick one and say it*: BusTub's pages are whatever the machine does (little-endian in practice); here it is explicit. `to_le_bytes`/`from_le_bytes` compile to a plain load or store on little-endian machines: no cost.

**Alignment.** A `u32` at offset 1 is "misaligned". x86 doesn't care; other CPUs fault; C and C++ say undefined behaviour. `from_le_bytes` over a byte slice has no alignment requirement, because it never forms a `*const u32` at all.

### In BusTub

```cpp
auto dir = guard.AsMut<ExtendibleHTableDirectoryPage>();   // reinterpret_cast<T *>(GetDataMut())
dir->Init(3);   dir->global_depth_ = 2;                    // fields at compiler-chosen offsets
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `*reinterpret_cast<uint32_t *>(page + offset)`: UB if misaligned or if it violates strict aliasing | `u32::from_le_bytes(page[offset..offset + 4].try_into().unwrap())` |
| `uint32_t v; memcpy(&v, page + offset, 4);` (the portable C way, still host byte order) | the same idea; `from_ne_bytes` is host order, `from_le_bytes` is explicit |
| `std::bit_cast<uint32_t>(std::array<char,4>{..})` (C++20) | `u32::from_le_bytes([a, b, c, d])` |
| `htole32`, `le32toh`, `ntohl`, `htonl` (`<endian.h>`, `<arpa/inet.h>`) | `to_le_bytes`, `from_be_bytes`, ... |
| out-of-range offset: reads other memory | panics with an index error |

**Port rule:** `reinterpret_cast<T *>(buffer + off)` over a byte buffer becomes an explicit read of `size_of::<T>()` bytes at `off` and a `from_le_bytes`, or a typed view struct that does the same per field (this module).

### Learn more
- [`u32::from_le_bytes`](https://doc.rust-lang.org/std/primitive.u32.html#method.from_le_bytes) · [`to_le_bytes`](https://doc.rust-lang.org/std/primitive.u32.html#method.to_le_bytes) · [`TryInto`](https://doc.rust-lang.org/std/convert/trait.TryInto.html)
- [Endianness](https://en.wikipedia.org/wiki/Endianness) · [Data structure alignment](https://en.wikipedia.org/wiki/Data_structure_alignment) · [What is the strict aliasing rule?](https://gist.github.com/shafik/848ae25ee209f698763cffee272a58f8) (the C++ side of the story)
- C++ [`reinterpret_cast`](https://en.cppreference.com/w/cpp/language/reinterpret_cast) · [`std::bit_cast`](https://en.cppreference.com/w/cpp/numeric/bit_cast)

## Part 2 · Page ids on disk: -1 means none

**Where this fits.** Pages point at other pages (a directory at its buckets, a B+ tree node at its child). On disk there is no `Option`; "no page" is a special value.

### The task

In `src/storage/page/page_bytes.rs`:
- `read_page_id(page, offset)` / `write_page_id(page, offset, id)`: a `PageId` is an `i32` stored in 4 little-endian bytes. **Signed**: `-1` must survive.
- `read_optional_page_id` / `write_optional_page_id`: the same, but `PageId::INVALID` (`-1`) is `None` in memory.

### Tests

- Ids round trip; `INVALID` is stored as `FF FF FF FF`.
- `None` is stored as `INVALID` and read back as `None`; `Some(PageId(0))` stays `Some`: **0 is a real page**, only -1 means none.
- A zero-filled page reads as page 0 (a lesson in why new pages must write `INVALID` explicitly).

### Syntax and methods

```rust
PageId(i32::from_le_bytes(page[offset..offset + 4].try_into().unwrap()))
Some(read_page_id(page, offset)).filter(|id| id.is_valid())     // Option::filter: keep the Some only if the predicate holds
id.unwrap_or(PageId::INVALID)
```

### Notes

**In memory use `Option`, on disk use a sentinel.** The sentinel is a *storage format* decision (BusTub's `INVALID_PAGE_ID = -1`); `Option<PageId>` is what your code should pass around. Convert at the boundary, exactly once, in these two functions. The bug to avoid is a zero-filled fresh page whose "next page" field reads as page 0 instead of "none": code that walks a page chain then loops into page 0.

### In BusTub

```cpp
static constexpr int INVALID_PAGE_ID = -1;   // size of the fields: static_assert(sizeof(page_id_t) == 4)
page_id_t next_page_id_ = INVALID_PAGE_ID;   // in B+ tree leaves: the sibling pointer
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `int32_t` page ids, `-1` as "none", compared by hand everywhere (`if (id == INVALID_PAGE_ID)`) | `PageId(i32)` with `is_valid()`; `Option<PageId>` in code |
| `static_assert(sizeof(page_id_t) == 4)` | `const _: () = assert!(size_of::<PageId>() == 4);` |
| signed vs unsigned mismatch: `uint32_t` read of a `-1` field gives 4294967295 | read as `i32` explicitly |
| `std::optional<page_id_t>` (not storable in a page: it has a hidden bool) | the same: never put an `Option` in an on-disk struct |

### Learn more
- [`Option::filter`](https://doc.rust-lang.org/std/option/enum.Option.html#method.filter) · [`Option::unwrap_or`](https://doc.rust-lang.org/std/option/enum.Option.html#method.unwrap_or) · Tony Hoare's ["billion dollar mistake"](https://en.wikipedia.org/wiki/Null_pointer#History) (why `Option` exists)

## Part 3 · Rid: where a tuple lives

**Where this fits.** An index maps keys to **record ids**: (the page a tuple is on, its slot on that page). Hash table and B+ tree leaves store them.

### The task

`Rid` (`src/storage/page/page_bytes.rs`) has its fields, `new`, accessors and `Default` (the invalid rid) given. Implement:
- `get() -> i64`: the whole rid as one integer, the page id in the **high 32 bits** and the slot in the **low 32**;
- `from_i64(i64) -> Rid`: the inverse.

### Tests

- `Rid::new(PageId(1), 2).get()` is `(1 << 32) | 2`; page 0 slot 5 is 5; page 3 slot 0 is `3 << 32`.
- A **negative** page id keeps its sign (`-1` page, slot 0 is `-(1 << 32)`), and round trips.
- The slot never leaks into the page: slot `u32::MAX` round trips and the high half is untouched. 100 random round trips. The default rid is invalid.

### Syntax and methods

```rust
((self.page_id.0 as i64) << 32) | self.slot_num as i64     // i32 -> i64 sign-extends; u32 -> i64 zero-extends
PageId((rid >> 32) as i32)     // >> on a signed integer is arithmetic (keeps the sign); `as i32` keeps the low 32 bits
rid as u32                     // truncating cast: the low 32 bits
```

### Notes

**Casts do the packing.** Rust's `as` between integer types is defined: widening a signed value sign-extends, widening an unsigned one zero-extends, narrowing keeps the low bits. That is exactly the behaviour the packing needs, but it makes the *order* of casts matter: `(slot as i64)` after `slot: u32` is fine; `(slot as i32) as i64` would sign-extend a slot with the top bit set and corrupt the page id. The test with slot `u32::MAX` is there for that.

### In BusTub

```cpp
inline auto Get() const -> int64_t { return (static_cast<int64_t>(page_id_)) << 32 | slot_num_; }
explicit RID(int64_t rid) : page_id_(static_cast<page_id_t>(rid >> 32)), slot_num_(static_cast<uint32_t>(rid)) {}
```

(Left-shifting a *negative* signed value is undefined behaviour before C++20; Rust defines it.)

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `static_cast<int64_t>(page_id_) << 32 \| slot_num_`: precedence and promotion rules decide the result | `((page_id as i64) << 32) \| slot as i64`: casts are explicit |
| `class RID` with private fields and a `Get()` | `struct Rid` with private fields; `#[derive(PartialEq, Eq, Hash, Ord)]` replaces `operator==` and `std::hash<RID>` |
| `std::hash<RID>` specialisation in `namespace std` | `#[derive(Hash)]` |
| `RID() = default` giving an invalid rid via in-class initialisers | `impl Default for Rid` |

**Port rule:** `operator==`, `operator<`, `std::hash` specialisations on a plain data class become `#[derive(PartialEq, Eq, PartialOrd, Ord, Hash)]`.

### Learn more
- The Rust Reference: [numeric cast semantics](https://doc.rust-lang.org/reference/expressions/operator-expr.html#numeric-cast) · [`#[derive]`](https://doc.rust-lang.org/book/appendix-03-derivable-traits.html)
- BusTub [rid.h](https://github.com/cmu-db/bustub/blob/master/src/include/common/rid.h)

## Part 4 · FixedSize: what a value looks like in a page

**Where this fits.** BusTub's bucket page is a C++ template over the key and value types. It works because C++ can ask `sizeof(T)` and `memcpy` a `T`. Rust needs the type to say how big it is and how to turn it into bytes: a trait.

### The task

In `src/storage/page/page_bytes.rs`, `trait FixedSize { const SIZE: usize; fn encode(&self, out: &mut [u8]); fn decode(bytes: &[u8]) -> Self; }` is given. Implement it for `i32`, `u32`, `i64`, `PageId` (an `i32`) and `Rid` (its `i64`). `out`/`bytes` are exactly `SIZE` bytes.

### Tests

- Sizes 4, 4, 8, 4, 8. Every type round trips (including `i32::MIN`, `u32::MAX`, `PageId::INVALID`, the default rid).
- Little-endian: `0x0A0B0C0D` encodes as `0D 0C 0B 0A`. A `PageId` is laid out like its raw `i32`.

### Syntax and methods

```rust
impl FixedSize for i32 {
    const SIZE: usize = 4;                                  // an associated constant: part of the type, known at compile time
    fn encode(&self, out: &mut [u8]) { out.copy_from_slice(&self.to_le_bytes()); }
    fn decode(bytes: &[u8]) -> i32 { i32::from_le_bytes(bytes.try_into().expect("4 bytes")) }
}
```

### Notes

**An associated const is a compile-time `sizeof`.** `T::SIZE` can size an array (`[u8; T::SIZE]` in a `const fn`, with caveats), compute a capacity (next stages), and be checked by `const _: () = assert!(..)`. It works for generics: `fn capacity<T: FixedSize>() -> usize { PAGE / T::SIZE }`, resolved per type at compile time, with no run-time cost: C++ templates, but with the requirement written down (`T: FixedSize`) rather than discovered from error messages.

### In BusTub

```cpp
template <typename KeyType, typename ValueType, typename KeyComparator>
class ExtendibleHTableBucketPage { ...  MappingType array_[HTableBucketArraySize(sizeof(MappingType))]; };
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `sizeof(T)` | `T::SIZE` (explicit) or `std::mem::size_of::<T>()` (the in-memory size, which includes padding: not the same thing) |
| `memcpy(dst, &value, sizeof(T))` for trivially copyable `T` | `value.encode(dst)` |
| `template <typename T> ... static_assert(std::is_trivially_copyable_v<T>)` | `T: FixedSize` bound |
| copying a struct's raw bytes into a page also copies **padding** and host byte order | explicit encoding: nothing hidden |
| concepts (C++20): `template <FixedSize T>` | trait bounds: `fn f<T: FixedSize>()` |

**Port rule:** a C++ template parameter that is only ever used as `sizeof(T)` + `memcpy` is a trait with `SIZE`, `encode`, `decode`.

### Learn more
- The Rust Book: [traits](https://doc.rust-lang.org/book/ch10-02-traits.html) and [generics](https://doc.rust-lang.org/book/ch10-01-syntax.html) · The Reference: [associated constants](https://doc.rust-lang.org/reference/items/associated-items.html#associated-constants)
- [`mem::size_of`](https://doc.rust-lang.org/std/mem/fn.size_of.html) and why it isn't `SIZE` · C++ [`templates`](https://en.cppreference.com/w/cpp/language/templates)

## Part 5 · GenericKey: an index key of N opaque bytes

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

## Part 6 · KeyComparator: ordering keys

**Where this fits.** An index needs to sort keys. The ordering lives in a comparator object, because the same bytes can mean different things.

### The task

`trait KeyComparator<K> { fn compare(&self, lhs: &K, rhs: &K) -> Ordering; }` is given in `src/storage/index/generic_key.rs`. Implement it for:
- `IntComparator` over `i32` (`src/storage/index/int_comparator.rs`): the numeric order;
- `GenericComparator<N>` over `GenericKey<N>`: compare the **signed integers** in their first 8 bytes.

### Tests

- `1 < 2`, `2 == 2`, `3 > -3`, `i32::MIN < i32::MAX`.
- Keys 5 < 9, 9 == 9, 10 > 9; **negative numbers sort first** (`-1 < 0`, `-100 < -2`), and `256 > 1` even though 256's first byte is 0.
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

## Part 7 · Pairs, and how many entries fit in a page

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
