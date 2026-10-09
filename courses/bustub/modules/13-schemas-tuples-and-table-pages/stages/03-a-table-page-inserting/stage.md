Tuples live in pages, and a page must give each tuple an **address that stays valid**: the record id `(page id, slot number)` is stored in indexes and in undo logs, so a tuple may never move to a different slot, even when its neighbours are deleted. The classic design is the **slotted page**: a small header, an array of slots growing from the front, and the tuples themselves growing from the back; the page is full when they meet. This stage designs and implements the page for inserting: the contract is behaviour, not a byte layout, and the test checks the one thing that matters about a layout: how much it wastes.

> [!CHECK] A page holds slots at the front and tuples at the back, growing toward each other. A tuple is deleted. Why can its space not simply be reused by the next insert, in this design? What does a database do about the wasted space, and when?
> ||The slot number is the tuple's address and indexes point at it; if deletion removed the slot or shifted later tuples, every record id after it would be wrong. So deletion only marks the slot (a flag); the bytes stay. The space is reclaimed later by a **vacuum** or **compaction** that rewrites the page when no transaction can still see the old version, and rewrites the references (or only runs when nothing refers to the dead tuples). This is why MVCC systems need garbage collection (module 4).||
>
> - What would make a slot number change?
> - What does the page do when the slot array and the tuples would overlap?
> - What state must live in the page's bytes?

## The task

`TablePage<B>` is a view over a page's bytes (`B = &[u8]` to read, `&mut [u8]` to change); everything the page knows must live in those bytes, because the buffer pool will write them to disk and read them back. Implement, with the layout of your design:

- `init()`: format a page (no next page, no tuples, none deleted); a recycled page may hold anything.
- `get_num_tuples()` (deleted ones included), `get_num_deleted_tuples()`, `get_next_page_id() -> Option<PageId>` and `set_next_page_id(..)`: the link to the next page of the table.
- `get_next_tuple_offset(meta, tuple) -> Option<u16>`: where the next tuple would go, or `None` if it does not fit; your page's idea of "the offset".
- `insert_tuple(meta, tuple) -> Option<u16>`: stores the tuple and its meta in the next slot and returns the **slot number** (0, 1, 2, ...), or `None` if the tuple does not fit (and then the page is unchanged). `get_next_tuple_offset` and `insert_tuple` agree on whether a tuple fits.

The tests: a fresh page (even on garbage) is empty; slots are consecutive; the next page id survives inserts; a tuple larger than the page is refused and changes nothing; the largest tuple an empty page takes is almost the whole page (overhead under 100 bytes); and a property over tuple sizes 1 to 399: the page fills to **at least `(8192 - 64) / (len + 32)` and at most `8192 / len` tuples**, so your layout may waste no more than a 64-byte header and 32 bytes per tuple.

## Your freedom

The whole layout: header fields, slot size and contents (offset, size, the meta), where tuples go, byte order, whether slots are fixed-size. A slot must hold the tuple's `TupleMeta` (a timestamp and a deleted flag). BusTub's layout (header 8 bytes, slots of 24, tuples from the back) is described in the notes.

## The Rust toolbox

**A view struct over bytes.** `pub struct TablePage<B> { page: B }` and two `impl` blocks: one for `B: AsRef<[u8]>` (reads) and one for `B: AsRef<[u8]> + AsMut<[u8]>` (writes). `TablePage::new(&bytes[..])` is a read-only view; `TablePage::new(&mut bytes[..])` a writable one; a `&[u8; 8192]` array coerces to `&[u8]`.

**Reading and writing integers at offsets.** `u16::from_le_bytes(self.page.as_ref()[at..at + 2].try_into().unwrap())`; `self.page.as_mut()[at..at + 2].copy_from_slice(&v.to_le_bytes())`. Small private helpers (`read_u16`, `write_u16`) keep the layout code readable.

**Checked subtraction for "does it fit".** `slot_end.checked_sub(tuple_len)?` returns `None` instead of underflowing when the tuple is longer than the free space.

**`Option` chains in `insert_tuple`.** `let offset = self.get_next_tuple_offset(meta, tuple)?;`: if there is no room the function returns `None` before touching anything.

**A page is nothing but its bytes.** The test copies the array to another buffer and reads it through a new `TablePage`: if your page keeps anything in a field outside `page`, it breaks.

## If this is new

- [S3 Vec & slices](/t/s3-vec-slices): slicing, `copy_from_slice`, `try_into`.
- [F2 Data layout](/t/f2-data-layout): slotted pages, headers, padding.
- [S1 Option & Result](/t/s1-option-result): `?` on `Option`.
- The optional *slotted pages* concept draws the layout.

## Tests

- A fresh page is empty, whatever it held.
- Tuples get slots 0, 1, 2, ...; the next page id is kept.
- A tuple larger than the page is refused; the page is unchanged; the biggest tuple an empty page takes is nearly a whole page.
- A page fills to within the bounds for every tuple size; `get_next_tuple_offset` and `insert_tuple` agree.
- A refused insert changes nothing.

## Hints

### Draw the page for three tuples

Header, three slots, free space, three tuples from the back. Write the offset of each slot and tuple for lengths 100, 50, 200. Then write the "does the next one fit" rule as an inequality.

### The slot for the new tuple

When you test "fits", remember the *new slot* needs room too: `slots_end = header + slot_size * (n + 1)`.

### Where is "the end of the previous tuple"?

The previous tuple's offset, kept in its slot; for the first tuple, the page size. You do not need a separate "free space pointer" in the header.

## Performance

An insert is two small writes and a copy: tens of nanoseconds plus the tuple's bytes. A page of 100-byte tuples holds about 70; a table of a million such rows is 14 000 pages. The 32-byte per-tuple overhead of BusTub's design is large for small tuples (PostgreSQL's is 4 bytes of line pointer plus a 23-byte header).

**Measure it.** Fill pages with tuples of 10, 100, 1000 bytes and compute the occupancy (tuple bytes over page bytes) for your layout.

## Experiment

Optional. Predict first, then run.

1. **A smaller slot.** Use a 12-byte slot (offset, size, a 4-byte timestamp and a flag packed together). How many more tuples of 20 bytes fit, and what does it cost the timestamp?
2. **A free-space pointer.** Store where the tuples start in the header instead of reading the last slot. Is `insert` faster? What new invariant must you keep?

## Other designs

- **Slotted page, tuples from the back (ours, BusTub's).**
- **Fixed-size records with a bitmap:** no slots; `O(1)` allocation of equal-sized records.
- **Log-structured pages:** append only; compaction rewrites.
- **Column groups in a page** (PAX): the page holds one column after another for a few hundred rows.

## In BusTub

`Column`, `Schema` and `Tuple` are classes in `src/catalog` and `src/storage/table`; `TablePage` is the slotted page in `src/storage/page/table_page.{h,cpp}`. BusTub's `TableHeap` (module 3c) links `TablePage`s into a table.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `class TablePage { char page_start_[0]; }` overlaid on the buffer | `TablePage<B>` over a slice `B` |
| `TupleInfo tuple_info_[0]` flexible array | slot reads and writes at computed offsets |
| `INVALID_PAGE_ID` | `Option<PageId>` |
| `std::optional<uint16_t> InsertTuple(...)` | `Option<u16>` |

**Port rule:** a class overlaid on a page becomes a view over a slice; "no room" is `None`.

## Learn more

- [`usize::checked_sub`](https://doc.rust-lang.org/std/primitive.usize.html#method.checked_sub) · Hellerstein et al., *Architecture of a Database System*, section 5.3 (page layout)
