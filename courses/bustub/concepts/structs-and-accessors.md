---
title: Structs, constructors and accessors
summary: Private fields with getter methods, named constructors instead of overloads, copy-with-changes, pub(crate) instead of friend, and Arc for shared immutable data: how a C++ class becomes a Rust type.
minutes: 8
---
A C++ class bundles data with methods, hides its fields behind `private`, and lets a few other classes in with `friend`. A Rust **struct** does the same job with a different grammar. Module 3 is full of small ones (`Column`, `Schema`, `Tuple`, `TupleMeta`, `Rid`), so it is worth knowing the idioms.

## Definition, constructor, methods

```rust
#[derive(Clone, Debug, PartialEq)]
pub struct Column {
    name: String,          // private: only code in this module can touch it
    type_id: TypeId,
    length: u32,
    offset: u32,
}

impl Column {
    pub fn new(name: &str, type_id: TypeId) -> Column { Column { name: name.to_owned(), type_id, length: 4, offset: 0 } }
    pub fn name(&self) -> &str { &self.name }                    // a getter: borrows, does not copy the String
    pub fn offset(&self) -> u32 { self.offset }
    pub(crate) fn set_offset(&mut self, offset: u32) { self.offset = offset; }   // visible in this crate only
}
```

| C++ | Rust |
|---|---|
| `private:` fields | fields without `pub` (private to the *module*, not the struct) |
| `public:` methods | `pub fn` in an `impl` block |
| `friend class Schema;` | `pub(crate)` or `pub(super)` on the item, or put the two types in one module |
| constructor overloads `Column(name, type)` / `Column(name, type, len)` | named associated functions: `Column::new`, `Column::new_varchar` |
| `auto GetName() const -> std::string` (copies) | `fn name(&self) -> &str` (borrows) |
| copy constructor / `operator=` | `#[derive(Clone)]` and `.clone()` |
| `operator==` | `#[derive(PartialEq)]` |
| `friend std::ostream &operator<<` / `fmt::formatter` | `impl fmt::Display` |

## Visibility is module-based

In Rust, "private" means *private to the module the struct is in* (and its children). Two types in the same file can read each other's fields. That is why a `Schema` in `schema.rs` could not set a `Column`'s offset (different module) until `set_offset` was made `pub(crate)`: a narrow door for exactly one caller.

## Copy with changes

Struct update syntax copies all the other fields from another value:

```rust
fn with_column_name(&self, name: &str) -> Column { Column { name: name.to_owned(), ..self.clone() } }
```

The original is untouched. (This is the Rust form of "builder": methods that take `self` or `&self` and return a changed copy.)

## Sharing: `Arc`

A plan node and the executor built from it both need the same `Schema`. C++ writes `std::shared_ptr<const Schema>`; Rust writes `Arc<Schema>` (an immutable value behind a reference count). Cloning an `Arc` copies a pointer and bumps a counter; the schema itself is never copied. `type SchemaRef = Arc<Schema>;` is the alias used everywhere.

## Getters: when to write them

Rust code often just makes a field `pub` when there is no invariant to protect. A getter earns its place when the field must not be changed from outside (`offset`), when the representation may change later, or when the returned type differs (`&str` for a `String`). Setters are rarer than in C++: prefer constructors and methods that express *what* changes.

## In real code

### Using it: a small struct, accessors, copy-with and sharing

