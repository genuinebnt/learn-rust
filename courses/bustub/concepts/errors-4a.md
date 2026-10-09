---
title: Errors you will meet: Timestamps, transactions and version chains
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 12
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0382: Use of a moved value

**Where you will meet it here.** A transaction handle (`Arc<Transaction>`) moved into a closure: clone the `Arc`.

**A small program that does it:**

```rust
struct Frame { data: Vec<u8> }

fn main() {
    let frame = Frame { data: vec![0; 4096] };
    let handle = std::thread::spawn(move || frame.data.len());
    println!("{}", frame.data.len());
    handle.join().unwrap();
}
```

**What the compiler says:**

```text
error[E0382]: borrow of moved value: `frame.data`
 --> src/main.rs:6:20
  |
5 |     let handle = std::thread::spawn(move || frame.data.len());
  |                                     ------- ---------- variable moved due to use in closure
  |                                     |
  |                                     value moved into closure here
6 |     println!("{}", frame.data.len());
  |                    ^^^^^^^^^^ value borrowed here after move
  |
  = note: move occurs because `frame.data` has type `Vec<u8>`, which does not implement the `Copy` trait
```

**What it means.** A value has one owner. Passing it somewhere by value (a function call, a `move` closure, an assignment) gives the ownership away, and the old name is no longer usable.

**The usual ways out:**

- Borrow instead of moving: pass `&frame` where the callee only reads.
- Share ownership when two places really need it: `Arc` across threads, `Rc` on one thread, and clone the `Arc`, not the data.
- Clone the value if a copy is what you mean (and cheap enough).

**One fix, compiled and checked:**

```rust
use std::sync::Arc;

struct Frame { data: Vec<u8> }

fn main() {
    let frame = Arc::new(Frame { data: vec![0; 4096] });
    let mine = Arc::clone(&frame);
    let handle = std::thread::spawn(move || mine.data.len());
    println!("{}", frame.data.len());
    handle.join().unwrap();
}
```

## E0277: Cannot be sent between threads safely

**Where you will meet it here.** A transaction shared between threads must be `Send + Sync`.

**A small program that does it:**

```rust
use std::rc::Rc;

fn main() {
    let shared = Rc::new(5);
    let h = std::thread::spawn(move || println!("{}", shared));
    h.join().unwrap();
}
```

**What the compiler says:**

```text
error[E0277]: `Rc<i32>` cannot be sent between threads safely
   --> src/main.rs:5:32
    |
  5 |     let h = std::thread::spawn(move || println!("{}", shared));
    |             ------------------ -------^^^^^^^^^^^^^^^^^^^^^^^
    |             |                  |
    |             |                  `Rc<i32>` cannot be sent between threads safely
    |             |                  within this `{closure@not_send_bad.rs:5:32}`
    |             required by a bound introduced by this call
    |
    = help: within `{closure@not_send_bad.rs:5:32}`, the trait `Send` is not implemented for `Rc<i32>`
note: required because it's used within this closure
   --> src/main.rs:5:32
    |
  5 |     let h = std::thread::spawn(move || println!("{}", shared));
    |                                ^^^^^^^
note: required by a bound in `spawn`
   --> src/main.rs:128:8
    |
125 | pub fn spawn<F, T>(f: F) -> JoinHandle<T>
    |        ----- required by a bound in this function
...
128 |     F: Send + 'static,
    |        ^^^^ required by this bound in `spawn`
    = note: the full name for the type has been written to '/var/folders/w_/3v26sb_54bz5x_m_msjh4g800000gn/T/tmp2er014bx/not_send_bad.long-type-15024984715928364356.txt'
    = note: consider using `--verbose` to print the full type name to the console
```

**What it means.** A value that goes to another thread must be `Send`; a value shared by reference between threads must be `Sync`. `Rc`, `RefCell` and raw pointers are neither, because their bookkeeping is not thread safe.

**The usual ways out:**

- Use `Arc` for shared ownership across threads and `Mutex`/`RwLock` for shared changes.
- Read the *last* lines of the message: they say which field or type inside your struct is the one that is not `Send`.
- A `MutexGuard` is not `Send` either: finish with it before the thread boundary.

**One fix, compiled and checked:**

```rust
use std::sync::Arc;

fn main() {
    let shared = Arc::new(5);
    let h = std::thread::spawn(move || println!("{}", shared));
    h.join().unwrap();
}
```

## E0308: Mismatched types

**Where you will meet it here.** Timestamps are `i64`, ids are `u64`, positions are `usize`.

**A small program that does it:**

```rust
struct PageId(i32);

fn offset(page: PageId, page_size: usize) -> u64 {
    page.0 * page_size
}

fn main() {}
```

**What the compiler says:**

