---
title: Lock poisoning and when unwrap is the right answer
summary: Why Mutex::lock returns a Result, what a poisoned lock means, why this course unwraps it, and when you should recover the data instead.
minutes: 5
---
`Mutex::lock()` returns `Result<MutexGuard<T>, PoisonError<MutexGuard<T>>>`, which is why the reference code is full of `.lock().unwrap()` (112 of them). The `Err` case is **poisoning**: a thread panicked **while it held the lock**, so the protected data may be half-updated. Rust marks the mutex as poisoned so that later threads do not silently use inconsistent data.

## What to do with it

- **Propagate the panic (`unwrap()` / `expect(..)`).** If a panic while holding the lock means a bug broke an invariant, continuing is unsafe; crashing the other thread too is the honest answer. This is the default, and what the course does.
- **Recover the data (`unwrap_or_else(PoisonError::into_inner)`).** Right when the data cannot be left inconsistent by a panic: a counter, a cache that can be rebuilt, a log. Then poisoning is just noise.
- **Use a lock that does not poison** (`parking_lot::Mutex`): a design decision for the whole program, not a local fix.

Which is right depends on *what the critical section does*. Keep critical sections small and free of anything that can panic (indexing, `unwrap`, arithmetic overflow in debug builds), and poisoning becomes rare enough that propagating is fine.

## Related rules from the same family

- **`unwrap()` on a `Result` of I/O or parsing is a bug;** `unwrap()` on a lock is a deliberate "this cannot happen unless a bug already happened". Say so with `expect("the buffer pool lock is poisoned")` when you want the reason in the crash message.
- A panic inside a `Mutex` held by `catch_unwind` code (see the panics article) is the case where recovering matters.

## C++ comparison

| C / C++ | Rust |
|---|---|
| a thread that throws while holding a `std::mutex` via `lock_guard`: the guard unlocks during unwinding; later threads see whatever state was left | the same, but later threads are *told* (poisoned) and choose |
| `std::terminate` on an uncaught exception | a panic unwinds one thread; poisoning spreads the news |

**Port rule:** `lock_guard` plus exceptions becomes `lock().unwrap()`; ask whether the section could leave data broken, and recover only if not.

## In real code

### Using it: seeing a poisoned lock and recovering

```rust test
use std::sync::{Arc, Mutex};
use std::thread;

#[test]
fn a_panic_while_holding_the_lock_poisons_it() {
    let m = Arc::new(Mutex::new(vec![1, 2, 3]));
    let m2 = m.clone();
    let _ = thread::spawn(move || {
        let mut g = m2.lock().unwrap();
        g.push(4);
        panic!("while holding the lock");
    })
    .join();
    assert!(m.is_poisoned());
    assert!(m.lock().is_err());
}

#[test]
fn into_inner_recovers_the_data_when_that_is_safe() {
    let m = Arc::new(Mutex::new(0u32));
    let m2 = m.clone();
    let _ = thread::spawn(move || {
        *m2.lock().unwrap() += 1;
        panic!("boom");
    })
    .join();
    let value = *m.lock().unwrap_or_else(|poisoned| poisoned.into_inner());
    assert_eq!(value, 1, "the counter is fine; only the thread died");
}
```

### Using it: a small helper that states the policy once

```rust test
use std::sync::{Mutex, MutexGuard};

/// The course's policy in one place: a poisoned lock means a bug already happened, so say so and stop.
fn lock<'a, T>(m: &'a Mutex<T>, what: &str) -> MutexGuard<'a, T> {
    m.lock().unwrap_or_else(|_| panic!("{what} lock is poisoned: an earlier panic left it half-updated"))
}

#[test]
fn the_helper_locks_normally() {
    let m = Mutex::new(5);
    *lock(&m, "counter") += 1;
    assert_eq!(*lock(&m, "counter"), 6);
}

#[test]
fn the_helper_names_the_lock_in_its_message() {
    let m = std::sync::Arc::new(Mutex::new(0));
    let m2 = m.clone();
    let _ = std::thread::spawn(move || {
        let _g = m2.lock().unwrap();
        panic!("x");
    })
    .join();
    let err = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| drop(lock(&m, "pool")))).unwrap_err();
    let msg = err.downcast_ref::<String>().cloned().unwrap_or_default();
    assert!(msg.contains("pool lock is poisoned"));
}
```

### In the exercises

- **1b-01:** the channel's mutex.
- **1f:** the buffer pool's latch table.
- **4a-02 / 4a-03:** `begin` and `commit` lock the watermark; a panic inside would poison it.
- **0a-04:** `TrieStore` takes two locks per write.

### Where it is used

- The standard library documents poisoning on `Mutex` and `RwLock`; the `tracing`, `log` and many server crates unwrap or recover depending on the data.
- `parking_lot`, `crossbeam` and Tokio's `sync::Mutex` do not poison.
