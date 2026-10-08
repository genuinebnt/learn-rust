**Where this fits.** Which directory does a hash belong to?

## The task

Implement `hash_to_directory_index(hash: u32) -> u32` in `src/storage/page/extendible_htable_header_page.rs`: the **top `max_depth` bits** of the hash, as a number. With `max_depth == 0` there is one directory and the answer is 0.

## Tests

- With max depth 2 the hashes 32768, 1073774592, 2147516416 and 3221258240 (top bits 00, 01, 10, 11) map to 0, 1, 2, 3 (BusTub's own sample).
- Depth 0: always 0. Depth 1: the top bit. Depth 9: `u32::MAX` is 511. The low bits are ignored.

## Syntax and methods

```rust
match self.max_depth() { 0 => 0, depth => hash >> (32 - depth) }     // a shift by 32 would overflow: depth 0 needs its own case
```

## Notes

**Shift amounts.** `x >> 32` on a `u32` is an error in Rust (a panic in debug builds, "attempt to shift right with overflow") and **undefined behaviour in C and C++**: the CPU masks the shift count to 5 bits, so `x >> 32` is `x >> 0` on x86 and something else on ARM. BusTub's depth-0 header would trip this in C++; the explicit case, or `checked_shr`, avoids it. `u32::checked_shr(n)` returns `None` for `n >= 32`: `hash.checked_shr(32 - depth).unwrap_or(0)` is a one-liner for the same result.

**Top bits for the header, low bits for the directory.** They use different ends of the hash on purpose: a directory splits on its low bits one at a time as it grows, so the header must not consume those. This is the same trick as a radix tree: successive levels consume successive bit ranges.

## In BusTub

```cpp
auto ExtendibleHTableHeaderPage::HashToDirectoryIndex(uint32_t hash) const -> uint32_t { /* TODO(P2) */ }   // "the upper max_depth_ bits"
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `hash >> (32 - max_depth_)` with `max_depth_ == 0`: undefined behaviour | an explicit case, or `checked_shr` |
| `hash >> n` where `hash` is signed: implementation-defined (arithmetic vs logical) | `u32` is always a logical shift; for signed `i32` Rust's `>>` is arithmetic and documented |
| bit-twiddling with `0xFFFFFFFF << n` masks | `(1u32 << n) - 1` or `u32::MAX >> (32 - n)` (same care at n = 0 and n = 32) |

**Port rule:** every shift whose amount is data-dependent needs a look at the boundary values 0 and the type's width; Rust turns the bug into a panic (debug) instead of a silent wrong answer.

## Learn more
- [`u32::checked_shr`](https://doc.rust-lang.org/std/primitive.u32.html#method.checked_shr) · [Arithmetic overflow in the Reference](https://doc.rust-lang.org/reference/expressions/operator-expr.html#overflow) · CMU 15-445 "Hash Tables"
