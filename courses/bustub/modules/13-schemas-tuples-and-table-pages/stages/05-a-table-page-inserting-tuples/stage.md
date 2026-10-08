Tuples live in pages, and the page format is the oldest design in databases: the **slotted page**. A small **slot array** at the front of the page records, for each tuple, where it is and how big it is; the tuples themselves are packed from the **back** of the page towards the front. The page is full when the two meet. A tuple is addressed by its **slot number**, and since tuples never move, that address stays valid even as other tuples are added or deleted.

```text
| header 8 | slot 0 | slot 1 | slot 2 |   free space   | tuple 2 | tuple 1 | tuple 0 |
0          8                                                                       8192
```

## The task

In `src/storage/page/table_page.rs` (the struct, `new`, the byte-level slot reader/writer and the setters are given; the header is `next_page_id i32 | num_tuples u16 | num_deleted_tuples u16` and a slot is 24 bytes: offset, size and a `TupleMeta`):
- `init()`: no next page, zero tuples, zero deleted;
- `get_num_tuples()`, `get_num_deleted_tuples()`, `get_next_page_id() -> Option<PageId>` (the header fields; `INVALID` is `None`);
- `get_next_tuple_offset(meta, tuple) -> Option<u16>`: where a tuple of this size would go. The first tuple ends at the page's end; each later tuple ends where the previous one *starts* (the last slot's offset). The new tuple's start is that minus its length; it fits only if that start is **not below** the end of the slot array *including the new slot*: `8 + 24 * (num_tuples + 1)`. A tuple longer than the room must give `None`, never an underflow panic;
- `insert_tuple(meta, tuple) -> Option<u16>`: find the offset (`None` if it does not fit), write the slot (offset, length, meta) and the tuple's bytes, count one more tuple, return the new slot number.

## Tests

- A fresh page (even on garbage bytes) is empty; slots are consecutive and the first tuple sits at the very end of the page; 66 tuples of 100 bytes fill a page exactly, a 67th and even a 1-byte tuple are refused with the page unchanged.
- Free space is what lies between the slots and the tuples: after 60 such tuples a 720-byte tuple fits and a 721-byte one does not; the largest tuple an empty page takes is 8160 bytes; the next-page id round-trips (page 0 is a real page).

## Syntax and methods

```rust
let slot_end_offset = if n > 0 { self.slot(n - 1).0 as usize } else { BUSTUB_PAGE_SIZE };   // where the last tuple starts
let tuple_offset = slot_end_offset.checked_sub(tuple.get_length() as usize)?;               // None instead of an underflow
let slots_end = TABLE_PAGE_HEADER_SIZE + TUPLE_INFO_SIZE * (n as usize + 1);
(tuple_offset >= slots_end).then_some(tuple_offset as u16)
self.page.as_mut()[offset..offset + len].copy_from_slice(tuple.data());
```

## Notes

**Why the slot array.** Without it, a tuple's address would be its byte offset, and compacting the page (to reuse the space of deleted tuples) would change every address. With it, the address is the slot *number*; compaction only changes the offset stored in the slot. BusTub's page never compacts (a deleted tuple's space stays used until the table is rebuilt), but the design is what allows real systems to (PostgreSQL's `VACUUM`, SQLite's defragmentation).

**The two ends meet.** Both regions grow towards each other, so the page uses all its space whatever mix of small and large tuples arrives. Two fixed regions (say 100 slots, then data) would waste space for big tuples and run out of slots for small ones.

**Unsigned arithmetic bites.** `slot_end_offset - length` underflows when a tuple is larger than the room, and in Rust that is a panic in debug and a huge number in release. `checked_sub` turns it into `None`, which is the right answer: "does not fit".

**One slot per tuple costs 24 bytes** in BusTub's layout (a 16-byte `TupleMeta` plus offset and size). A 4-byte tuple takes 28 bytes of page.

## In BusTub

`table_page.h` ("Slotted page format: | HEADER | ... FREE SPACE ... | ... INSERTED TUPLES ... | ... free space pointer") and `table_page.cpp`: `GetNextTupleOffset` ("auto tuple_offset = slot_end_offset - tuple.GetLength(); auto offset_size = TABLE_PAGE_HEADER_SIZE + TUPLE_INFO_SIZE * (num_tuples_ + 1); if (tuple_offset < offset_size) { return std::nullopt; }") and `InsertTuple`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `char page_start_[0]; TupleInfo tuple_info_[0];` (flexible array members over the page) | a view over `&mut [u8]` with `slot_at(i)` offsets |
| `std::optional<uint16_t>` | `Option<u16>` |
| `size_t` subtraction that wraps | `checked_sub` |
| `memcpy(page_start_ + *tuple_offset, tuple.data_.data(), tuple.GetLength())` | `copy_from_slice` |

**Port rule:** `char x[0]` at the end of a struct is a view with an offset; "optional result" is `Option`.

## Learn more
- PostgreSQL: [page layout](https://www.postgresql.org/docs/current/storage-page-layout.html) (line pointers are slots) · [`checked_sub`](https://doc.rust-lang.org/std/primitive.usize.html#method.checked_sub) · [`bool::then_some`](https://doc.rust-lang.org/std/primitive.bool.html#method.then_some)

## Performance

Insert is `O(1)`: read the last slot, one subtraction, write one slot and one `memcpy`. Reading a tuple by slot is `O(1)` too. The cost of the design is internal: deleted tuples leave holes that only a rebuild reclaims, and a page that is full of small tuples spends 24 bytes of every 28 on bookkeeping.

An 8 KiB page holds 66 tuples of 100 bytes, and each page read from disk brings in all of them: the page is the unit of I/O, so tuples that are inserted together and read together (a scan) cost one I/O per 66 tuples.

**Measure it.** Insert tuples of 10, 100 and 1,000 bytes until the page is full and print how many fit and what fraction of the page is payload.

## Hints

### Draw the page

Write on paper: header 8, slots 24 each from byte 8, tuples from byte 8192 downward. For three tuples of 100, 50 and 10 bytes, where does each start? The offsets are `8092`, `8042`, `8032`; if your insert gives them, the arithmetic is right.

### Which comparison decides "fits"?

The new tuple starts at `end - len`; the slot array, *with the slot you are about to add*, ends at `8 + 24 * (n + 1)`. The tuple fits if it starts at or after that. The edge case is equality: touching is allowed.

### A refused insert must not touch the page

Compute the offset first and return before changing anything: no slot written, no count changed. The tests check `get_num_tuples()` after a refusal.
