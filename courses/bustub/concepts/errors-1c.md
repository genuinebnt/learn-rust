---
title: Errors you will meet: Simple replacers: LRU and CLOCK
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 10
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0502: Mutating something you are reading

**Where you will meet it here.** Evicting while walking the recency list: collect the victim first, then change the map.

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

## E0499: Two mutable borrows at once

**Where you will meet it here.** Moving a frame between two lists needs two `&mut`: take it out of one, then put it in the other.

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

## E0507: Cannot move out of a borrowed place

**Where you will meet it here.** Removing a node from a linked structure behind `&mut self` is a job for `take()` or `mem::replace`.

**A small program that does it:**

```rust
struct Node { next: Option<Box<Node>> }
struct List { head: Option<Box<Node>> }

impl List {
    fn pop_node(&mut self) -> Option<Box<Node>> {
        let head = self.head;
        head
    }
}

fn main() {}
```

**What the compiler says:**

```text
error[E0507]: cannot move out of `self.head` which is behind a mutable reference
 --> src/main.rs:6:20
  |
6 |         let head = self.head;
  |                    ^^^^^^^^^ move occurs because `self.head` has type `Option<Box<Node>>`, which does not implement the `Copy` trait
  |
note: if `Node` implemented `Clone`, you could clone the value
 --> src/main.rs:1:1
  |
1 | struct Node { next: Option<Box<Node>> }
  | ^^^^^^^^^^^ consider implementing `Clone` for this type
...
6 |         let head = self.head;
  |                    --------- you could clone this value
help: consider borrowing here
  |
6 |         let head = &self.head;
  |                    +
```

**What it means.** You only have `&mut self`, not ownership of `self`, so you cannot take a field out and leave a hole. The compiler will not let a struct be half-empty.

**The usual ways out:**

- `Option::take()` swaps `None` in and gives you the old value.
- `std::mem::replace(&mut self.x, new)` and `mem::take` do the same for any type.
- Borrow the field (`as_ref`, `as_mut`) when you only need to look.

**One fix, compiled and checked:**

```rust
struct Node { next: Option<Box<Node>> }
struct List { head: Option<Box<Node>> }

impl List {
    fn pop_node(&mut self) -> Option<Box<Node>> {
        let mut head = self.head.take()?;
        self.head = head.next.take();
        Some(head)
    }
}

fn main() {}
```

## E0382: Use of a moved value

**Where you will meet it here.** An id or a value you pushed into a list is gone from its old place: copy the id if you still need it.

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
