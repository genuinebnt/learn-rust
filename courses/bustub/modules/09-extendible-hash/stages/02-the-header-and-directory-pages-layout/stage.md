This stage has 5 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · The header page: init and directory slots

**Where this fits.** An extendible hash table has **three levels**. The **header** page is the root: it maps the *top* bits of a hash to one of up to 512 **directory** pages (so a table can grow many directories, each independently). A directory maps the *low* bits to a **bucket** page; a bucket holds the pairs.

### The task

`ExtendibleHTableHeaderPage<B>` (`src/storage/page/extendible_htable_header_page.rs`) is a view over page bytes (`B` is `&[u8]` or `&mut [u8]`), laid out as `| directory_page_ids [i32; 512] | max_depth u32 |` (stage 2a-03). Implement:
- `init(max_depth)`: panic with "does not fit" if `max_depth > 9`; store it, and set **every** slot to `PageId::INVALID`;
- `max_depth()`, `max_size()` (`2^max_depth`);
- `get_directory_page_id(idx)` / `set_directory_page_id(idx, id)`: panic with "out of range" for a slot at or past `max_size`.

### Tests

- After `init(2)`: depth 2, size 4, all slots `INVALID`. Ids round trip; the bytes land where BusTub's layout says (slot 1 at byte 4, max depth at byte 2048). A read-only view works. Slot 4 of a 4-slot header, and depth 10, panic.

### Syntax and methods

```rust
impl<B: AsRef<[u8]>> ExtendibleHTableHeaderPage<B> { fn max_depth(&self) -> u32 { read_u32(self.page.as_ref(), HEADER_MAX_DEPTH_OFFSET) } }
impl<B: AsRef<[u8]> + AsMut<[u8]>> ExtendibleHTableHeaderPage<B> { fn init(&mut self, max_depth: u32) { write_u32(self.page.as_mut(), ..) } }
```

### Notes

**Fresh pages are zeros, and 0 is a real page id.** `init` must write `INVALID` explicitly into every slot, or the table would believe "directory 0 is page 0". (`new_page` hands out zero-filled memory.) The same is true of every on-disk "pointer" field.

**A view is not an object.** C++ casts the page to `ExtendibleHTableHeaderPage *` and calls methods on that pointer. Here the view is a small struct holding the page's bytes (by reference or by value) and reading fields on demand. Two flavours from one struct: `&[u8]` gives the read-only methods, `&mut [u8]` also the writers, so a `ReadPageGuard` can't call `init`.

### In BusTub

```cpp
void ExtendibleHTableHeaderPage::Init(uint32_t max_depth) { /* TODO(P2): set max_depth_ and fill directory_page_ids_ with INVALID_PAGE_ID */ }
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `ExtendibleHTableHeaderPage() = delete; DISALLOW_COPY_AND_MOVE(...)`: the class can't be constructed, only viewed through a cast pointer | a view struct that holds the bytes; nothing to forbid |
| `page_id_t directory_page_ids_[HTABLE_HEADER_ARRAY_SIZE]; uint32_t max_depth_;` | offsets in `layout.rs` + `read_page_id` / `read_u32` |
| `BUSTUB_ASSERT(directory_idx < MaxSize(), ...)` | `assert!(directory_idx < self.max_size(), "...")` |
| `std::fill(std::begin(a), std::end(a), INVALID_PAGE_ID)` | a loop writing `PageId::INVALID` (or `chunks_exact_mut`) |

**Port rule:** the page *classes* of BusTub become views; their data members become offset constants; `Init()` is the only place a page's bytes are formatted.

### Learn more
- [`AsRef`/`AsMut`](https://doc.rust-lang.org/std/convert/trait.AsRef.html) · BusTub [extendible_htable_header_page.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/page/extendible_htable_header_page.h) · CMU 15-445 "Hash Tables" (extendible hashing, from slide ~40)
- [Extendible hashing](https://en.wikipedia.org/wiki/Extendible_hashing) (Fagin, Nievergelt, Pippenger, Strong, 1979)

## Part 2 · hash_to_directory_index: the top bits

**Where this fits.** Which directory does a hash belong to?

### The task

Implement `hash_to_directory_index(hash: u32) -> u32` in `src/storage/page/extendible_htable_header_page.rs`: the **top `max_depth` bits** of the hash, as a number. With `max_depth == 0` there is one directory and the answer is 0.

### Tests

- With max depth 2 the hashes 32768, 1073774592, 2147516416 and 3221258240 (top bits 00, 01, 10, 11) map to 0, 1, 2, 3 (BusTub's own sample).
- Depth 0: always 0. Depth 1: the top bit. Depth 9: `u32::MAX` is 511. The low bits are ignored.

### Syntax and methods

```rust
match self.max_depth() { 0 => 0, depth => hash >> (32 - depth) }     // a shift by 32 would overflow: depth 0 needs its own case
```

### Notes

**Shift amounts.** `x >> 32` on a `u32` is an error in Rust (a panic in debug builds, "attempt to shift right with overflow") and **undefined behaviour in C and C++**: the CPU masks the shift count to 5 bits, so `x >> 32` is `x >> 0` on x86 and something else on ARM. BusTub's depth-0 header would trip this in C++; the explicit case, or `checked_shr`, avoids it. `u32::checked_shr(n)` returns `None` for `n >= 32`: `hash.checked_shr(32 - depth).unwrap_or(0)` is a one-liner for the same result.

**Top bits for the header, low bits for the directory.** They use different ends of the hash on purpose: a directory splits on its low bits one at a time as it grows, so the header must not consume those. This is the same trick as a radix tree: successive levels consume successive bit ranges.

### In BusTub

```cpp
auto ExtendibleHTableHeaderPage::HashToDirectoryIndex(uint32_t hash) const -> uint32_t { /* TODO(P2) */ }   // "the upper max_depth_ bits"
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `hash >> (32 - max_depth_)` with `max_depth_ == 0`: undefined behaviour | an explicit case, or `checked_shr` |
| `hash >> n` where `hash` is signed: implementation-defined (arithmetic vs logical) | `u32` is always a logical shift; for signed `i32` Rust's `>>` is arithmetic and documented |
| bit-twiddling with `0xFFFFFFFF << n` masks | `(1u32 << n) - 1` or `u32::MAX >> (32 - n)` (same care at n = 0 and n = 32) |

