BusTub's `tuple_test.cpp`: the one test of this module that BusTub ships, `TableHeapTest`. It builds a table of the schema `a varchar(20), b smallint, c bigint, d bool, e varchar(16)`, inserts the same tuple 5,000 times through a 50-frame buffer pool, and walks the table with an iterator. This port also checks what the C++ test only prints (every rid is returned, every tuple is read back equal), and adds a second test that goes from a catalog to rows to an index and back.

## The task

Make `tuple_test` pass (`cargo test --test tuple_test`): `table_heap_test` (the port) and `a_table_and_an_index_through_the_catalog` (the course's: 2,000 rows, a primary-key index and a non-unique one, point lookups index to rid to tuple, and an ordered full index scan).

## Tests

- `tuple_test.rs`: 2 tests.

## Notes

**What the second test shows.** It is the whole path of a point query, `SELECT name FROM people WHERE id = 999`, minus the SQL: catalog lookup, index lookup, heap fetch, tuple decode. Module 3b's `IndexScan` and `SeqScan` executors are loops around these calls.

**The non-unique column.** Indexing `score` (50 distinct values over 2,000 rows) keeps one row per value: the test asserts `50`, documenting the engine's limitation rather than hiding it.

## In BusTub

`test/table/tuple_test.cpp` (`TEST(TupleTest, DISABLED_TableHeapTest)`: "std::string create_stmt = "a varchar(20), b smallint, c bigint, d bool, e varchar(16)"; ... for (int i = 0; i < 5000; ++i) { auto rid = table->InsertTuple(TupleMeta{0, false}, tuple); ...").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto *disk_manager = new DiskManager(db_fname); remove(db_fname);` | `Arc::new(DiskManagerUnlimitedMemory::new())`: nothing to clean up |
| `TableIterator itr = table->MakeIterator(); while (!itr.IsEnd()) { ++itr; }` | `while !itr.is_end() { itr.advance(); }`, or `for (meta, t) in table.make_iterator()` |
| `delete table; delete buffer_pool_manager;` | values drop at the end of the scope, in reverse order |

## Learn more
- [`tuple_test.cpp`](https://github.com/cmu-db/bustub/blob/master/test/table/tuple_test.cpp)

## Performance

5,000 tuples of about 40 bytes fill roughly 30 pages; the whole test runs in milliseconds in memory. Run it with a file-backed disk manager (module 1a) and a pool of 50 frames and time the insert and the scan separately: the scan reads each page once, in order; the insert writes each page once (when it is evicted or flushed).

**Measure it.** Print pages used, time to insert and time to scan, for 5,000, 50,000 and 500,000 tuples.

## Hints

### If the iteration count is off by one

The last tuple of the last page is the one most often lost: check `advance` at "no next page" and at a stopping rid that is the end of a full page.

### If the catalog test fails on the index scan

The scan must return rids in *key order*: if ids come back in the wrong order the comparator is comparing bytes instead of values (stage 4).

### If a lookup finds the wrong row

The index stores rids; a rid is only stable if the table's tuples never move (module 3b). If a lookup returns a row of another id, the key tuple was built with the wrong schema (stage 4's last hint).
