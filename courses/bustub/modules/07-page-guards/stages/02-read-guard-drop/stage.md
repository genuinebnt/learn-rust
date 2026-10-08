**Where this fits.** The point of a guard.

## The task

In `src/storage/page/page_guard.rs`:
- `ReadPageGuard::release(&mut self)`: if the guard still holds its latch, **drop the latch**, then **unpin the page**. Calling it again does nothing. (BusTub's `Drop()`.)
- `impl Drop for ReadPageGuard`: call `release`.

## Tests

- Dropping a guard (explicitly, or by leaving its scope) takes the pin count from 1 to 0. Two readers: each releases only its own pin.
- `release()` is idempotent, and so is the destructor after it.
- A released guard gave up the latch (`try_write` on the frame succeeds); an unpinned page's frame can be reused for another page.

## Syntax and methods

```rust
if let Some(latch) = self.latch.take() {      // Option::take: `release` only has &mut self, so move the latch out of the Option
    drop(latch);                              // 1. unlatch
    self.bpm.unpin_page(self.page_id, false); // 2. unpin
}
impl Drop for ReadPageGuard<'_> { fn drop(&mut self) { self.release(); } }
```

## Notes

**The order matters.** Unlatch *before* unpin. Between the two, the page is still pinned (can't be evicted) but unlatched: harmless. The other way round, the page could be unpinned (and evicted, and its frame reused) while this thread still holds the old frame's latch: the evictor would then block on, or worse bypass, a latch it assumes nobody holds. Rust drops fields in declaration order *after* your `drop` body, so putting the latch in an `Option` and taking it explicitly is how you control the order.

**Why `release()` and not just `drop(guard)`?** `drop(guard)` moves the guard, so a second drop can't even be written: ownership already prevents what BusTub's test checks ("Another drop should have no effect"). The test still calls `release()` twice because a C++ guard can be dropped twice; this method is the C++ `Drop()` in Rust.

## In BusTub

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

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `bool is_valid_{false}` so a moved-from or default guard's destructor does nothing | `Option` field (`None` = released): the type says it |
| `~ReadPageGuard() { Drop(); }` | `impl Drop`; fields are dropped afterwards automatically |
| a moved-from C++ object still exists and is destroyed (so the move constructor must neutralise it) | Rust moves are bitwise and the source is never dropped |
| RAII for locks: `std::lock_guard`, `std::unique_lock` | `MutexGuard`, `RwLockReadGuard`: the same idea, enforced by the type system |

**Port rule:** `is_valid_`-style flags in C++ move-aware classes disappear in Rust: either the value exists (and owns the resource) or it doesn't.

## Learn more
- The Rust Book: [`Drop`](https://doc.rust-lang.org/book/ch15-03-drop.html) · [drop order](https://doc.rust-lang.org/reference/destructors.html#drop-scopes) · [`Option::take`](https://doc.rust-lang.org/std/option/enum.Option.html#method.take)
- CMU 15-445 "Memory Management" lecture (pinning) · *Rust Atomics and Locks*, [guards and RAII](https://marabos.nl/atomics/building-locks.html)
