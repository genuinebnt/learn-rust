---
title: Changing things behind a shared reference: Cell, RefCell, Mutex and atomics
summary: Why a method that takes &self sometimes has to change state, the five tools for it (Cell, RefCell, Mutex, RwLock, atomics), how to choose, what each costs, and how to recognise the compiler errors that point you at one.
minutes: 15
---
Rust's central rule is that a value can be changed through a `&mut` reference, and that there can only be one `&mut` at a time. It is what makes data races impossible to write by accident. It also seems to forbid half of real programs: a cache that fills itself on read, a counter that every call increments, a disk manager shared by twenty threads whose methods all take `&self`. The language's answer is that the *rule* stays, and a few library types move the check from compile time to run time, safely. The family is called **interior mutability**, and the useful part is knowing which member to choose.

## Why `&self` and not `&mut self`

Start with the question the course forces on you. `DiskManager::write_page(&self, ...)` takes `&self` because many threads call it at once through an `Arc<DiskManager>`; you cannot hand out many `&mut`. Yet writing a page changes the page table. The state has to be changeable *behind* the shared reference, with something guaranteeing that only one change happens at a time. That something is the choice you make.

## The five tools

**`Cell<T>`** is the simplest. It holds a value you can `get()` (for `Copy` types) and `set()`, with no borrowing at all, because you can never hold a reference *into* a `Cell`. Zero overhead beyond the value. Single thread only (`Cell` is not `Sync`). Good for small counters and flags inside a struct that is otherwise shared immutably.

**`RefCell<T>`** allows real references, checked at run time. `cell.borrow()` gives a shared guard, `cell.borrow_mut()` an exclusive one, and if you break the rule (a second `borrow_mut` while one is alive) the program **panics**. It is the single-threaded cousin of a mutex: the same exclusion rule, enforced by counting, with a panic instead of waiting. Reach for it when a data structure is shared by `Rc` on one thread, such as a tree with parent pointers. If you find yourself writing `.borrow_mut()` in a hot loop, ask whether a plain `&mut` would do.

**`Mutex<T>`** is the thread-safe version. `lock()` blocks until it can give you a guard; the data is only reachable through the guard, and the lock is released when the guard goes out of scope. In Rust the mutex *owns* the data, so you cannot forget to lock it. `lock()` returns a `Result` because a thread that panics while holding the lock **poisons** it; the usual response is `.unwrap()`, which spreads the panic (see the lock-poisoning article).

**`RwLock<T>`** allows many readers or one writer. Use it when reads vastly outnumber writes *and* readers hold the lock long enough that sharing matters; otherwise a `Mutex` is faster, because an `RwLock` has more bookkeeping. A page latch in a buffer pool is the classic case.

**Atomics** (`AtomicUsize`, `AtomicBool`, `AtomicPtr`) make a single machine word safely shareable with no lock at all: `fetch_add`, `load`, `store`, `compare_exchange`. Right for counters, flags and the occasional lock-free structure. They cannot protect a multi-field invariant: two atomics updated one after the other can be observed in between.

## Choosing

| State | One thread | Many threads |
|---|---|---|
| a small `Copy` value (a counter, a flag) | `Cell<T>` | an atomic |
| a structure you need references into | `RefCell<T>` | `Mutex<T>` (or `RwLock<T>` for read-mostly) |
| an invariant across several fields | `RefCell` around the whole struct | one `Mutex` around the whole struct |
| a statistic where an approximate value is fine | `Cell` | `AtomicUsize` with `Relaxed` |

The last column hides the most important design rule: **protect the invariant, not the field.** If two pieces of state must change together (the page table and the free list), put them behind *one* lock so no thread ever sees one changed and not the other. Several fine-grained locks are faster only when you can prove that no operation needs more than one.

## How the compiler points you here

When you take `&self` and try to assign to a field you will see `error[E0594]: cannot assign to `self.count`, which is behind a `&` reference`. When you put a `RefCell` in a type that needs to be shared between threads you will see `error[E0277]: RefCell<..> cannot be shared between threads safely`. Both errors mean the same thing: the type needs a member of this family, and which one depends on the threads.

