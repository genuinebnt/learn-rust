**Where this fits.** The extendible hash pages are fixed layouts: a header with 512 directory page ids, a directory with depths and 512 bucket ids. Their offsets must be known, exact, and checked.

## The task

`src/storage/page/layout.rs` has the constants for the array sizes. Write the two page descriptions as `#[repr(C)]` structs and derive the layout constants from them:

```
Directory page: | max_depth u32 | global_depth u32 | local_depths [u8; 512] | bucket_page_ids [i32; 512] |
Header page:    | directory_page_ids [i32; 512] | max_depth u32 |
```

Define `DIRECTORY_MAX_DEPTH_OFFSET`, `DIRECTORY_GLOBAL_DEPTH_OFFSET`, `DIRECTORY_LOCAL_DEPTHS_OFFSET`, `DIRECTORY_BUCKET_PAGE_IDS_OFFSET`, `DIRECTORY_PAGE_SIZE`, `HEADER_DIRECTORY_PAGE_IDS_OFFSET`, `HEADER_MAX_DEPTH_OFFSET`, `HEADER_PAGE_SIZE` with `std::mem::offset_of!` and `size_of`, and a **compile-time assertion** that each page fits in `BUSTUB_PAGE_SIZE`.

## Tests

- Directory: offsets 0, 4, 8, 520; size 2568. Header: offsets 0, 2048; size 2052. Array sizes are `2^9 = 512`; both pages fit with room to spare (5624 bytes free in a directory page).
- Writing a local depth and a bucket page id by offset with the `page_bytes` helpers lands where the layout says.

## Syntax and methods

```rust
#[repr(C)] struct DirectoryPage { max_depth: u32, global_depth: u32, local_depths: [u8; 512], bucket_page_ids: [i32; 512] }
pub const DIRECTORY_LOCAL_DEPTHS_OFFSET: usize = std::mem::offset_of!(DirectoryPage, local_depths);
pub const DIRECTORY_PAGE_SIZE: usize = std::mem::size_of::<DirectoryPage>();
const _: () = assert!(DIRECTORY_PAGE_SIZE <= BUSTUB_PAGE_SIZE);        // a compile error if false
```

## Notes

**`repr(C)`** asks Rust for C's layout rules: fields in declaration order, each aligned to its own alignment, the struct padded to its largest alignment. Without it Rust may reorder fields to save space (`repr(Rust)`), which is fine for in-memory types and useless for on-disk formats. Here the numbers work out with no padding: `u8 × 512` followed by `i32` needs the array to end on a multiple of 4, and 8 + 512 is.

You never create a `DirectoryPage` value or cast page bytes to one; the struct is a **description**, and the compiler computes sizes and offsets from it. That keeps the benefit of the C++ class (the compiler checks the layout) without its danger (reading through a pointer of the wrong alignment).

## In BusTub

```cpp
/* Directory page format:  | MaxDepth (4) | GlobalDepth (4) | LocalDepths (512) | BucketPageIds(2048) | Free(1528) | */
static_assert(sizeof(page_id_t) == 4);
static_assert(sizeof(ExtendibleHTableDirectoryPage) <= BUSTUB_PAGE_SIZE);
```

(The comment's "Free(1528)" is for a 4 KiB page; at 8 KiB, 5624 bytes remain.)

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `offsetof(Type, member)` (`<cstddef>`; only well-defined for standard-layout types) | `std::mem::offset_of!(Type, field)` |
| `sizeof(Type)`, `alignof(Type)` | `size_of::<Type>()`, `align_of::<Type>()` |
| `static_assert(cond, "msg")` | `const _: () = assert!(cond, "msg");` |
| `#pragma pack(push, 1)` / `__attribute__((packed))` to remove padding | `#[repr(C, packed)]` (taking references to its fields is an error) |
| `struct` fields in declaration order (standard-layout), unless the compiler reorders (it may not in C++; Rust may) | `#[repr(C)]` for C's rules; plain `struct` is free to reorder |
| the layout depends on the ABI and compiler flags | `repr(C)` is fixed per target; test the numbers |

**Port rule:** a C++ class whose bytes are the on-disk format becomes `#[repr(C)]` description + explicit offsets/readers. Never rely on `repr(Rust)` layout, or on `transmute`, for a persistent format.

## Learn more
- The Reference: [type layout](https://doc.rust-lang.org/reference/type-layout.html) · The Nomicon: [`repr(C)` and other reprs](https://doc.rust-lang.org/nomicon/other-reprs.html), [data layout](https://doc.rust-lang.org/nomicon/repr-rust.html) · [`offset_of!`](https://doc.rust-lang.org/std/mem/macro.offset_of.html)
- Crates that do the casting for you, safely: [`bytemuck`](https://docs.rs/bytemuck) and [`zerocopy`](https://docs.rs/zerocopy) (they require the alignment this module avoids needing) · C++ [`offsetof`](https://en.cppreference.com/w/cpp/types/offsetof) · [`static_assert`](https://en.cppreference.com/w/cpp/language/static_assert)