```text
error[E0308]: mismatched types
 --> src/main.rs:4:14
  |
4 |     page.0 * page_size
  |              ^^^^^^^^^ expected `i32`, found `usize`

error[E0308]: mismatched types
 --> src/main.rs:4:5
  |
3 | fn offset(page: PageId, page_size: usize) -> u64 {
  |                                              --- expected `u64` because of return type
4 |     page.0 * page_size
  |     ^^^^^^^^^^^^^^^^^^ expected `u64`, found `i32`
  |
help: you can convert an `i32` to a `u64` and panic if the converted value doesn't fit
  |
4 |     (page.0 * page_size).try_into().unwrap()
  |     +                  +++++++++++++++++++++

error[E0277]: cannot multiply `i32` by `usize`
   --> src/main.rs:4:12
    |
  4 |     page.0 * page_size
    |            ^ no implementation for `i32 * usize`
    |
    = help: the trait `Mul<usize>` is not implemented for `i32`
help: the following other types implement trait `Mul<Rhs>`
   --> src/main.rs:344:9
    |
344 |         const impl Mul for $t {
    |         ^^^^^^^^^^^^^^^^^^^^^ `i32` implements `Mul`
...
359 | mul_impl! { usize u8 u16 u32 u64 u128 isize i8 i16 i32 i64 i128 f16 f32 f64 f128 }
    | ---------------------------------------------------------------------------------- in this macro invocation
    |
   ::: /Users/genuinebasilnt/.rustup/toolchains/stable-aarch64-apple-darwin/lib/rustlib/src/rust/library/core/src/internal_macros.rs:22:9
    |
 22 |         const impl $imp<$u> for &$t {
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^ `&i32` implements `Mul<i32>`
...
 33 |         const impl $imp<&$u> for $t {
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^ `i32` implements `Mul<&i32>`
...
 44 |         const impl $imp<&$u> for &$t {
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^ `&i32` implements `Mul`
    = note: this error originates in the macro `mul_impl` (in Nightly builds, run with -Z macro-backtrace for more info)
```

**What it means.** Rust never converts between integer types behind your back: `i32`, `usize` and `u64` are three different types, and so is a newtype around one of them.

**The usual ways out:**

- Convert on purpose: `as` for a plain cast, `u64::from(x)` when it cannot fail, `usize::try_from(x)?` when it can.
- Decide one type per quantity (an offset is `u64`, a length is `usize`) and convert at the edges.
- Check for a sign: converting a negative `i32` with `as u64` gives a huge number.

**One fix, compiled and checked:**

```rust
struct PageId(i32);

fn offset(page: PageId, page_size: usize) -> u64 {
    page.0 as u64 * page_size as u64
}

fn main() {}
```

## E0502: Mutating something you are reading

**Where you will meet it here.** Walking an undo chain while appending to the log.

**A small program that does it:**

```rust
use std::collections::HashMap;

fn main() {
    let mut frames: HashMap<u32, u32> = HashMap::new();
    frames.insert(1, 10);
    for (page, _frame) in frames.iter() {
        frames.remove(page);
    }
}
```

**What the compiler says:**

```text
error[E0502]: cannot borrow `frames` as mutable because it is also borrowed as
    immutable
 --> src/main.rs:7:9
  |
6 |     for (page, _frame) in frames.iter() {
  |                           -------------
  |                           |
  |                           immutable borrow occurs here
  |                           immutable borrow later used here
7 |         frames.remove(page);
  |         ^^^^^^^^^^^^^^^^^^^ mutable borrow occurs here
```

**What it means.** A loop over a collection holds a shared borrow of it until the loop ends; changing the collection inside the loop needs a mutable borrow at the same time.

**The usual ways out:**

- Collect what you need first (keys, ids), end the borrow, then change the collection.
- Use `retain` or `drain` when the loop is really 'remove what matches'.
- Mark what to change in the loop and apply it after.

**One fix, compiled and checked:**

```rust
use std::collections::HashMap;

fn main() {
    let mut frames: HashMap<u32, u32> = HashMap::new();
    frames.insert(1, 10);
    let pages: Vec<u32> = frames.keys().copied().collect();
    for page in pages {
        frames.remove(&page);
    }
}
```

## E0716: Temporary value dropped while borrowed

**Where you will meet it here.** `txn.lock().unwrap().logs.last()` returns a reference into a guard that ends with the statement.

**A small program that does it:**

```rust
use std::sync::Mutex;

fn main() {
    let state = Mutex::new(vec![1, 2, 3]);
    let first = state.lock().unwrap().first().unwrap();
    println!("{}", first);
}
```

**What the compiler says:**

```text
error[E0716]: temporary value dropped while borrowed
 --> src/main.rs:5:17
  |
5 |     let first = state.lock().unwrap().first().unwrap();
  |                 ^^^^^^^^^^^^^^^^^^^^^                 - temporary value is freed at the end of this statement
  |                 |
  |                 creates a temporary value which is freed while still in use
6 |     println!("{}", first);
  |                    ----- borrow later used here
  |
help: consider using a `let` binding to create a longer lived value
  |
5 ~     let binding = state.lock().unwrap();
6 ~     let first = binding.first().unwrap();
  |
```

**What it means.** `state.lock().unwrap()` creates a guard that lives only until the end of the statement, and you kept a reference into it. The reference would point into a lock that was already released.

**The usual ways out:**

- Copy or clone the value out inside the statement (`let first = *state.lock().unwrap().first().unwrap();`).
- Or give the guard a name (`let guard = state.lock().unwrap();`) so it lives as long as you need it.
- This error is the compiler protecting you from reading data without the lock.

**One fix, compiled and checked:**

```rust
use std::sync::Mutex;

fn main() {
    let state = Mutex::new(vec![1, 2, 3]);
    let first = *state.lock().unwrap().first().unwrap();
    println!("{}", first);
}
```
