---
title: Errors you will meet: Buffer pool manager
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 12
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0499: Two mutable borrows at once

**Where you will meet it here.** The buffer pool state (page table, free list, replacer) is one struct; borrowing two of its parts mutably at once needs a different shape or a `Mutex` around the whole.

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

## E0502: Mutating something you are reading

**Where you will meet it here.** Looking a page up in the page table while changing the table in the same expression.

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

## E0597: Borrowed value does not live long enough

**Where you will meet it here.** A page guard borrowed from the pool must not outlive the pool.

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

## E0106: Missing lifetime specifier

**Where you will meet it here.** A guard that holds `&BufferPool` needs a lifetime parameter.

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

## E0505: Cannot move out while borrowed

**Where you will meet it here.** Dropping or moving the pool while a guard still borrows it.

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
