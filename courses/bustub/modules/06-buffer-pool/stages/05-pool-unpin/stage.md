**Where this fits.** The counterpart of `fetch_page`.

## The task

Implement `unpin_page(page_id, is_dirty) -> bool` in `src/buffer/buffer_pool_manager.rs`: if the page is in memory with a pin count above zero, subtract one, **OR** `is_dirty` into the frame's dirty flag (a flag, once set, stays set until the page is written), and if the count reached zero tell the replacer the frame is **evictable**; return `true`. Otherwise (not in memory, or pin count already 0) return `false` and change nothing.

## Tests

- Two pins, two unpins: counts 1 then 0, the page stays in memory. Unpinning an unknown page or a page at 0 returns `false` (and the count doesn't go negative).
- A page can be fetched again after being unpinned, with no new disk read.

## Syntax and methods

```rust
meta.pin_count -= 1;
meta.dirty |= is_dirty;                          // bool |= bool
if meta.pin_count == 0 { inner.replacer.set_evictable(frame, true); }
```

## Notes

The borrow checker's first complaint here: `let meta = &mut inner.meta[frame.0];` borrows `inner.meta`, then `inner.replacer.set_evictable(..)` borrows `inner.replacer`. Because `inner` is a `MutexGuard`, `inner.meta` and `inner.replacer` both go through `DerefMut` on the *whole* guard, so the compiler sees two `&mut` of `inner` and refuses. The fix is either to finish with `meta` before touching `replacer` (copy the count out), or to take `let inner = &mut *guard;` once, which lets Rust split the borrow across fields. Remember this one: it comes up whenever you lock a struct and use two of its fields.

## In BusTub

The destructor of `ReadPageGuard`/`WritePageGuard` does this: lock the pool, `pin_count_--`, `is_dirty_ |= ...`, and `if (pin_count_ == 0) replacer_->SetEvictable(frame_id_, true)`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `frame->is_dirty_ \|= is_dirty;` (`bool \|=` is legal C++ but promotes through `int`) | `meta.dirty \|= is_dirty;` |
| `pin_count_--` on a `size_t` at 0 wraps to 2^64 - 1 | `-= 1` on `usize` panics in debug; the explicit check returns `false` first |
| two locks: `bpm_latch_` and the frame's `rwlatch_` | two locks, taken in a fixed order (pool first, then never frame while waiting; see the next module) |

## Learn more
- Rust Nomicon, [splitting borrows](https://doc.rust-lang.org/nomicon/borrow-splitting.html) · [`MutexGuard` deref](https://doc.rust-lang.org/std/sync/struct.MutexGuard.html)
