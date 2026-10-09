---
title: Send and Sync: which types may cross threads
summary: What the two marker traits promise, which common types have them and which do not, how the compiler uses them to reject data races, and the pattern of Arc around a Mutex that satisfies them.
minutes: 7
---
C++ lets you pass anything to a thread and hopes you locked correctly. Rust makes the compiler check it with two **marker traits** (they have no methods; they are facts about a type that the compiler derives from its fields):

- **`Send`**: a value of this type may be **moved** to another thread.
- **`Sync`**: a **shared reference** `&T` may be used from several threads at once. (`T: Sync` exactly when `&T: Send`.)

`thread::spawn` requires its closure, and so everything it captures, to be `Send` (and `'static`). A type is `Send`/`Sync` automatically if all its fields are; you opt out only with raw pointers or `PhantomData` tricks, and opt in only with `unsafe impl`.

| type | `Send` | `Sync` | why |
|---|---|---|---|
| `i32`, `String`, `Vec<T>` (of Send) | yes | yes | plain owned data |
| `Rc<T>` | **no** | **no** | its reference count is not atomic; two threads cloning it would corrupt it |
| `Arc<T>` | if `T: Send + Sync` | if `T: Send + Sync` | the count is atomic, but the `T` is shared, so it must be shareable |
| `Cell<T>`, `RefCell<T>` | if `T: Send` | **no** | they mutate through `&self` without any synchronisation |
| `Mutex<T>` | if `T: Send` | if `T: Send` | the lock serialises access, so `T` need not be `Sync` |
| `RwLock<T>` | if `T: Send` | if `T: Send + Sync` | many readers see `&T` at once |
| `AtomicU64` and friends | yes | yes | the hardware serialises access |
| `MutexGuard<'_, T>` | **no** | if `T: Sync` | a lock must be released by the thread that took it |
| `*const T`, `*mut T` | **no** | **no** | the compiler knows nothing about them |

## The pattern that satisfies the compiler

Shared **and** mutable across threads means: `Arc` for shared ownership, a `Mutex` (or `RwLock`, or atomics) for the mutation:

```text
Arc<Mutex<State>>    // clone the Arc into every thread; lock to touch State
```

Most of this course's concurrent types are built this way: `TrieStore` (two `Mutex`es), `Watermark` behind `Mutex`, the skip list and Robin Hood set behind one `RwLock`, the count-min sketch with `AtomicU32` counters (no lock at all, since atomics are `Sync`).

## What the error looks like, and what to ask

```text
error[E0277]: `Rc<..>` cannot be sent between threads safely
```

Do not just change `Rc` to `Arc` and move on: ask *does this value have to cross threads?* If not, restructure (keep it on one thread, send messages instead). If yes, choose the smallest tool that fits: immutable data needs only `Arc<T>`; a counter wants an atomic; structured state wants a lock.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::shared_ptr` (atomic count, always) | `Arc<T>`; `Rc<T>` is the non-atomic one you may not send |
| "this class is thread-safe" in a comment | `Send + Sync` checked by the compiler |
| data race = undefined behaviour you find with TSan | data race = compile error in safe code |

**Port rule:** a field you would guard with `std::mutex` is a `Mutex<T>` that *owns* the data it guards; then the type is `Sync` for free.

## In real code

### Using it: assert the properties you rely on

```rust test
use std::sync::{Arc, Mutex, RwLock};
use std::sync::atomic::AtomicU32;

fn assert_send<T: Send>() {}
fn assert_sync<T: Sync>() {}

struct Store {
    values: Mutex<Vec<i32>>,
    hits: AtomicU32,
    config: RwLock<String>,
}

#[test]
fn a_type_built_from_locks_and_atomics_can_be_shared() {
    assert_send::<Store>();
    assert_sync::<Store>();
    assert_send::<Arc<Store>>();
    assert_sync::<Arc<Store>>();
}

#[test]
fn plain_data_and_mutex_guarded_data_cross_threads() {
    assert_send::<Vec<String>>();
    assert_sync::<Mutex<std::cell::Cell<i32>>>(); // a Mutex makes a !Sync Cell shareable
}
```

### Using it: threads share an Arc and lock the mutable part

```rust test
use std::sync::{Arc, Mutex};
use std::thread;

#[test]
fn eight_threads_append_through_one_mutex() {
    let log = Arc::new(Mutex::new(Vec::new()));
    let handles: Vec<_> = (0..8)
        .map(|t| {
            let log = Arc::clone(&log);
            thread::spawn(move || {
                for i in 0..100 {
                    log.lock().unwrap().push(t * 100 + i);
                }
            })
        })
        .collect();
    handles.into_iter().for_each(|h| h.join().unwrap());
    let mut all = log.lock().unwrap().clone();
    all.sort();
    assert_eq!(all, (0..800).collect::<Vec<_>>(), "no push was lost");
}

#[test]
fn immutable_data_needs_only_an_arc() {
    let table = Arc::new(vec![1, 2, 3]);
    let sums: Vec<i32> = (0..3)
        .map(|_| {
            let table = Arc::clone(&table);
            thread::spawn(move || table.iter().sum::<i32>())
        })
        .map(|h| h.join().unwrap())
        .collect();
    assert_eq!(sums, vec![6, 6, 6]);
}
```

### In the exercises

- **1b-03 / 1b-06:** the scheduler's worker thread (and the sharded workers): what has to be `Send` to cross into `thread::spawn`.
- **1f:** the buffer pool shares frames behind latches across threads.
- **0a-04:** `TrieStore` is `Sync` because its two fields are `Mutex`es.
- **0d-01:** `AtomicU32` counters make the sketch `Sync` with no lock.

### Where it is used

- **Every threaded Rust program**: `tokio::spawn` requires `Send` futures; Rayon requires `Send` closures.
- **The standard library** implements `Send`/`Sync` for its types by exactly the table above; the rules are documented in the Rustonomicon chapter "Send and Sync".
