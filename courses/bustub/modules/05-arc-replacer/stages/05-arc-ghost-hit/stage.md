**Where this fits.** The adaptive part of ARC.

## The task

In `src/buffer/arc_replacer.rs`:
1. In `record_access`, when the page is not on a live frame but **is a ghost on `mru_ghost`**: remove the ghost, **raise the target** `p` by `delta`, and bring the page back as a live frame (the frame passed in) at the newest end of **`mfu`**, not evictable. `delta` is `1` if `mru_ghost` is at least as long as `mfu_ghost`, otherwise `mfu_ghost.len() / mru_ghost.len()` (compute it *before* removing the hit ghost). `p` never exceeds `c`, the number of frames.
2. In `evict`, choose the side by the target: take from `mru` first if it holds **at least `p` live frames** (pinned ones count), otherwise from `mfu` first; if the preferred list has no evictable frame, use the other.

## Tests

- A page evicted and re-accessed comes back on `mfu` (it is evicted after the `mru` frames).
- An unseen page is **not** a ghost hit (BusTub: "this should NOT be a hit on ghost list since we've never seen page 7").
- BusTub's `SampleTest` up to "mru is smaller than target, mfu is victimized": `p` goes 0 → 1 → 3 through two ghost hits, then eviction switches side.
- If the preferred side has nothing evictable, the other is used.

## Syntax and methods

```rust
let delta = if self.mru_ghost.len() >= self.mfu_ghost.len() { 1 } else { self.mfu_ghost.len() / self.mru_ghost.len() };
self.mru_target_size = (self.mru_target_size + delta).min(self.replacer_size);
let order = if self.mru.len() >= self.mru_target_size { [ArcStatus::Mru, ArcStatus::Mfu] } else { [ArcStatus::Mfu, ArcStatus::Mru] };
```

## Notes

Integer division by zero: `mfu_ghost.len() / mru_ghost.len()` is only evaluated in the branch where `mru_ghost` is *shorter* than `mfu_ghost`, hence non-zero, because it contains the ghost that was just hit. The branch structure makes that safe; a rewrite with `max(1, a / b)` would divide by zero when `mru_ghost` is empty. (Rust panics on integer division by zero; C and C++ have **undefined behaviour**, usually a crash from `SIGFPE`.)

## In BusTub

"Case II: the page is in mru_ghost: adapt the target: p = min(p + delta, c), delta = 1 if |B1| >= |B2| else |B2| / |B1|. Move the page to the front of mfu."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::min(a, b)` | `a.min(b)` (method on `Ord`) |
| `a / b` with `b == 0`: undefined behaviour | panics ("attempt to divide by zero") in every build |
| `size_t` arithmetic that underflows (`p - delta`) wraps to a huge number | `usize` subtraction panics in debug; use `saturating_sub` when 0 is the answer |
| `if (a >= b) {...} else {...}` | `if a >= b { .. } else { .. }` as an expression |

## Learn more
- ARC paper, section III.B ("Adaptation") · [`usize::saturating_sub`](https://doc.rust-lang.org/std/primitive.usize.html#method.saturating_sub) · [`Ord::min`](https://doc.rust-lang.org/std/cmp/trait.Ord.html#method.min)
