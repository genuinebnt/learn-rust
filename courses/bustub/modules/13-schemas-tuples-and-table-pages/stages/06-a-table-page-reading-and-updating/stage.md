The rest of the page's API: read a tuple back by its slot number, read just its metadata, mark it deleted, and overwrite it in place. Together with the previous stage this is the whole interface the table heap (module 3c) uses; the heap adds only "which page?".

**Where this fits.** A tuple's address, a **record id** `Rid(page_id, slot_num)`, is the pair of a page and a slot. Because a slot's tuple never moves, an index (module 2) can store a rid and find the row years later, however many other rows were inserted or deleted.

## The task

In `src/storage/page/table_page.rs`:
- `get_tuple(rid) -> Result<(TupleMeta, Tuple)>`: an error ("Tuple ID out of range") for a slot number `>= num_tuples`; otherwise the slot's metadata and a copy of its bytes as a `Tuple` carrying `rid`;
- `get_tuple_meta(rid) -> Result<TupleMeta>`;
- `update_tuple_meta(meta, rid) -> Result<()>`: replace the metadata (offset and size kept); if the tuple was live and the new metadata says deleted, count one more in `num_deleted_tuples` (a tuple already deleted is **not** counted twice);
- `update_tuple_in_place_unsafe(meta, tuple, rid) -> Result<()>`: the same checks and counting, plus the tuple must have **exactly the slot's size** ("Tuple size mismatch" otherwise) and its bytes overwrite the old ones. "Unsafe" because nothing here stops two writers: the caller holds the page's write latch.

## Tests

- A tuple and its meta come back by slot, with the tuple knowing its rid; a slot past the last tuple is an error from all four functions (never a panic).
- Marking deleted counts once and keeps the bytes and the slot; a same-length replacement changes the bytes (and only those) and can delete; a different length is refused and nothing changes (not even the deleted count).

## Syntax and methods

```rust
let id = rid.slot_num();
if id >= self.get_num_tuples() { return Err(Exception::new(ExceptionType::Invalid, "Tuple ID out of range")); }
let (offset, size, old) = self.slot(id);
if !old.is_deleted && meta.is_deleted { /* one more deleted tuple */ }
Ok((meta, Tuple::from_bytes(rid, &self.bytes()[offset as usize..offset as usize + size as usize])))
```

## Notes

**Errors, not panics.** A bad slot number is a runtime condition (a stale rid, a deleted-and-reused page), not a bug in the page code, so it is an `Err` the caller can handle; BusTub throws an `Exception` for the same cases.

**Deleting is a flag.** Nothing is erased: `is_deleted` is set and the slot stays. A scan skips deleted tuples (module 3b), the bytes are overwritten only if the slot is reused (never, in this format), and an `UPDATE` in module 3b is "delete the old, insert the new" or an in-place overwrite when the size allows. Module 4's transactions need exactly this: an old version of a row that is "deleted" for new readers must still be readable by old ones.

**Why in-place update needs the same size.** The tuple is wedged between its neighbours: more bytes would overwrite the previous tuple, fewer would leave a hole that nobody can use. A different-size update is not an in-place operation; the heap's callers handle it by inserting a new tuple.

**`ts` in the meta** is the transaction timestamp of module 4; module 3 always writes 0.

## In BusTub

`table_page.cpp`: `GetTuple` ("if (tuple_id >= num_tuples_) { throw bustub::Exception("Tuple ID out of range"); }"), `UpdateTupleMeta` ("if (!old_meta.is_deleted_ && meta.is_deleted_) { num_deleted_tuples_++; }") and `UpdateTupleInPlaceUnsafe` ("if (size != tuple.GetLength()) { throw bustub::Exception("Tuple size mismatch"); }").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `throw bustub::Exception("Tuple ID out of range")` | `return Err(Exception::new(..))` |
| `auto &[offset, size, meta] = tuple_info_[tuple_id];` (structured binding by reference) | `let (offset, size, meta) = self.slot(id);` (a decoded copy) |
| `std::pair<TupleMeta, Tuple>` | `(TupleMeta, Tuple)` |
| `memmove(tuple.data_.data(), page_start_ + offset, size)` | `Tuple::from_bytes(rid, &bytes[offset..offset + size])` |

**Port rule:** a structured binding to an array element in a page becomes a small decode function returning a value; writes go back through a `set_slot`.

## Learn more
- [`Result`](https://doc.rust-lang.org/std/result/index.html) · [`slice::copy_from_slice`](https://doc.rust-lang.org/std/primitive.slice.html#method.copy_from_slice) · PostgreSQL's [`HEAP_XMAX` and dead tuples](https://www.postgresql.org/docs/current/storage-page-layout.html)

## Performance

Every function is `O(1)` apart from the copy of the tuple's bytes (`O(size)`). `get_tuple` copies the tuple out of the page, which keeps the page unlatched quickly (the caller can drop the guard before using the tuple); a version returning a borrowed slice is faster and ties the tuple's lifetime to the latch.

**Measure it.** Read the same slot a hundred million times with `get_tuple` and with a slice-returning variant you write; compare.

## Hints

### Check the slot first, in all four functions

The test for the error is the same in each: put it in a helper if you like. A slot number equal to `num_tuples` is already out of range (slots are `0..num_tuples`).

### Count the transition, not the state

`num_deleted_tuples` goes up when a live tuple becomes deleted, not whenever the new meta says deleted. Read the old meta before writing the new one.

### Refuse before you write

In `update_tuple_in_place_unsafe`, do every check (slot, size) before changing the count, the metadata or the bytes. The test "a refused update does not mark anything deleted" catches an implementation that bumped the counter first.
