---
title: Mutex<T> owns its data: critical sections without a forgotten lock
summary: Why std::mutex plus a variable is a convention and Mutex<T> is a guarantee, how the guard defines the critical section, and what poisoning and lock ordering mean.
minutes: 9
---
BusTub protects its shared state with latches: `db_io_latch_`, the buffer pool's `latch_`, a page's reader-writer latch. Rust has the same primitives, but ties each one to the data it protects. That one change removes the commonest concurrency bug in C++ code.

## The C++ way: a mutex next to a variable

```cpp
std::mutex latch_;
std::unordered_map<page_id_t, size_t> pages_;           // "protected by latch_" says a comment

void DiskManager::DeletePage(page_id_t id) {
  std::scoped_lock lock(latch_);                         // RAII: unlocks at the closing brace
  ...
}
size_t DiskManager::Count() { return pages_.size(); }    // compiles; forgot the lock; a data race = undefined behaviour
```

Nothing connects `latch_` to `pages_`. The compiler cannot tell you that `Count` forgot to lock. Clang's thread-safety annotations (`GUARDED_BY`) and ThreadSanitizer find it, if you run them.

## The Rust way: the data lives inside

```rust
struct DbIo { file: File, pages: HashMap<PageId, usize>, free_slots: Vec<usize>, num_slots: usize, page_capacity: usize }

pub struct DiskManager { db_io: Mutex<DbIo>, /* .. */ }

fn delete_page(&self, id: PageId) {
    let mut io = self.db_io.lock().unwrap();     // io: MutexGuard<DbIo>: the only way to reach the fields
    if let Some(slot) = io.pages.remove(&id) { io.free_slots.push(slot); }
}                                                // `io` is dropped here: unlocked
```

`Mutex<T>` **contains** the `T`. The only way to the data is `lock()`, which returns a `MutexGuard<T>` that derefs to `&mut T`; when the guard is dropped, the lock is released. There is no code path that reaches `pages` without holding the lock, and forgetting to unlock is impossible. The compiler also stops you leaking a reference past the guard: `let r = &io.pages;` cannot outlive `io`.

```svg
caption: Two threads call write_page at the same time. Each guard's lifetime is its critical section, and the two sections cannot overlap: thread B's lock() waits until thread A's guard is dropped.
<svg viewBox="0 0 760 190" role="img" aria-label="Two thread timelines where the second thread waits for the first to drop its lock guard">
<line class="grid" x1="90" y1="50" x2="740" y2="50"/><line class="grid" x1="90" y1="130" x2="740" y2="130"/>
<text class="big" x="20" y="55">A</text><text class="big" x="20" y="135">B</text>
<rect class="live" x="150" y="32" width="250" height="36" rx="4"/><text class="mid t-g" x="275" y="55">guard held: pwrite</text>
<text class="dim sm" x="100" y="26">lock()</text><text class="dim sm" x="380" y="26">drop</text>
<rect class="never" x="170" y="112" width="230" height="36" rx="4"/><text class="mid dim sm" x="285" y="135">B waits in lock()</text>
<rect class="live" x="400" y="112" width="250" height="36" rx="4"/><text class="mid t-g" x="525" y="135">guard held: pwrite</text>
<path class="ln-w dash" d="M400 70 V110"/><text class="t-w sm" x="410" y="95">A's drop wakes B</text>
<text class="dim sm" x="150" y="180">time &#8594;</text>
</svg>
```

## The guard is the critical section

The critical section is exactly the guard's lifetime, which is a lexical scope. That is useful and a trap:

```rust
let slot = {
    let mut io = self.db_io.lock().unwrap();
    io.allocate_slot()?
};                               // lock released here, before the slow part
write_slot(&file, slot, data)?;  // but now another thread can see the new slot before it is written: is that safe?
```

Two rules of thumb. **Keep the section as small as the invariant allows**, because every thread that wants the lock waits for the whole of it. And **never split one decision across two acquisitions**: "do I have a slot for this page?" and "give it one" are one critical section, as the concept on slot allocation shows. To release early on purpose, use an inner block or `drop(guard)`.

The disk manager deliberately holds its lock across the `pwrite`. That serialises I/O, which BusTub accepts; the point is that it is a *choice you can read in the code*.

## Poisoning

If a thread panics while holding the guard, the data may be half-updated. Rust marks the mutex **poisoned**, and every later `lock()` returns `Err(PoisonError)`. Calling `.unwrap()` on it panics too: the failure spreads instead of letting other threads read a corrupt structure. C++'s `std::mutex` has no equivalent; the lock is released during unwinding and the damage is invisible. (You can recover the data with `into_inner()` if you can prove it is consistent.)

## `&self` and interior mutability

`DiskManager` methods take `&self`, not `&mut self`, so many threads can hold `&DiskManager` at once. That would be impossible if mutation required `&mut`; `Mutex` is the *interior mutability* that makes `&self` enough: shared reference in, exclusive access out, checked at run time by the lock instead of at compile time by the borrow checker. The compiler lets you share it between threads because `Mutex<T>` is `Sync` whenever `T` is `Send`.

## Lock ordering

When code needs two locks, every thread must take them in the same order, or two threads can each hold one and wait for the other: a **deadlock**. Rust does not prevent it; the discipline is the same as in C++. The disk manager sidesteps it by having one lock; the buffer pool in module 1f has a pool lock *and* per-page latches and has to choose, in writing, which comes first.

| | C++ | Rust |
|---|---|---|
| declare | `std::mutex m; T data;` | `Mutex<T>` |
| lock for a scope | `std::scoped_lock l(m);` / `lock_guard` | `let g = m.lock().unwrap();` |
| unlock early | `l.unlock()` / inner scope | `drop(g)` / inner scope |
| forgot to lock | compiles; a data race | does not compile |
| reader/writer | `std::shared_mutex` | `RwLock<T>` |
| a thread died holding it | lock released, data possibly torn | the mutex is poisoned |
