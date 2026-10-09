---
title: Errors you will meet: Access-method executors
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 12
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0106: Missing lifetime specifier

**Where you will meet it here.** An executor that borrows its child or the catalog needs a lifetime; `Box<dyn Executor>` often needs to own instead.

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

## E0502: Mutating something you are reading

**Where you will meet it here.** Reading the table while the same executor inserts into it.

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

## E0382: Use of a moved value

**Where you will meet it here.** The child executor moved into the parent is gone from the old name.

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

## E0499: Two mutable borrows at once

**Where you will meet it here.** `self.child.next()` while also changing `self.state`: split the struct or finish one borrow first.

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

**Where you will meet it here.** A tuple reference that outlives the page guard it came from.

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
