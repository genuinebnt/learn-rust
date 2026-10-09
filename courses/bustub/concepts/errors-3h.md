---
title: Errors you will meet: Optimizer rules
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 12
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0382: Use of a moved value

**Where you will meet it here.** Plan nodes are boxed trees: rewriting one moves it; rebuild instead of reusing the old name.

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

## E0004: Non-exhaustive patterns

**Where you will meet it here.** A `match` over plan node kinds must cover every kind.

**A small program that does it:**

```rust
enum Mode { IntentionShared, Shared, Exclusive }

fn is_write(m: Mode) -> bool {
    match m {
        Mode::Exclusive => true,
        Mode::Shared => false,
    }
}

fn main() {}
```

**What the compiler says:**

```text
error[E0004]: non-exhaustive patterns: `Mode::IntentionShared` not covered
 --> src/main.rs:4:11
  |
4 |     match m {
  |           ^ pattern `Mode::IntentionShared` not covered
  |
note: `Mode` defined here
 --> src/main.rs:1:6
  |
1 | enum Mode { IntentionShared, Shared, Exclusive }
  |      ^^^^   --------------- not covered
  = note: the matched value is of type `Mode`
help: ensure that all possible cases are being handled by adding a match arm with a
    wildcard pattern or an explicit pattern as shown
  |
6 ~         Mode::Shared => false,
7 ~         Mode::IntentionShared => todo!(),
  |
```

**What it means.** A `match` must cover every possible value. The message names the one you forgot, which is exactly why enums are good for states: add a variant and the compiler lists every `match` to update.

**The usual ways out:**

- Add the arm the message names.
- A catch-all `_ =>` silences the error now and hides the next forgotten variant: prefer it only when 'everything else' really is one case.
- Combine arms with `|` when they do the same thing.

**One fix, compiled and checked:**

```rust
enum Mode { IntentionShared, Shared, Exclusive }

fn is_write(m: Mode) -> bool {
    match m {
        Mode::Exclusive => true,
        Mode::Shared | Mode::IntentionShared => false,
    }
}

fn main() {}
```

## E0507: Cannot move out of a borrowed place

**Where you will meet it here.** Taking a child out of a node behind `&mut`: `mem::replace` or rebuild.

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

## E0505: Cannot move out while borrowed

**Where you will meet it here.** Moving a node while a reference into it is still held.

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

## E0599: No method named … found

**Where you will meet it here.** `Arc<PlanNode>` needs `Arc::as_ref` or deref to reach the node's methods.

**A small program that does it:**

```rust
use std::fs::File;

fn main() {
    let f = File::open("db").unwrap();
    let mut buf = [0u8; 8];
    f.read_at(&mut buf, 0).unwrap();
}
```

**What the compiler says:**

```text
error[E0599]: no method named `read_at` found for struct `File` in the current scope
   --> src/main.rs:6:7
    |
  6 |     f.read_at(&mut buf, 0).unwrap();
    |       ^^^^^^^
    |
   ::: /Users/genuinebasilnt/.rustup/toolchains/stable-aarch64-apple-darwin/lib/rustlib/src/rust/library/std/src/os/unix/fs.rs:59:8
    |
 59 |     fn read_at(&self, buf: &mut [u8], offset: u64) -> io::Result<usize>;
    |        ------- the method is available for `File` here
    |
    = help: items from traits can only be used if the trait is in scope
help: there is a method `read` with a similar name, but with different arguments
   --> src/main.rs:800:5
    |
800 |     fn read(&mut self, buf: &mut [u8]) -> Result<usize>;
    |     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
help: trait `FileExt` which provides `read_at` is implemented but not in scope;
    perhaps you want to import it
    |
  1 + use std::os::unix::fs::FileExt;
    |
```

**What it means.** The method exists, but it belongs to a trait, and a trait's methods can only be called when the trait is in scope. The message usually says which `use` to add.

**The usual ways out:**

- Read the `help:` line: it names the trait to import.
- If the method really does not exist for your type, check the type: you may be calling it on an `Option`, a `&&T` or a wrapper.
- Check the feature or platform: `FileExt` is in `std::os::unix`.

**One fix, compiled and checked:**

```rust
use std::fs::File;
use std::os::unix::fs::FileExt;

fn main() {
    let f = File::open("db").unwrap();
    let mut buf = [0u8; 8];
    f.read_at(&mut buf, 0).unwrap();
}
```
