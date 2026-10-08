The index half of the catalog. `CREATE INDEX` must (1) build an index over some columns of an existing table, (2) **fill it with the rows the table already has**, and (3) remember it so that later `INSERT`s, `UPDATE`s and `DELETE`s (module 3b) can keep it current and the optimiser (module 3c) can find it.

## The task

In `src/catalog/catalog.rs`:
- `create_index(index_name, table_name, key_attrs, is_primary_key) -> Result<Option<Arc<IndexInfo>>>`:
  - `Ok(None)` if the table does not exist, or the table already has an index with that name;
  - an error unless every key column is an `Integer` ("only support creating index on integer column"), the key has at least one column ("Index columns cannot be empty") and at most 64 bytes (16 integers: "Unsupported: index key size exceeds 64 bytes");
  - the key size is `4 * columns`; build a `BPlusTreeIndex<N>` with `N` the smallest of 4, 8, 16, 32, 64 that fits, boxed as `dyn Index`;
  - **populate**: for every tuple of the table that is not deleted, `insert_entry(tuple.key_from_tuple(table_schema, key_schema, key_attrs), rid)`; a key already present is ignored (the tree's keys are unique);
  - take the next index oid (0, 1, ...), remember the `IndexInfo` by oid and by `(table, name)`;
- `get_index(index_name, table_name)`, `get_index_by_oid(oid)`: the info or `None`;
- `get_table_indexes(table_name)`: the table's indexes in creation order (none for an unknown table).

## Tests

- A new index is filled from the table (lookups by key find the right rows); deleted rows are not indexed; a duplicate key keeps the first row.
- A missing table or a taken name is `Ok(None)` (names are per table); a `VARCHAR` or `DECIMAL` column, no columns, or 17 integers is an error and 16 is accepted with key size 64.
- Lookups by name, by oid and by table (in creation order); a composite index over `(i % 10, i)` scans in that order.

## Syntax and methods

```rust
let index: Box<dyn Index + 'a> = match key_size {
    1..=4 => Box::new(BPlusTreeIndex::<4>::new(metadata, self.bpm)),
    5..=8 => Box::new(BPlusTreeIndex::<8>::new(metadata, self.bpm)),
    /* 9..=16, 17..=32, 33..=64 */
    _ => return Err(Exception::new(ExceptionType::NotImplemented, "...")),
};
for (meta, tuple) in table.table.make_iterator() { if !meta.is_deleted { index.insert_entry(&key, tuple.get_rid()); } }
```

## Notes

**Populate with a snapshot iterator.** `make_iterator()` (stage 3) sees the table as it is when the loop starts, which is exactly what "build the index from the current rows" means. (Concurrent inserts during an index build are a real problem in real systems; BusTub's catalog does not handle them, nor does this course.)

**Runtime choice of a compile-time size.** `BPlusTreeIndex<const N: usize>` has a size known to the compiler, but the key size here is known only when `CREATE INDEX` runs. The `match` instantiates the five sizes at compile time and picks one at run time; the result is boxed as `dyn Index` so the caller sees one type. This is the standard way to bridge "generic over a number" and "decided by data".

**Error or `None`?** The two failures are different in kind. A missing table or a taken name is something the *statement* got wrong in a way the binder reports in its own words, so it is the unremarkable `None`. A column of the wrong type or a key that is too big is a limit of the engine: a real `Err` that aborts the statement.

**Who keeps the index current?** Not the catalog. `create_index` fills it once; module 3b's insert, update and delete executors call `insert_entry`/`delete_entry` on every index of the table (`get_table_indexes`) for each row they change.

## In BusTub

`catalog.h` (`CreateIndex`: "Reject the creation request for nonexistent table ... Determine if the requested index already exists for this table ... Populate the index with all tuples in table heap: for (auto iter = table_meta->table_->MakeIterator(); !iter.IsEnd(); ++iter) { auto [meta, tuple] = iter.GetTuple(); // we have to silently ignore the error here for a lot of reasons... index->InsertEntry(tuple.KeyFromTuple(schema, key_schema, key_attrs), tuple.GetRid(), txn); }") and `bustub_ddl.cpp` (`HandleIndexStatement`: the key size ladder 4, 8, 16, 32, 64 and "only support creating index on integer column").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `if (key_size <= 4) { CreateIndex<GenericKey<4>, RID, GenericComparator<4>>(...) } else if (key_size <= 8) { ... }` | `match key_size { 1..=4 => Box::new(BPlusTreeIndex::<4>::new(..)), 5..=8 => ... }` |
| `throw NotImplementedException("...")` | `Err(Exception::new(ExceptionType::NotImplemented, ".."))` |
| `return NULL_INDEX_INFO;` | `Ok(None)` |
| a template member function taking `KeyType`, `ValueType`, `KeyComparator` | const generic `N` fixed by the `match` |

**Port rule:** "return null for not found, throw for impossible" becomes `Result<Option<T>>`: `Err` for impossible, `Ok(None)` for not found.

## Learn more
- [Trait objects](https://doc.rust-lang.org/book/ch18-02-trait-objects.html) · [`Result<Option<T>>`](https://doc.rust-lang.org/std/result/index.html#iterating-over-option-and-result) · PostgreSQL [`CREATE INDEX`](https://www.postgresql.org/docs/current/sql-createindex.html)

## Performance

Building an index by inserting rows one at a time is `O(n log n)` page reads and writes; production systems sort the keys first and build the tree bottom-up (a bulk load), which is `O(n)` and produces fuller pages. For this course's sizes it does not matter; for a billion rows it is the difference between hours and minutes.

`get_table_indexes` runs for every row an insert, update or delete touches; it sorts a handful of oids, so keep the lists short or store the indexes of a table as a `Vec` in creation order to begin with.

**Measure it.** Create an index over 1,000,000 rows and time it; then insert the same keys sorted ascending versus shuffled into an empty index and compare the number of leaf pages afterwards (module 2c's fill-factor result).

## Hints

### Decide before you build

Do every check (table, name, column types, size) before allocating the index's pages and before spending an oid, so a failed creation leaves the catalog as it was.

### The key tuple needs the *key* schema

`tuple.key_from_tuple(&table.schema, &key_schema, &key_attrs)` reads the table's columns by the table's offsets and writes the key under the key schema's. Passing the table schema twice gives garbage keys for any index that is not on the first columns.

### Skip deleted rows

A tuple that is marked deleted still occupies its slot (module 3b) and the iterator returns it. Indexing it would make a lookup find a row that is gone; the test `deleted_rows_are_not_indexed` covers it.
