Removing a pair from a leaf means shifting every later pair one slot left. A **tombstone** is a cheaper delete: leave the pair where it is and write down that it is deleted. This module gives every leaf a small fixed **buffer of tombstones**: the keys of the last few pairs that were "deleted" but are still physically in the page. Later stages make the tree use it; this stage builds the buffer and changes the leaf's layout to make room for it.

The number of tombstones a leaf can hold is a property of the *type* (BusTub's `NumTombs` template parameter), because it moves where the entries start. In Rust that is a **const generic**: `BPlusTreeLeafPage<B, K, V, const TOMBS: usize = 0>`. With `TOMBS = 0` the layout is exactly module 2c's, byte for byte, so nothing you built stops working.

**Where this fits.** Everything above the leaf (internal pages, splits, the iterator) will carry the same `TOMBS` parameter in the next stage. The template already declares it, so your tree compiles with its default of 0; this module is where you give it meaning.

## The task

In `src/storage/page/b_plus_tree_leaf_page.rs` (the const generic and the layout helpers are given: `TOMB_REGION` is the bytes before the entries, `ENTRIES_AT` where they start, and `capacity()` and the entry accessors already use them; if you wrote them in module 2c without these helpers, make `capacity()` and the entry array start at `ENTRIES_AT`):

```text
| header (16) | num_tombstones u32 | tombstone keys [K; TOMBS], oldest first | (key, value) | ...
```
- `num_tombstones()` (always 0 when `TOMBS == 0`) and `tombstones() -> Vec<K>` (decoded from the buffer);
- `set_tombstones(&[K])` (panic if more than `TOMBS`), `add_tombstone(key)` (the newest; panic if the buffer is full) and `remove_tombstone(key, cmp) -> bool` (the others keep their order);
- `is_tombstoned(key, cmp)` and `is_deleted_at(slot)` (the key of that slot is in the buffer; compare the encoded bytes, a leaf iterator has no comparator);
- `init` also empties the buffer (a recycled page may hold garbage).

## Tests

- Capacities by `TOMBS`: 511 for 0 (the old layout), 509 for 2 and 3, 508 for 4.
- A fresh leaf has an empty buffer even on a page of `0xFF` bytes; tombstones come back oldest first; a full buffer refuses another; with `TOMBS = 0` there is no buffer at all.
- Lookup by key or by slot, removal keeping the others' order, and the buffer and the entries never overlap.

## Syntax and methods

```rust
pub struct BPlusTreeLeafPage<B, K, V, const TOMBS: usize = 0> { /* ... */ }   // a const generic with a default

const TOMB_REGION: usize = if TOMBS == 0 { 0 } else { 4 + TOMBS * K::SIZE };   // an associated const computed from the parameters

let at = NUM_TOMBSTONES_OFFSET + 4 + i * K::SIZE;                             // key i of the buffer
K::decode(&self.page.as_ref()[at..at + K::SIZE])
```

## Notes

**Why a type parameter and not a field?** The entries start at a different byte for every `TOMBS`. If the number were a runtime field of the page every access to an entry would have to read it first, and a leaf of one `TOMBS` could be misread as another. A const generic puts the number in the type: `Leaf<_, K, V, 2>` and `Leaf<_, K, V, 3>` are different types, the compiler computes the offsets once, and `TOMBS == 0` compiles to code with no tombstone handling at all. This is the same trick as C++'s `template <size_t NumTombs>`.

**Store keys, not indexes.** BusTub stores indexes into the entry array; this port stores the **keys**. A key survives a shift of the entries (an index would have to be adjusted every time a pair moves) and `tombstones()` can return keys directly. The price is `K::SIZE` bytes per tombstone instead of 4.

**The invariant.** Every key in the buffer belongs to a pair that is physically in the page, and no key is buffered twice. The later stages keep it; the structure checker in the tests verifies it.

## In BusTub

`b_plus_tree_leaf_page.h`: "Leaf pages also contain a fixed buffer of "tombstone" indexes for entries that have been deleted." and the layout comment "| HEADER | TOMB_SIZE | (where TOMB_SIZE is num_tombstones_)", "| TOMB(0) | TOMB(1) | ... | TOMB(k) |", then the keys and rids; `GetTombstones` returns "The last `NumTombs` keys with pending deletes in this page in order of recency (oldest at front)."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `template <typename K, typename V, typename C, ssize_t NumTombs = 0> class BPlusTreeLeafPage` | `struct BPlusTreeLeafPage<B, K, V, const TOMBS: usize = 0>` |
| `#define LEAF_PAGE_TOMB_CNT ((NumTombs < 0) ? 0 : NumTombs)` and `size_t tombstones_[LEAF_PAGE_TOMB_CNT]` | an associated `const` and a computed offset |
| a zero-length array when `NumTombs` is 0 (a compiler extension) | no bytes at all: the region's size is 0 |

**Port rule:** a C++ template parameter that changes a struct's size becomes a const generic parameter; a macro that computes sizes from it becomes an associated `const`.

## Learn more
- [Const generics](https://doc.rust-lang.org/reference/items/generics.html#const-generics) · [Associated constants](https://doc.rust-lang.org/reference/items/associated-items.html#associated-constants) · [`std::array`](https://doc.rust-lang.org/std/primitive.array.html)

## Performance

The buffer costs `4 + TOMBS * K::SIZE` bytes per leaf: 20 bytes for two 8-byte keys, which is 1 pair fewer in a 511-pair leaf (0.2%), and a linear scan of at most `TOMBS` keys per tombstone check. `TOMBS` is small on purpose: every operation that asks "is this deleted?" scans the buffer, so the check must stay as cheap as a few comparisons.

With `TOMBS = 0` the generic code is compiled away: `if TOMBS == 0 { return 0; }` is a constant condition and the buffer functions become no-ops, which is what keeps module 2c's tests (and speed) unchanged.

**Measure it.** Compare `capacity()` for `TOMBS` 0 to 8 and print the lost pairs; time 10 million `is_deleted_at` calls for `TOMBS` 1, 2, 4 and 8.

## Hints

### Where does the count live, and who writes it?

At byte 16, right after the header (four bytes, little-endian), only when `TOMBS > 0`. `set_tombstones` writes the keys *and* the count; `add_tombstone` and `remove_tombstone` are "read the list, change it, write it back", which is slower than shifting bytes in place and much harder to get wrong.

### Compare tombstones by bytes in the iterator's path

`is_deleted_at(slot)` has no comparator: encode the slot's key and the buffered keys with `FixedSize::encode` and compare the byte vectors. A tombstone is a copy of the entry's key, so the bytes are equal exactly when it is the same key.

### Keep `TOMBS = 0` free

Guard the buffer code with `if TOMBS == 0 { return ... }` and test it: a leaf of `TOMBS = 0` must have capacity 511, no buffer, and entries at byte 16, or module 2c's tests will break.
