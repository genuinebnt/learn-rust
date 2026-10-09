---
title: Errors you will meet: B+ tree index
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 12
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0499: Two mutable borrows at once

**Where you will meet it here.** A node and its sibling during a borrow or a merge: two mutable pages at once.

**A small program that does it:**

```rust
fn main() {
    let mut pages = vec![1u32, 2, 3];
    let first = &mut pages[0];
    let second = &mut pages[1];
    *first += *second;
}
```

**What the compiler says:**

```text
error[E0499]: cannot borrow `pages` as mutable more than once at a time
 --> src/main.rs:4:23
  |
3 |     let first = &mut pages[0];
  |                      ----- first mutable borrow occurs here
4 |     let second = &mut pages[1];
  |                       ^^^^^ second mutable borrow occurs here
5 |     *first += *second;
  |     ----------------- first borrow later used here
  |
  = help: use `.split_at_mut(position)` to obtain two mutable non-overlapping sub-slices
```

**What it means.** At any moment there can be many readers or exactly one writer of a value. Two `&mut` into the same `Vec` (even to different elements) break that, because the compiler cannot see that the indexes differ.

**The usual ways out:**

- Split the data: `split_at_mut`, `iter_mut`, `swap`, or separate fields instead of one big struct.
- Finish with the first borrow before you start the second.
- Keep indexes or ids instead of references, and look them up when you need them.

**One fix, compiled and checked:**

```rust
fn main() {
    let mut pages = vec![1u32, 2, 3];
    let (left, right) = pages.split_at_mut(1);
    left[0] += right[0];
}
```

## E0597: Borrowed value does not live long enough

**Where you will meet it here.** A reference into a page that a guard owns, kept after the guard is gone.

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

## E0382: Use of a moved value

**Where you will meet it here.** A guard moved down the tree (latch crabbing) is gone from the variable above.

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

## E0106: Missing lifetime specifier

**Where you will meet it here.** The iterator over leaves holds a guard or a reference: it needs a lifetime or ownership.

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

## E0716: Temporary value dropped while borrowed

**Where you will meet it here.** `tree.lock().unwrap().first()` returns a reference into a temporary guard.

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
