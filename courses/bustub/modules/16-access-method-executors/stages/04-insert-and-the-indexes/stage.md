`create index t_a on t(a)` builds an index from the rows that exist *now* (the catalog did that in module 3c). It is only worth having if the rows that arrive *later* get into it too. This stage makes the insert executor keep every index of the table in step: a second copy of part of each row, written at the same moment.

## The task

In `src/execution/executors/insert_executor.rs`, `insert_into_indexes(tuple, rid)` (called by `next` for every inserted tuple, with the rid `insert_tuple` returned):
- for each index in `self.indexes`, build the **key tuple** for the row, `tuple.key_from_tuple(&table_schema, &index.key_schema, index.index.metadata().get_key_attrs())`, and add it: `index.index.insert_entry(&key, rid)`;
- a refused insert (the key is already there: the `bool` returned is `false`) is ignored.

## Tests

- After `insert`, an index lookup of each key finds exactly one rid, and the row at that rid is the inserted row; missing keys find nothing.
- All indexes of the table are updated: single-column, a second index on another column, a composite `(a, b)` (and `(b, a)` is a different key).
- The primary-key index created by `primary key` is an index like the others.
- A duplicate key keeps the first row in the index while both rows are in the table.
- An index created after some inserts has those rows and later inserts join them; the indexes of other tables are untouched.

## Syntax and methods

```rust
for index in &self.indexes {                                   // Vec<Arc<IndexInfo>>
    let key = tuple.key_from_tuple(&self.table_info.schema, &index.key_schema, index.index.metadata().get_key_attrs());
    index.index.insert_entry(&key, rid);                       // false if the key was already there
}
```

## Notes

**Which schema for what.** `key_from_tuple(table_schema, key_schema, key_attrs)` reads the columns `key_attrs` out of a tuple laid out by the *table* schema and writes them in a tuple laid out by the *key* schema. For an index on `(b)` of a table `(a, b, c)` the key has one column even though `b` is the table's second.

**An index never fails the insert.** BusTub's indexes keep one entry per key, so a duplicate is refused with `false`; the catalog and the executors "silently ignore the error". The table keeps both rows and the index remembers the first (the tests document it). A real unique index would abort the statement.

**The index is not the truth.** The table is. A lookup that finds a rid must still check the row (stage 7); an index that missed an entry only makes some rows unfindable by key, it never makes a row disappear from a scan.

## In BusTub

`catalog.h`'s `CreateIndex` ("Populate the index with all tuples in table heap ... `index->InsertEntry(tuple.KeyFromTuple(schema, key_schema, key_attrs), tuple.GetRid(), txn);` ... we have to silently ignore the error here for a lot of reasons") and the project's insert contract: indexes are updated on every write.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `for (auto &index_info : catalog->GetTableIndexes(table_info_->name_))` per call | fetch the indexes once in `new`, keep `Vec<Arc<IndexInfo>>` |
| `index_info->index_->InsertEntry(key, rid, txn)` through a virtual base `Index` | `index.index.insert_entry(&key, rid)` through `Box<dyn Index>` |
| ignoring a `bool` return silently | `let _ = ...` or a bare call; the unused `bool` is deliberate |

**Port rule:** a loop over the table's indexes with a virtual `InsertEntry` is a loop over `Arc<IndexInfo>` calling a trait method.

## Learn more
- [Trait objects](https://doc.rust-lang.org/book/ch18-02-trait-objects.html) · PostgreSQL [index types](https://www.postgresql.org/docs/current/indexes-types.html) · [Use The Index, Luke](https://use-the-index-luke.com/sql/dml/insert)

## Performance

Every index adds a B+ tree insert (module 2c) to every row insert: a table with five indexes writes six structures per row. That is the reason not to index everything: indexes speed up reads and slow down writes, and a bulk load often drops its indexes first and rebuilds them at the end.

**Measure it.** Insert 100,000 rows into a table with 0, 1 and 3 indexes and compare.

## Hints

### Key from the table's schema, laid out with the key's

Passing the *table* schema twice, or the key schema twice, happens to work for an index on the first column and fails for the second. The composite index test catches it.

### Use the rid you were given

`insert_tuple` returns the new row's rid; that is what the index must store. Do not look the row up again.

### Ignore the refusal, deliberately

`insert_entry` returning `false` is not an error here. Do not `unwrap` it or turn it into an `Err`.
