**Where this fits.** Sometimes a page must reach the disk *now* (a checkpoint, a test, a shutdown).

## The task

In `src/buffer/buffer_pool_manager.rs`:
- `flush_page(page_id) -> bool`: if the page is in memory, write it to disk **whether or not it is dirty**, mark it clean, return `true`; if not, return `false` and write nothing. A pinned page may be flushed (the pin stays);
- `flush_all_pages()`: flush every page that is in memory.

## Tests

- A dirty page flushed is on disk (the disk's copy has the bytes); a clean page is written too; an unknown page returns `false` with no write.
- After a flush, evicting the page writes nothing more. A pinned page can be flushed and stays pinned.
- `flush_all_pages` writes every resident page, and again on a second call.

## Syntax and methods

```rust
let pages: Vec<PageId> = self.inner.lock().unwrap().page_table.keys().copied().collect();   // snapshot the keys, release the lock
for page in pages { self.flush_page(page); }                                                // flush_page locks again, one page at a time
```

## Notes

**Never call a locking method while holding the lock.** `std::sync::Mutex` is not reentrant: locking it twice on one thread **deadlocks** (or panics). `flush_all_pages` collects the page ids, drops its guard, and then calls `flush_page`, which takes the lock itself. The C++ solutions use `std::scoped_lock` in both and need a private unlocked helper (`FlushPageUnsafe` in BusTub's header) for exactly this reason.

## In BusTub

```cpp
auto FlushPageUnsafe(page_id_t page_id) -> bool;   // flushes without taking the latch: the caller holds it
auto FlushPage(page_id_t page_id) -> bool;         // takes the latch, then does the same
void FlushAllPagesUnsafe();  void FlushAllPages();
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `Foo` / `FooUnsafe` pairs: one locks, one assumes the lock is held | a private function that takes `&mut Inner` (the lock's contents), and a public one that locks and calls it |
| `std::recursive_mutex` to allow re-locking | no recursive mutex in std; restructure instead |
| `fsync` after writing, for durability | the disk manager decides (`sync_all` in `shut_down`); a flush here means "handed to the disk layer" |

**Port rule:** when C++ has `Method` and `MethodUnsafe`/`MethodLocked`, Rust usually has a function taking the guard (or `&mut Inner`) as an argument: you can't call it without proof that you hold the lock.

## Learn more
- [Deadlock](https://en.wikipedia.org/wiki/Deadlock) · [`Mutex` docs: "locking twice on the same thread"](https://doc.rust-lang.org/std/sync/struct.Mutex.html#method.lock)
