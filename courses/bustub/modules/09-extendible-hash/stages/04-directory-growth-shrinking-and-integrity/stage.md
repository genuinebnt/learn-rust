A directory can **grow**: doubling its global depth copies the first half of the slots into the second, so every bucket is now referenced by twice as many slots without any bucket moving. It can **shrink** when no bucket uses the full depth. And `verify_integrity` checks every invariant the table relies on, which you will call after almost every operation from here on.

The checker is the most useful code in the module: it turns a subtle corruption (a stale pointer, a depth off by one) into an immediate, specific failure at the operation that caused it.

## Part 1 · incr_global_depth: double the directory

**Where this fits.** When a bucket whose local depth equals the global depth must split, the directory has to double so there are slots for both halves.

### The task

Implement `incr_global_depth()` in `src/storage/page/extendible_htable_directory_page.rs`: panic ("max depth") if the directory is already at its max depth; otherwise copy slots `0..size` into `size..2*size` (**bucket page ids and local depths**), then raise the global depth. Nothing else changes: until some bucket splits, a hash with the new top bit set goes to the same bucket as before.

### Tests

- Growing from 1 slot to 2 copies slot 0 into slot 1; depths are copied too; growing again to 4 gives `[1, 2, 1, 2]` for ids `[1, 2]`.
- BusTub's directory walkthrough (depths 1, 2, 3 with buckets 2..5), line by line. Growing past the max depth panics; growing to the full 512 slots works.

### Syntax and methods

```rust
let size = 1usize << global;
for i in 0..size {
    let (id, depth) = (self.get_bucket_page_id(i as u32), self.get_local_depth(i as u32));
    /* write them at slot size + i: note get_bucket_page_id asserts against max_size, so reading slot i < size is fine */
}
```

### Notes

The upper half is a **mirror** of the lower half: slot `i + size` points where slot `i` does. That is the invariant "a bucket of local depth `d` has `2^(g-d)` slots pointing at it" holding after the doubling: every pointer count doubled and `g` rose by one. `verify_integrity` (stage 10) checks exactly this.

### In BusTub

"IncrGlobalDepth: ... the new half of the directory is a copy of the old half" and the test comment: "uncommenting this code line below should cause an 'Assertion failed' since this would be exceeding the max depth we initialized".

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::copy(first, last, d_first)` / `memcpy(dest, src, n)` for the doubling | `copy_within` on the byte ranges, or a loop of get/set |
| two parallel arrays (ids and depths) copied in two loops: easy to forget one | the same: the tests check both |
| `assert(global_depth_ < max_depth_)` | `assert!` with a message the test can match |

### Learn more
- [Extendible hashing: directory doubling](https://en.wikipedia.org/wiki/Extendible_hashing#Example) · CMU 15-445 "Hash Tables"

## Part 2 · can_shrink and decr_global_depth

**Where this fits.** After merges, the directory may be bigger than it needs to be.

### The task

In `src/storage/page/extendible_htable_directory_page.rs`:
- `can_shrink()`: true if the global depth is above 0 **and** every slot in use (`0..size`) has a local depth **below** the global depth, so no bucket uses the top bit and the upper half just mirrors the lower;
- `decr_global_depth()`: panic ("depth 0") at depth 0; otherwise lower it by one (the stale upper half is simply no longer part of the directory).

### Tests

- A bucket at full depth blocks the shrink (one slot at depth 3 of 3, the rest at 2: no). All depths below global: yes, and `decr` makes size 8 → 4. Depth 0 can't shrink. **Only slots in use count**: stale depths beyond `size` after a shrink must not block the next one.

### Syntax and methods

```rust
global > 0 && (0..self.size()).all(|i| self.get_local_depth(i) < global)     // Iterator::all short-circuits on the first false
```

### Notes

`(0..self.size())` is the whole trick of "only the slots in use": the page still holds the old upper half after `decr_global_depth` (it isn't zeroed), so reading past `size` would see stale data. The same lesson as the array stages: **the length lives in the header, and bytes beyond it are garbage.**

### In BusTub

"CanShrink() -> bool" and, in the sample test: "at this time, we cannot shrink the directory since we have ld = gd = 3" followed by lowering two local depths and `ASSERT_EQ(directory_page->CanShrink(), true)`.

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `for (...) { if (ld[i] == gd) return false; } return true;` | `.all(\|i\| ld < gd)` |
| `std::all_of(first, last, pred)` | `Iterator::all` |
| `std::any_of` / `std::none_of` | `Iterator::any` / `!any` |

### Learn more
- [`Iterator::all`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.all) · [`any`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.any) · C++ [`std::all_of`](https://en.cppreference.com/w/cpp/algorithm/all_any_none_of)

## Part 3 · verify_integrity: check the invariants

**Where this fits.** The table's own tests call `verify_integrity()` after every phase. A good checker turns a mysterious wrong answer into "slot 5 is wrong".

### The task

Implement `verify_integrity()` in `src/storage/page/extendible_htable_directory_page.rs`. It panics, with a message naming the slot or bucket, if any invariant fails:
1. every local depth is **at most** the global depth (message contains "above the global depth");
2. a bucket with local depth `d` is pointed to by **exactly `2^(g - d)` slots** (message contains "slots");
3. all slots with the same bucket page id have the **same local depth** (message contains "two different local depths").

### Tests

- A correct depth-2 directory (buckets at slots 0 and 2, one shared by 1 and 3) passes; so does a fresh one-bucket directory.
- Each invariant is broken in turn and must panic with its message.

### Syntax and methods

```rust
let mut pointers: HashMap<PageId, (u32, u32)> = HashMap::new();         // page id -> (local depth, number of slots)
let entry = pointers.entry(page_id).or_insert((depth, 0));
assert_eq!(entry.0, depth, "slot {i}: bucket {} appears with two different local depths", page_id.0);
```

### Notes

**Write the checker before the algorithm.** `verify_integrity` is short, independent of the splitting code, and catches every mistake in stages 18-21 close to its cause. In a real system the same idea is called an *invariant checker*: `PRAGMA integrity_check` in SQLite, `amcheck` in PostgreSQL, `fsck` for file systems. Property tests run them after random operations (stage 21's model test does).

The three invariants say: depths make sense (1), the pointer counts add up (2), and a bucket has one depth (3). Together they say the directory is a valid partition of the hash space.

### In BusTub

"VerifyIntegrity: Verify the following invariants: (1) All LD <= GD. (2) Each bucket has precisely 2^(GD - LD) pointers pointing to it. (3) The LD is the same at each index with the same bucket_page_id".

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::unordered_map<page_id_t, uint32_t> cnt; ++cnt[page_id];` (`operator[]` default-inserts 0) | `*map.entry(k).or_insert(0) += 1;` |
| `assert(cond)` (gone in release builds) or `BUSTUB_ENSURE` | `assert!` / `assert_eq!` with a message |
| `throw Exception(...)` for corruption | a panic with the details; a real system might return `Result<(), Corruption>` |

