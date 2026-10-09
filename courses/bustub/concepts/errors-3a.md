---
title: Errors you will meet: Values and types
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 12
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0004: Non-exhaustive patterns

**Where you will meet it here.** `Value` is an enum of types; every operation `match`es over it and must cover the combinations.

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

## E0308: Mismatched types

**Where you will meet it here.** Integers of different widths: `TINYINT` + `INTEGER` is a decision you write.

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

**Where you will meet it here.** `==` on `Value` needs `PartialEq`; NULL makes equality three-valued, so you may write your own.

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

## E0599: No method named … found

**Where you will meet it here.** Converting between types is `i64::from(x)` or `try_from`, not a method on the value.

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

## E0599: The method exists, but its trait bounds were not satisfied

**Where you will meet it here.** Using a `Value` as a hash key needs `Hash`, which floats do not have.

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
