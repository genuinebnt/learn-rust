**Where this fits.** After merges, the directory may be bigger than it needs to be.

## The task

In `src/storage/page/extendible_htable_directory_page.rs`:
- `can_shrink()`: true if the global depth is above 0 **and** every slot in use (`0..size`) has a local depth **below** the global depth, so no bucket uses the top bit and the upper half just mirrors the lower;
- `decr_global_depth()`: panic ("depth 0") at depth 0; otherwise lower it by one (the stale upper half is simply no longer part of the directory).

## Tests

- A bucket at full depth blocks the shrink (one slot at depth 3 of 3, the rest at 2: no). All depths below global: yes, and `decr` makes size 8 → 4. Depth 0 can't shrink. **Only slots in use count**: stale depths beyond `size` after a shrink must not block the next one.

## Syntax and methods

```rust
global > 0 && (0..self.size()).all(|i| self.get_local_depth(i) < global)     // Iterator::all short-circuits on the first false
```

## Notes

`(0..self.size())` is the whole trick of "only the slots in use": the page still holds the old upper half after `decr_global_depth` (it isn't zeroed), so reading past `size` would see stale data. The same lesson as the array stages: **the length lives in the header, and bytes beyond it are garbage.**

## In BusTub

"CanShrink() -> bool" and, in the sample test: "at this time, we cannot shrink the directory since we have ld = gd = 3" followed by lowering two local depths and `ASSERT_EQ(directory_page->CanShrink(), true)`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `for (...) { if (ld[i] == gd) return false; } return true;` | `.all(\|i\| ld < gd)` |
| `std::all_of(first, last, pred)` | `Iterator::all` |
| `std::any_of` / `std::none_of` | `Iterator::any` / `!any` |

## Learn more
- [`Iterator::all`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.all) · [`any`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.any) · C++ [`std::all_of`](https://en.cppreference.com/w/cpp/algorithm/all_any_none_of)