### Learn more
- [`HashMap::entry`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.entry) · SQLite [`PRAGMA integrity_check`](https://www.sqlite.org/pragma.html#pragma_integrity_check) · PostgreSQL [`amcheck`](https://www.postgresql.org/docs/current/amcheck.html)

## Performance

Doubling is **O(directory size)**: copy up to 256 bucket ids and 256 depth bytes; no bucket page is read or written, so it is cheap next to a split's I/O. `can_shrink` is a scan of the local depths, O(2^global_depth); shrinking is a decrement (the second half is simply no longer considered). `verify_integrity` is O(directory size) plus a pass to count references per bucket: fine in tests, too slow to leave in a hot path, so keep it behind `debug_assert!` or a test-only call.

The structural point: because only the *directory* doubles, the cost of growth does not depend on how many keys the table holds. A conventional hash table rehashes all `n` keys when it resizes.

**Measure it.** Double a depth-0 directory to depth 9 and time it (microseconds), then compare with rehashing 100 000 keys into a table twice the size. Run `verify_integrity` on a directory with 512 slots 1 000 000 times and note it is well under a microsecond per slot.

## Hints

### What exactly gets copied when the directory doubles?

Slots `[0, n)` stay; slots `[n, 2n)` become copies of them, **bucket id and local depth both**. The new slot `i + n` must point at the same bucket as `i` because until a split distinguishes them, they differ only in a bit the bucket does not look at. After the copy `global_depth` is incremented. Test the invariant directly: for every `i < n`, slot `i + n` equals slot `i`. Also decide what doubling at the maximum depth does (a panic: the caller must check first).

### `can_shrink` is about local depths, not about being empty

The directory may halve exactly when **no bucket has local depth equal to the global depth**: then every pair `(i, i + n/2)` is a duplicate. A directory with several empty buckets at full depth cannot shrink; a directory with no empty buckets at all can. Do not confuse the two. And `decr_global_depth` must keep slot data in the first half intact (nothing is copied) and refuse to go below 0.

### Write the invariants as a list before writing the checker

For each slot below `2^global`: the bucket page id is valid; the local depth is at most the global depth; and, per bucket, the number of slots pointing to it is exactly `2^(global - local)`, *all with the same local depth*. Implement the third check by counting references in a map from page id to count and comparing, and make each panic message say which slot and which bucket. Then break the directory deliberately in a test (change one depth by hand) and check you get the right message.
