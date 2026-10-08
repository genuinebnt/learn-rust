A **schema** is an ordered list of columns, and with it the **layout** of a tuple: which byte of a tuple belongs to which column. Everything that reads or writes a tuple goes through this layout, so the schema's one real job is arithmetic: give each column its offset.

The layout has two parts. The **fixed part** has one slot per column, in order: an inlined column (a number, a boolean) stores its value right there; a `VARCHAR` stores a 4-byte **offset** pointing into the second part. The **variable part** holds the strings, one after another.

```text
| a: INTEGER (4) | b: VARCHAR slot (4) | c: BIGINT (8) | d: VARCHAR slot (4) | "b's string" | "d's string" |
0                4                     8               16                    20
```

## The task

In `src/catalog/schema.rs` (fields and the plain accessors are given):
- `Schema::new(columns)`: walk the columns in order keeping a running offset; give each its offset (`Column::set_offset`); an inlined column advances the offset by its storage size, a `VARCHAR` by **4**; remember the indexes of the `VARCHAR` columns; the final offset is the schema's `length` (the size of the fixed part); the schema is inlined if there are no `VARCHAR`s;
- `copy_schema(from, attrs)`: a new schema of the columns `from[attrs[0]]`, `from[attrs[1]]`, ... **with new offsets**;
- `try_col_idx(name)` (the first column with that name) and `col_idx(name)` (a missing column is a panic);
- `to_string(simplified)`: `(a:INTEGER, b:VARCHAR(20))`, or `Schema[NumColumns:2, IsInlined:0, Length:8] :: (Column[...], Column[...])`.

## Tests

- A five-column mixed schema: offsets `[0, 4, 8, 16, 20]` and fixed length 21; the `VARCHAR` indexes; a fixed-size-only schema is "inlined".
- Lookup by name (first match, missing), `copy_schema` recomputing offsets and leaving the source alone, both printed formats, an empty schema.

## Syntax and methods

```rust
let mut offset = 0u32;
for (index, mut column) in columns.into_iter().enumerate() {   // into_iter: we own the columns, so we can change them
    column.set_offset(offset);
    offset += if column.is_inlined() { column.storage_size() } else { 4 };
}
attrs.iter().map(|&i| from.columns[i as usize].clone()).collect()
self.columns.iter().position(|c| c.name() == name)              // first match, as an Option<usize>
```

## Notes

**Offsets belong to a schema, not a column.** The same `Column` has a different offset in different schemas: column `c` is at 8 in the table's schema and at 0 in an index's key schema. That is why `copy_schema` must go through `Schema::new` again and why `Column::new` starts at 0.

**Why a `VARCHAR` takes exactly 4 bytes in the fixed part.** The fixed part must be fixed: every tuple of a schema has the same offsets, so reading column `k` is one addition, no scanning. The string's real size varies per tuple, so it goes elsewhere and the fixed slot stores *where*. This is the "fixed part plus heap" layout of almost every row store (PostgreSQL's varlena, SQLite's record header).

**Names can repeat.** A join's output schema has two columns called `id`. Lookup by name returns the first; later modules look up by position after the planner has resolved names, so the first-match rule rarely matters.

## In BusTub

`schema.cpp`: "Schema::Schema(const std::vector<Column> &columns) { uint32_t curr_offset = 0; for (uint32_t index = 0; index < columns.size(); index++) { ... if (!column.IsInlined()) { tuple_is_inlined_ = false; uninlined_columns_.push_back(index); } column.column_offset_ = curr_offset; if (column.IsInlined()) { curr_offset += column.GetStorageSize(); } else { curr_offset += sizeof(uint32_t); } ..." and `Schema::ToString`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `class Schema { std::vector<Column> columns_; ... }` with `friend class Schema` poking `column_offset_` | `Schema::new` calls `column.set_offset` (`pub(crate)`) |
| `UNREACHABLE("Column does not exist")` | `panic!` in `col_idx`; `try_col_idx` returns `Option` |
| `std::vector<uint32_t> uninlined_columns_` | `Vec<u32>` |
| `using SchemaRef = std::shared_ptr<const Schema>;` | `type SchemaRef = Arc<Schema>;` |

**Port rule:** `shared_ptr<const T>` becomes `Arc<T>` (immutable once built); a `const &` becomes `&T`.

## Learn more
- [`Iterator::position`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.position) · [`Arc`](https://doc.rust-lang.org/std/sync/struct.Arc.html) · PostgreSQL's [tuple layout](https://www.postgresql.org/docs/current/storage-page-layout.html)

## Performance

`Schema::new` is linear in the number of columns and runs when a table or a plan is created, not per row. What matters is the property it establishes: **reading a column of a tuple is O(1)** (an offset from the schema, plus one more load for a `VARCHAR`), however many columns precede it. A layout that stored every column variable-length would make reading column 20 a walk over columns 0 to 19.

**Measure it.** Read column 15 of a 20-column tuple a hundred million times, once with the offset from the schema and once by scanning length-prefixed fields from the start.

## Hints

### Offsets first, length last

The schema's length is the running offset after the last column, so compute it in the same loop. Test the offsets of a schema with a `VARCHAR` in the middle: the column after it must start 4 bytes later, not `length` bytes later.

### `copy_schema` is `new` on a selection

Pick the columns in the order of `attrs` (they may repeat or reorder), then build a schema from them. Do not copy offsets across: they are the old schema's.

### Return the first match

`position` returns the first index for which the predicate holds, which is what the doc comment asks; do not collect all matches and take one.
