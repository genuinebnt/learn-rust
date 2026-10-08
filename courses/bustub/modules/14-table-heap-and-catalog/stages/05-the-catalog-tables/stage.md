The **catalog** is the database's own metadata: which tables exist, what their schemas are, where their heaps are, which indexes exist. Every statement starts with the catalog (`SELECT ... FROM t1` resolves `t1`), and every executor holds a reference to it. BusTub's is **in memory**: it is rebuilt empty each time the engine starts (a persistent catalog would be stored in tables of its own, as PostgreSQL's `pg_class` and SQLite's `sqlite_schema` are).

This stage is the table half: create a table, look it up by name or by number.

## The task

In `src/catalog/catalog.rs` (the struct, `TableInfo`, `IndexInfo` and the oid types are given):
- `create_table(name, schema) -> Option<Arc<TableInfo>>`: `None` if the name is in use; otherwise take the next **table oid** (0, 1, 2, ... in creation order; a refused creation uses none), build the `TableInfo` with a new `TableHeap`, remember it by oid and by name, and give the table an (empty) set of indexes;
- `get_table(name)` and `get_table_by_oid(oid)`: the shared info, or `None`;
- `get_table_names()`: every table's name (no particular order).

## Tests

- A created table is found by name and by oid and is the *same* `Arc`; unknown names and oids give `None`.
- Oids count up from 0 in creation order; a duplicate name is refused without using an oid; the names list; each table has its own heap (different first pages, independent contents).
- A new catalog has no tables; names are compared exactly (`People` and `people` are two tables); 100 tables are each found by name and by oid.

## Syntax and methods

```rust
let oid = self.next_table_oid; self.next_table_oid += 1;
let info = Arc::new(TableInfo { schema: schema.clone(), name: name.to_owned(), table: TableHeap::new(self.bpm), oid });
self.tables.insert(oid, info.clone());                      // Arc::clone: a second owner, not a copy of the table
self.table_names.get(name).and_then(|oid| self.tables.get(oid)).cloned()   // Option<&Arc<..>> -> Option<Arc<..>>
```

## Notes

**Two maps, one truth.** Tables are stored by oid (`tables`) and found by name through `table_names`. Plans and executors refer to a table by *oid* (a number is stable and cheap to compare), users by name; the catalog converts. Keeping the maps consistent (both updated, in one place) is the catalog's invariant; module 3c's tests check it from the outside.

**`Option`, not an exception.** "Does this table exist?" is an ordinary question with an ordinary "no" answer, so `get_table` returns `Option`. The *binder* (given) turns a `None` into the error message `table not found`; the catalog does not decide what a missing table means.

**`Arc` because executors share.** Several executors of one query may hold the same `TableInfo`; they read its schema and use its heap, and nobody mutates the info. `Arc<TableInfo>` is a shared, immutable view, and the catalog's own map keeps the table alive for the whole instance.

**Reserved names.** BusTub reserves names starting with `__` for system tables (`__mock_table_1` and friends exist for tests); the catalog itself does not enforce it, the binder does.

## In BusTub

`catalog.h`: `CreateTable` ("if (table_names_.count(table_name) != 0) { return NULL_TABLE_INFO; } ... const auto table_oid = next_table_oid_.fetch_add(1); auto meta = std::make_shared<TableInfo>(schema, table_name, std::move(table), table_oid); tables_.emplace(table_oid, meta); table_names_.emplace(table_name, table_oid); index_names_.emplace(table_name, std::unordered_map<std::string, index_oid_t>{});") and the two `GetTable` overloads.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::shared_ptr<TableInfo>` and `NULL_TABLE_INFO` (a null `shared_ptr`) | `Arc<TableInfo>` and `Option::None` |
| `std::atomic<table_oid_t> next_table_oid_; fetch_add(1)` | a plain counter: creation takes `&mut self` (the instance holds the catalog behind a lock) |
| `std::unordered_map` | `HashMap` |
| `static inline const std::shared_ptr<TableInfo> NULL_TABLE_INFO{nullptr};` | `None` |

**Port rule:** a sentinel null pointer meaning "not found" becomes `Option`; `shared_ptr` becomes `Arc`.

## Learn more
- [`HashMap`](https://doc.rust-lang.org/std/collections/struct.HashMap.html) · [`Arc`](https://doc.rust-lang.org/std/sync/struct.Arc.html) · PostgreSQL [system catalogs](https://www.postgresql.org/docs/current/catalogs.html) · SQLite's [schema table](https://www.sqlite.org/schematab.html)

## Performance

A lookup is a hash lookup (`O(1)`) and an `Arc` clone (an atomic increment); creating a table allocates a page. The catalog is read on every statement, so lookups must be cheap, and written rarely, so a coarse lock (the instance's `RwLock<Catalog>`) is fine: many statements read at once, `CREATE TABLE` takes the write lock.

**Measure it.** Look up one of 1,000 tables 10 million times by name and by oid and compare.

## Hints

### Keep the maps in step

Add the table to `tables`, to `table_names`, and give it an entry in `index_names`, in that order, after you have checked the name. If you update one map and return early, `get_table` and `get_table_by_oid` disagree.

### The oid is spent only on success

Check for the duplicate name first, then take the oid. The test "a refused creation does not use an oid" creates a table after a refusal and expects the next number.

### Clone the `Arc`, not the table

`tables.insert(oid, info.clone())` and return `info`: two handles to the same `TableInfo`. The test checks pointer equality with `Arc::ptr_eq`.
