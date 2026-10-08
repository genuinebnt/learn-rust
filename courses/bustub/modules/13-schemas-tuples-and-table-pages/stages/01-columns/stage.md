A table has columns: a name and a type, and for a text column a maximum length. A **column** is the smallest piece of the catalog, and building it teaches the shape that most of module 3's types follow: a struct with private fields, a couple of constructors, accessor methods and a method that returns a modified copy.

**Where this fits.** A schema (next stage) is a list of columns; a tuple is read through a schema. The one fact that matters about a column is **how many bytes it takes in a tuple**: the type's size, or for a `VARCHAR` the declared maximum length.

## The task

In `src/catalog/column.rs` (fields, accessors `name`, `storage_size`, `offset`, `type_id` and the `pub(crate)` `set_offset` are given):
- `Column::new(name, type_id)`: a column of a fixed-size type; its length is the type's size (module 3a); panic for `Varchar` ("Wrong constructor for VARCHAR type.") and for `Invalid`;
- `Column::new_varchar(name, length)`: a `VARCHAR` column with that maximum length;
- `with_column_name(name)`: the same column with another name (type, length and offset kept; the original untouched);
- `is_inlined()`: true unless the column is a `VARCHAR`;
- `to_string(simplified)`: simplified is `name:TYPE`, with `(length)` after `VARCHAR`; otherwise `Column[name, TYPE, Offset:o, Length:l]`.

## Tests

- Every fixed type's size; a `VARCHAR` column's length and `is_inlined() == false`; `Column::new` panics for `VARCHAR` and for `Invalid`.
- Renaming keeps everything else; both printed formats.

## Syntax and methods

```rust
Column { name: name.to_owned(), ..self.clone() }          // struct update syntax: copy, change one field
assert_ne!(type_id, TypeId::Varchar, "Wrong constructor for VARCHAR type.");
type_id.type_size().expect("Cannot get size of invalid type") as u32
format!("{}:{}", self.name, self.type_id.type_id_to_string())
```

## Notes

**Two constructors, not one with a default.** C++ overloads `Column(name, type)` and `Column(name, type, length)`. Rust has no overloading, and the two cases are different enough (one can fail, one needs a length) that two names read better: `new` and `new_varchar`. A constructor that panics on a wrong argument is acceptable here because the wrong call is a programming mistake, never user input.

**Private fields and accessors.** The offset is set by the schema that contains the column and only read elsewhere: the field is private, `offset()` reads it and `set_offset` is `pub(crate)` so the schema (same crate) can set it and nobody else can. In C++ that is `friend class Schema;`.

**Why `length` is the VARCHAR's maximum.** The tuple stores a string's actual bytes, not its maximum; `length` is what a *declaration* said (`VARCHAR(20)`), kept for the catalog and for the printed schema.

## In BusTub

`column.h`: "Non-variable-length constructor for creating a Column ... BUSTUB_ASSERT(type != TypeId::VARCHAR, "Wrong constructor for VARCHAR type.");" and `column.cpp` (`Column::ToString`: "os << column_name_ << ":" << Type::TypeIdToString(column_type_); if (column_type_ == VARCHAR) { os << "(" << length_ << ")"; }").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| two constructor overloads | `new` and `new_varchar` |
| `friend class Schema;` to let the schema set the offset | `pub(crate) fn set_offset` |
| `auto WithColumnName(std::string n) -> Column { Column c = *this; c.column_name_ = std::move(n); return c; }` | `Column { name, ..self.clone() }` |
| `BUSTUB_ASSERT(cond, msg)` | `assert!(cond, msg)` / `assert_ne!` |

**Port rule:** friend classes become `pub(crate)` items (or a module boundary); overloaded constructors become named constructors.

## Learn more
- [Struct update syntax](https://doc.rust-lang.org/book/ch05-01-defining-structs.html#creating-instances-from-other-instances-with-struct-update-syntax) · [API Guidelines: constructors](https://rust-lang.github.io/api-guidelines/naming.html) · [`assert_ne!`](https://doc.rust-lang.org/std/macro.assert_ne.html)

## Performance

A `Column` owns a `String` name, so cloning one allocates; schemas clone columns when they are copied (`copy_schema`) and plans carry schemas around, which is why they are shared through `Arc<Schema>` (`SchemaRef`) rather than copied per row. `to_string` is for humans and tests: do not call it on a hot path.

**Measure it.** Clone a 20-column schema a million times and compare with cloning an `Arc<Schema>`.

## Hints

### Which constructor is allowed for which type?

`new` is for the types with a size known from the type alone; the check is "not `Varchar`". The size comes from `type_size()` and can only fail for `Invalid`: a panic with a message is right (a column of no type is a bug in the caller).

### `with_column_name` is a copy, not a mutation

It takes `&self` and returns a new `Column`. Struct update syntax (`..self.clone()`) copies every other field, including the offset.

### Keep `to_string` exact

The next stages' tests compare printed schemas as strings. `Offset:` and `Length:` are capitalised with a colon and no space; `VARCHAR(20)` has the length in parentheses.
