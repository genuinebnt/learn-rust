---
title: Errors you will meet: The lock manager
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 12
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0373: The closure may outlive the current function

**Where you will meet it here.** Every test thread that takes locks needs a `move` closure with its own `Arc<LockManager>`.

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

## E0382: Use of a moved value

**Where you will meet it here.** The lock manager is shared: clone the `Arc`, do not move it into the first thread.

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

## E0382: A lock guard moved by `wait`

**Where you will meet it here.** `Condvar::wait` takes your `MutexGuard` and gives a new one back: assign it, in a loop.

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

## E0277: Cannot be sent between threads safely

**Where you will meet it here.** A `MutexGuard` cannot be sent to another thread; neither can a type that holds one.

**A small program that does it:**

```rust
use std::rc::Rc;

fn main() {
    let shared = Rc::new(5);
    let h = std::thread::spawn(move || println!("{}", shared));
    h.join().unwrap();
}
```

**What the compiler says:**

```text
error[E0277]: `Rc<i32>` cannot be sent between threads safely
   --> src/main.rs:5:32
    |
  5 |     let h = std::thread::spawn(move || println!("{}", shared));
    |             ------------------ -------^^^^^^^^^^^^^^^^^^^^^^^
    |             |                  |
    |             |                  `Rc<i32>` cannot be sent between threads safely
    |             |                  within this `{closure@not_send_bad.rs:5:32}`
    |             required by a bound introduced by this call
    |
    = help: within `{closure@not_send_bad.rs:5:32}`, the trait `Send` is not implemented for `Rc<i32>`
note: required because it's used within this closure
   --> src/main.rs:5:32
    |
  5 |     let h = std::thread::spawn(move || println!("{}", shared));
    |                                ^^^^^^^
note: required by a bound in `spawn`
   --> src/main.rs:128:8
    |
125 | pub fn spawn<F, T>(f: F) -> JoinHandle<T>
    |        ----- required by a bound in this function
...
128 |     F: Send + 'static,
    |        ^^^^ required by this bound in `spawn`
    = note: the full name for the type has been written to '/var/folders/w_/3v26sb_54bz5x_m_msjh4g800000gn/T/tmp2er014bx/not_send_bad.long-type-15024984715928364356.txt'
    = note: consider using `--verbose` to print the full type name to the console
```

**What it means.** A value that goes to another thread must be `Send`; a value shared by reference between threads must be `Sync`. `Rc`, `RefCell` and raw pointers are neither, because their bookkeeping is not thread safe.

**The usual ways out:**

- Use `Arc` for shared ownership across threads and `Mutex`/`RwLock` for shared changes.
- Read the *last* lines of the message: they say which field or type inside your struct is the one that is not `Send`.
- A `MutexGuard` is not `Send` either: finish with it before the thread boundary.

**One fix, compiled and checked:**

```rust
use std::sync::Arc;

fn main() {
    let shared = Arc::new(5);
    let h = std::thread::spawn(move || println!("{}", shared));
    h.join().unwrap();
}
```

## E0004: Non-exhaustive patterns

**Where you will meet it here.** Lock modes, isolation levels and phases are enums: a `match` on all three must be complete.

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
