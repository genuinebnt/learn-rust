**Where this fits.** The mirror of the last stage.

## The task

In `record_access` (`src/buffer/arc_replacer.rs`): for a page that is a ghost on **`mfu_ghost`**: remove the ghost, **lower** `p` by `delta` (never below 0), and bring the page back on `mfu` as before. Here `delta` is `1` if `mfu_ghost` is at least as long as `mru_ghost`, otherwise `mru_ghost.len() / mfu_ghost.len()`.

## Tests

- BusTub's `SampleTest` through "p is adjusted down by 1/1 = 1": after the second eviction `p` is 3, a hit on page 1 (an `mfu_ghost`) lowers it to 2, and the next eviction takes from `mru` (page 7), skipping the pinned frame 6.
- The target stops at 0 and doesn't wrap around to a huge `usize`.

## Syntax and methods

```rust
self.mru_target_size = self.mru_target_size.saturating_sub(delta);   // 0 is the floor
```

## Notes

If your tests pass with `p` going negative-as-huge, that is `usize` underflow: in a debug build it panics, in release it wraps and the policy silently degenerates into "always evict from `mfu`". `saturating_sub` states the intent. Rust's integer overflow checking in debug builds is one of the cheapest bug-finders you get for free: leave it on in tests.

## In BusTub

"Case III: the page is in mfu_ghost: p = max(p - delta, 0), delta = 1 if |B2| >= |B1| else |B1| / |B2|. Move the page to the front of mfu."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `p = std::max<size_t>(p - delta, 0)`: the subtraction wraps *before* `max` sees it (a classic ARC port bug) | `p.saturating_sub(delta)` |
| `-fsanitize=undefined` / `-ftrapv` to catch signed overflow (unsigned wraps by definition) | debug builds panic on any overflow; `checked_*`, `wrapping_*`, `saturating_*` say what you mean |
| compare `int` with `size_t` (sign-compare warnings, surprising conversions) | no implicit conversions: the compiler makes you cast |

## Learn more
- [Integer overflow in Rust](https://doc.rust-lang.org/book/ch03-02-data-types.html#integer-overflow) · [`checked_sub`](https://doc.rust-lang.org/std/primitive.usize.html#method.checked_sub)
