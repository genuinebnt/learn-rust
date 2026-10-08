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
