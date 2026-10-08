**Where this fits.** The writer's side: exclusive access, and telling the pool the page changed.

## The task

In `src/buffer/buffer_pool_manager.rs`, `checked_write_page(page_id)`: like `checked_read_page`, with the frame's **write** latch. In `src/storage/page/page_guard.rs` for `WritePageGuard`:
- `get_data()`: the bytes;
- `get_data_mut()`: **mark the guard dirty**, then hand out the bytes mutably;
- `release()` and `Drop`: as for the read guard, but `unpin_page(page_id, self.is_dirty)`, so the pool learns about the change. (`is_dirty()`, `Deref` and `DerefMut` are given.)

## Tests

- A write is visible afterwards. `get_data()` doesn't mark dirty, `get_data_mut()` does.
- Dirt reaches the pool: a page changed through a guard survives eviction (it is written back exactly once); an untouched write guard leaves the page clean (no write).
- A writer excludes everybody: a reader on another thread gets in only after the writer is dropped. `release()` is idempotent; `guard[0] = 7` works through `DerefMut`.

## Syntax and methods

```rust
let latch = self.frames[frame.0].write().unwrap();              // RwLockWriteGuard<'_, Box<PageData>>
self.is_dirty = true;
self.latch.as_mut().expect("this guard has been released")      // Option<RwLockWriteGuard> -> &mut Box<PageData> -> &mut PageData by deref coercion
```

## Notes

**Dirty on request, not on suspicion.** The guard doesn't know whether you changed bytes, but it knows whether you *asked for permission to*: `get_data_mut()`. This is why Rust APIs split `&self`/`&mut self` getters: the type system tells the guard when a write may happen. BusTub does the same: `GetDataMut()` sets `is_dirty_`. A write guard that never calls it costs no disk write on eviction.

**`&mut self` on the getter** is the borrow checker enforcing "one writer at a time" *within* a thread too: you can't hold the `&mut PageData` and call `get_data()` on the same guard.

## In BusTub

```cpp
auto WritePageGuard::GetDataMut() -> char * { BUSTUB_ENSURE(is_valid_, "tried to use an invalid write guard"); is_dirty_ = true; ... }
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `GetData()` const vs `GetDataMut()` non-const, but a `const_cast` or a stored `char *` bypasses both | `&self` vs `&mut self`: no bypass without `unsafe` |
| `template <class T> auto AsMut() -> T * { return reinterpret_cast<T *>(GetDataMut()); }` | `DerefMut` to the byte array; typed views are the next module's topic |
| `BUSTUB_ENSURE(is_valid_, "...")` | `.expect("this guard has been released")` |
| `frame_->rwlatch_.lock()` / `unlock()` | `RwLock::write()` guard |

**Port rule:** a `const`/non-`const` method pair that encodes "reads" and "writes" becomes `&self` / `&mut self`; side effects tied to the write (dirty flag) go into the `&mut self` one.

## Learn more
- [`RwLockWriteGuard`](https://doc.rust-lang.org/std/sync/struct.RwLockWriteGuard.html) · [`DerefMut`](https://doc.rust-lang.org/std/ops/trait.DerefMut.html) · The Rust Book: [references and mutability](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html#mutable-references)
