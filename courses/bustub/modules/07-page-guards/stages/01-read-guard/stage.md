**Where this fits.** `fetch_page` / `unpin_page` work, but every caller must remember to unpin on every path, and to latch the frame while using it. Forget either and the pool leaks pins or corrupts pages. A **page guard** makes that impossible: an object whose existence *is* the pin and the latch.

## The idea

A `ReadPageGuard` holds three things: the pool (to unpin later), the page id, and the **read latch** of the page's frame (the `RwLockReadGuard` your pool's `frame_data` hands out). While it lives: the page is pinned, so it can't be evicted, and shared-latched, so nobody can write it, and any number of other readers may also hold it.

## The task

`src/storage/page/page_guard.rs` has `ReadPageGuard<'a>` (it borrows the pool for `'a`) with its fields; `new` is given. In `src/buffer/buffer_pool_manager.rs` implement `checked_read_page(page_id) -> Option<ReadPageGuard<'_>>`: **pin** the page with `fetch_page` (`None` if every frame is pinned), **then** take the frame's read latch, **then** build the guard. In `src/storage/page/page_guard.rs` implement `get_data()`: the page's bytes behind the latch.

Do not worry about dropping yet: this stage's guards never give their pin back.

## Tests

- A read guard pins the page (pin count 1), reports its page id and shows 8192 zero bytes; it derefs to the page; three readers of one page give pin count 3.
- With every frame pinned, no guard: `None`.

## Syntax and methods

```rust
let frame = self.fetch_page(page_id)?;                      // pins; the pool's lock is released when fetch_page returns
let latch = self.frames[frame.0].read().unwrap();           // may block while a writer holds the frame: no pool lock is held
Some(ReadPageGuard::new(self, page_id, frame, latch))
pub fn get_data(&self) -> &PageData { self.latch.as_ref().expect("this guard has been released") }   // &RwLockReadGuard<Box<PageData>> derefs to &PageData
```

## Notes

**Lifetimes.** `ReadPageGuard<'a>` can't outlive the pool it borrows (`&'a BufferPoolManager`) or the latch it holds (borrowed from the pool's frames): `'a` ties them together, and the compiler refuses code that would let a guard outlive its pool. In C++ the guard holds `shared_ptr`s to the replacer, the latch and the scheduler (BusTub's `ReadPageGuard` constructor takes four of them) to keep those alive; in Rust the borrow checker does that job at compile time, for free.

**Order.** Pin *first* (under the pool lock), latch *second* (without it). If you latch first, the page might be evicted before you pin; if you wait for the latch while holding the pool lock, you block everyone (stage 6).

## In BusTub

```cpp
auto BufferPoolManager::CheckedReadPage(page_id_t page_id, AccessType access_type) -> std::optional<ReadPageGuard> {
  /* find or load the frame, pin it, register the access, set it non-evictable, release bpm_latch_, THEN: */
  frame->rwlatch_.lock_shared();   // inside the ReadPageGuard constructor
  return ReadPageGuard(page_id, frame, replacer_, bpm_latch_, disk_scheduler_);
}
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `class ReadPageGuard` holding `shared_ptr<FrameHeader>`, `shared_ptr<ArcReplacer>`, `shared_ptr<mutex>`, `shared_ptr<DiskScheduler>` | `struct ReadPageGuard<'a> { bpm: &'a BufferPoolManager, .. }`: one borrow, checked at compile time |
| `frame_->rwlatch_.lock_shared()` / `unlock_shared()` by hand (RAII wrapper optional) | `RwLockReadGuard`: the lock is held exactly as long as the guard value lives |
| `template <class T> auto As() const -> const T * { return reinterpret_cast<const T *>(GetData()); }` | `Deref<Target = PageData>`; typed views come in the Index module (no `reinterpret_cast`) |
| `const char *GetData() const` (a pointer: no length, no lifetime) | `&PageData` (`&[u8; 8192]`): length in the type, lifetime tied to the guard |
| `std::optional<ReadPageGuard>` returned from `Checked*` | `Option<ReadPageGuard<'_>>` |

**Port rule:** a C++ class that locks in the constructor and unlocks in the destructor *is* a guard type: in Rust it usually wraps an std lock guard, and the destructor is the field's own `Drop`.

## Learn more
- The Rust Book: [lifetimes in structs](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#lifetime-annotations-in-struct-definitions) · [`RwLockReadGuard`](https://doc.rust-lang.org/std/sync/struct.RwLockReadGuard.html) · [`Deref`](https://doc.rust-lang.org/std/ops/trait.Deref.html)
- C++ [`std::shared_lock`](https://en.cppreference.com/w/cpp/thread/shared_lock) · BusTub [page_guard.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/page/page_guard.h)
