---
title: Struct layout: repr(C), offset_of! and assertions that run at compile time
summary: How the compiler lays out a struct, why Rust's default layout is not a file format, how #[repr(C)] and offset_of! give you BusTub's offsets without a pointer cast, and how const assertions pin them.
minutes: 9
---
BusTub's directory page is a C++ struct: `max_depth_`, `global_depth_`, `local_depths_[512]`, `bucket_page_ids_[512]`. The *file format* is whatever the compiler's layout of that struct happens to be. To match it (and to be able to say what the format is), you need to know how layout works and how to ask for the offsets.

## What the compiler decides

Each field has a **size** and an **alignment** (a `u32` must sit at a multiple of 4, a `u64` at a multiple of 8). The compiler inserts **padding** so that every field is aligned, and rounds the struct's total size up to a multiple of its largest alignment.

```rust
#[repr(C)]
struct DirectoryPage {
    max_depth: u32,                           // offset 0, 4 bytes
    global_depth: u32,                        // offset 4, 4 bytes
    local_depths: [u8; 512],                  // offset 8, 512 bytes  (align 1: no padding)
    bucket_page_ids: [i32; 512],              // offset 520, 2048 bytes (align 4: 520 is a multiple of 4)
}                                              // size 2568
```

| field | size | align | offset |
|---|---|---|---|
| `max_depth: u32` | 4 | 4 | 0 |
| `global_depth: u32` | 4 | 4 | 4 |
| `local_depths: [u8; 512]` | 512 | 1 | 8 |
| `bucket_page_ids: [i32; 512]` | 2048 | 4 | 520 |

That `520` is the number the stage tests check (`&page[520 + 8..520 + 12]`): the first bucket page id sits right after the 512 local depths.

```svg
caption: The directory page as bytes. Each field starts at the end of the previous one (u32 needs 4-byte alignment; the u8 array needs none), and the struct is 2568 bytes: well inside the 8192-byte page. offset_of! gives 8 and 520; a const assert pins them.
<svg viewBox="0 0 760 170" role="img" aria-label="The layout of the directory page from offset 0 to 2568">
<rect class="hot" x="20" y="40" width="60" height="50" rx="3"/><text class="mid t-a sm" x="50" y="62">max_depth</text><text class="mid dim sm" x="50" y="78">u32</text>
<rect class="hot" x="82" y="40" width="70" height="50" rx="3"/><text class="mid t-a sm" x="117" y="62">global_depth</text><text class="mid dim sm" x="117" y="78">u32</text>
<rect class="blue" x="154" y="40" width="190" height="50" rx="3"/><text class="mid t-b" x="249" y="62">local_depths</text><text class="mid dim sm" x="249" y="78">[u8; 512]</text>
<rect class="live" x="346" y="40" width="394" height="50" rx="3"/><text class="mid t-g" x="543" y="62">bucket_page_ids</text><text class="mid dim sm" x="543" y="78">[i32; 512]  (2048 bytes)</text>
<line class="ln" x1="20" y1="94" x2="20" y2="108"/><line class="ln" x1="82" y1="94" x2="82" y2="108"/><line class="ln" x1="154" y1="94" x2="154" y2="108"/><line class="ln" x1="346" y1="94" x2="346" y2="108"/><line class="ln" x1="740" y1="94" x2="740" y2="108"/>
<text class="dim sm" x="20" y="124">0</text><text class="dim sm" x="76" y="124">4</text><text class="t-b sm" x="148" y="124">8</text><text class="t-g sm" x="336" y="124">520</text><text class="dim sm end" x="740" y="124">2568</text>
<text class="dim sm" x="20" y="152">offset_of!(DirectoryPage, local_depths) = 8      offset_of!(DirectoryPage, bucket_page_ids) = 520      size_of = 2568 (page: 8192)</text>
<text class="dim sm" x="20" y="24">not to scale</text>
</svg>
```

## `#[repr(C)]` and Rust's default layout

