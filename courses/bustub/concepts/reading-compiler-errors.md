---
title: Reading a Rust compiler error, and the six you will meet first
summary: How to read what rustc prints from the top, what the six errors a newcomer to systems Rust hits most often really mean (moved value, borrow conflicts, missing trait import, wrong integer type, cannot move out of a borrow, not thread-safe), and the two usual fixes for each.
minutes: 15
---
You write forty lines, run `cargo test`, and the screen fills with red. The first week of Rust feels like this for almost everyone, and the reason is not that the language is hostile. It is that the compiler is doing work other languages leave to a debugger at three in the morning: it is proving that no two threads write the same bytes, that nothing is used after it is freed, that a reference never outlives what it points to. When it cannot prove one of those things it tells you, in great detail, and the detail is the part worth learning to read.

## How to read one

An error has the same shape every time. Here is a typical one:

```text
error[E0502]: cannot borrow `pages` as mutable because it is also borrowed as immutable
  --> src/disk.rs:14:13
   |
12 |         let slot = pages.get(&id);
   |                    ----- immutable borrow occurs here
13 |         if slot.is_none() {
14 |             pages.insert(id, 0);
   |             ^^^^^ mutable borrow occurs here
15 |         }
16 |         println!("{:?}", slot);
   |                          ---- immutable borrow later used here
```

Read it in this order. The first line is a one-sentence diagnosis with an **error code** (`E0502`), which you can look up with `rustc --explain E0502` for a full essay with examples. The arrow line says which file and line the *main* problem is on. Then come the **labels**: a dashed label marks a place that is part of the story, a caret label (`^^^`) marks the place the compiler is objecting to. Read the labels as a short story in line order: *here the shared borrow starts; here you try to mutate; here the shared borrow is still needed.* The error is not "line 14 is wrong"; it is "these three lines cannot all be true at once". Often the last label, the one that says *later used here*, is the one to change, because it is what keeps the first borrow alive.

After the labels there may be a `note:` (more context) and a `help:` (a suggestion). Treat `help:` as a hint, not an order: the suggested fix often compiles but is not always what you want, especially `clone()`.

Two habits make everything faster. Use `cargo check` while you edit: it runs the compiler without producing a binary, which is much quicker. And fix the **first** error only, then re-run; later errors are often consequences of the first.

## The six you will meet first

### 1. Use of a moved value (E0382)

```text
error[E0382]: borrow of moved value: `page`
```

A value in Rust has exactly one owner. Passing it by value *moves* it, and the old name becomes unusable. Large arrays and `Vec`s move; small `Copy` types (integers, `bool`, a `PageId` that derives `Copy`) are copied instead. Two usual fixes: pass a reference (`&page`) when the callee only needs to look, or `clone()` when you really need two owners and have decided the copy is acceptable. If you find yourself cloning to quiet the compiler, stop and ask which of the two places should own the data.

### 2. Cannot borrow as mutable because it is also borrowed as immutable (E0502, E0499)

The example above. A reference is a lock checked at compile time: any number of shared (`&`) borrows, or exactly one mutable (`&mut`) borrow, never both at once. `map.get(&k)` returns an `Option<&V>`: a *shared borrow of the whole map*, alive as long as you keep that value. Calling `map.insert(..)` while it is alive wants a mutable borrow. The fixes are all ways to end the first borrow early: copy the value out (`map.get(&k).copied()` gives an `Option<usize>` that does not borrow), finish with the reference before you mutate, or use `map.entry(k).or_insert_with(..)`, which does lookup and insert as one operation.

### 3. Cannot move out of a borrowed value (E0507)

```text
error[E0507]: cannot move out of `self.buffer` which is behind a mutable reference
```

You have `&mut self` and you want to take a field *by value*, for example to hand a `Vec` to another function. If the compiler let you, `self.buffer` would be left holding nothing valid. The standard tools replace the field with something valid as you take it: `std::mem::take(&mut self.buffer)` leaves an empty `Vec` (any type with a `Default`), `Option::take()` leaves `None`, and `std::mem::replace(&mut self.state, State::Done)` leaves what you choose. You will use `take` and `replace` constantly in systems code.

### 4. No method named `write_all_at` found (E0599): the trait is not in scope

```text
error[E0599]: no method named `write_all_at` found for struct `File` in the current scope
  = help: items from traits can only be used if the trait is in scope
```

In Rust a method that comes from a trait is only callable if the trait is imported. `File::write_all_at` belongs to `std::os::unix::fs::FileExt`; `write_all` on a `Vec<u8>` belongs to `std::io::Write`. The fix is one line, `use std::os::unix::fs::FileExt;`, and the `help:` usually says exactly which. This error also appears when a method exists on a different type than you think.

### 5. Mismatched types: `u64` and `usize` (E0308)

```text
error[E0308]: mismatched types: expected `u64`, found `usize`
```

Rust never converts between integer types silently. File offsets and lengths are `u64`; indexes and counts are `usize`. Convert on purpose: `x as u64` (always allowed; truncates silently if the value does not fit, so use it when widening), or `u64::try_from(x)?` and `usize::try_from(y)?` (returns an error if it does not fit). **Widen before you multiply**: `slot as u64 * PAGE_SIZE as u64`, not `(slot * PAGE_SIZE) as u64`, which can overflow first.

