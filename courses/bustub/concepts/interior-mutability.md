---
title: Interior mutability: changing data through a shared reference
summary: Why a method taking &self may still mutate, the four tools (Cell, RefCell, atomics, Mutex and RwLock), how to choose among them, and how each one fails.
minutes: 8
---
Rust's borrowing rule says: at any moment you hold **either** many `&T` **or** one `&mut T`. Usually that is what you want. Sometimes a value is shared (many `&`) and still has to change: a counter many threads bump, a cache filled on demand, a list behind a lock. **Interior mutability** moves the check from compile time to runtime, or to the hardware, inside a type that exposes only `&self` methods.

| tool | threads | works for | the check | failure mode |
|---|---|---|---|---|
| `Cell<T>` | one | `Copy` values (get/set, no references out) | none needed: you never hold a reference | none |
| `RefCell<T>` | one | any `T`, with `borrow()`/`borrow_mut()` | counts borrows at run time | **panics** on a conflicting borrow |
| `Atomic*` | many | integers, bools, pointers | the CPU's atomic instructions | wrong memory ordering (see the atomics article) |
| `Mutex<T>` | many | any `T` | one holder at a time | blocks; deadlock; **poisoning** if a holder panics |
| `RwLock<T>` | many | any `T`, read-heavy | many readers or one writer | same as `Mutex`, plus writer starvation on some platforms |

Rules of thumb (the same as the Rust Book's and the `rust-skills` mutability guide): single thread and `Copy`: `Cell`. Single thread and not `Copy`: `RefCell`. Several threads and a simple number: an atomic. Several threads and structured data: `Mutex`, or `RwLock` when reads dominate. A `Mutex` in code that never leaves one thread is unnecessary overhead; a `RefCell` sprinkled everywhere is a panic waiting for the right input.

## Why the APIs take `&self`

`AtomicU32::fetch_add(&self, ..)`, `Mutex::lock(&self)`: they must, or you could not share them. That is why this course's sketches and stores expose `&self` methods even though they mutate: the *type* synchronises, so the caller needs only a shared reference (often inside an `Arc`).

## Keep the guard's life short

A `Mutex` hands out a **guard**; the lock lasts as long as the guard. Take the lock, do the small thing, let the guard drop. Do not call out to unknown code (callbacks, user closures) while holding it, and when two locks are needed always take them in one fixed order (see the deadlock article).

## C++ comparison

| C / C++ | Rust |
|---|---|
| a `mutable` field on a `const` method | `Cell`/`RefCell`/atomic field behind `&self` |
| `std::atomic<int>` | `AtomicI32`, with an explicit `Ordering` on every call |
| `std::mutex` next to the data it protects (a convention) | `Mutex<T>` that owns the data (enforced) |

**Port rule:** a `mutable` member becomes the interior-mutability type that matches its threading.

## In real code

### Using it: Cell, RefCell and an atomic

```rust test
use std::cell::{Cell, RefCell};
use std::sync::atomic::{AtomicUsize, Ordering};

struct Counters {
    single_thread: Cell<u32>,
    log: RefCell<Vec<String>>,
    shared: AtomicUsize,
}

impl Counters {
    fn hit(&self, what: &str) {
        self.single_thread.set(self.single_thread.get() + 1);
        self.log.borrow_mut().push(what.to_string());
        self.shared.fetch_add(1, Ordering::Relaxed);
    }
}

#[test]
fn methods_taking_a_shared_reference_can_still_mutate() {
    let c = Counters { single_thread: Cell::new(0), log: RefCell::new(vec![]), shared: AtomicUsize::new(0) };
    c.hit("a");
    c.hit("b");
    assert_eq!(c.single_thread.get(), 2);
    assert_eq!(*c.log.borrow(), vec!["a", "b"]);
    assert_eq!(c.shared.load(Ordering::Relaxed), 2);
}

#[test]
fn a_refcell_checks_at_run_time_and_try_borrow_reports_instead_of_panicking() {
    let cell = RefCell::new(5);
    let first = cell.borrow_mut();
    assert!(cell.try_borrow().is_err(), "a second borrow while the first lives is refused");
    drop(first);
    assert_eq!(*cell.borrow(), 5);
}
```

### Using it: Mutex and RwLock across threads

```rust test
use std::sync::{Arc, Mutex, RwLock};
use std::thread;

#[test]
fn a_mutex_serialises_writers() {
    let total = Arc::new(Mutex::new(0u64));
    let hs: Vec<_> = (0..4).map(|_| { let t = total.clone(); thread::spawn(move || (0..1000).for_each(|_| *t.lock().unwrap() += 1)) }).collect();
    hs.into_iter().for_each(|h| h.join().unwrap());
    assert_eq!(*total.lock().unwrap(), 4000);
}

#[test]
fn an_rwlock_lets_readers_overlap() {
    let data = Arc::new(RwLock::new(vec![1, 2, 3]));
    let r1 = data.read().unwrap();
    let r2 = data.read().unwrap(); // a second reader at the same time
    assert_eq!(r1.len() + r2.len(), 6);
    assert!(data.try_write().is_err(), "a writer must wait for the readers");
    drop((r1, r2));
    data.write().unwrap().push(4);
    assert_eq!(data.read().unwrap().len(), 4);
}
```

### In the exercises

- **1d / 1f:** replacer and buffer pool state behind one lock.
- **4a-01 / 4a-02:** the watermark and the commit counter: a lock and an atomic side by side.
- **0b-03:** the skip list's `RwLock` lets eight readers overlap.
- **0d-01:** `AtomicU32` counters mutated through `&self`.

### Where it is used

- `std::sync::OnceLock` and `LazyLock` (one-time initialisation), `Arc<Mutex<..>>` application state in servers, `RefCell` in GUI event handlers.
- The `parking_lot` crate offers faster locks that do not poison.
