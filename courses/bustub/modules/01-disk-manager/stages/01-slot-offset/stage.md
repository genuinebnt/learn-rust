**Where this fits.** The disk manager stores pages in a file. Before any I/O, one question: where in the file does a page go?

## The task

The db file is a row of equal-sized **slots**, one page each: slot 0 is bytes `0..8192`, slot 1 is `8192..16384`, and so on.
Implement `slot_offset(slot)` in `src/storage/disk/disk_manager.rs`: the byte where slot `slot` starts. Slot numbers are `usize`; file offsets are `u64`.

## Tests

- `slot_offset(0)` is `0`; `slot_offset(1)` is `8192`; `slot_offset(3)` is `3 * 8192`.
- Slot `1_000_000` starts at byte `8_192_000_000`, which doesn't fit in 32 bits.

## Syntax and methods

| | |
|---|---|
| `x as u64` | numeric cast. There is no `From<usize> for u64` (a `usize` might be wider one day), so you cast |
| `slot as u64 * BUSTUB_PAGE_SIZE as u64` | `as` binds tighter than `*`: both sides become `u64`, then multiply |
| `BUSTUB_PAGE_SIZE` | a `usize` constant in `src/common/config.rs` |

## Notes

In debug builds integer overflow **panics**; in release it wraps. Doing the arithmetic in `u64` makes neither a worry for any real file.

## In BusTub

```cpp
return pages_.size() * BUSTUB_PAGE_SIZE;        // AllocatePage(): the offset of a fresh slot
```

## The C/C++ way
| C / C++ | Rust |
|---|---|
| `(size_t)slot * PAGE_SIZE`, `static_cast<uint64_t>(slot) * kPageSize` | `slot as u64 * BUSTUB_PAGE_SIZE as u64` |
| `off_t` (signed, 64-bit on modern systems), `size_t` (unsigned, pointer-sized) | `i64` / `u64`, `usize` |
| implicit conversions and integer promotion between `int`, `long`, `size_t` | none: every conversion is written (`as`, `From`, `try_from`) |
| signed overflow is **undefined behaviour** (`int * int` that overflows) | debug: panic; release: wraps; or choose `checked_mul` / `wrapping_mul` / `saturating_mul` |

**The classic bug when porting:** `int offset = slot * PAGE_SIZE;` in C. If `slot` is an `int`, the multiplication happens in `int` and overflows
long before the result is widened. Cast one operand to the wide type *first*. Rust makes you write the type, so the bug can't hide.

## Learn more
- The Rust Reference: [type cast expressions](https://doc.rust-lang.org/reference/expressions/operator-expr.html#type-cast-expressions)
- BusTub's [disk_manager.cpp](https://github.com/cmu-db/bustub/blob/master/src/storage/disk/disk_manager.cpp)
