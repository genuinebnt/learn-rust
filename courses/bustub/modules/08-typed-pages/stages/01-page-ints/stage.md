**Where this fits.** Every index in BusTub lives inside 8 KiB pages. A page is just bytes; the index code needs to read "the 4-byte count at byte 0" and "the 8-byte value at byte 4096". This module builds the small toolkit for that, in safe Rust, before the hash table and the B+ tree use it.

## The idea

BusTub casts the page's `char *` to a pointer to a struct (`reinterpret_cast<ExtendibleHTableDirectoryPage *>(data)`) and reads fields as members. That is undefined behaviour in C++ unless the alignment and the aliasing rules happen to hold, and it silently depends on the machine's byte order. The safe version reads the bytes it wants: **which bytes** (an offset), **how many** (4 for a `u32`), **in which order** (little-endian, stated).

## The task

In `src/storage/page/page_bytes.rs`: `read_u32`, `write_u32`, `read_u64`, `write_u64` (page, offset, [value]). Little-endian. Any offset, aligned or not. They must **panic** (not read garbage) if the range is past the end of the slice.

## Tests

- `0x12345678` is stored as bytes `78 56 34 12`; a `u64` likewise.
- Values read back at offsets 0, 1, 2, 3, 5, 100, and at the very end; a write changes only its own bytes; extremes (`u32::MAX`, `u64::MAX`).
- Reading or writing past the end panics.

## Syntax and methods

```rust
u32::from_le_bytes(page[offset..offset + 4].try_into().expect("a 4-byte slice"))   // &[u8] (len 4) -> [u8; 4] -> u32
page[offset..offset + 4].copy_from_slice(&value.to_le_bytes());                    // [u8; 4] -> the page
```

`page[a..b]` panics if the range is out of bounds: Rust's replacement for "undefined behaviour on a bad offset".

## Notes

**Endianness.** A `u32` is four bytes; which byte comes first is a convention. x86 and ARM run little-endian, network protocols are big-endian, files are whatever their format says. A page written on one machine must read the same on another, so *pick one and say it*: BusTub's pages are whatever the machine does (little-endian in practice); here it is explicit. `to_le_bytes`/`from_le_bytes` compile to a plain load or store on little-endian machines: no cost.

**Alignment.** A `u32` at offset 1 is "misaligned". x86 doesn't care; other CPUs fault; C and C++ say undefined behaviour. `from_le_bytes` over a byte slice has no alignment requirement, because it never forms a `*const u32` at all.

## In BusTub

```cpp
auto dir = guard.AsMut<ExtendibleHTableDirectoryPage>();   // reinterpret_cast<T *>(GetDataMut())
dir->Init(3);   dir->global_depth_ = 2;                    // fields at compiler-chosen offsets
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `*reinterpret_cast<uint32_t *>(page + offset)`: UB if misaligned or if it violates strict aliasing | `u32::from_le_bytes(page[offset..offset + 4].try_into().unwrap())` |
| `uint32_t v; memcpy(&v, page + offset, 4);` (the portable C way, still host byte order) | the same idea; `from_ne_bytes` is host order, `from_le_bytes` is explicit |
| `std::bit_cast<uint32_t>(std::array<char,4>{..})` (C++20) | `u32::from_le_bytes([a, b, c, d])` |
| `htole32`, `le32toh`, `ntohl`, `htonl` (`<endian.h>`, `<arpa/inet.h>`) | `to_le_bytes`, `from_be_bytes`, ... |
| out-of-range offset: reads other memory | panics with an index error |

**Port rule:** `reinterpret_cast<T *>(buffer + off)` over a byte buffer becomes an explicit read of `size_of::<T>()` bytes at `off` and a `from_le_bytes`, or a typed view struct that does the same per field (this module).

## Learn more
- [`u32::from_le_bytes`](https://doc.rust-lang.org/std/primitive.u32.html#method.from_le_bytes) · [`to_le_bytes`](https://doc.rust-lang.org/std/primitive.u32.html#method.to_le_bytes) · [`TryInto`](https://doc.rust-lang.org/std/convert/trait.TryInto.html)
- [Endianness](https://en.wikipedia.org/wiki/Endianness) · [Data structure alignment](https://en.wikipedia.org/wiki/Data_structure_alignment) · [What is the strict aliasing rule?](https://gist.github.com/shafik/848ae25ee209f698763cffee272a58f8) (the C++ side of the story)
- C++ [`reinterpret_cast`](https://en.cppreference.com/w/cpp/language/reinterpret_cast) · [`std::bit_cast`](https://en.cppreference.com/w/cpp/numeric/bit_cast)
