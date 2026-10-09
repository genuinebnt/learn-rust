---
title: Errors you will meet: Schemas, tuples and table pages
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 10
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0308: Mismatched types

**Where you will meet it here.** Offsets inside a tuple are `u16` on the page and `usize` in code.

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

**Where you will meet it here.** Reading a column out of bytes: `from_le_bytes` on a fixed-size array, via `try_into`.

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

## E0382: Use of a moved value

**Where you will meet it here.** A `Tuple` handed to the page is gone from the variable; clone it if you still need it.

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

## E0282: Type annotations needed

**Where you will meet it here.** Collecting column values needs the collection type.

**A small program that does it:**

```rust
fn main() {
    let ids = "1 2 3".split(' ').map(|s| s.parse().unwrap()).collect();
    println!("{}", ids.len());
}
```

**What the compiler says:**

```text
error[E0282]: type annotations needed
 --> src/main.rs:2:9
  |
2 |     let ids = "1 2 3".split(' ').map(|s| s.parse().unwrap()).collect();
  |         ^^^
3 |     println!("{}", ids.len());
  |                    --- type must be known at this point
  |
help: consider giving `ids` an explicit type
  |
2 |     let ids: Vec<_> = "1 2 3".split(' ').map(|s| s.parse().unwrap()).collect();
  |            ++++++++
```

**What it means.** `collect`, `parse`, `into` and `Default::default()` can produce many types, and nothing says which one you want.

**The usual ways out:**

- Annotate the variable (`let ids: Vec<u32> = …`).
- Or use the turbofish: `.collect::<Vec<u32>>()`, `.parse::<u32>()`.
- The annotation is often the best documentation of what you meant.

**One fix, compiled and checked:**

```rust
fn main() {
    let ids: Vec<u32> = "1 2 3".split(' ').map(|s| s.parse().unwrap()).collect();
    println!("{}", ids.len());
}
```
