**Where this fits.** When a bucket whose local depth equals the global depth must split, the directory has to double so there are slots for both halves.

## The task

Implement `incr_global_depth()` in `src/storage/page/extendible_htable_directory_page.rs`: panic ("max depth") if the directory is already at its max depth; otherwise copy slots `0..size` into `size..2*size` (**bucket page ids and local depths**), then raise the global depth. Nothing else changes: until some bucket splits, a hash with the new top bit set goes to the same bucket as before.

## Tests

- Growing from 1 slot to 2 copies slot 0 into slot 1; depths are copied too; growing again to 4 gives `[1, 2, 1, 2]` for ids `[1, 2]`.
- BusTub's directory walkthrough (depths 1, 2, 3 with buckets 2..5), line by line. Growing past the max depth panics; growing to the full 512 slots works.

## Syntax and methods

```rust
let size = 1usize << global;
for i in 0..size {
    let (id, depth) = (self.get_bucket_page_id(i as u32), self.get_local_depth(i as u32));
    /* write them at slot size + i: note get_bucket_page_id asserts against max_size, so reading slot i < size is fine */
}
```

## Notes

The upper half is a **mirror** of the lower half: slot `i + size` points where slot `i` does. That is the invariant "a bucket of local depth `d` has `2^(g-d)` slots pointing at it" holding after the doubling: every pointer count doubled and `g` rose by one. `verify_integrity` (stage 10) checks exactly this.

## In BusTub

"IncrGlobalDepth: ... the new half of the directory is a copy of the old half" and the test comment: "uncommenting this code line below should cause an 'Assertion failed' since this would be exceeding the max depth we initialized".

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::copy(first, last, d_first)` / `memcpy(dest, src, n)` for the doubling | `copy_within` on the byte ranges, or a loop of get/set |
| two parallel arrays (ids and depths) copied in two loops: easy to forget one | the same: the tests check both |
| `assert(global_depth_ < max_depth_)` | `assert!` with a message the test can match |

## Learn more
- [Extendible hashing: directory doubling](https://en.wikipedia.org/wiki/Extendible_hashing#Example) · CMU 15-445 "Hash Tables"
