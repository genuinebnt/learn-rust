---
title: Newtypes and type-driven design: let the compiler catch the mix-ups
summary: Wrapping a primitive in its own type so that a page id cannot be passed where a frame id is expected, why a type alias does not do that, and the neighbouring patterns: PhantomData, typestate and builders.
minutes: 8
---
The question behind type-driven design is: **can the compiler catch this mistake?** A buffer pool has page ids, frame ids, transaction ids and timestamps; in C++ they are all `int32_t` or `int64_t`, and passing one where another is expected compiles and corrupts data quietly. In Rust you give each its own type.

## Newtype

```rust
pub struct PageId(pub i32);
pub struct FrameId(pub usize);
```

A **newtype** is a one-field tuple struct. It costs nothing at run time (same layout as the field) and the compiler treats it as a different type: `fn read_page(id: PageId)` cannot be called with a `FrameId`. You choose which operations it offers: no arithmetic between a page id and a frame id, but `PageId::INVALID` and a `next()` if you want them.

### A type alias is not a newtype

```rust
pub type TxnId = i64;       // an alias: the same type, a different name
pub type Timestamp = i64;
```

`type` only renames. A `TxnId` and a `Timestamp` are both `i64`, so `begin(read_ts)` where a transaction id was meant compiles. This course's `TxnId` and `Timestamp` are aliases (as in BusTub's `using`), and a mix-up between them is exactly what a newtype would have prevented; `PageId` and `FrameId` are newtypes, and the compiler has caught every confusion between them. When two values are *used together but mean different things*, prefer the newtype.

## Validated construction

A newtype can enforce a rule by keeping the field private and offering a constructor that checks it: `Capacity::new(0)` returns an error, so every `Capacity` in the program is positive and nothing downstream needs to re-check. (Public fields with rules attached invite violations.)

## `PhantomData`

Sometimes a type carries a parameter it does not store: a typed index `Id<Table>` that is just a number, or a handle that borrows from something. `PhantomData<T>` is a zero-sized field that tells the compiler "act as if I hold a `T`" for variance, drop checking and `Send`/`Sync`. This course uses it in the count-min sketch (`PhantomData<fn(&K)>`: the key type is only used in method signatures, and `fn(&K)` keeps the sketch `Send + Sync` whatever `K` is).

## Typestate and builders

Encode a protocol in types so that invalid sequences do not compile:

```rust
struct Connection<State> { /* ... */ _s: PhantomData<State> }
struct Closed; struct Open;
impl Connection<Closed> { fn open(self) -> Connection<Open> { ... } }
impl Connection<Open>   { fn send(&self, data: &[u8]) { ... } fn close(self) -> Connection<Closed> { ... } }
```

`send` exists only on an open connection. A **builder** is the same idea for construction: required fields appear as method calls; `build()` is available only when they are all set. Do not use boolean flags or `Option` fields for states that types can express.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `using page_id_t = int32_t;` (an alias) | `struct PageId(i32);` (a distinct type) |
| `static_assert` or runtime checks for "this was validated" | a private field and a constructor returning `Result` |
| a `bool is_open_` checked in every method | `Connection<Open>` |
| tag-dispatch with an empty struct | `PhantomData<Tag>` |

**Port rule:** a C++ `using` alias that you rely on for safety becomes a newtype; one that is only a convenience can stay an alias.

## In real code

### Using it: two ids that cannot be mixed

```rust test
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
struct PageId(i32);
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash)]
struct FrameId(usize);

impl PageId {
    const INVALID: PageId = PageId(-1);
    fn is_valid(self) -> bool {
        self.0 >= 0
    }
}

fn frame_for(page: PageId, table: &[Option<PageId>]) -> Option<FrameId> {
    table.iter().position(|p| *p == Some(page)).map(FrameId)
}

#[test]
fn each_id_has_its_own_operations() {
    assert!(!PageId::INVALID.is_valid());
    assert!(PageId(7).is_valid());
}

#[test]
fn the_types_carry_the_meaning() {
    let table = [None, Some(PageId(9)), Some(PageId(4))];
    assert_eq!(frame_for(PageId(4), &table), Some(FrameId(2)));
    assert_eq!(frame_for(PageId(5), &table), None);
    // frame_for(FrameId(2), &table) would not compile
}
```

### Using it: validated construction and typestate

```rust test
use std::marker::PhantomData;

struct Capacity(usize);

impl Capacity {
    fn new(n: usize) -> Result<Capacity, &'static str> {
        if n == 0 { Err("capacity must be positive") } else { Ok(Capacity(n)) }
    }
    fn get(&self) -> usize {
        self.0
    }
}

struct Open;
struct Closed;
struct File<State> {
    lines: Vec<String>,
    _state: PhantomData<State>,
}

impl File<Closed> {
    fn new() -> File<Closed> {
        File { lines: vec![], _state: PhantomData }
    }
    fn open(self) -> File<Open> {
        File { lines: self.lines, _state: PhantomData }
    }
}

impl File<Open> {
    fn write(&mut self, line: &str) {
        self.lines.push(line.to_string());
    }
    fn close(self) -> File<Closed> {
        File { lines: self.lines, _state: PhantomData }
    }
}

#[test]
fn a_validated_type_is_valid_everywhere_it_appears() {
    assert!(Capacity::new(0).is_err());
    assert_eq!(Capacity::new(8).unwrap().get(), 8);
}

#[test]
fn write_exists_only_on_an_open_file() {
    let mut f = File::new().open();
    f.write("a");
    let closed = f.close();
    assert_eq!(closed.lines, vec!["a"]);
    // closed.write("b") would not compile: no such method on File<Closed>
    assert_eq!(std::mem::size_of::<PhantomData<Open>>(), 0);
}
```

### In the exercises

- **1a-03:** `PageId` and slot numbers; the page table maps one to the other.
- **2a:** `PageId`, `Rid` and typed page layouts.
- **4a-01 / 4a-02:** `Timestamp` and `TxnId` are aliases; try mixing a read timestamp with an id in a test and see nothing stop you.
- **0c-01:** capacity validated at construction.
- **0d-01:** `PhantomData<fn(&K)>` in the sketch.

### Where it is used

- **The standard library**: `NonZeroU32`, `Duration`, `PathBuf` (a newtype over `OsString`), and typestate in `std::process::Command` builders.
- **Embedded Rust HALs** encode pin modes as types (`Pin<Output>`); **`tokio::net::TcpStream`** and **`hyper`** use builders.
- The `rust-skills` type-driven guide gives the same table: newtype for meaning, typestate for transitions, `PhantomData` for phantom relations, sealed traits for closed sets.
