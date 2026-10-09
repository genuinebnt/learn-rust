A **tuple** is a row as bytes. This stage writes the constructor: given the values of a row and the schema, produce the byte string that stores them. It is the layout of the previous stage made real: write each inlined value at its column's offset, and each `VARCHAR`'s bytes after the fixed part with an offset in the column's slot pointing at them.

## The task

In `src/storage/table/tuple.rs` (the struct, `TupleMeta`, `empty`, `with_rid`, `from_bytes`, `get_rid`, `set_rid`, `data` and `get_length` are given) implement `Tuple::new(values: &[Value], schema: &Schema) -> Tuple`.
A tuple's bytes are the schema's fixed part followed by a variable part. An inlined column's value is serialised at the column's offset. A `VARCHAR` column's fixed slot holds the `u32` (little-endian) offset where its value is serialised in the variable part, which grows in column order by each value's `storage_size()` (a NULL string takes its 4-byte marker). `new` panics if the number of values differs from the column count or a value's type differs from its column's (the planner casts values to the table's types before a tuple is built).

> [!ASIDE] The steps, if you would rather not work them out
> 1. check `values.len() == schema.column_count()` and that each value has its column's type (a panic otherwise: the planner casts values to the table's types before a tuple is built);
> 2. the tuple's size is the schema's fixed part plus, for each `VARCHAR` column, the value's `storage_size()` (a NULL string takes its 4-byte marker);
> 3. allocate that many zero bytes; for each column: an inlined value is `serialize_to`'d at the column's offset; a `VARCHAR` gets the current variable-part offset written (`u32`, little-endian) at the column's offset, then the value is serialised at that offset, which advances by its `storage_size()`.

The record id of a new tuple is `Rid::default()` (invalid): a tuple gets one when it is stored in a table.

## Tests

- A fixed-size tuple is its values' bytes one after another (13 bytes for an integer, a bigint and a boolean); a tuple with a `VARCHAR` has the string after the fixed part and its slot holds where (offset 16, then length 3, `h`, `i`, 0).
- Several `VARCHAR`s follow each other in column order; a NULL string takes 4 bytes and an empty one 5; a NULL number is its reserved pattern.
- A wrong number of values or a wrong value type panics; a new tuple has no record id.

## Syntax and methods

```rust
let mut data = vec![0u8; tuple_size];                                     // zeroed buffer
value.serialize_to(&mut data[column.offset() as usize..]);                // a value writes at the start of a slice
data[slot..slot + 4].copy_from_slice(&(offset as u32).to_le_bytes());     // the offset of the string, little-endian
for &i in schema.uninlined_columns() { tuple_size += values[i as usize].storage_size(); }
```

## Notes

**Two passes.** The size must be known before you allocate, and the size depends on every string, so the constructor first adds up, then writes. (Growing a `Vec` as you go also works; BusTub's way keeps one allocation.)

**Why a `VARCHAR` stores an offset and not the string.** The fixed part's layout is the same for every tuple of a schema, which is what lets `get_value` find a column with one addition. An offset is a fixed-size stand-in for a variable-size string. (PostgreSQL's and SQLite's formats make the same trade.)

**The check is a panic, not an error.** A value of the wrong type cannot be produced by correct engine code: the binder and planner cast. So this is an assertion of a precondition; a function that returned `Result` here would force every caller to handle a case that cannot happen.

**NULLs cost nothing extra.** A NULL integer is `i32::MIN` in its 4-byte slot; a NULL string is its length marker. There is no null bitmap (module 3a explained the trade).

## In BusTub

`tuple.cpp`: "Tuple::Tuple(std::vector<Value> values, const Schema *schema) { assert(values.size() == schema->GetColumnCount()); // 1. Calculate the size of the tuple. uint32_t tuple_size = schema->GetInlinedStorageSize(); for (auto &i : schema->GetUnlinedColumns()) { auto len = values[i].GetStorageSize(); if (len == BUSTUB_VALUE_NULL) { len = 0; } tuple_size += sizeof(uint32_t) + len; } ..." and its "TODO(Amadou): It does not look like nulls are supported. Add a null bitmap?".

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::vector<char> data_; data_.resize(n); std::fill(..., 0)` | `vec![0u8; n]` |
| `*reinterpret_cast<uint32_t *>(data_.data() + col.GetOffset()) = offset;` | `copy_from_slice(&offset.to_le_bytes())` |
| `values[i].SerializeTo(data_.data() + offset)` | `values[i].serialize_to(&mut data[offset..])` |
| `assert(values.size() == schema->GetColumnCount())` (gone in release builds) | `assert_eq!` (always on) |

**Port rule:** a pointer into a buffer plus an offset becomes a mutable sub-slice (`&mut data[offset..]`); no pointer arithmetic.

## Learn more
- [`slice::copy_from_slice`](https://doc.rust-lang.org/std/primitive.slice.html#method.copy_from_slice) · [`vec!`](https://doc.rust-lang.org/std/macro.vec.html) · [`assert_eq!`](https://doc.rust-lang.org/std/macro.assert_eq.html)

## Performance

Building a tuple is one allocation and one pass over the values: `O(columns + total string bytes)`. It happens for every row an `INSERT` produces and for every row a join or projection outputs, so the allocation is the cost to watch: executors that emit many tuples (module 3b's joins) pay one `Vec` allocation per output row, which is why real engines work on batches of columns instead.

**Measure it.** Build a million tuples of the mixed schema and report rows per second; then reuse one buffer across rows (write into a `&mut Vec<u8>`) and compare.

## Hints

### Write the golden bytes by hand first

For `(a INTEGER, b VARCHAR, c BIGINT)` with `(7, "hi", 9)`, write the 23 bytes on paper: `07 00 00 00`, the offset 16, nine as eight bytes, then `03 00 00 00 68 69 00`. If your constructor produces those, the rest is bookkeeping.

### A running offset for the variable part

Start it at the schema's fixed length; each `VARCHAR` writes there and advances by its `storage_size()` (which already includes the 4-byte length and the zero byte). A NULL string advances by 4.

### Do not write the string's bytes into the fixed slot

The slot holds the *offset*; the string is serialised at that offset. If tests show the string's length where the offset should be, you serialised into the wrong place.