### 6. Cannot be shared between threads safely (E0277: `Send` and `Sync`)

```text
error[E0277]: `RefCell<Vec<u8>>` cannot be shared between threads safely
  = help: within `DiskMem`, the trait `Sync` is not implemented for `RefCell<Vec<u8>>`
```

Two marker traits describe thread-safety. `Send`: a value can be moved to another thread. `Sync`: a shared reference can be used from several threads. The compiler derives them from a type's fields. `RefCell` and `Rc` are neither, on purpose; they would race. When the compiler says a type "cannot be shared between threads safely" read it as: *this type needs a lock or an atomic.* `Mutex<T>` and `RwLock<T>` are `Sync` (they provide the exclusion), `Arc<T>` is the shared pointer that goes with them, and `AtomicUsize` is `Sync` by itself. A trait declared `trait DiskIo: Send + Sync` makes the compiler enforce this on every implementation.

## When the message is a wall

A long error usually has one real cause and many echoes. Fix the top one. If the message talks about lifetimes (`'a`, `'static`), the question is almost always "what does this reference point into, and does that outlive the use?" and the usual escape is to *own* the data instead of borrowing it (store a `Vec`, not a `&[u8]`, in a struct that is going to be moved around). If a trait bound error scrolls past (`the trait bound ... is not satisfied`), find the line `required by a bound in ...` near the bottom: it names the trait you must implement or the wrapper you must add.

## C++ comparison

| C / C++ | Rust |
|---|---|
| use after free, found by AddressSanitizer or in production | E0382, found by the compiler before the program exists |
| a data race, found by ThreadSanitizer if you are lucky | E0277 about `Send`/`Sync` |
| iterator invalidation (`push_back` while holding an iterator) | E0502: a mutable borrow while a shared one is alive |
| `std::move` leaves a valid-but-unspecified source | a moved-from name cannot be used at all |
| a missing `#include` | a missing `use` for a trait (E0599) |

**Port rule:** every compiler error is a bug you did not have to find at run time. Read it as a code review from someone who has seen every mistake before.

## In real code

### Using it: the fixes in running code

```rust test
use std::collections::HashMap;
use std::io::Write; // E0599: the trait must be in scope to call write_all
use std::sync::{Arc, Mutex};

/// E0502: look up, end the borrow, then insert.
fn slot_for(pages: &mut HashMap<u32, usize>, id: u32, next: &mut usize) -> usize {
    if let Some(slot) = pages.get(&id).copied() {
        return slot; // the borrow of `pages` ended at `.copied()`
    }
    let slot = *next;
    *next += 1;
    pages.insert(id, slot);
    slot
}

/// E0507: take a field by value out of `&mut self`.
struct Batch {
    buffer: Vec<u8>,
}

impl Batch {
    fn flush(&mut self) -> Vec<u8> {
        std::mem::take(&mut self.buffer) // leaves an empty Vec behind
    }
}

#[test]
fn the_borrow_ends_before_the_insert() {
    let mut pages = HashMap::new();
    let mut next = 0;
    assert_eq!(slot_for(&mut pages, 7, &mut next), 0);
    assert_eq!(slot_for(&mut pages, 9, &mut next), 1);
    assert_eq!(slot_for(&mut pages, 7, &mut next), 0, "a known page keeps its slot");
}

#[test]
fn take_moves_a_field_out_and_leaves_something_valid() {
    let mut b = Batch { buffer: vec![1, 2, 3] };
    assert_eq!(b.flush(), vec![1, 2, 3]);
    assert!(b.buffer.is_empty());
    let mut sink = Vec::new();
    sink.write_all(b"ok").unwrap(); // needs `use std::io::Write`
    assert_eq!(sink, b"ok");
}

#[test]
fn u64_and_usize_are_converted_on_purpose() {
    let slot: usize = 3;
    let page: u64 = 8192;
    let offset = slot as u64 * page; // widen first, then multiply
    assert_eq!(offset, 24576);
    assert_eq!(usize::try_from(offset).unwrap(), 24576);
    assert!(u8::try_from(300u32).is_err(), "try_from reports a value that does not fit");
}

#[test]
fn a_mutex_makes_shared_state_sync() {
    let shared = Arc::new(Mutex::new(Vec::<u8>::new()));
    let handles: Vec<_> = (0..4u8)
        .map(|i| {
            let shared = Arc::clone(&shared);
            std::thread::spawn(move || shared.lock().unwrap().push(i))
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    let mut v = shared.lock().unwrap().clone();
    v.sort();
    assert_eq!(v, vec![0, 1, 2, 3]);
}
```

### In the exercises

Any stage can send you here. The first one that will: **1a-01** (trait not in scope for `write_all_at`, the `HashMap` borrow, `u64` against `usize`) and **1a-04** (`Send` and `Sync` on a memory disk).

### Where it is used

- Every Rust codebase; the habit of reading the labels as a story is what separates a week-one reader from a month-one reader.
- `rustc --explain E0xxx`, `cargo check` and `cargo clippy` are the tools the Rust project itself recommends for the loop.
