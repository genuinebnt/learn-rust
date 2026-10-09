The textbook interface asks callers to pair `fetch_page` with `unpin_page` by hand, and a forgotten unpin leaks a frame until the pool stops working. A **page guard** makes the pairing impossible to forget: creating the guard pins the page and takes its latch, and dropping it releases both, on every path, including an early `return`, a `?` and a panic.

This stage builds `ReadPageGuard` and `WritePageGuard` on top of the pool you wrote: shared and exclusive access, a dirty flag set automatically when you take the mutable view, and a release that is idempotent. The lesson is as much about **Rust's ownership and lifetimes** as about the buffer pool.

## Part 1 · ReadPageGuard: pin the page, then take its read latch

**Where this fits.** `fetch_page` / `unpin_page` work, but every caller must remember to unpin on every path, and to latch the frame while using it. Forget either and the pool leaks pins or corrupts pages. A **page guard** makes that impossible: an object whose existence *is* the pin and the latch.

### The idea

A `ReadPageGuard` holds three things: the pool (to unpin later), the page id, and the **read latch** of the page's frame (the `RwLockReadGuard` your pool's `frame_data` hands out). While it lives: the page is pinned, so it can't be evicted, and shared-latched, so nobody can write it, and any number of other readers may also hold it.

> [!CHECK] A guard is dropped. In which order does it give back its latch and its pin, and what could go wrong with the other order? Think about who else can run in between.
> ||Latch first, then pin. Dropping the pin makes the frame evictable. If that came first, the pool could evict the page and reuse the frame for another page while the guard still holds (and is about to release) a latch on it, so the latch would be released on a frame that now holds something else.||
>
> - What does unpinning tell the replacer?
> - What can a thread do to a frame whose pin count is zero?
> - A latch protects the bytes of one page: which page is in the frame after an eviction?

### The task

`src/storage/page/page_guard.rs` has `ReadPageGuard<'a>` (it borrows the pool for `'a`) with its fields; `new` is given. In `src/buffer/buffer_pool_manager.rs` implement `checked_read_page(page_id) -> Option<ReadPageGuard<'_>>`: **pin** the page with `fetch_page` (`None` if every frame is pinned), **then** take the frame's read latch, **then** build the guard. In `src/storage/page/page_guard.rs` implement `get_data()`: the page's bytes behind the latch.

Do not worry about dropping yet: this stage's guards never give their pin back.

### Tests

- A read guard pins the page (pin count 1), reports its page id and shows 8192 zero bytes; it derefs to the page; three readers of one page give pin count 3.
- With every frame pinned, no guard: `None`.

### Syntax and methods

```rust
let frame = self.fetch_page(page_id)?;                      // pins; the pool's lock is released when fetch_page returns
let latch = self.frames[frame.0].read().unwrap();           // may block while a writer holds the frame: no pool lock is held
Some(ReadPageGuard::new(self, page_id, frame, latch))
pub fn get_data(&self) -> &PageData { self.latch.as_ref().expect("this guard has been released") }   // &RwLockReadGuard<Box<PageData>> derefs to &PageData
```

### Notes

**Lifetimes.** `ReadPageGuard<'a>` can't outlive the pool it borrows (`&'a BufferPoolManager`) or the latch it holds (borrowed from the pool's frames): `'a` ties them together, and the compiler refuses code that would let a guard outlive its pool. In C++ the guard holds `shared_ptr`s to the replacer, the latch and the scheduler (BusTub's `ReadPageGuard` constructor takes four of them) to keep those alive; in Rust the borrow checker does that job at compile time, for free.

**Order.** Pin *first* (under the pool lock), latch *second* (without it). If you latch first, the page might be evicted before you pin; if you wait for the latch while holding the pool lock, you block everyone (stage 6).

### In BusTub

```cpp
auto BufferPoolManager::CheckedReadPage(page_id_t page_id, AccessType access_type) -> std::optional<ReadPageGuard> {
  /* find or load the frame, pin it, register the access, set it non-evictable, release bpm_latch_, THEN: */
  frame->rwlatch_.lock_shared();   // inside the ReadPageGuard constructor
  return ReadPageGuard(page_id, frame, replacer_, bpm_latch_, disk_scheduler_);
}
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `class ReadPageGuard` holding `shared_ptr<FrameHeader>`, `shared_ptr<ArcReplacer>`, `shared_ptr<mutex>`, `shared_ptr<DiskScheduler>` | `struct ReadPageGuard<'a> { bpm: &'a BufferPoolManager, .. }`: one borrow, checked at compile time |
| `frame_->rwlatch_.lock_shared()` / `unlock_shared()` by hand (RAII wrapper optional) | `RwLockReadGuard`: the lock is held exactly as long as the guard value lives |
| `template <class T> auto As() const -> const T * { return reinterpret_cast<const T *>(GetData()); }` | `Deref<Target = PageData>`; typed views come in the Index module (no `reinterpret_cast`) |
| `const char *GetData() const` (a pointer: no length, no lifetime) | `&PageData` (`&[u8; 8192]`): length in the type, lifetime tied to the guard |
| `std::optional<ReadPageGuard>` returned from `Checked*` | `Option<ReadPageGuard<'_>>` |

