---
title: Errors you will meet: Rust on-ramp
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 12
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0308: Mismatched types

**Where you will meet it here.** Page numbers are `u64`, lengths are `usize`, and the header's `len` is a `u64`: the offset arithmetic of `PageFile` mixes them.

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

## E0599: No method named … found

**Where you will meet it here.** `read_at` and `write_all_at` are methods of `FileExt`, which you have to import.

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

## E0507: Cannot move out of a borrowed place

**Where you will meet it here.** `Stack::pop` takes the head out of `&mut self`; `Option::take` is the answer.

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

## E0373: The closure may outlive the current function

**Where you will meet it here.** The shared-state stage spawns threads: without `move` the closure borrows a local.

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

## E0382: A lock guard moved by `wait`

**Where you will meet it here.** `BoundedQueue::push` and `pop` wait on a `Condvar`, which takes your lock guard and gives a new one back.

**A small program that does it:**

```rust
use std::sync::{Condvar, Mutex};

fn main() {
    let m = Mutex::new(false);
    let cv = Condvar::new();
    let guard = m.lock().unwrap();
    let _ = cv.wait(guard);
    println!("{}", *guard);
}
```

**What the compiler says:**

```text
error[E0382]: borrow of moved value: `guard`
   --> src/main.rs:8:21
    |
  6 |     let guard = m.lock().unwrap();
    |         ----- move occurs because `guard` has type `std::sync::MutexGuard<'_, bool>`, which does not implement the `Copy` trait
  7 |     let _ = cv.wait(guard);
    |                     ----- value moved here
  8 |     println!("{}", *guard);
    |                     ^^^^^ value borrowed here after move
    |
    = note: borrow occurs due to deref coercion to `bool`
note: deref defined here
   --> src/main.rs:726:5
    |
726 |     type Target = T;
    |     ^^^^^^^^^^^
```

**What it means.** `Condvar::wait` takes the guard by value (it releases the lock while sleeping) and gives a new guard back. The old guard variable was moved into the call.

**The usual ways out:**

- Assign the result back: `guard = cv.wait(guard).unwrap();`.
- Wait in a loop that re-checks the condition: wake-ups can be spurious.
- `wait_while(guard, |state| …)` does the loop for you.

**One fix, compiled and checked:**

```rust
use std::sync::{Condvar, Mutex};

fn main() {
    let m = Mutex::new(true);
    let cv = Condvar::new();
    let mut guard = m.lock().unwrap();
    while !*guard {
        guard = cv.wait(guard).unwrap();
    }
    println!("{}", *guard);
}
```
