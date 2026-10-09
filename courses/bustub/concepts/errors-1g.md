---
title: Errors you will meet: Page guards
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 12
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0106: Missing lifetime specifier

**Where you will meet it here.** `ReadPageGuard<'a>` and `WritePageGuard<'a>` hold references; the lifetime goes on the struct and on every `impl`.

**A small program that does it:**

```rust
struct Page { data: [u8; 8] }

struct Guard {
    page: &Page,
}

fn main() {}
```

**What the compiler says:**

```text
error[E0106]: missing lifetime specifier
 --> src/main.rs:4:11
  |
4 |     page: &Page,
  |           ^ expected named lifetime parameter
  |
help: consider introducing a named lifetime parameter
  |
3 ~ struct Guard<'a> {
4 ~     page: &'a Page,
  |
```

**What it means.** A struct that holds a reference has to say how long the reference is valid, so the compiler can check that the struct never outlives what it points at. The name `'a` ties the two together.

**The usual ways out:**

- Add the lifetime parameter to the struct and every `impl` that mentions it.
- Own the data instead (`Arc<Page>`, an id) when the borrow makes the type hard to use: a guard that must be stored in a `Vec` or sent to a thread usually wants ownership.
- Remember: the lifetime is a promise you must keep, not a way to make the compiler stop.

**One fix, compiled and checked:**

```rust
struct Page { data: [u8; 8] }

struct Guard<'a> {
    page: &'a Page,
}

fn main() {}
```

## E0597: Borrowed value does not live long enough

**Where you will meet it here.** Returning a guard that borrows a local, or keeping a guard longer than its pool.

**A small program that does it:**

```rust
struct Pool { pages: Vec<u8> }
struct Guard<'a> { pool: &'a Pool }

fn main() {
    let guard;
    {
        let pool = Pool { pages: vec![0; 8] };
        guard = Guard { pool: &pool };
    }
    println!("{}", guard.pool.pages.len());
}
```

**What the compiler says:**

```text
error[E0597]: `pool` does not live long enough
  --> src/main.rs:8:31
   |
 7 |         let pool = Pool { pages: vec![0; 8] };
   |             ---- binding `pool` declared here
 8 |         guard = Guard { pool: &pool };
   |                               ^^^^^ borrowed value does not live long enough
 9 |     }
   |     - `pool` dropped here while still borrowed
10 |     println!("{}", guard.pool.pages.len());
   |                    ---------------- borrow later used here
```

**What it means.** A reference cannot outlive the thing it points to. Here the pool is dropped at the end of the inner block, while the guard that points at it is used after.

**The usual ways out:**

- Declare the owner first (earlier = lives longer) and the borrower after it.
- Return owned data (a clone, an `Arc`) instead of a reference to a local.
- If a guard must outlive its creator's scope, make it own what it needs.

**One fix, compiled and checked:**

```rust
struct Pool { pages: Vec<u8> }
struct Guard<'a> { pool: &'a Pool }

fn main() {
    let pool = Pool { pages: vec![0; 8] };
    let guard = Guard { pool: &pool };
    println!("{}", guard.pool.pages.len());
}
```

## E0505: Cannot move out while borrowed

**Where you will meet it here.** Moving the pool while a guard exists.

**A small program that does it:**

```rust
fn consume(v: Vec<u8>) -> usize { v.len() }

fn main() {
    let page = vec![0u8; 8];
    let first = &page[0];
    let n = consume(page);
    println!("{} {}", first, n);
}
```

**What the compiler says:**

```text
error[E0505]: cannot move out of `page` because it is borrowed
 --> src/main.rs:6:21
  |
4 |     let page = vec![0u8; 8];
  |         ---- binding `page` declared here
5 |     let first = &page[0];
  |                  ---- borrow of `page` occurs here
6 |     let n = consume(page);
  |                     ^^^^ move out of `page` occurs here
7 |     println!("{} {}", first, n);
  |                       ----- borrow later used here
  |
help: consider cloning the value if the performance cost is acceptable
  |
5 |     let first = &page.clone()[0];
  |                      ++++++++
```

**What it means.** You gave away a value while a reference to it was still going to be used. The reference would be left pointing at something that no longer belongs to you.

**The usual ways out:**

- Finish using the reference before you move the value.
- Copy the small thing you need (`page[0]`) instead of holding a reference.
- Pass a reference to the function if it only needs to read.

**One fix, compiled and checked:**

```rust
fn consume(v: Vec<u8>) -> usize { v.len() }

fn main() {
    let page = vec![0u8; 8];
    let first = page[0];
    let n = consume(page);
    println!("{} {}", first, n);
}
```

## E0382: Use of a moved value

**Where you will meet it here.** A guard moved into a closure or a thread is gone from the original place.

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

**Where you will meet it here.** A `MutexGuard` inside a guard makes the guard not `Send`: you cannot hand it to another thread.

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
