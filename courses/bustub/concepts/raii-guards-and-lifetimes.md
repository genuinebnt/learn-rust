---
title: RAII guards and lifetimes: a handle that cannot outlive its pool
summary: How a page guard ties a pin and a latch to a scope, why it carries a lifetime, how Deref makes it look like the page, and why unlatch comes before unpin.
minutes: 10
---
The textbook buffer pool asks you to pair `fetch_page` with `unpin_page` by hand. Module 1g removes that burden with a **guard**: an object whose existence *is* the pin and the latch, and whose destruction releases them. The pattern is **RAII**; the new ingredient Rust adds is the **lifetime**, which makes "use the guard after the pool is gone" a compile error.

## What a guard owns

```rust
pub struct ReadPageGuard<'a> {
    bpm: &'a BufferPoolManager,                              // to unpin when released
    page_id: PageId,
    frame: FrameId,
    latch: Option<RwLockReadGuard<'a, Box<PageData>>>,       // the page's read latch; None once released
}
```

The guard holds the *latch guard* itself (the `RwLockReadGuard`), a shared reference to the pool, and the ids it needs to unpin. It is created only by the pool (`pub(crate) fn new`) *after* the page is pinned and the latch taken, so a guard that exists is always a pinned, latched page.

## The lifetime `'a`

`ReadPageGuard<'a>` borrows the pool for `'a`. The compiler therefore refuses to let a guard outlive the `BufferPoolManager` (which would unpin into freed memory), and refuses to return a reference *into the page* that outlives the guard. C++ has neither check: a `PageGuard` holding a `BufferPoolManager*` can be returned from a function after the pool is destroyed, and a `const char *` from `GetData()` outlives the guard's pin silently.

| C++ (BusTub) | Rust |
|---|---|
| `BasicPageGuard` / `ReadPageGuard` move-only classes | the same structs, move-only by default (no `Copy`) |
| `page_guard.AsMut<T>()` returns a raw pointer | `guard.get_data_mut()` returns `&mut PageData` borrowed from the guard |
| `Drop()` method called by hand or by the destructor | `release()` (idempotent) called from `Drop` |
| move constructor must null the source's pointers | a move leaves nothing behind to forget |
| use after move: undefined behaviour | a compile error |

## `Deref` makes the guard look like the page

`impl Deref for ReadPageGuard { type Target = PageData; ... }` lets you write `guard[0]` or `&guard[..16]` as if `guard` were the 8 KiB array: the dot and index operators see through it. `WritePageGuard` also implements `DerefMut`, and **taking the mutable view marks the page dirty**: the type system turns "I changed this page" into something that cannot be forgotten, where BusTub's `AsMut` also sets `is_dirty_` but a raw pointer lets you write through a *read* guard.

## The order of release: unlatch, then unpin

```rust
pub fn release(&mut self) {
    if let Some(latch) = self.latch.take() {
        drop(latch);                                  // 1. unlatch first
        self.bpm.unpin_page(self.page_id, false);     // 2. then unpin
    }
}
```

If the pin were dropped first, the page would be evictable *while still latched*; the replacer could choose it, and the pool would reuse a frame whose latch is held. The invariant is **a latched page is always pinned**, so the pin is released last and taken first.

`release` is **idempotent** (the `Option` is `None` the second time), which is why `Drop` can always call it, and why an explicit `guard.release()` followed by the end of scope is harmless. It is also why the guard holds an `Option<…Guard>` rather than the guard itself: you cannot move a field out of a struct that implements `Drop` without leaving something behind.

> [!WARNING] The temporary that lives too long
> `let n = bpm.read_page(id).get_data()[0];` drops the guard at the end of the statement: fine. `let data = bpm.read_page(id).get_data();` does not compile, because `data` would outlive the temporary guard: the borrow checker is catching exactly the dangling pointer BusTub's API allows.

> [!PORT] Move semantics
> A C++ move leaves the source in a "valid but unspecified" state, so every guard method must check for a moved-from object. A Rust move makes the source *unusable* by the compiler, so there is nothing to check; the only run-time state is whether `release` has run.

## In real code

### The API you will use

| syntax | what it does | when |
|---|---|---|
| `struct Guard<'a> { pool: &'a Pool, .. }` | a type that borrows something for `'a` | a handle that cannot outlive its owner |
| `impl Drop for Guard<'_> { fn drop(&mut self) {..} }` | cleanup on every exit path | unpin, unlatch, close |
| `impl Deref for Guard { type Target = T; fn deref(&self) -> &T }` | `guard.field` / `&*guard` see through the guard | read access |
| `impl DerefMut for Guard` | `&mut *guard` | write access (and set a dirty flag) |
| `Option<Inner>` + `.take()` | release exactly once, and be able to release early | idempotent `release()` |
| `std::mem::drop(g)` | end the guard now | releasing before the end of scope |
| `pub(crate) fn new(..)` | only your crate can build one | "a guard that exists is valid" |

