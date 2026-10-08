This stage has 3 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · HashFunction: hash a key's bytes

**Where this fits.** The table hashes keys of any `FixedSize` type: ints, `GenericKey<8>`, ...

### The task

In `src/container/hash/hash_function.rs`, implement `HashFunction::get_hash(&self, key: &K) -> u64`: encode the key into its bytes (`K::SIZE` of them, via `FixedSize::encode`), hash them with `murmur_hash3_x64_128` (seed 0), and return the **first** 64-bit half. The table's private `hash` method (in `src/container/disk/hash/disk_extendible_hash_table.rs`, also part of this stage) then truncates it to 32 bits: `as u32`, the low half.

### Tests

- Ints 0, 1, 2, 3, 7, 8, 100, -1, 123456789 hash to the values BusTub's C++ produces (4 bytes of the int, little-endian). `GenericKey<8>` keys hash by their 8 bytes. Only the first half of the 128 bits is kept.
- The low two bits of the hashes of 0..16 spread over all four values (the table uses low bits for buckets).

### Syntax and methods

```rust
let mut bytes = vec![0u8; K::SIZE];
key.encode(&mut bytes);
murmur_hash3_x64_128(&bytes, 0)[0]
self.hash_fn.get_hash(key) as u32       // `as u32` on a u64 keeps the low 32 bits
```

### Notes

**What gets hashed.** BusTub hashes `sizeof(KeyType)` raw bytes of the key object: for an `int`, its 4 bytes in host order. The port hashes the key's *page encoding* (little-endian), which is the same bytes on the x86/ARM machines BusTub runs on. Rust's own `std::hash::Hash`/`Hasher` is a different design: it feeds a key's *fields* into a hasher and is allowed to change between releases; it is not stable enough to base a persistent structure on. A database needs a hash whose output never changes (it decides where data lives on disk).

### In BusTub

```cpp
virtual auto GetHash(KeyType key) const -> uint64_t {
  uint64_t hash[2];
  murmur3::MurmurHash3_x64_128(reinterpret_cast<const void *>(&key), static_cast<int>(sizeof(KeyType)), 0, reinterpret_cast<void *>(&hash));
  return hash[0];
}
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `template <typename KeyType> class HashFunction` with a `virtual GetHash` | `struct HashFunction<K>` + a method; override by writing another type with the same method and making the table generic over it |
| `std::hash<T>` (implementation-defined, can vary between runs and compilers) | `std::hash::Hash` + `Hasher` (also unstable across releases; `RandomState` is seeded per process) |
| `reinterpret_cast<const void *>(&key)`: hashes padding bytes and host byte order | `key.encode(&mut bytes)`: explicit bytes |
| `uint64_t hash[2]; ...; return hash[0];` | `murmur_hash3_x64_128(..)[0]` |

**Port rule:** a hash used only in memory can be `std::hash`/`ahash`/`FxHash`; a hash whose value is persisted or must match another system needs a fixed, specified algorithm (Murmur3, xxHash, CityHash, SipHash with a fixed key).

### Learn more
- [`std::hash::Hash`](https://doc.rust-lang.org/std/hash/trait.Hash.html) and [`Hasher`](https://doc.rust-lang.org/std/hash/trait.Hasher.html) · [`RandomState`](https://doc.rust-lang.org/std/collections/hash_map/struct.RandomState.html) · [`ahash`](https://docs.rs/ahash), [`rustc-hash`](https://docs.rs/rustc-hash) (fast in-memory hashers)
- BusTub [hash_function.h](https://github.com/cmu-db/bustub/blob/master/src/include/container/hash/hash_function.h) · C++ [`std::hash`](https://en.cppreference.com/w/cpp/utility/hash)

## Part 2 · The header page: init and directory slots

**Where this fits.** An extendible hash table has **three levels**. The **header** page is the root: it maps the *top* bits of a hash to one of up to 512 **directory** pages (so a table can grow many directories, each independently). A directory maps the *low* bits to a **bucket** page; a bucket holds the pairs.

### The task

`ExtendibleHTableHeaderPage<B>` (`src/storage/page/extendible_htable_header_page.rs`) is a view over page bytes (`B` is `&[u8]` or `&mut [u8]`), laid out as `| directory_page_ids [i32; 512] | max_depth u32 |` (stage 2a-04). Implement:
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

## Part 3 · hash_to_directory_index: the top bits

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