**Port rule:** a C++ class that locks in the constructor and unlocks in the destructor *is* a guard type: in Rust it usually wraps an std lock guard, and the destructor is the field's own `Drop`.

### Learn more
- The Rust Book: [lifetimes in structs](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#lifetime-annotations-in-struct-definitions) · [`RwLockReadGuard`](https://doc.rust-lang.org/std/sync/struct.RwLockReadGuard.html) · [`Deref`](https://doc.rust-lang.org/std/ops/trait.Deref.html)
- C++ [`std::shared_lock`](https://en.cppreference.com/w/cpp/thread/shared_lock) · BusTub [page_guard.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/page/page_guard.h)

## Part 2 · Dropping a read guard: unlatch, then unpin

**Where this fits.** The point of a guard.

### The task

In `src/storage/page/page_guard.rs`:
- `ReadPageGuard::release(&mut self)`: if the guard still holds its latch, **drop the latch**, then **unpin the page**. Calling it again does nothing. (BusTub's `Drop()`.)
- `impl Drop for ReadPageGuard`: call `release`.

### Tests

- Dropping a guard (explicitly, or by leaving its scope) takes the pin count from 1 to 0. Two readers: each releases only its own pin. `release()` is idempotent, and so is the destructor after it.
- A released guard gave up the latch (`try_write` on the frame succeeds); an unpinned page's frame can be reused for another page.

### Syntax and methods

```rust
if let Some(latch) = self.latch.take() {      // Option::take: `release` only has &mut self, so move the latch out of the Option
    drop(latch);                              // 1. unlatch
    self.bpm.unpin_page(self.page_id, false); // 2. unpin
}
impl Drop for ReadPageGuard<'_> { fn drop(&mut self) { self.release(); } }
```

### Notes

**The order matters.** Unlatch *before* unpin. Between the two, the page is still pinned (can't be evicted) but unlatched: harmless. The other way round, the page could be unpinned (and evicted, and its frame reused) while this thread still holds the old frame's latch: the evictor would then block on, or worse bypass, a latch it assumes nobody holds. Rust drops fields in declaration order *after* your `drop` body, so putting the latch in an `Option` and taking it explicitly is how you control the order.

**Why `release()` and not just `drop(guard)`?** `drop(guard)` moves the guard, so a second drop can't even be written: ownership already prevents what BusTub's test checks ("Another drop should have no effect"). The test still calls `release()` twice because a C++ guard can be dropped twice; this method is the C++ `Drop()` in Rust.

### In BusTub

```cpp
void ReadPageGuard::Drop() {
  if (!is_valid_) { return; }
  frame_->rwlatch_.unlock_shared();                      // unlatch first
  { std::scoped_lock l(*bpm_latch_);                     // then, under the pool's latch:
    if (--frame_->pin_count_ == 0) { replacer_->SetEvictable(frame_->frame_id_, true); } }
  is_valid_ = false;
}
ReadPageGuard::~ReadPageGuard() { Drop(); }
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `bool is_valid_{false}` so a moved-from or default guard's destructor does nothing | `Option` field (`None` = released): the type says it |
| `~ReadPageGuard() { Drop(); }` | `impl Drop`; fields are dropped afterwards automatically |
| a moved-from C++ object still exists and is destroyed (so the move constructor must neutralise it) | Rust moves are bitwise and the source is never dropped |
| RAII for locks: `std::lock_guard`, `std::unique_lock` | `MutexGuard`, `RwLockReadGuard`: the same idea, enforced by the type system |

**Port rule:** `is_valid_`-style flags in C++ move-aware classes disappear in Rust: either the value exists (and owns the resource) or it doesn't.

### Learn more
- The Rust Book: [`Drop`](https://doc.rust-lang.org/book/ch15-03-drop.html) · [drop order](https://doc.rust-lang.org/reference/destructors.html#drop-scopes) · [`Option::take`](https://doc.rust-lang.org/std/option/enum.Option.html#method.take)
- CMU 15-445 "Memory Management" lecture (pinning) · *Rust Atomics and Locks*, [guards and RAII](https://marabos.nl/atomics/building-locks.html)

## Part 3 · WritePageGuard: the write latch and the dirty flag

**Where this fits.** The writer's side: exclusive access, and telling the pool the page changed.

### The task

In `src/buffer/buffer_pool_manager.rs`, `checked_write_page(page_id)`: like `checked_read_page`, with the frame's **write** latch. In `src/storage/page/page_guard.rs` for `WritePageGuard`:
- `get_data()`: the bytes;
- `get_data_mut()`: **mark the guard dirty**, then hand out the bytes mutably;
- `release()` and `Drop`: as for the read guard, but `unpin_page(page_id, self.is_dirty)`, so the pool learns about the change. (`is_dirty()`, `Deref` and `DerefMut` are given.)

### Tests

- A write is visible afterwards. `get_data()` doesn't mark dirty, `get_data_mut()` does. Dirt reaches the pool: a page changed through a guard survives eviction (it is written back exactly once); an untouched write guard leaves the page clean (no write).
- A writer excludes everybody: a reader on another thread gets in only after the writer is dropped. `release()` is idempotent; `guard[0] = 7` works through `DerefMut`.

### Syntax and methods

```rust
let latch = self.frames[frame.0].write().unwrap();              // RwLockWriteGuard<'_, Box<PageData>>
self.is_dirty = true;
self.latch.as_mut().expect("this guard has been released")      // Option<RwLockWriteGuard> -> &mut Box<PageData> -> &mut PageData by deref coercion
```

### Notes

**Dirty on request, not on suspicion.** The guard doesn't know whether you changed bytes, but it knows whether you *asked for permission to*: `get_data_mut()`. This is why Rust APIs split `&self`/`&mut self` getters: the type system tells the guard when a write may happen. BusTub does the same: `GetDataMut()` sets `is_dirty_`. A write guard that never calls it costs no disk write on eviction.

**`&mut self` on the getter** is the borrow checker enforcing "one writer at a time" *within* a thread too: you can't hold the `&mut PageData` and call `get_data()` on the same guard.

### In BusTub

```cpp
auto WritePageGuard::GetDataMut() -> char * { BUSTUB_ENSURE(is_valid_, "tried to use an invalid write guard"); is_dirty_ = true; ... }
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `GetData()` const vs `GetDataMut()` non-const, but a `const_cast` or a stored `char *` bypasses both | `&self` vs `&mut self`: no bypass without `unsafe` |
| `template <class T> auto AsMut() -> T * { return reinterpret_cast<T *>(GetDataMut()); }` | `DerefMut` to the byte array; typed views are the next module's topic |
| `BUSTUB_ENSURE(is_valid_, "...")` | `.expect("this guard has been released")` |
| `frame_->rwlatch_.lock()` / `unlock()` | `RwLock::write()` guard |

**Port rule:** a `const`/non-`const` method pair that encodes "reads" and "writes" becomes `&self` / `&mut self`; side effects tied to the write (dirty flag) go into the `&mut self` one.

### Learn more
- [`RwLockWriteGuard`](https://doc.rust-lang.org/std/sync/struct.RwLockWriteGuard.html) · [`DerefMut`](https://doc.rust-lang.org/std/ops/trait.DerefMut.html) · The Rust Book: [references and mutability](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html#mutable-references)

## Performance

Creating a guard costs what `fetch_page` costs (one pool-latch acquisition, a pin) **plus** one frame-latch acquisition; dropping it costs one frame-latch release and one pool-latch acquisition for the unpin. Both are in the tens to hundreds of nanoseconds uncontended. The guard struct itself is a few words and lives on the stack: **no allocation**, which is the cost model that makes RAII guards free abstractions.

Contention is where the choice of latch matters: many readers of one page share the frame's read latch and run in parallel; one writer excludes everyone for as long as the guard lives. Holding a guard across a slow operation (I/O, another latch wait) is the expensive mistake, and the type system does not catch it.

**Measure it.** Time 1 000 000 `read_page` + `drop` pairs from 1 and from 8 threads on the same page and on 8 different pages: the same-page case should scale (a read latch is shared) and the different-pages case should be limited only by the pool latch. Then time the same loop with a write guard on the same page and watch it serialise.

## Hints

### Pin first, latch second; unlatch first, unpin second

Acquire in the order **pin → latch** and release in the reverse, **unlatch → unpin**. The invariant is *a latched page is always pinned*: if the pin were dropped first, the replacer could choose the frame while a thread still holds its latch. And the pool's lock must **not** be held while waiting for the latch: take the pool lock to pin, release it, then block on the frame latch.

### Why does the guard keep an `Option` of the latch?

A struct that implements `Drop` cannot have a field moved out of it, but `release` must drop the latch *before* it unpins. Storing `Option<RwLockReadGuard<..>>` lets you `take()` the latch, drop it explicitly, and leave `None` behind, which also makes `release` **idempotent** (the second call finds `None` and does nothing) so `Drop` can always call it. Check that `release` followed by the end of scope unpins exactly once.

### Mutable access is what makes a page dirty

`get_data_mut` (and `DerefMut`) sets `is_dirty` as a side effect: the type system makes "I changed this page" part of taking the mutable view, rather than a flag the caller may forget to pass to `unpin`. `release` then passes that flag to `unpin_page`. Verify both directions with the pool's counters: a read guard never makes a page dirty, and a write guard that never took the mutable view does not either, so no needless write-back follows.
