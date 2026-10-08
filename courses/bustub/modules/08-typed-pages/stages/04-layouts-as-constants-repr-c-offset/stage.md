This stage has 2 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · lower_bound: binary search inside the page

**Where this fits.** Sorted entries can be searched in `O(log n)` page reads... or rather, entry reads. Both the hash bucket (no: unsorted) and the B+ tree page need it.

### The task

Implement `lower_bound(len, cmp)` in `src/storage/page/page_array.rs`: among the sorted entries `0..len`, the index of the **first entry that is not `Less`** than the target. `cmp` compares an entry with the target (`FnMut(&T) -> Ordering`). If every entry is less, the answer is `len`.

### Tests

- An existing entry returns its index; a missing one returns where it would go; before everything is 0, after everything is `len`; an empty range is 0.
- With duplicates, the **first** of them. Entries at or after `len` (stale bytes) are never examined.
- It works with a keyed comparator on `(GenericKey<8>, Rid)` entries, agrees with `partition_point` on 200 random arrays, and probes at most 11 entries out of 1024.

### Syntax and methods

```rust
let (mut lo, mut hi) = (0, len);
while lo < hi {
    let mid = lo + (hi - lo) / 2;                    // not (lo + hi) / 2: that overflows for huge ranges
    if cmp(&self.get(mid)) == Ordering::Less { lo = mid + 1 } else { hi = mid }
}
lo
```

### Notes

**Half-open ranges, one invariant.** `lo..hi` always contains the answer; each step halves it; when `lo == hi` that's the answer. Binary search is famous for off-by-one and overflow bugs (Java's `Arrays.binarySearch` had the `(lo + hi) / 2` overflow for years); the closure-based `lower_bound` shape avoids "found / not found" branching, so it needs no `+1`/`-1` juggling. The lookup `find` is then `lower_bound` plus one comparison.

**Why a closure.** The comparator takes the *entry* and returns how it compares to a target the caller holds: the array doesn't need to know what a key is, or how to extract it from an entry (`|(k, _)| cmp.compare(k, &target)`).

### In BusTub

```cpp
// B+ tree: "find the first key >= target"; students write it by hand or with std::lower_bound over array_ with a comparator
auto it = std::lower_bound(array_, array_ + GetSize(), key, [&](const MappingType &e, const KeyType &k) { return comparator(e.first, k) < 0; });
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::lower_bound(first, last, value, comp)` (comp = "is less") | `lower_bound(len, \|e\| e.cmp(&target))` (an `Ordering`) or `slice::partition_point(\|e\| e < target)` |
| `std::upper_bound`, `std::binary_search`, `std::equal_range` | `partition_point` with `<=`; `binary_search_by` (returns `Result<usize, usize>`) |
| `bsearch(key, base, n, size, cmp)` from `<stdlib.h>` (returns a pointer or NULL) | `binary_search_by`; no pointer |
| `(lo + hi) / 2` | `lo + (hi - lo) / 2` |

**Port rule:** `std::lower_bound` with a "less than" lambda becomes `partition_point` (on a slice) or a hand-written loop (over a page array) with an `Ordering`-returning closure.

