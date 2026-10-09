---
title: Errors you will meet: MVCC writes, abort, garbage collection and serializability
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 12
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0499: Two mutable borrows at once

**Where you will meet it here.** A write touches the table heap and the transaction's write set at once.

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

## E0505: Cannot move out while borrowed

**Where you will meet it here.** Moving the transaction while a reference into its undo logs is held.

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

**Where you will meet it here.** An `Arc<Transaction>` moved into the executor: clone it.

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

## E0502: Mutating something you are reading

**Where you will meet it here.** Garbage collection walking the version chains while editing them.

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

## E0373: The closure may outlive the current function

**Where you will meet it here.** Test threads that start transactions need `move` closures.

**A small program that does it:**

```rust
fn main() {
    let name = String::from("worker");
    let h = std::thread::spawn(|| println!("{}", name));
    h.join().unwrap();
}
```

**What the compiler says:**

```text
error[E0373]: closure may outlive the current function, but it borrows `name`, which
    is owned by the current function
 --> src/main.rs:3:32
  |
3 |     let h = std::thread::spawn(|| println!("{}", name));
  |                                ^^                ---- `name` is borrowed here
  |                                |
  |                                may outlive borrowed value `name`
  |
note: function requires argument type to outlive `'static`
 --> src/main.rs:3:13
  |
3 |     let h = std::thread::spawn(|| println!("{}", name));
  |             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
help: to force the closure to take ownership of `name` (and any other referenced
    variables), use the `move` keyword
  |
3 |     let h = std::thread::spawn(move || println!("{}", name));
  |                                ++++
```

**What it means.** `thread::spawn` may keep the closure running after the function that created it has returned, so the closure may not borrow from the function's variables.

**The usual ways out:**

- Add `move` so the closure owns what it uses (clone an `Arc` first if you need it elsewhere too).
- If the threads are all joined before the function ends, use `thread::scope`: its threads may borrow.
- Pass the data in through a channel instead of capturing it.

**One fix, compiled and checked:**

```rust
fn main() {
    let name = String::from("worker");
    let h = std::thread::spawn(move || println!("{}", name));
    h.join().unwrap();
}
```
