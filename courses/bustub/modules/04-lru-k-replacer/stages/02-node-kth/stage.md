**Where this fits.** The number the policy ranks frames by.

## The task

Implement `kth_timestamp()` in `src/buffer/lru_k_replacer.rs`: the timestamp of the **k-th most recent access** (the oldest one kept), or `None` if there have been fewer than `k` accesses. `None` means the **backward k-distance is +infinity** ("never accessed k times"). The distance itself is `now − kth_timestamp`; you never need `now`, since the oldest k-th timestamp is the largest distance.

## Tests

- With k = 3: `None` after 0, 1 and 2 accesses; `Some(oldest)` once there are 3, and it moves forward as old accesses fall out.
- With k = 1 it is the latest access.

## Syntax and methods

```rust
if self.history.len() < self.k { None } else { self.history.front().copied() }
```

## Notes

`Option<usize>` here carries a real idea: **infinity**. Modelling "no value yet, and it ranks above every value" as `None` is natural; ordering it is the next stages' job. (`Option<T>` orders `None < Some(_)`, which is the *opposite* of what we want for distance, a trap in stage 6.)

## In BusTub

"A frame with less than k historical references is given +inf as its backward k-distance. When multiple frames have +inf backward k-distance, classical LRU is used to choose victim." (the header comment of `lru_k_replacer.h`)

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::numeric_limits<size_t>::max()` or `INFINITY` as a sentinel for "infinite" | `None` |
| `-1` / `SIZE_MAX` as "not found" in an unsigned type | `Option<usize>` |
| comparing a sentinel by accident with a real value | the type forces you to handle `None` |

**Port rule:** in-band sentinels (`-1`, `UINT_MAX`, `nullptr`, `end()`) become `Option`. Decide explicitly how `None` ranks when you sort.

## Learn more
- [`Option`](https://doc.rust-lang.org/std/option/enum.Option.html) · The Rust Book: [the `Option` enum](https://doc.rust-lang.org/book/ch06-01-defining-an-enum.html#the-option-enum-and-its-advantages-over-null-values)
