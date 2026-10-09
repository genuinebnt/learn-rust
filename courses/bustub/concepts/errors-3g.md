---
title: Errors you will meet: Sorting, limits and window functions
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 12
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0599: The method exists, but its trait bounds were not satisfied

**Where you will meet it here.** Sorting by a key needs `Ord`; `f64` is only `PartialOrd`: use `total_cmp`.

**A small program that does it:**

```rust
use std::collections::HashMap;

#[derive(PartialEq)]
struct Key(f64);

fn main() {
    let mut m: HashMap<Key, u32> = HashMap::new();
    m.insert(Key(1.0), 1);
}
```

**What the compiler says:**

```text
error[E0599]: the method `insert` exists for struct `HashMap<Key, u32>`, but its trait
    bounds were not satisfied
 --> src/main.rs:8:7
  |
4 | struct Key(f64);
  | ---------- doesn't satisfy `Key: Eq` or `Key: Hash`
...
8 |     m.insert(Key(1.0), 1);
  |       ^^^^^^
  |
  = note: the following trait bounds were not satisfied:
          `Key: Eq`
          `Key: Hash`
help: consider annotating `Key` with `#[derive(Eq, Hash, PartialEq)]`
  |
4 + #[derive(Eq, Hash, PartialEq)]
5 | struct Key(f64);
  |
```

**What it means.** A generic function or type needs a capability (`Hash + Eq` for a `HashMap` key, `Ord` for a `BTreeMap` key or `sort`) and your type does not have it. The message ends with a `help:` naming the missing trait.

**The usual ways out:**

- Derive or implement the trait. Floats have no `Eq`/`Hash`: store bits (`f64::to_bits`) or a fixed-point integer.
- If you cannot change the type, wrap it in a newtype that has the trait.
- Read the `required by a bound in …` note: it points at the exact generic that asked.

**One fix, compiled and checked:**

```rust
use std::collections::HashMap;

#[derive(PartialEq, Eq, Hash)]
struct Key(u64);

fn main() {
    let mut m: HashMap<Key, u32> = HashMap::new();
    m.insert(Key(1), 1);
}
```

## E0382: Use of a moved value

**Where you will meet it here.** Run files moved into the merge are gone from the variable.

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

**Where you will meet it here.** Merging two runs into one buffer.

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

## E0308: Mismatched types

**Where you will meet it here.** Row counts are `usize`, limits and offsets are `i64` in SQL.

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

## E0369: Binary operation cannot be applied

**Where you will meet it here.** A sort key made of several columns needs its own `Ord`.

**A small program that does it:**

```rust
struct Rid { page: u32, slot: u32 }

fn main() {
    let a = Rid { page: 1, slot: 2 };
    let b = Rid { page: 1, slot: 2 };
    println!("{}", a == b);
}
```

**What the compiler says:**

```text
error[E0369]: binary operation `==` cannot be applied to type `Rid`
 --> src/main.rs:6:22
  |
6 |     println!("{}", a == b);
  |                    - ^^ - Rid
  |                    |
  |                    Rid
  |
note: an implementation of `PartialEq` might be missing for `Rid`
 --> src/main.rs:1:1
  |
1 | struct Rid { page: u32, slot: u32 }
  | ^^^^^^^^^^ must implement `PartialEq`
help: consider annotating `Rid` with `#[derive(PartialEq)]`
  |
1 + #[derive(PartialEq)]
2 | struct Rid { page: u32, slot: u32 }
  |
```

**What it means.** `==`, `<`, `+` and the like are methods of traits (`PartialEq`, `PartialOrd`, `Add`). A type has them only if it implements them; a struct starts with none.

**The usual ways out:**

- `#[derive(PartialEq, Eq, Hash, Clone, Copy, Debug)]` for the usual set; add `PartialOrd, Ord` for ordering.
- Floats are `PartialOrd` but not `Ord` (NaN): sort with `total_cmp` or a wrapper.
- Implement the trait by hand when equality means something other than 'all fields equal'.

**One fix, compiled and checked:**

```rust
#[derive(PartialEq)]
struct Rid { page: u32, slot: u32 }

fn main() {
    let a = Rid { page: 1, slot: 2 };
    let b = Rid { page: 1, slot: 2 };
    println!("{}", a == b);
}
```