By default Rust **reorders fields** to minimise padding and promises nothing about order: a `struct { a: u8, b: u32, c: u8 }` may be laid out `b, a, c`. That is a feature (smaller structs) and makes the layout unusable as a file format. `#[repr(C)]` says "lay the fields out in declaration order, with C's padding rules": the layout a C++ compiler would give the same struct. Related attributes: `#[repr(u8)]` (an enum's representation), `#[repr(packed)]` (no padding: references to fields can be misaligned, so it is easy to misuse), `#[repr(align(64))]` (a minimum alignment, say a cache line).

## `offset_of!` and `size_of`: the offsets without a cast

```rust
pub const DIRECTORY_LOCAL_DEPTHS_OFFSET: usize = offset_of!(DirectoryPage, local_depths);   // 8
pub const DIRECTORY_BUCKET_PAGE_IDS_OFFSET: usize = offset_of!(DirectoryPage, bucket_page_ids); // 520
pub const DIRECTORY_PAGE_SIZE: usize = size_of::<DirectoryPage>();                             // 2568
```

The struct exists **only so the compiler computes the numbers**. You never create a `DirectoryPage` or cast a page to one; the page view (previous concept) reads and writes at those constants. C++'s `offsetof(Type, member)` is the same macro.

## Assertions that run before the program does

```rust
const _: () = assert!(DIRECTORY_PAGE_SIZE <= BUSTUB_PAGE_SIZE);
const _: () = assert!(DIRECTORY_BUCKET_PAGE_IDS_OFFSET == 520);
```

An `assert!` in a `const` item is evaluated **at compile time**: if it fails, the program does not build. It is `static_assert` from C++, and the right place to write *every* layout fact you depend on (the format fits in the page; the metadata is 8 bytes; the array starts where the other module expects). Change the struct and the build tells you which fact broke, instead of a test failing on a corrupted page a week later.

| C++ | Rust |
|---|---|
| a struct's layout is implicit | `#[repr(C)]` makes it explicit and stable |
| `offsetof(T, m)` | `offset_of!(T, m)` |
| `sizeof(T)`, `alignof(T)` | `size_of::<T>()`, `align_of::<T>()` |
| `static_assert(cond, "msg")` | `const _: () = assert!(cond, "msg");` |
| `#pragma pack(1)` | `#[repr(C, packed)]` |
| `reinterpret_cast<T*>(bytes)` | not needed: read by offset |

> [!WARNING] Padding bytes and serialisation
> Writing a `#[repr(C)]` struct's memory to disk includes its padding bytes, which are *uninitialised* (and a source of nondeterministic files and information leaks). Writing field by field at explicit offsets, as the views do, writes exactly the bytes you mean.

## In real code

### The API you will use

| syntax | what it does | when |
|---|---|---|
| `#[repr(C)]` | declaration-order fields with C padding rules | a layout you can name |
| `std::mem::size_of::<T>()` / `align_of::<T>()` | size and alignment, a `const fn` | fitting a page |
| `std::mem::offset_of!(T, field)` | a field's byte offset, a constant | where a field starts |
| `const X: usize = offset_of!(..);` | a named constant for it | page views |
| `const _: () = assert!(cond, "msg");` | a compile-time check | pinning every fact |
| `#[repr(C, packed)]` / `#[repr(align(64))]` | no padding / a minimum alignment | wire formats / cache lines |
| `#[repr(u8)]` on an `enum` | the discriminant's type | page-type bytes |

```rust test
use std::mem::{align_of, offset_of, size_of};

#[repr(C)]
struct DirectoryPage {
    max_depth: u32,
    global_depth: u32,
    local_depths: [u8; 512],
    bucket_page_ids: [i32; 512],
}

const LOCAL_DEPTHS_OFFSET: usize = offset_of!(DirectoryPage, local_depths);
const BUCKET_IDS_OFFSET: usize = offset_of!(DirectoryPage, bucket_page_ids);
const _: () = assert!(size_of::<DirectoryPage>() <= 8192, "the directory must fit a page");
const _: () = assert!(BUCKET_IDS_OFFSET == 520, "BusTub's layout");

#[test]
fn the_compiler_computes_the_offsets() {
    assert_eq!(offset_of!(DirectoryPage, max_depth), 0);
    assert_eq!(offset_of!(DirectoryPage, global_depth), 4);
    assert_eq!(LOCAL_DEPTHS_OFFSET, 8);
    assert_eq!(BUCKET_IDS_OFFSET, 520);                           // 8 + 512, already a multiple of 4: no padding
    assert_eq!(size_of::<DirectoryPage>(), 2568);
    assert_eq!(align_of::<DirectoryPage>(), 4);
}
```

```rust test
use std::mem::{offset_of, size_of};

#[repr(C)]
struct WithPadding { a: u8, b: u32, c: u8 }                       // a at 0, then 3 padding bytes, b at 4, c at 8, then 3 more
#[repr(C, packed)]
struct Packed { a: u8, b: u32, c: u8 }                            // no padding: fields may be misaligned (never take references to them)

#[test]
fn padding_and_packing() {
    assert_eq!(offset_of!(WithPadding, b), 4);
    assert_eq!(size_of::<WithPadding>(), 12);                     // rounded up to a multiple of 4
    assert_eq!(size_of::<Packed>(), 6);
    let p = Packed { a: 1, b: 2, c: 3 };
    let b = p.b;                                                  // copy out: a reference `&p.b` would be misaligned
    assert_eq!(b, 2);
}
```

### In the exercises

- **2b:** the hash table's header, directory and bucket pages are laid out with `#[repr(C)]` structs and `offset_of!`; `layout.rs` is given as an example of the technique.
- **2b-02:** if you lay the pages out as `#[repr(C)]` structs, `offset_of!` and `size_of` give the offsets and a `const` assertion keeps the page within 8 KiB; plain offsets work as well.

### Where it is used

- **FFI and C interop**: every Rust struct passed to C is `#[repr(C)]`; `bindgen` generates them from C headers with the same `offset_of`-style tests.
- **Protocol and file headers**: kernel structs, network packet headers (`packed`), database page headers.
- **Performance**: `#[repr(align(64))]` keeps two hot counters from sharing a cache line (false sharing).
- **Compile-time checks**: Linux's `BUILD_BUG_ON` and Rust's `const _: () = assert!(..)` are the same idea: break the build, not the data.
