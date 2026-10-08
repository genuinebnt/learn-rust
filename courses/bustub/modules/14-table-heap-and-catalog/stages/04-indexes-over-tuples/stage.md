Module 2c built a B+ tree of fixed-size byte keys. A database index is something more specific: *the indexed columns of a row*, as a tuple, mapped to the row's rid. This stage is the adapter between the two worlds: an `Index` trait the executors talk to (they never see a B+ tree), a key tuple converted to the tree's fixed-size key, and a **comparator** that orders those key bytes by their *column values* (a plain byte comparison would sort `-3` after `2`, and compare the first column's bytes before looking at the second).

## The task

In `src/storage/index/index.rs` (the `Index` trait, `IndexType`, `key_to_value` and the struct definitions are given):
- `IndexMetadata::new(name, table_name, tuple_schema, key_attrs, is_primary_key)`: remember them; the **key schema** is the table schema restricted to `key_attrs` (`Schema::copy_schema`), shared in an `Arc`;
- `generic_key_from_tuple::<N>(tuple) -> GenericKey<N>`: a zeroed key with the tuple's bytes at the start (a tuple longer than `N` is a bug: panic);
- `SchemaComparator<N>::compare(lhs, rhs)`: for each column of the key schema, read both values (`key_to_value`) and compare; the first column that differs decides; all equal is `Equal`;
- `BPlusTreeIndex::<N>::new(metadata, bpm)`: allocate the tree's header page and build a `BPlusTree<GenericKey<N>, Rid, SchemaComparator<N>>` with the default node sizes;
- the `Index` methods over the tree: `insert_entry` (false for a key already present), `delete_entry`, `scan_key` (the rid, or none), `scan_all` (every rid in key order) and `scan_from(key)` (from the first key not less than it).

## Tests

- The metadata's key schema and offsets (the key's, not the table's); a key tuple becomes the bytes `[4, 3, 2, 1]` of `0x01020304` (little-endian, zero padded); a key longer than the index key panics.
- The comparator orders column by column as **numbers** (`(-3, 0) < (2, 0)`, `(1, 6) < (2, 0)`).
- An index of 500 keys inserts, scans, refuses a duplicate and deletes; composite and negative keys scan in key order, and `scan_from` starts at the right key.

## Syntax and methods

```rust
let mut key = GenericKey::<N>::default();                       // zeros
key.data[..tuple.data().len()].copy_from_slice(tuple.data());
Value::deserialize_from(&key.data[column.offset() as usize..], column.type_id())
l.compare_less_than(&r)? == CmpBool::True                       // the Value comparison of module 3a
self.tree.begin().map(|(_, rid)| rid).collect()                 // the tree's iterator yields (key, rid)
pub trait Index: Send + Sync { fn insert_entry(&self, key: &Tuple, rid: Rid) -> bool; /* ... */ }
```

## Notes

**Why not compare bytes.** A key is a tuple's bytes: integers in little-endian two's complement. Compared as bytes, `1` (`01 00 00 00`) sorts after `256` (`00 01 00 00`) and every negative number sorts after every positive one. Ordering must come from the *values*, which is why the comparator needs the schema: it rebuilds each column's value from the key bytes and compares those with module 3a's `Value` comparison. (Production systems solve this with order-preserving key encodings, e.g. big-endian with the sign bit flipped, so a `memcmp` is enough.)

**A trait, so the executors need not know `N`.** The tree is generic over the key size (4, 8, 16, 32 or 64 bytes); a catalog holds indexes of different sizes in one map. `dyn Index` hides `N`: the catalog stores `Box<dyn Index>` and executors call `insert_entry` and `scan_key`. This is C++'s virtual `Index` base class with `BPlusTreeIndex<GenericKey<N>, RID, GenericComparator<N>>` as the derived classes.

**Keys are unique.** The B+ tree refuses a duplicate key, so a **non-unique** column indexes only its first row per value; BusTub's catalog "silently ignores the error". A primary key is unique by definition; this is a limitation of the course's engine, noted again when the catalog fills an index.

**Only integers.** BusTub's `CREATE INDEX` accepts INTEGER columns only (`only support creating index on integer column`): the keys are `4 * columns` bytes, small and inlined, and the comparator needs no varlen handling.

## In BusTub

`index.h` (`IndexMetadata`: "key_schema_ = std::make_shared<Schema>(Schema::CopySchema(tuple_schema, key_attrs_));", and the `Index` base class with `InsertEntry`, `DeleteEntry`, `ScanKey`), `b_plus_tree_index.cpp` (`KeyType index_key; index_key.SetFromKey(key); return container_->Insert(index_key, rid);`), `generic_key.h` (`SetFromKey`, `ToValue`, and `GenericComparator::operator()`: "if (lhs_value.CompareLessThan(rhs_value) == CmpBool::CmpTrue) { return -1; } ...").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `class Index { virtual InsertEntry(...) = 0; }` and `BPlusTreeIndex<KeyType, ...> : public Index` | `trait Index` and `impl<const N: usize> Index for BPlusTreeIndex<'_, N>` |
| `template class BPlusTreeIndex<GenericKey<4>, RID, GenericComparator<4>>;` (explicit instantiations) | a generic `N` instantiated at the call site (`BPlusTreeIndex::<4>`) |
| `KeyType index_key; index_key.SetFromKey(key);` | `generic_key_from_tuple::<N>(key)` |
| `std::unique_ptr<Index>` | `Box<dyn Index + 'a>` |

**Port rule:** an abstract base class with a few concrete implementations becomes a trait; the vtable is `dyn Trait`.

## Learn more
- [Trait objects](https://doc.rust-lang.org/book/ch18-02-trait-objects.html) · [Const generics](https://doc.rust-lang.org/reference/items/generics.html#const-generics) · [Order-preserving key encodings (memcomparable)](https://en.wikipedia.org/wiki/Lexicographic_order)

## Performance

An index operation is a B+ tree operation (module 2c: `O(log n)` page reads) plus the key conversion, which costs a copy of at most 64 bytes, and the comparator, which decodes up to `columns` values per comparison: a binary search over a 500-entry leaf does about 9 comparisons, each decoding two keys. That is the price of a schema-aware comparator; an order-preserving encoding would make it a `memcmp`.

**Measure it.** Insert 100,000 integer keys and look all of them up through the index; then replace the comparator by one that compares the first 4 bytes as `i32` and see how much of the time was the generic value comparison.

## Hints

### The key schema decides the offsets

The comparator reads a column at the *key schema's* offset, not the table's. Build the key tuple with `key_from_tuple(table_schema, key_schema, key_attrs)` (module 3b) and compare with `key_schema`.

### Compare with the value type

`Value::compare_less_than` returns a `Result<CmpBool>`; keys are never NULL (index keys are inlined integers, and NULL is `i32::MIN`: a NULL key would sort as a value in the tree: module 3b's executors reject NULL keys), so unwrap or handle the `Null` case as you see fit.

### The tree's iterator yields `(key, rid)`

`scan_all` is `tree.begin().map(|(_, rid)| rid).collect()`; `scan_from` is the same from `begin_at`.