**Port rule:** every shift whose amount is data-dependent needs a look at the boundary values 0 and the type's width; Rust turns the bug into a panic (debug) instead of a silent wrong answer.

### Learn more
- [`u32::checked_shr`](https://doc.rust-lang.org/std/primitive.u32.html#method.checked_shr) · [Arithmetic overflow in the Reference](https://doc.rust-lang.org/reference/expressions/operator-expr.html#overflow) · CMU 15-445 "Hash Tables"

## Part 3 · The directory page: init and accessors

**Where this fits.** The middle level. A directory has `2^global_depth` slots; slot `hash & mask` holds a bucket's page id, and each slot records the **local depth** of its bucket (how many hash bits that bucket actually distinguishes). Many slots can share a bucket: when a bucket has local depth `d` and the directory has global depth `g`, exactly `2^(g-d)` slots point at it.

### The task

In `src/storage/page/extendible_htable_directory_page.rs` (`| max_depth u32 | global_depth u32 | local_depths [u8; 512] | bucket_page_ids [i32; 512] |`), implement:
- `init(max_depth)`: panic ("does not fit") above 9; store the max depth, global depth 0, zero every local depth, set every bucket slot to `INVALID`;
- `get_max_depth`, `get_global_depth`, `size()` (`2^global`), `max_size()` (`2^max`);
- `get_bucket_page_id(idx)` / `set_bucket_page_id(idx, id)` and `get_local_depth(idx)`: panic ("out of range") for `idx >= max_size`.

### Tests

- A fresh directory: depths (max 3, global 0), size 1, max size 8, slot 0 `INVALID` with depth 0. Init overwrites garbage. Ids are stored per slot; the bytes match BusTub's layout (bucket ids from byte 520); out-of-range and over-deep panic.

### Syntax and methods

```rust
page[DIRECTORY_LOCAL_DEPTHS_OFFSET..DIRECTORY_LOCAL_DEPTHS_OFFSET + 512].fill(0);       // slice::fill
self.page.as_ref()[DIRECTORY_LOCAL_DEPTHS_OFFSET + bucket_idx as usize] as u32          // a u8 field
1u32 << self.get_global_depth()                                                         // size = 2^global
```

### Notes

The bounds check is against `max_size`, not `size`: slots beyond the current size are *reserved* (the directory will grow into them), and `set_bucket_page_id(5, ..)` on a depth-2 directory is a bug the page can't detect on its own. The table keeps to `size()`; the page guards its memory.

### In BusTub

```cpp
class ExtendibleHTableDirectoryPage { uint32_t max_depth_; uint32_t global_depth_; uint8_t local_depths_[512]; page_id_t bucket_page_ids_[512]; };
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `uint8_t local_depths_[512]` read as `local_depths_[i]` (an `int` promotion) | a byte at an offset, `as u32` |
| `(1 << global_depth_)` with `int`: overflows at 31 | `1u32 << depth` (depth ≤ 9 here) |
| `std::fill_n` / `memset` | `slice.fill(0)` |
| `assert(...)` compiled out by `NDEBUG` | `assert!` always on (`debug_assert!` for debug-only) |

### Learn more
- BusTub [extendible_htable_directory_page.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/page/extendible_htable_directory_page.h) · [`slice::fill`](https://doc.rust-lang.org/std/primitive.slice.html#method.fill) · [Extendible hashing](https://en.wikipedia.org/wiki/Extendible_hashing)

## Part 4 · Masks, hash_to_bucket_index and the split image

**Where this fits.** How a hash picks a slot, and which slot is a bucket's sibling.

### The task

In `src/storage/page/extendible_htable_directory_page.rs`:
- `get_global_depth_mask()`: `global_depth` one-bits from the low end (`0b111` for depth 3); `get_local_depth_mask(idx)`: the same for slot `idx`'s local depth;
- `hash_to_bucket_index(hash)`: `hash & global_depth_mask`;
- `get_split_image_index(idx)`: the slot of the bucket this one splits from / merges with: flip bit `local_depth - 1` of `idx`. A bucket of local depth 0 has no sibling: return `idx` itself.

### Tests

- Depth 3: mask `0b111`; a slot of local depth 2: mask `0b11`; depth 0: mask 0 and every hash maps to slot 0.
- Global depth 2 maps `h` to `h % 4`. Split images: depth-1 slots 0 and 1 are each other's; depth-2 slot 5 (`101`) pairs with `111` = 7; depth-3 slot 3 pairs with 7; depth 0 is its own image.

### Syntax and methods

```rust
(1u32 << depth) - 1                                    // `depth` one-bits (fine for depth < 32)
bucket_idx ^ (1 << (depth - 1))                        // XOR flips one bit
```

### Notes

**Why flip bit `d - 1`?** A bucket of local depth `d` is identified by the low `d` bits of its slots' indexes. It came into being when a depth-`d-1` bucket split on bit `d - 1` (counting from 0), so its sibling is the slot that agrees on the lower `d - 1` bits and differs in bit `d - 1`: `idx ^ (1 << (d - 1))`. Draw the depth-2 directory (slots 00, 01, 10, 11) once and the rule is obvious: slot 01 and slot 11 are siblings at depth 2; if those two later merge into one depth-1 bucket, slot 1's sibling is slot 0.

### In BusTub

"GetGlobalDepthMask - returns a mask of global_depth 1's and the rest 0's ... DirectoryIndex = Hash(key) & GLOBAL_DEPTH_MASK". (`GetSplitImageIndex` has no comment: you derive it.)

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `(1 << depth) - 1` with `int`: `1 << 31` is UB in C++ before C++20, and `depth == 32` is UB | `1u32 << depth` is fine below 32; a shift of 32 panics in debug builds |
| `~(~0u << depth)` mask idiom | `(1u32 << depth) - 1`, or `u32::MAX >> (32 - depth)` (careful at depth 0) |
| `hash & mask` | the same |
| `x ^ (1u << k)` flip a bit | the same; `x ^= 1 << k` |

### Learn more
- [Bit manipulation in Rust's integer docs](https://doc.rust-lang.org/std/primitive.u32.html) (`count_ones`, `leading_zeros`, `trailing_zeros`, `rotate_left`) · CMU 15-445 "Hash Tables" (extendible hashing: the directory)

## Part 5 · Local depths: set, incr, decr

**Where this fits.** A bucket's local depth changes when it splits (+1) or merges (-1).

### The task

In `src/storage/page/extendible_htable_directory_page.rs`:
- `set_local_depth(idx, depth)`: panic ("out of range") for a slot at or past `max_size`, and panic ("max depth") for a depth above the directory's max depth; store the byte;
- `incr_local_depth(idx)`: +1, panic ("max depth") if already at the max depth;
- `decr_local_depth(idx)`: -1, panic ("already 0") at 0.

### Tests

- Set and read at slots 3 and 15; incr/decr move one step and leave other slots alone; the three panics.

### Syntax and methods

```rust
self.page.as_mut()[DIRECTORY_LOCAL_DEPTHS_OFFSET + idx as usize] = local_depth;
```

### Notes

The directory page does not know *which bucket* a slot's depth belongs to, and so `incr_local_depth(5)` changes slot 5 only; if slots 1, 3, 5 share a bucket, the **table** must update all three. That bookkeeping is stage 18 (split) and 20 (merge): the page is deliberately dumb.

### In BusTub

```cpp
void IncrLocalDepth(uint32_t bucket_idx);  void DecrLocalDepth(uint32_t bucket_idx);  void SetLocalDepth(uint32_t bucket_idx, uint8_t local_depth);
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `uint8_t depth = ...; depth - 1` promotes to `int` (so `0 - 1 == -1`, then narrowed back to 255 on store) | `u8` arithmetic overflows loudly; the asserts catch the 0 case first |
| `BUSTUB_ASSERT(local_depths_[idx] > 0, ...)` | `assert!(depth > 0, "local depth is already 0")` |
| `static_cast<uint8_t>(x)` | `x as u8` (truncating, so check range first) |

### Learn more
- [Integer overflow](https://doc.rust-lang.org/book/ch03-02-data-types.html#integer-overflow) · BusTub [extendible_htable_directory_page.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/page/extendible_htable_directory_page.h)
