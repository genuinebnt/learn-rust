The three pieces of this module used together, the way the table heap will use them: columns and a schema describe rows, tuples encode them, pages store the tuples at record ids. BusTub has no unit test of a table page on its own (its `tmp_tuple_page_test` is disabled and about a page type that no longer exists), and its `tuple_test` exercises the pages through the table heap, which is module 3c. So this boss is the course's.

## The task

Make `table_page_test` pass: a page filled with tuples of BusTub's `TableHeapTest` schema (`a varchar(20), b smallint, c bigint, d bool, e varchar(16)`) comes back value by value, deleting marks but does not move, an in-place update changes a value, and a **chain of pages** (what the heap is) holds a thousand tuples reachable by rid.

## Tests

- Four tests in `table_page_test.rs` (fill a page and read it back; delete every third tuple; update in place; build and follow a chain of pages).

## Notes

**The chain is the table.** The last test does by hand what `TableHeap::insert_tuple` will do: try the last page, and when it refuses, allocate a new page, link it with `set_next_page_id`, and insert there. The rid it returns is `(page, slot)` and is all a caller needs to get the tuple back.

**What is still missing for a real table.** Pages here are plain byte arrays; the heap's pages live in the buffer pool (module 1) behind guards, so every access takes a latch. That is the next module.

## In BusTub

`test/storage/tmp_tuple_page_test.cpp` ("There are many ways to do this assignment, and this is only one of them. If you don't like the TmpTuplePage idea, please feel free to delete this test case entirely.") and `test/table/tuple_test.cpp` (`TableHeapTest`, module 3c's boss) use these classes.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `TableHeap::InsertTuple` loops over pages in `bpm` | the same loop, with guards (module 3c) |
| `RID{page_id, slot}` | `Rid::new(PageId, u32)` |

## Learn more
- PostgreSQL [heap page layout](https://www.postgresql.org/docs/current/storage-page-layout.html) · [`TableHeapTest`](https://github.com/cmu-db/bustub/blob/master/test/table/tuple_test.cpp)

## Performance

The chain test inserts 1,000 tuples of about 60 bytes: roughly 8 pages. Count how many pages your layout needs for a million of them and what fraction of each page is wasted on slots (24 bytes per tuple) and on the free gap at the end.

**Measure it.** Fill pages with tuples of a mixed schema and print pages used, bytes used and the fraction of the page that is payload.

## Hints

### If the chain test fails

Check what `insert_tuple` returns for a tuple that does not fit: `None`, with the page untouched. The test then starts a new page and links it; a page that was half-written on failure would corrupt the chain.

### If a read after many inserts returns the wrong tuple

Print the slot offsets: they must decrease by each tuple's length. An off-by-one in `get_next_tuple_offset` shows up as overlapping tuples.

### If `get_value` panics on a tuple from the page

The tuple's bytes are a copy of what was inserted; if a string column fails, the stored offset in its slot is relative to the *tuple*, not to the page.
