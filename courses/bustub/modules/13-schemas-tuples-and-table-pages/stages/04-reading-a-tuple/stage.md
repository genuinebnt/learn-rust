A tuple built, it must be read: given the schema and a column number, find the column's bytes and decode them. This is the other half of the layout, and the one executors use constantly: every `WHERE v1 = 5` reads column `v1` of every tuple. This stage also adds the three smaller conveniences built on it: testing for NULL, projecting a **key** out of a tuple (for an index) and printing a tuple.

## The task

In `src/storage/table/tuple.rs`:
- `get_value(schema, column_idx) -> Value`: the column's bytes start at its offset; for an inlined column that is where they are; for a `VARCHAR` the 4 bytes at its offset are the offset (a `u32`, little-endian) where the string's bytes start. Decode with `Value::deserialize_from(bytes, column type)`;
- `is_null(schema, column_idx)`;
- `key_from_tuple(schema, key_schema, key_attrs)`: the values of the columns `key_attrs`, built into a new tuple under `key_schema` (`Tuple::new`);
- `to_string(schema)`: `(` the values separated by `, ` `)`, a NULL printed as `<NULL>` (not as `integer_null`);
- `serialize_to(storage)` / `deserialize_from(storage)`: a 4-byte length (little-endian) followed by the tuple's bytes, and back (a copy; the record id is not stored).

## Tests

- Every column of the mixed schema comes back equal; every type and every NULL round-trips through a tuple; 300 random tuples with NULL strings and multi-byte text.
- `is_null` and the two string formats (`(4, <NULL>, 1.500000)`); a key tuple under a different schema; serialise and deserialise.

## Syntax and methods

```rust
let slot = column.offset() as usize;
let at = u32::from_le_bytes(self.data[slot..slot + 4].try_into().unwrap()) as usize;   // the stored offset of a VARCHAR
Value::deserialize_from(&self.data[at..], column.type_id()).expect("a column has a valid type")
(0..schema.column_count()).map(|i| ...).collect::<Vec<_>>().join(", ")
```

## Notes

**Reading is a slice, not a copy.** `&self.data[at..]` hands the decoder the rest of the tuple from that column on; the decoder reads only what its type needs. For an integer that is 4 bytes; for a string, the length and the text.

**A key is a tuple too.** An index (module 2) is keyed on a few columns; the executor builds each key with `key_from_tuple` from the row's columns, under the key schema that `copy_schema` made. Having keys be ordinary tuples means the index code needs no special case for composite keys.

**NULL prints differently from its value's `Display`.** A tuple's `to_string` checks `is_null` first: `<NULL>` is how a *row* shows a missing value, `integer_null` is how a *value* prints itself in a debugger. The `.slt` expected outputs use the shell's own formatting (module 3b), so this exact string matters mostly for tests and logs.

## In BusTub

`tuple.cpp`: `Tuple::GetValue` ("const char *data_ptr = GetDataPtr(schema, column_idx); return Value::DeserializeFrom(data_ptr, column_type);"), `GetDataPtr` ("For inline type, data is stored where it is. ... We read the relative offset from the tuple data."), `KeyFromTuple` and `Tuple::ToString` ("if (IsNull(schema, column_itr)) { os << "<NULL>"; }").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `const char *GetDataPtr(...)` returning a raw pointer into the buffer | an index `at`, then `&self.data[at..]` (bounds-checked) |
| `*reinterpret_cast<const int32_t *>(data_.data() + col.GetOffset())` | `u32::from_le_bytes(self.data[slot..slot + 4].try_into().unwrap())` |
| `std::stringstream os; os << "(" ...` | `Vec<String>` and `join(", ")` |
| `memcpy(storage, &sz, sizeof(int32_t))` | `copy_from_slice(&sz.to_le_bytes())` |

**Port rule:** a function that returns `const char *` into a buffer becomes a function that returns an offset (or a slice with the buffer's lifetime).

## Learn more
- [`<[u8; 4]>::try_from(&[u8])`](https://doc.rust-lang.org/std/convert/trait.TryFrom.html#impl-TryFrom%3C%26'a+%5BT%5D%3E-for-%5BT;+N%5D) · [`slice::join`](https://doc.rust-lang.org/std/primitive.slice.html#method.join) · PostgreSQL's [`heap_getattr`](https://www.postgresql.org/docs/current/storage-page-layout.html) idea: an attribute is found by offset

## Performance

`get_value` of an inlined column is one slice and one decode: nanoseconds. A `VARCHAR` adds one more read and, because `Value::Varchar` owns a `String`, an allocation and a copy. That allocation is the main cost of evaluating a predicate on a string column row after row; engines that care keep strings as `&str` views into the tuple (a borrowed value type) for the duration of the predicate.

`to_string` and the key projection allocate per call: fine for tests and for building index keys, not for an inner loop.

**Measure it.** Read an integer column and a `VARCHAR(20)` column of the same tuple a hundred million times each; the ratio is the cost of the string's allocation.

## Hints

### Find the bytes, then decode

Two cases for "where": inlined (the column's offset) and uninlined (the offset *stored* at the column's offset). Everything after is the same call. Write the helper that returns the start position once; use it for `get_value` and `is_null`.

### A key tuple needs the key schema's types

`Tuple::new` checks each value's type against its column. The key schema from `copy_schema` has the same types as the source columns in the order of `key_attrs`, so the check passes; if it panics, `key_attrs` and `key_schema` disagree.

### Length prefix: little-endian `i32`

BusTub writes the size as an `int32_t`. Read it back as `u32` or `i32`, but write and read the same way; the test checks the first four bytes.
