---
title: Bytes, endianness and typed views over a page
summary: How an integer is laid out in bytes, why a page is a &[u8] and not a struct pointer, how to read and write fixed-width fields safely, and why C++'s reinterpret_cast is undefined behaviour.
minutes: 10
---
A page is 8192 bytes. A header page, a directory page and a bucket page are *interpretations* of those bytes: a `u32` here, an array of `i32` there. This page is how to do the interpretation without a pointer cast.

## Endianness

An integer wider than a byte is stored as several bytes in some order. **Little-endian** puts the least significant byte first (x86, ARM in its usual mode); **big-endian** puts it last (network byte order).

| value | little-endian bytes | big-endian bytes |
|---|---|---|
| `0x0000_0102_u32` (258) | `02 01 00 00` | `00 00 01 02` |
| `-1_i32` | `ff ff ff ff` | `ff ff ff ff` |
| `42_u32` | `2a 00 00 00` | `00 00 00 2a` |

A file or page format must **say** which. If you write a struct's raw memory (as BusTub's C++ does by casting the page to a struct pointer), the file is little-endian on x86 and would read back wrong on a big-endian machine. This course fixes **little-endian**: `to_le_bytes` / `from_le_bytes`, so the on-disk format is the same everywhere and the tests can check exact bytes (`&page[0..4] == [3, 0, 0, 0]`).

```rust
pub fn read_u32(page: &[u8], offset: usize) -> u32 {
    u32::from_le_bytes(page[offset..offset + 4].try_into().expect("4 bytes"))
}
pub fn write_u32(page: &mut [u8], offset: usize, value: u32) {
    page[offset..offset + 4].copy_from_slice(&value.to_le_bytes());
}
```

`page[offset..offset + 4]` is a bounds-checked slice (a panic if it runs past the end), and `try_into()` turns the `&[u8]` into the `[u8; 4]` that `from_le_bytes` wants (it cannot fail here, since the slice has length 4).

```svg
caption: The little-endian u32 258 (0x00000102) stored at offset 4 of a page. The view reads bytes 4..8 and reassembles them: byte 4 is the least significant. Nothing is cast; the four bytes are copied out.
<svg viewBox="0 0 760 190" role="img" aria-label="Eight bytes of a page with a u32 at offset 4 and its byte order">
<defs><marker id="by-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<text class="dim sm" x="40" y="24">page bytes</text>
<rect class="box" x="40" y="34" width="60" height="44" rx="3"/><text class="mid fg" x="70" y="62">03</text><text class="mid dim sm" x="70" y="98">0</text>
<rect class="box" x="104" y="34" width="60" height="44" rx="3"/><text class="mid fg" x="134" y="62">00</text><text class="mid dim sm" x="134" y="98">1</text>
<rect class="box" x="168" y="34" width="60" height="44" rx="3"/><text class="mid fg" x="198" y="62">00</text><text class="mid dim sm" x="198" y="98">2</text>
<rect class="box" x="232" y="34" width="60" height="44" rx="3"/><text class="mid fg" x="262" y="62">00</text><text class="mid dim sm" x="262" y="98">3</text>
<rect class="hot" x="296" y="34" width="60" height="44" rx="3"/><text class="mid t-a" x="326" y="62">02</text><text class="mid dim sm" x="326" y="98">4</text>
<rect class="hot" x="360" y="34" width="60" height="44" rx="3"/><text class="mid t-a" x="390" y="62">01</text><text class="mid dim sm" x="390" y="98">5</text>
<rect class="hot" x="424" y="34" width="60" height="44" rx="3"/><text class="mid t-a" x="454" y="62">00</text><text class="mid dim sm" x="454" y="98">6</text>
<rect class="hot" x="488" y="34" width="60" height="44" rx="3"/><text class="mid t-a" x="518" y="62">00</text><text class="mid dim sm" x="518" y="98">7</text>
<text class="dim sm" x="40" y="118">0..4: max_depth = 3</text>
<path class="ln-w" d="M296 120 H548" /><text class="t-w sm" x="296" y="140">read_u32(page, 4):  bytes 02 01 00 00</text>
<text class="t-a sm" x="296" y="160">0x02 + 0x01 &#215; 256 + 0 + 0 = 258</text>
<text class="dim sm" x="580" y="56">least significant</text><text class="dim sm" x="580" y="72">byte first</text>
<path class="ln" d="M575 52 H552" marker-end="url(#by-a)"/>
</svg>
```

## The C++ way, and why it is undefined behaviour

```cpp
class ExtendibleHTableHeaderPage { uint32_t max_depth_; page_id_t directory_page_ids_[512]; };
auto *header = reinterpret_cast<ExtendibleHTableHeaderPage *>(page->GetData());   // "this char buffer IS a header page"
header->max_depth_ = 3;
```

This works in practice on x86, and it is **undefined behaviour twice**: it breaks *strict aliasing* (accessing a `char` buffer through a struct type that was never constructed there) and may break *alignment* (the buffer need not be aligned for `uint32_t`). Compilers can and do miscompile it at high optimisation levels. BusTub does it because it is convenient.

The Rust alternatives, in increasing power:

| approach | what it is | cost |
|---|---|---|
| **a view type over `&[u8]`** (this course) | a struct holding the slice and methods that read/write by offset with `from_le_bytes` | a copy of 4 bytes per access: free in practice |
| `#[repr(C)]` struct + `unsafe { &*(ptr as *const T) }` | the C++ cast, in `unsafe` | the same UB if alignment or validity is wrong |
| the `bytemuck` / `zerocopy` crates | the cast, with the safety conditions checked by traits (`Pod`) | an extra dependency; still needs alignment |
| `#[repr(C)]` + `size_of`/`offset_of!` for the **layout only** | compute the offsets at compile time, but access through the view | none: this is what `layout.rs` does |

The view approach is slower to write and **safe by construction**: no pointer, no alignment, no aliasing question, and the byte-level layout is explicit and testable.

## One view, two modes: `AsRef` and `AsMut`

A page view wants to be created from `&[u8]` (read) or `&mut [u8]` (read-write). A single generic struct covers both:

```rust
pub struct ExtendibleHTableHeaderPage<B> { page: B }
impl<B: AsRef<[u8]>> ExtendibleHTableHeaderPage<B> { pub fn max_depth(&self) -> u32 { read_u32(self.page.as_ref(), HEADER_MAX_DEPTH_OFFSET) } }
impl<B: AsRef<[u8]> + AsMut<[u8]>> ExtendibleHTableHeaderPage<B> { pub fn init(&mut self, d: u32) { /* writes */ } }
```

The *read* methods exist for any `B` that can be viewed as bytes; the *write* methods only when `B` is mutable. So a view over a `ReadPageGuard`'s bytes **cannot call `init`**: the compiler enforces "a read latch does not permit writes" that C++ expresses only as a comment.

> [!WARNING] Alignment is not your problem here, but it is C's
> Copying through `from_le_bytes` makes alignment irrelevant: you never form a `&u32` into the buffer. The moment you cast the buffer to `*const u32` you must prove it is 4-byte aligned. `Box<[u8; 8192]>` is only guaranteed 1-byte aligned.
