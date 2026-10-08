This stage has 4 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

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
