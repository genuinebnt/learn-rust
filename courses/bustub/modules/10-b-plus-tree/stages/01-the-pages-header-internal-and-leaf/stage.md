A B+ tree index is a tree of **pages**. There are three kinds, and this stage builds the typed views over their bytes: the **header page** (one number: where the root is), the **internal pages** (separator keys and child page ids, which only direct a search) and the **leaf pages** (the actual key/value pairs, chained to the next leaf). Nothing searches or inserts yet; it is the vocabulary the rest of the module speaks.

Every view follows the pattern of module 2a and the hash table: a struct holding `B` (the page's bytes, `&[u8]` to read, `&mut [u8]` to read and write) with methods that read and write fields at fixed offsets. BusTub casts the page to a C++ class with `reinterpret_cast`; here nothing is cast, so there is no alignment or padding to get wrong.

## Part 1 · The common header and the header page

**Where this fits.** Internal and leaf pages both start with the same 12 bytes, so code that has just latched an unknown page can ask "are you a leaf?" before it knows which view to build. The header page is a page of its own because the root's id *changes* when the tree grows or shrinks, and anything that changes needs a latch.

### The task

In `src/storage/page/b_plus_tree_page.rs` implement the shared header (`| page_type u32 | size u32 | max_size u32 |`, little-endian):
- `page_type()` (a fresh zero page is `Invalid`), `is_leaf_page()`, `size()`, `max_size()`;
- `set_page_type`, `set_size`, `set_max_size`, and `change_size_by(amount)` (a negative amount shrinks; a size below zero is a bug, so panic);
- `min_size()`: the fewest entries a page that is **not the root** may hold: a leaf `max_size / 2`, an internal page `ceil(max_size / 2)` (its entries are *children*).

In `src/storage/page/b_plus_tree_header_page.rs` implement `root_page_id()`, `set_root_page_id()` and `init()` (the root is `PageId::INVALID`: an empty tree).

### Tests

- The type field round-trips through the stored numbers 1 (leaf) and 2 (internal), a zero page is neither; size and max size are separate fields at bytes 4 and 8, and going below zero panics.
- `min_size` for every max size from 2 to 12, leaf and internal.
- A zero header page says the root is page 0 (!) until `init` makes it `INVALID`.

### Syntax and methods

```rust
match read_u32(self.page.as_ref(), PAGE_TYPE_OFFSET) {
    1 => IndexPageType::Leaf,
    2 => IndexPageType::Internal,
    _ => IndexPageType::Invalid,
}
let size = self.size().checked_add_signed(amount).expect("a page's size cannot go below zero");   // u32 + i32, None on overflow or underflow
max_size.div_ceil(2)                                                                              // ceil(max_size / 2) for unsigned integers
```

### Notes

**Why the minimum is not "half the maximum".** A leaf is split the moment it holds `max_size` pairs, so at rest it holds at most `max_size - 1`; an internal page can hold up to `max_size` children. Splitting a full node leaves the halves with `ceil` and `floor` of half the entries, and the smaller half must still reach `min_size`. For a leaf with `max_size = 5` a split produces 3 + 2 pairs, so `min_size` is `5 / 2 = 2`; for an internal page with `max_size = 5` a split of 6 children produces 3 + 3, so `min_size` is `ceil(5 / 2) = 3`. The delete stages use `min_size` as "too empty".

**The zero page trap.** A freshly allocated page is all zeros, and 0 is a valid page id. A tree whose header page was never formatted would think its root is page 0. `init` writes `INVALID` (-1) explicitly.

### In BusTub

`b_plus_tree_page.h`: "Both internal and leaf page are inherited from this page. It actually serves as a header part for each B+ tree page ... Header format (size in byte, 12 bytes in total): | PageType (4) | CurrentSize (4) | MaxSize (4) | ...". And for the header page: "The header page is just used to retrieve the root page, preventing potential race condition under concurrent environment."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `class BPlusTreePage { IndexPageType page_type_; int size_; int max_size_; }` cast from `char *` | a struct holding the bytes, reading `u32`s at offsets 0, 4, 8 |
| `enum class IndexPageType { INVALID_INDEX_PAGE = 0, LEAF_PAGE, INTERNAL_PAGE }` stored as an `int` | a `#[repr]`-free enum converted by hand: the numbers are the file format |
| `int size` plus `size += amount` (can silently go negative) | `u32` with `checked_add_signed`: a bug is a panic, not a corrupt page |
| `(max_size + 1) / 2` | `div_ceil(2)` |

**Port rule:** C++ code that reads a struct out of a byte buffer becomes a view with explicit offsets; keep the offsets in one place so the layout is written once.

### Learn more
- [`u32::checked_add_signed`](https://doc.rust-lang.org/std/primitive.u32.html#method.checked_add_signed) · [`u32::div_ceil`](https://doc.rust-lang.org/std/primitive.u32.html#method.div_ceil) · CMU 15-445 "Tree Indexes" (page layout)

## Part 2 · The internal page

**Where this fits.** An internal page holds `n` children and `n - 1` separator keys. Child `i` is where the keys `K` with `key(i) <= K < key(i + 1)` live. BusTub keeps two parallel arrays (keys and child ids) with `key(0)` unused; this port stores `(key, child)` pairs side by side, which is the same information in one array, so one `PageArray`, one shift on insert. Slot 0's key exists in the bytes and means nothing.

```text
| page_type u32 | size u32 | max_size u32 | (key0 unused, child0) | (key1, child1) | ... |
```

### The task

In `src/storage/page/b_plus_tree_internal_page.rs`:
- `capacity()`: how many `(key, child)` pairs fit after the 12-byte header (`array_size`);
- `init(max_size)` (type `Internal`, size 0; panic if `max_size` does not fit), `entry_at(i)` (panic past `size`), `key_at(i)`, `value_at(i)`;
- `set_entry_at(i, key, child)` (does **not** change the size), `set_key_at(i, key)` (keeps the child), `set_value_at(i, child)` (keeps the key);
- `value_index(child)`: which slot holds this child, if any.

### Tests

- `init` makes an empty `Internal` page; entries written with `set_entry_at` and a size read back; `set_key_at` and `set_value_at` change one half of a pair and leave the other.
- `value_index` finds a child and returns `None` for one that was overwritten or never there; reading a slot past the size panics.
- `capacity()` is `(8192 - 12) / 12` for 8-byte keys.

### Syntax and methods

```rust
PageArray::new(&self.page.as_ref()[INTERNAL_PAGE_HEADER_SIZE..])        // entries start right after the header
self.entries().get(index as usize)                                       // -> (K, PageId): tuples of FixedSize types are FixedSize
(0..self.size()).find(|&i| self.value_at(i) == value)                    // Iterator::find returns Option
```

### Notes

`size` counts **children**, not keys: an internal page with `size` 3 has keys in slots 1 and 2 and children in slots 0, 1 and 2. Every loop over "the keys" runs `1..size`.

`set_*` functions that do not touch the size are deliberate: the tree code fills a *new* page by writing slots first and setting the size once, and a split moves entries around without ever going through an "append" that keeps the count.

### In BusTub

`b_plus_tree_internal_page.h`: "Store n indexed keys and n + 1 child pointers (page_id) within internal page. Pointer PAGE_ID(i) points to a subtree in which all keys K satisfy: K(i) <= K < K(i+1). NOTE: Since the number of keys does not equal to number of child pointers, the first key in key_array_ always remains invalid. That is to say, any search / lookup should ignore the first key."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `KeyType key_array_[INTERNAL_PAGE_SLOT_CNT]; ValueType page_id_array_[...];` (two arrays, sized by a macro) | one array of `(K, PageId)` pairs viewed through `PageArray`; the count is a `const fn` |
| `#define INTERNAL_PAGE_SLOT_CNT ((BUSTUB_PAGE_SIZE - 12) / ((int)(sizeof(KeyType) + sizeof(ValueType))))` | `array_size(INTERNAL_PAGE_HEADER_SIZE, <(K, PageId)>::SIZE)` |
| `ValueIndex(value)` returning `-1` when missing | `Option<u32>` |

### Learn more
- CMU 15-445 "Tree Indexes" · [`Iterator::find`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.find) · SQLite's [file format: B-tree pages](https://www.sqlite.org/fileformat2.html#b_tree_pages)

## Part 3 · The leaf page

**Where this fits.** The leaf is where the data is. It holds sorted `(key, value)` pairs and the id of the next leaf to its right; following those ids from the leftmost leaf visits every key in order, which is what makes a range scan cheap.

```text
| page_type u32 | size u32 | max_size u32 | next_page_id i32 | (key, value) | (key, value) | ... |
```

### The task

In `src/storage/page/b_plus_tree_leaf_page.rs`:
- `capacity()`: pairs that fit after the 16-byte header; `init(max_size)` (type `Leaf`, size 0, **no next leaf**);
- `next_page_id()` returning `Option<PageId>` and `set_next_page_id(Option<PageId>)` (on disk `None` is `-1`, so page 0 stays usable);
- `entry_at(i)` (panic past `size`), `key_at`, `value_at`, and `set_entry_at(i, key, value)` (does not change the size).

### Tests

- A fresh leaf has size 0, the given max size, no next leaf; the next pointer does not disturb the entries, and `Some(PageId(0))` is not `None`; entries round-trip, and `init` rejects a max size that does not fit.
- Capacities: 511 pairs for an 8-byte key and an 8-byte rid.

### Syntax and methods

```rust
read_optional_page_id(self.page.as_ref(), NEXT_PAGE_ID_OFFSET)          // INVALID (-1) becomes None
write_optional_page_id(self.page.as_mut(), NEXT_PAGE_ID_OFFSET, next)   // None becomes -1
const NEXT_PAGE_ID_OFFSET: usize = 12;                                  // after page_type, size, max_size
```

### Notes

**`Option` in memory, `-1` on disk.** BusTub uses `INVALID_PAGE_ID` in both places and a forgotten check is a quiet bug. The page format keeps the `-1` (it is the file format), but the Rust API hands out an `Option<PageId>`, so "is there a next leaf?" has to be asked before the id is used.

**What the page does not do.** It does not keep itself sorted or refuse to overflow: those rules belong to insert (next stages). For now it is a typed view of 16 + 16 * n bytes.

### In BusTub

`b_plus_tree_leaf_page.h`: "Store indexed key and record id (record id = page id combined with slot id, see include/common/rid.h for detailed implementation) together within leaf page. Only support unique key." and "Header format (size in byte, 16 bytes in total): | PageType (4) | CurrentSize (4) | MaxSize (4) | NextPageId (4) |".

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `page_id_t next_page_id_;` with `INVALID_PAGE_ID` meaning none | `Option<PageId>` in the API, `-1` in the bytes |
| `LEAF_PAGE_SLOT_CNT` macro | `capacity()` computed from `FixedSize::SIZE` |
| `static_assert(sizeof(Leaf) <= BUSTUB_PAGE_SIZE)` | an `assert!` in `init` that `max_size` pairs fit |

### Learn more
- [`Option`](https://doc.rust-lang.org/std/option/enum.Option.html) · CMU 15-445 "Tree Indexes" · SQLite's [leaf pages](https://www.sqlite.org/fileformat2.html#b_tree_pages)

## Performance

All of this is a handful of integer reads and writes at fixed offsets; a page view costs nothing to build (it is a reference and a type, no copy). The numbers that matter come from the layout: with 8 KiB pages a leaf of 8-byte keys and 8-byte rids holds **511** pairs and an internal page **681** children, so a tree of three levels already addresses up to `681 * 681 * 511 ≈ 237 million` pairs. That is why a B+ tree on disk is almost always 3 or 4 levels high, and why one lookup costs 3 or 4 page reads, the first two or three of which are nearly always in the buffer pool.

**Measure it.** Compute `capacity()` for key sizes 4, 8, 16, 32 and 64 and tabulate the fan-out and the number of levels needed for one billion pairs. Then time 10 million `key_at` calls on a page and compare with reading the same keys from a `Vec<i64>`.

## Hints

### Where do the fields live, and in which byte order?

`page_type` at byte 0, `size` at 4, `max_size` at 8: three little-endian `u32`s. A leaf adds `next_page_id` (an `i32`) at byte 12, so its entries start at byte 16; an internal page's entries start at byte 12. Write those numbers down as constants once and the rest is `read_u32`/`write_u32` and `read_page_id`. Test the byte positions directly: set a size of 1 and check that bytes 4..8 are `[1, 0, 0, 0]`.

### What can a new page's header say?

Nothing you can rely on: a page from `new_page` is all zeros, which reads as type `Invalid`, size 0, max size 0 and *next leaf: page 0*. `init` must set every field it is responsible for, in particular the leaf's "no next leaf" and the header page's `INVALID` root. Treat `init` as "make this page valid", not "set the size".

### Why `min_size` differs for leaves and internal pages

Count what a split leaves behind. A leaf splits at `max_size` pairs (all of them present), an internal page when it would need `max_size + 1` children. Work the smallest cases by hand (`max_size` 2, 3, 4, 5) and check that the smaller half of the split always reaches your `min_size`; if it does not, a freshly split page would immediately be "too empty".
