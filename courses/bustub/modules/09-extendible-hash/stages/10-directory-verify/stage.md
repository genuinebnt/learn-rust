**Where this fits.** The table's own tests call `verify_integrity()` after every phase. A good checker turns a mysterious wrong answer into "slot 5 is wrong".

## The task

Implement `verify_integrity()` in `src/storage/page/extendible_htable_directory_page.rs`. It panics, with a message naming the slot or bucket, if any invariant fails:
1. every local depth is **at most** the global depth (message contains "above the global depth");
2. a bucket with local depth `d` is pointed to by **exactly `2^(g - d)` slots** (message contains "slots");
3. all slots with the same bucket page id have the **same local depth** (message contains "two different local depths").

## Tests

- A correct depth-2 directory (buckets at slots 0 and 2, one shared by 1 and 3) passes; so does a fresh one-bucket directory.
- Each invariant is broken in turn and must panic with its message.

## Syntax and methods

```rust
let mut pointers: HashMap<PageId, (u32, u32)> = HashMap::new();         // page id -> (local depth, number of slots)
let entry = pointers.entry(page_id).or_insert((depth, 0));
assert_eq!(entry.0, depth, "slot {i}: bucket {} appears with two different local depths", page_id.0);
```

## Notes

**Write the checker before the algorithm.** `verify_integrity` is short, independent of the splitting code, and catches every mistake in stages 18-21 close to its cause. In a real system the same idea is called an *invariant checker*: `PRAGMA integrity_check` in SQLite, `amcheck` in PostgreSQL, `fsck` for file systems. Property tests run them after random operations (stage 21's model test does).

The three invariants say: depths make sense (1), the pointer counts add up (2), and a bucket has one depth (3). Together they say the directory is a valid partition of the hash space.

## In BusTub

"VerifyIntegrity: Verify the following invariants: (1) All LD <= GD. (2) Each bucket has precisely 2^(GD - LD) pointers pointing to it. (3) The LD is the same at each index with the same bucket_page_id".

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::unordered_map<page_id_t, uint32_t> cnt; ++cnt[page_id];` (`operator[]` default-inserts 0) | `*map.entry(k).or_insert(0) += 1;` |
| `assert(cond)` (gone in release builds) or `BUSTUB_ENSURE` | `assert!` / `assert_eq!` with a message |
| `throw Exception(...)` for corruption | a panic with the details; a real system might return `Result<(), Corruption>` |

## Learn more
- [`HashMap::entry`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.entry) · SQLite [`PRAGMA integrity_check`](https://www.sqlite.org/pragma.html#pragma_integrity_check) · PostgreSQL [`amcheck`](https://www.postgresql.org/docs/current/amcheck.html)