## C++ comparison

| C / C++ | Rust |
|---|---|
| a `mutable` member inside a `const` method | `Cell` or `RefCell` |
| `std::atomic<size_t>` | `AtomicUsize` |
| `std::mutex m; Data d;` next to each other, by convention | `Mutex<Data>`: the data is inside the lock |
| `std::shared_mutex` | `RwLock<T>` |
| a data race (undefined behaviour) | a compile error, or a panic on a `RefCell` misuse |

**Port rule:** `mutable` plus a comment saying "protected by mu_" becomes a `Mutex<T>` that owns the data.

## In real code

### Using it: one tool for each situation

```rust test
use std::cell::{Cell, RefCell};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex, RwLock};

struct Counter {
    hits: Cell<u32>,
}

impl Counter {
    fn touch(&self) -> u32 {
        self.hits.set(self.hits.get() + 1); // mutation through &self, no borrow to track
        self.hits.get()
    }
}

#[test]
fn cell_counts_through_a_shared_reference() {
    let c = Counter { hits: Cell::new(0) };
    assert_eq!((c.touch(), c.touch(), c.touch()), (1, 2, 3));
}

#[test]
fn refcell_checks_the_borrow_rules_at_run_time() {
    let log = RefCell::new(vec![1, 2, 3]);
    {
        let first = log.borrow_mut();
        assert!(log.try_borrow_mut().is_err(), "a second exclusive borrow is refused while the first is alive");
        assert_eq!(first.len(), 3);
    }
    log.borrow_mut().push(4);
    assert_eq!(log.borrow().len(), 4);
}

#[test]
fn a_mutex_keeps_a_two_field_invariant() {
    // pages and free_list must change together: one lock around both
    struct State {
        pages: Vec<u32>,
        free: Vec<u32>,
    }
    let state = Arc::new(Mutex::new(State { pages: vec![], free: vec![9] }));
    let handles: Vec<_> = (0..4)
        .map(|i| {
            let state = Arc::clone(&state);
            std::thread::spawn(move || {
                let mut s = state.lock().unwrap();
                let slot = s.free.pop().unwrap_or(100 + i); // read and write under one guard
                s.pages.push(slot);
            })
        })
        .collect();
    for h in handles {
        h.join().unwrap();
    }
    let s = state.lock().unwrap();
    assert_eq!(s.pages.len(), 4);
    assert!(s.free.is_empty());
    assert_eq!(s.pages.iter().filter(|&&p| p == 9).count(), 1, "the one free slot was handed out exactly once");
}

#[test]
fn an_atomic_is_exact_without_a_lock_and_an_rwlock_allows_readers() {
    let n = Arc::new(AtomicUsize::new(0));
    let table = Arc::new(RwLock::new(vec![1, 2, 3]));
    let handles: Vec<_> = (0..8)
        .map(|_| {
            let (n, table) = (Arc::clone(&n), Arc::clone(&table));
            std::thread::spawn(move || {
                for _ in 0..1000 {
                    n.fetch_add(1, Ordering::Relaxed);
                }
                table.read().unwrap().len() // many readers at once
            })
        })
        .collect();
    for h in handles {
        assert_eq!(h.join().unwrap(), 3);
    }
    assert_eq!(n.load(Ordering::Relaxed), 8000);
    table.write().unwrap().push(4); // one writer, alone
    assert_eq!(table.read().unwrap().len(), 4);
}
```

### In the exercises

**1a-01** (the page table behind a `Mutex`, because every method takes `&self`), **1a-03** (counters as atomics), **1b** (the channel's `Mutex` and `Condvar`), **1f and 1g** (page latches as `RwLock`), and any later stage with a `&self` method that changes state.

### Where it is used

- Every shared server structure: caches, connection pools, metrics counters (atomics), configuration reloaded under an `RwLock`.
- The standard library's own `Arc<Mutex<T>>` pair is the single most common concurrency idiom in Rust code.
- Databases: buffer-pool latches (`RwLock`), statistics counters (atomics), and the "one lock protects the table and the free list" rule in nearly every allocator.
