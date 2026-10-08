**Where this fits.** An empty table has only a header. The first insert for a header slot has to build the rest.

## The task

In `insert` (and its helpers `insert_to_new_directory`, `insert_to_new_bucket`) in `src/container/disk/hash/disk_extendible_hash_table.rs`:
1. hash the key; **write-latch the header**; find the header slot for the hash;
2. if that slot has no directory (`INVALID`): allocate a page, make it a directory (`init(directory_max_depth)`), record its id in the header slot, compute the directory slot for the hash (`hash_to_bucket_index`), and **insert to a new bucket**: allocate a page, `init(bucket_max_size)`, point the directory slot at it with local depth 0, and insert the pair into it. Return that insert's result.
3. otherwise, for now, `return false` (stage 17).

## Tests

- The first insert returns `true`; the header now has one directory; it has global depth 0 and one bucket of local depth 0 and max size 4; the bucket holds the pair.
- Keys whose hashes differ in the top header bits get different directories. Nothing is left pinned. The new table verifies.

## Syntax and methods

```rust
let mut header_guard = self.bpm.write_page(self.header_page_id);
let mut directory_guard = self.bpm.write_page(self.bpm.new_page());        // new_page() then write_page(): a fresh zeroed page, latched
Header::new(&mut header_guard[..]).set_directory_page_id(directory_idx, directory_page_id);
```

## Notes

**Create lazily.** The table starts with only a header, and each directory (then each bucket) appears when a key first needs it: an empty table costs one page. **Initialise before publishing:** the new directory is formatted *before* the header points at it (and, under the header's write latch, nobody can see the half-built state anyway).

**Guard order is lock order.** The code takes header → directory → bucket, always top-down. Every operation in the table follows the same order, which is what makes deadlock between two inserts impossible (module 2c's latch crabbing is this idea on a tree).

## In BusTub

```cpp
auto InsertToNewDirectory(ExtendibleHTableHeaderPage *header, uint32_t directory_idx, uint32_t hash, const K &key, const V &value) -> bool;
auto InsertToNewBucket(ExtendibleHTableDirectoryPage *directory, uint32_t bucket_idx, const K &key, const V &value) -> bool;
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `ExtendibleHTableHeaderPage *header` passed to helpers: a raw pointer into a pinned frame that the helper must not outlive | `&mut [u8]` / `&mut Directory<&mut [u8]>`: a borrow of the caller's guard |
| `WritePageGuard` moved around with `std::move`, `Drop()` calls to release early | guards are values; `drop(guard)` releases early |
| `page_id_t new_id = bpm_->NewPage(); auto guard = bpm_->WritePage(new_id);` | the same two calls |
| return `false` on allocation failure | `write_page` panics if the pool is exhausted; a real system would return a `Result` here |

## Learn more
- CMU 15-445 "Hash Tables" · [Extendible hashing](https://en.wikipedia.org/wiki/Extendible_hashing) · BusTub [disk_extendible_hash_table.cpp](https://github.com/cmu-db/bustub/blob/master/src/container/disk/hash/disk_extendible_hash_table.cpp)
