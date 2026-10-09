---
title: The catalog: the database's own metadata
summary: What a system catalog stores, how a query finds its tables and indexes through it, why oids instead of names, and the choice between an in-memory catalog and one stored in tables.
minutes: 8
---
Before a database can run `SELECT name FROM people WHERE id = 3` it must know that `people` exists, which columns it has and of what types, where its pages are, and whether an index on `id` exists. That knowledge is the **catalog** (also *system catalog*, *data dictionary*, *information schema*). Every statement begins with catalog lookups, and every `CREATE` and `DROP` writes to it.

```svg
caption: The catalog maps names to objects. A table has an oid, a schema, a name and a heap; each index belongs to a table and has its own oid. Executors and plans hold oids and ask the catalog for the object; the binder holds names and turns them into oids.
<svg viewBox="0 0 760 200" role="img" aria-label="A catalog box pointing to a table info and two index infos">
<defs><marker id="ct-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<rect class="box" x="30" y="60" width="150" height="80" rx="3"/><text class="mid fg" x="105" y="92">Catalog</text><text class="mid dim sm" x="105" y="114">names → oids → infos</text>
<rect class="blue" x="270" y="20" width="200" height="80" rx="3"/><text class="mid t-b" x="370" y="48">TableInfo  oid 0</text><text class="mid dim sm" x="370" y="68">name "people"</text><text class="mid dim sm" x="370" y="86">schema · heap</text>
<rect class="live" x="540" y="20" width="190" height="60" rx="3"/><text class="mid fg sm" x="635" y="45">IndexInfo oid 0 "pk"</text><text class="mid dim sm" x="635" y="65">key_attrs [0] · B+ tree</text>
<rect class="live" x="540" y="104" width="190" height="60" rx="3"/><text class="mid fg sm" x="635" y="129">IndexInfo oid 1 "by_score"</text><text class="mid dim sm" x="635" y="149">key_attrs [2] · B+ tree</text>
<path class="ln" d="M180 90 L268 62" marker-end="url(#ct-a)"/><path class="ln" d="M470 50 L538 50" marker-end="url(#ct-a)"/><path class="ln" d="M440 100 C480 130 500 134 538 134" marker-end="url(#ct-a)"/>
</svg>
```

## What it stores

| object | what the catalog keeps |
|---|---|
| **table** | oid, name, schema (column names, types, nullability), where the data is (the heap's first page) |
| **index** | oid, name, owning table, key columns, kind, uniqueness |
| *real systems also:* | views, sequences, constraints, statistics (row counts, histograms for the optimiser), users and permissions, functions |

## Names, oids and who uses which

A **name** is for people (`people`), unique within a namespace, and can be changed with `ALTER ... RENAME`. An **oid** (*object id*) is a number, assigned at creation, never reused, and what plans refer to: renaming a table must not break a stored plan or a view. The *binder* turns names into oids (and errors on unknown names); the *executors* use oids. BusTub keeps the two maps in step: `tables_` by oid and `table_names_` name to oid.

## In memory or in tables?

- **In memory (BusTub).** The catalog is a struct of hash maps, rebuilt empty at startup; tables are gone when the process ends (the data pages persist, the knowledge of what they are does not). Simple, fast, and good enough for a teaching system.
- **In tables (every real database).** The catalog is itself stored as tables (`pg_class`, `pg_attribute`, `sqlite_schema`), so `CREATE TABLE` is an insert into a system table, the catalog survives restarts, is protected by the same transactions and recovery as user data, and can be queried with SQL. The bootstrap problem (to read the catalog table you need the catalog) is solved by hard-coding the first few system tables.

## Concurrency

The catalog is read constantly and written rarely, so a **reader-writer lock** fits: statements share the read lock to resolve names; `CREATE TABLE` takes the write lock for a moment. Real systems also lock the *objects* (a table cannot be dropped while a query reads it); that is part of the lock manager in module 4b.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::unordered_map<table_oid_t, std::shared_ptr<TableInfo>> tables_;` | `HashMap<TableOid, Arc<TableInfo>>` |
| `return NULL_TABLE_INFO;` (a null `shared_ptr`) | `None` |
| `std::atomic<index_oid_t> next_index_oid_` | a counter behind `&mut self` (the engine holds `RwLock<Catalog>`) |
| `const Schema &schema` inside `TableInfo` | `schema: Schema` owned, read through `&info.schema` |

## In real code

### Using it: a catalog of two maps

```rust test
use std::collections::HashMap;
use std::sync::Arc;

struct TableInfo { name: String, oid: u32, columns: Vec<String> }

#[derive(Default)]
struct Catalog {
    tables: HashMap<u32, Arc<TableInfo>>,
    names: HashMap<String, u32>,
    next_oid: u32,
}

impl Catalog {
    fn create_table(&mut self, name: &str, columns: &[&str]) -> Option<Arc<TableInfo>> {
        if self.names.contains_key(name) { return None; }          // check first: no oid is spent on a refusal
        let oid = self.next_oid;
        self.next_oid += 1;
        let info = Arc::new(TableInfo { name: name.to_string(), oid, columns: columns.iter().map(|c| c.to_string()).collect() });
        self.tables.insert(oid, info.clone());
        self.names.insert(name.to_string(), oid);
        Some(info)
    }
    fn get(&self, name: &str) -> Option<Arc<TableInfo>> {
        self.names.get(name).and_then(|oid| self.tables.get(oid)).cloned()
    }
    fn get_by_oid(&self, oid: u32) -> Option<Arc<TableInfo>> { self.tables.get(&oid).cloned() }
}

#[test]
fn a_table_is_found_by_name_and_by_oid_and_is_the_same_object() {
    let mut c = Catalog::default();
    let made = c.create_table("people", &["id", "name"]).unwrap();
    let by_name = c.get("people").unwrap();
    let by_oid = c.get_by_oid(made.oid).unwrap();
    assert!(Arc::ptr_eq(&made, &by_name) && Arc::ptr_eq(&by_name, &by_oid));
    assert_eq!(by_oid.columns, ["id", "name"]);
    assert!(c.get("nobody").is_none() && c.get_by_oid(9).is_none());
}

#[test]
fn oids_count_up_and_a_duplicate_name_spends_none() {
    let mut c = Catalog::default();
    assert_eq!(c.create_table("a", &[]).unwrap().oid, 0);
    assert!(c.create_table("a", &["x"]).is_none(), "the name is taken");
    assert_eq!(c.create_table("b", &[]).unwrap().oid, 1, "the refusal did not use oid 1");
    assert_eq!(c.get("a").unwrap().columns.len(), 0, "the refused create changed nothing");
}
```

### In the exercises

- **3c-04:** `create_table`, `get_table` and `get_table_by_oid` are these three functions with a `TableHeap` inside the info.
- **3c-04:** `create_index` adds a second pair of maps (`indexes`, and `index_names` keyed by table then index name) and *populates* the new index from the heap.
- **Module 3d:** the binder asks the catalog for the table and its schema to resolve column references; `CREATE TABLE` in SQL ends in `create_table`.

### Where it is used

- **PostgreSQL**: `pg_class`, `pg_attribute`, `pg_index` (oids are visible: `SELECT 'people'::regclass::oid`); the catalog is cached per backend and invalidated by messages when another session changes it.
- **SQLite**: `sqlite_schema` holds the original `CREATE` text of every object; opening a database re-parses it.
- **MySQL**: the *data dictionary* (InnoDB tables since 8.0); `information_schema` presents it as views.
- **BusTub / DuckDB / DataFusion**: in-memory catalogs of hash maps, DuckDB's persisted through its own storage.
