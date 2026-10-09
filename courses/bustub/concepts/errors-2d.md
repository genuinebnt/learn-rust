---
title: Errors you will meet: B+ tree tombstones
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 10
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0499: Two mutable borrows at once

**Where you will meet it here.** Tombstone compaction touches the leaf and its neighbour.

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

## E0382: Use of a moved value

**Where you will meet it here.** Guards moved into the helper that does the compaction.

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

## E0597: Borrowed value does not live long enough

**Where you will meet it here.** A reference into a leaf kept after the leaf's guard is dropped.

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

## E0004: Non-exhaustive patterns

**Where you will meet it here.** A slot is live, a tombstone or free: the `match` must say what to do for each.

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