### Learn more
- [`partition_point`](https://doc.rust-lang.org/std/primitive.slice.html#method.partition_point) · [`binary_search_by`](https://doc.rust-lang.org/std/primitive.slice.html#method.binary_search_by) · Joshua Bloch, [Nearly All Binary Searches and Mergesorts are Broken](https://research.google/blog/extra-extra-read-all-about-it-nearly-all-binary-searches-and-mergesorts-are-broken/)

## Part 2 · Layouts as constants: repr(C), offset_of!, const assertions

**Where this fits.** The extendible hash pages are fixed layouts: a header with 512 directory page ids, a directory with depths and 512 bucket ids. Their offsets must be known, exact, and checked.

### The task

`src/storage/page/layout.rs` has the constants for the array sizes. Write the two page descriptions as `#[repr(C)]` structs and derive the layout constants from them:

```
Directory page: | max_depth u32 | global_depth u32 | local_depths [u8; 512] | bucket_page_ids [i32; 512] |
Header page:    | directory_page_ids [i32; 512] | max_depth u32 |
```

Define `DIRECTORY_MAX_DEPTH_OFFSET`, `DIRECTORY_GLOBAL_DEPTH_OFFSET`, `DIRECTORY_LOCAL_DEPTHS_OFFSET`, `DIRECTORY_BUCKET_PAGE_IDS_OFFSET`, `DIRECTORY_PAGE_SIZE`, `HEADER_DIRECTORY_PAGE_IDS_OFFSET`, `HEADER_MAX_DEPTH_OFFSET`, `HEADER_PAGE_SIZE` with `std::mem::offset_of!` and `size_of`, and a **compile-time assertion** that each page fits in `BUSTUB_PAGE_SIZE`.

### Tests

- Directory: offsets 0, 4, 8, 520; size 2568. Header: offsets 0, 2048; size 2052. Array sizes are `2^9 = 512`; both pages fit with room to spare (5624 bytes free in a directory page).
- Writing a local depth and a bucket page id by offset with the `page_bytes` helpers lands where the layout says.

### Syntax and methods

```rust
#[repr(C)] struct DirectoryPage { max_depth: u32, global_depth: u32, local_depths: [u8; 512], bucket_page_ids: [i32; 512] }
pub const DIRECTORY_LOCAL_DEPTHS_OFFSET: usize = std::mem::offset_of!(DirectoryPage, local_depths);
pub const DIRECTORY_PAGE_SIZE: usize = std::mem::size_of::<DirectoryPage>();
const _: () = assert!(DIRECTORY_PAGE_SIZE <= BUSTUB_PAGE_SIZE);        // a compile error if false
```

### Notes

**`repr(C)`** asks Rust for C's layout rules: fields in declaration order, each aligned to its own alignment, the struct padded to its largest alignment. Without it Rust may reorder fields to save space (`repr(Rust)`), which is fine for in-memory types and useless for on-disk formats. Here the numbers work out with no padding: `u8 × 512` followed by `i32` needs the array to end on a multiple of 4, and 8 + 512 is.

You never create a `DirectoryPage` value or cast page bytes to one; the struct is a **description**, and the compiler computes sizes and offsets from it. That keeps the benefit of the C++ class (the compiler checks the layout) without its danger (reading through a pointer of the wrong alignment).

### In BusTub

```cpp
/* Directory page format:  | MaxDepth (4) | GlobalDepth (4) | LocalDepths (512) | BucketPageIds(2048) | Free(1528) | */
static_assert(sizeof(page_id_t) == 4);
static_assert(sizeof(ExtendibleHTableDirectoryPage) <= BUSTUB_PAGE_SIZE);
```

(The comment's "Free(1528)" is for a 4 KiB page; at 8 KiB, 5624 bytes remain.)

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `offsetof(Type, member)` (`<cstddef>`; only well-defined for standard-layout types) | `std::mem::offset_of!(Type, field)` |
| `sizeof(Type)`, `alignof(Type)` | `size_of::<Type>()`, `align_of::<Type>()` |
| `static_assert(cond, "msg")` | `const _: () = assert!(cond, "msg");` |
| `#pragma pack(push, 1)` / `__attribute__((packed))` to remove padding | `#[repr(C, packed)]` (taking references to its fields is an error) |
| `struct` fields in declaration order (standard-layout), unless the compiler reorders (it may not in C++; Rust may) | `#[repr(C)]` for C's rules; plain `struct` is free to reorder |
| the layout depends on the ABI and compiler flags | `repr(C)` is fixed per target; test the numbers |

**Port rule:** a C++ class whose bytes are the on-disk format becomes `#[repr(C)]` description + explicit offsets/readers. Never rely on `repr(Rust)` layout, or on `transmute`, for a persistent format.

### Learn more
- The Reference: [type layout](https://doc.rust-lang.org/reference/type-layout.html) · The Nomicon: [`repr(C)` and other reprs](https://doc.rust-lang.org/nomicon/other-reprs.html), [data layout](https://doc.rust-lang.org/nomicon/repr-rust.html) · [`offset_of!`](https://doc.rust-lang.org/std/mem/macro.offset_of.html)
- Crates that do the casting for you, safely: [`bytemuck`](https://docs.rs/bytemuck) and [`zerocopy`](https://docs.rs/zerocopy) (they require the alignment this module avoids needing) · C++ [`offsetof`](https://en.cppreference.com/w/cpp/types/offsetof) · [`static_assert`](https://en.cppreference.com/w/cpp/language/static_assert)
