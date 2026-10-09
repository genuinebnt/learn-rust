---
title: Errors you will meet: Disk scheduler
summary: The compiler messages this module is most likely to provoke, what each one means in plain words, and the usual ways out.
minutes: 12
---

Compiler errors are the course's second teacher. These are the ones this module's designs tend to provoke. Each shows the message as `rustc` prints it (read it from the top: the first line says what, the arrows say where, the `help:` line often says how), what it means, where you will probably meet it here, and the usual fixes. The messages and the fixes on this page were produced and checked with a real compiler.

## E0373: The closure may outlive the current function

**Where you will meet it here.** The scheduler's worker thread needs `move` to own its channel and the disk.

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

**Where you will meet it here.** A channel's `Sender` is moved into the thread that uses it; clone it first for a second user.

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

## E0277: Cannot be sent between threads safely

**Where you will meet it here.** A `Rc`, a `RefCell` or a raw `MutexGuard` inside a request makes it impossible to send to the worker.

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

## E0521: Borrowed data escapes outside of the function

**Where you will meet it here.** A method that starts a thread from `&self` borrows data the thread would keep: share the scheduler with an `Arc`.

**A small program that does it:**

```rust
struct Disk { name: String }

impl Disk {
    fn start(&self) {
        std::thread::spawn(move || println!("{}", self.name));
    }
}

fn main() {}
```

**What the compiler says:**

```text
error[E0521]: borrowed data escapes outside of method
 --> src/main.rs:5:9
  |
4 |     fn start(&self) {
  |              -----
  |              |
  |              `self` is a reference that is only valid in the method body
  |              let's call the lifetime of this reference `'1`
5 |         std::thread::spawn(move || println!("{}", self.name));
  |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  |         |
  |         `self` escapes the method body here
  |         argument requires that `'1` must outlive `'static`
```

**What it means.** A spawned thread may run for ever, so everything it uses must be owned or `'static`. A `&self` is a borrow that ends when the caller says so.

**The usual ways out:**

- Make the object shared (`Arc<Self>`) and clone the `Arc` into the thread.
- Move what the thread needs into it (clone the name, take the channel).
- Use `thread::scope` if the thread is joined before the method returns.

**One fix, compiled and checked:**

```rust
use std::sync::Arc;

struct Disk { name: String }

impl Disk {
    fn start(self: &Arc<Self>) {
        let me = Arc::clone(self);
        std::thread::spawn(move || println!("{}", me.name));
    }
}

fn main() {}
```

## E0382: A lock guard moved by `wait`

**Where you will meet it here.** The reader-writer latch waits on a `Condvar`: assign the guard that `wait` gives back.

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