```rust test
use std::sync::Arc;

mod catalog {
    #[derive(Clone, Debug, PartialEq)]
    pub struct Column { name: String, offset: u32 }
    impl Column {
        pub fn new(name: &str) -> Column { Column { name: name.to_owned(), offset: 0 } }
        pub fn name(&self) -> &str { &self.name }
        pub fn offset(&self) -> u32 { self.offset }
        pub(crate) fn set_offset(&mut self, offset: u32) { self.offset = offset; }
        pub fn with_column_name(&self, name: &str) -> Column { Column { name: name.to_owned(), ..self.clone() } }
    }

    #[derive(Debug, PartialEq)]
    pub struct Schema { columns: Vec<Column> }
    impl Schema {
        pub fn new(mut columns: Vec<Column>) -> Schema {
            for (i, c) in columns.iter_mut().enumerate() { c.set_offset(4 * i as u32); }
            Schema { columns }
        }
        pub fn columns(&self) -> &[Column] { &self.columns }
    }
}
use catalog::{Column, Schema};

#[test]
fn accessors_borrow_and_with_makes_a_changed_copy() {
    let c = Column::new("id");
    assert_eq!((c.name(), c.offset()), ("id", 0));
    let mut s = Schema::new(vec![c.clone(), Column::new("age")]);
    assert_eq!(s.columns()[1].offset(), 4, "the schema set it: a narrow, deliberate door");
    let renamed = s.columns()[1].with_column_name("years");
    assert_eq!((renamed.name(), renamed.offset()), ("years", 4));
    assert_eq!(s.columns()[1].name(), "age", "the original is unchanged");
    // c.set_offset(9);   // would not compile outside the crate's catalog code if it were pub(crate) in another crate; here it is the same crate
    s = Schema::new(vec![]);
    assert!(s.columns().is_empty());
}

#[test]
fn arc_shares_a_schema_without_copying_it() {
    let schema = Arc::new(Schema::new(vec![Column::new("a"), Column::new("b")]));
    let plan = Arc::clone(&schema);          // a plan node's copy of the pointer
    let executor = Arc::clone(&schema);      // an executor's
    assert_eq!(Arc::strong_count(&schema), 3);
    assert!(std::ptr::eq(plan.as_ref(), executor.as_ref()), "one schema, three owners");
    drop(plan);
    assert_eq!(Arc::strong_count(&schema), 2);
    assert_eq!(executor.columns().len(), 2);
}
```

```rust test
use std::fmt;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, PartialOrd, Ord, Default)]
struct Rid { page_id: i32, slot_num: u32 }

impl Rid {
    const INVALID_PAGE: i32 = -1;
    fn new(page_id: i32, slot_num: u32) -> Rid { Rid { page_id, slot_num } }
    fn is_valid(&self) -> bool { self.page_id != Self::INVALID_PAGE }
}

impl fmt::Display for Rid {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { write!(f, "page_id: {} slot_num: {}", self.page_id, self.slot_num) }
}

#[test]
fn derives_give_the_c_plus_plus_special_members_and_display_gives_the_stream_operator() {
    let a = Rid::new(3, 7);
    let b = a;                                         // Copy: the C++ default copy
    assert_eq!(a, b);                                  // PartialEq: operator==
    assert!(Rid::new(3, 8) > a, "Ord: derived field by field, page then slot");
    assert_eq!(a.to_string(), "page_id: 3 slot_num: 7");
    assert_eq!(Rid::default(), Rid::new(0, 0), "Default derives zeros (BusTub's default RID is INVALID: a manual Default)");
    assert!(!Rid::new(-1, 0).is_valid());
    let mut set = std::collections::HashSet::new();
    set.insert(a);
    assert!(set.contains(&b), "Hash: usable as a map key");
}
```

### In the exercises

- **3b-01, 3b-04:** `Column`'s and `Schema`'s fields are private with accessors (`name`, `offset`, ...); `SchemaRef = Arc<Schema>`; `TupleMeta` is a plain `Copy` struct with `pub` fields (no invariant to protect).
- **Later modules:** plan nodes, executors and the catalog are structs with `Arc<Schema>` fields and accessor methods.

### Where it is used

- **Every Rust crate**: the standard library's types are structs with private fields and methods (`Vec`, `String`, `Duration`).
- **The builder pattern**: `std::process::Command::new("ls").arg("-l")`, `reqwest::Client::builder()`: methods that take `self` and return the changed value.
- **`derive` macros**: `serde`'s `Serialize`/`Deserialize`, `clap`'s `Parser`, `thiserror`'s `Error`: struct definitions that generate their own trait implementations.