```rust test
use std::cell::{Cell, RefCell, RefMut};
use std::ops::{Deref, DerefMut};

struct Pool { pins: Cell<u32>, dirty: Cell<bool>, log: RefCell<Vec<&'static str>>, data: RefCell<[u8; 4]> }

impl Pool {
    fn write_page(&self) -> WriteGuard<'_> {
        self.pins.set(self.pins.get() + 1);                       // acquire: pin first...
        self.log.borrow_mut().push("pin");
        let latch = self.data.borrow_mut();                       // ...then latch (a RefCell stands in for the page's RwLock)
        WriteGuard { pool: self, latch: Some(latch), dirty: false }
    }
}

struct WriteGuard<'a> { pool: &'a Pool, latch: Option<RefMut<'a, [u8; 4]>>, dirty: bool }

impl WriteGuard<'_> {
    fn release(&mut self) {
        if let Some(latch) = self.latch.take() {                  // runs once, even if called twice
            drop(latch);                                          // 1. unlatch first...
            self.pool.log.borrow_mut().push("unlatch");
            self.pool.pins.set(self.pool.pins.get() - 1);         // 2. ...then unpin, remembering the dirt
            self.pool.dirty.set(self.pool.dirty.get() || self.dirty);
            self.pool.log.borrow_mut().push("unpin");
        }
    }
}
impl Drop for WriteGuard<'_> { fn drop(&mut self) { self.release(); } }

impl Deref for WriteGuard<'_> {
    type Target = [u8; 4];
    fn deref(&self) -> &[u8; 4] { self.latch.as_ref().expect("this guard has been released") }
}
impl DerefMut for WriteGuard<'_> {
    fn deref_mut(&mut self) -> &mut [u8; 4] { self.dirty = true; self.latch.as_mut().expect("this guard has been released") }   // the mutable view marks it dirty
}

#[test]
fn pin_unpin_dirty_and_idempotent_release() {
    let pool = Pool { pins: Cell::new(0), dirty: Cell::new(false), log: RefCell::new(vec![]), data: RefCell::new([0; 4]) };
    {
        let mut g = pool.write_page();
        assert_eq!(pool.pins.get(), 1);
        g[0] = 9;                                                  // DerefMut: marks the page dirty
        g.release();
        g.release();                                               // idempotent: nothing happens the second time
    }                                                              // Drop calls release a third time: still nothing
    assert_eq!(pool.pins.get(), 0);
    assert!(pool.dirty.get());
    assert_eq!(*pool.log.borrow(), vec!["pin", "unlatch", "unpin"]);
    assert_eq!(pool.data.borrow()[0], 9);
}
```

```rust test
#[test]
fn the_borrow_checker_ends_a_guard_with_its_pool() {
    struct Pool(Vec<u8>);
    struct Guard<'a>(&'a Pool);
    impl<'a> Pool { fn read(&'a self) -> Guard<'a> { Guard(self) } }
    impl Guard<'_> { fn first(&self) -> u8 { (self.0).0[0] } }

    let pool = Pool(vec![7]);
    let g = pool.read();
    assert_eq!(g.first(), 7);
    // drop(pool);                    // does not compile: `pool` is borrowed by `g` (in C++ this dangles silently)
    drop(g);
    drop(pool);                       // fine now: the guard is gone first
}
```

### In the exercises

- **1g-01:** `ReadPageGuard<'a>` and `WritePageGuard<'a>` have the first example's shape, with real parts: `bpm: &'a BufferPoolManager`, `Option<RwLockWriteGuard<..>>` for the latch (so `release` can `take()` it), `is_dirty`, `Deref`/`DerefMut`. `release()` drops the latch then calls `unpin_page(page_id, is_dirty)`; `Drop` calls `release()`.
- **1g-02:** `read_page` / `write_page` wrap `checked_*`; `flush()` copies the bytes out and writes them while the guard keeps its pin and latch.
- **2b-07, 08, 10:** the table's code holds guards in local variables; their scope *is* the critical section, and `drop(guard)` marks where it ends.

### Where it is used

- **All Rust synchronisation**: `MutexGuard`, `RwLockReadGuard`, `Ref`/`RefMut`, `File`, `JoinHandle`-with-`Drop`, `tracing`'s span guards.
- **C++ equivalents**: `std::lock_guard`, `std::unique_ptr`, `scoped_lock`, BusTub's own `ReadPageGuard`.
- **Transactions**: a "transaction guard" that rolls back on `Drop` unless `commit()` was called (the pattern in `rusqlite` and `sqlx`).
- **Scoped resources**: temp dirs deleted on drop, spans closed on drop, locks released on drop.
