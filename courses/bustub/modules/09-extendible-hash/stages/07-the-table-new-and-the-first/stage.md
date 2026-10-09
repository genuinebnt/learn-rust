Now the three levels become a table. `DiskExtendibleHashTable` owns a header page id and the parameters (`max_depths`, bucket size), and **creates its pages lazily**: a new table is one header page whose slots are all empty; the first insert under a header slot allocates a directory, and the first insert into a directory slot allocates a bucket. An empty table's `get_value` must answer without allocating anything.

This stage is about the table's **skeleton and its first path**, written with page guards so no pin or latch can leak. The recurring lesson is the *order of acquisition*: header, then directory, then bucket, and the parent released only once the child is held.

## Part 1 · The table: new, an empty get_value, verify_integrity

**Where this fits.** The three page types exist; now the table that owns them. `DiskExtendibleHashTable<K, V, C>` is generic over the key, the value and the comparator, holds a reference to the buffer pool, and keeps only **one page id**: the header's. Everything else is found by walking the pages.

### The task

In `src/container/disk/hash/disk_extendible_hash_table.rs`:
- `new(name, bpm, cmp, hash_fn, header_max_depth, directory_max_depth, bucket_max_size)`: allocate a page for the header (`bpm.new_page()`), format it (`init(header_max_depth)` through a write guard), and remember its id and the parameters. The struct and its fields are a starting point.
- `get_value(&key) -> Vec<V>` for the case of an **empty table**: hash the key, read the header; if the slot for that hash has no directory, return an empty vector. (The rest of `get_value` is stage 17.)
- `verify_integrity()`: for every directory the header knows, call the directory page's `verify_integrity`.

### Tests

- A new table has a header with the requested depth and every slot `INVALID`; an empty table has no value for any key; it verifies; the defaults fill a page (1023 `(i32, i32)` pairs, 511 `(GenericKey<8>, Rid)` pairs, depths 9); reading an empty table leaves nothing pinned.

### Syntax and methods

```rust
let header_page_id = bpm.new_page();
ExtendibleHTableHeaderPage::new(&mut bpm.write_page(header_page_id)[..]).init(header_max_depth);   // the guard derefs to the page; `[..]` makes it a slice
let header_guard = self.bpm.read_page(self.header_page_id);                                          // a read latch for the walk
pub struct DiskExtendibleHashTable<'a, K, V, C> { bpm: &'a BufferPoolManager, ... }                   // borrows the pool: it can't outlive it
```

### Notes

**What the table stores, and what it doesn't.** Only `header_page_id`. Every other page id is discovered through the header and the directories, because *those pages are the table*: persist the header id, and the whole table can be reopened (BusTub's catalog stores exactly that). The `'a` lifetime says the table can't outlive the pool it uses, which the C++ code states in a comment ("the BPM must outlive the table") and the compiler here enforces.

### In BusTub

```cpp
DiskExtendibleHashTable(const std::string &name, BufferPoolManager *bpm, const KC &cmp, const HashFunction<K> &hash_fn,
                        uint32_t header_max_depth = HTABLE_HEADER_MAX_DEPTH, uint32_t directory_max_depth = HTABLE_DIRECTORY_MAX_DEPTH,
                        uint32_t bucket_max_size = HTableBucketArraySize(sizeof(std::pair<K, V>)));
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| default arguments in the constructor | no default arguments: pass them, or provide `default_*` functions / a builder |
| `BufferPoolManager *bpm_` (raw pointer, lifetime by convention) | `&'a BufferPoolManager` |
| `auto GetValue(const K &key, std::vector<V> *result, Transaction *txn) const -> bool` | `get_value(&self, key: &K) -> Vec<V>`: return the vector; the `Transaction` parameter arrives in module 4a |
| `HashFunction<K> hash_fn_` copied in (`std::move`) | owned field, moved in |
| `template class DiskExtendibleHashTable<int, int, IntComparator>;` explicit instantiations in the `.cpp` | generics: instantiated wherever used |

### Learn more
- The Rust Book: [lifetimes in structs](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#lifetime-annotations-in-struct-definitions) · BusTub [disk_extendible_hash_table.h](https://github.com/cmu-db/bustub/blob/master/src/include/container/disk/hash/disk_extendible_hash_table.h)

## Part 2 · insert: the first key creates a directory and a bucket

**Where this fits.** An empty table has only a header. The first insert for a header slot has to build the rest.

### The task

In `insert` (and its helpers `insert_to_new_directory`, `insert_to_new_bucket`) in `src/container/disk/hash/disk_extendible_hash_table.rs`.
When the key's header slot has no directory yet, `insert` creates one: afterwards the header slot names a new directory page (initialised with `directory_max_depth`) whose slot for this hash points at a new bucket of local depth 0 (initialised with `bucket_max_size`), the pair is in that bucket, and `insert` returns what inserting into that bucket returns. The header is write-latched throughout. A header slot that already has a directory is stage 17: for now, `return false`.

> [!ASIDE] The steps, if you would rather not work them out
> 1. hash the key; **write-latch the header**; find the header slot for the hash;
> 2. if that slot has no directory (`INVALID`): allocate a page, make it a directory (`init(directory_max_depth)`), record its id in the header slot, compute the directory slot for the hash (`hash_to_bucket_index`), and **insert to a new bucket**: allocate a page, `init(bucket_max_size)`, point the directory slot at it with local depth 0, and insert the pair into it. Return that insert's result.
> 3. otherwise, for now, `return false` (stage 17).

### Tests

- The first insert returns `true`; the header now has one directory; it has global depth 0 and one bucket of local depth 0 and max size 4; the bucket holds the pair.
- Keys whose hashes differ in the top header bits get different directories. Nothing is left pinned. The new table verifies.

### Syntax and methods

```rust
let mut header_guard = self.bpm.write_page(self.header_page_id);
let mut directory_guard = self.bpm.write_page(self.bpm.new_page());        // new_page() then write_page(): a fresh zeroed page, latched
Header::new(&mut header_guard[..]).set_directory_page_id(directory_idx, directory_page_id);
```

### Notes

**Create lazily.** The table starts with only a header, and each directory (then each bucket) appears when a key first needs it: an empty table costs one page. **Initialise before publishing:** the new directory is formatted *before* the header points at it (and, under the header's write latch, nobody can see the half-built state anyway).

**Guard order is lock order.** The code takes header → directory → bucket, always top-down. Every operation in the table follows the same order, which is what makes deadlock between two inserts impossible (module 2c's latch crabbing is this idea on a tree).

### In BusTub

```cpp
auto InsertToNewDirectory(ExtendibleHTableHeaderPage *header, uint32_t directory_idx, uint32_t hash, const K &key, const V &value) -> bool;
auto InsertToNewBucket(ExtendibleHTableDirectoryPage *directory, uint32_t bucket_idx, const K &key, const V &value) -> bool;
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `ExtendibleHTableHeaderPage *header` passed to helpers: a raw pointer into a pinned frame that the helper must not outlive | `&mut [u8]` / `&mut Directory<&mut [u8]>`: a borrow of the caller's guard |
| `WritePageGuard` moved around with `std::move`, `Drop()` calls to release early | guards are values; `drop(guard)` releases early |
| `page_id_t new_id = bpm_->NewPage(); auto guard = bpm_->WritePage(new_id);` | the same two calls |
| return `false` on allocation failure | `write_page` panics if the pool is exhausted; a real system would return a `Result` here |

### Learn more
- CMU 15-445 "Hash Tables" · [Extendible hashing](https://en.wikipedia.org/wiki/Extendible_hashing) · BusTub [disk_extendible_hash_table.cpp](https://github.com/cmu-db/bustub/blob/master/src/container/disk/hash/disk_extendible_hash_table.cpp)

## Performance

A lookup on an existing key reads **three pages** (header, directory, bucket); an insert that creates the first directory and bucket allocates **two new pages** and writes the header slot, directory and bucket once each. In a warm buffer pool all of these are memory accesses plus latch operations: about 3 latch acquire/release pairs and one hash, on the order of a microsecond. In a cold pool each missing page is a disk read, which dominates by 100x.

`verify_integrity` reads every directory the header points to: O(directories x directory size): a testing tool, not a production call.

The header is read by *every* operation: keep its read latch for as short a time as possible (just long enough to latch the directory), because its contention limits the whole table's concurrency.

**Measure it.** Insert 1 000 keys with `header_max_depth` 0 and with 4 and count `bpm` page reads and writes with a counting disk (4 depth bits spread keys over 16 directories, each smaller). Verify every pin count is 0 after the run.

## Hints

### What does an empty table look like on disk?

One header page, with every directory slot `INVALID`. `new` allocates and initialises it (through `new_page` and a write guard), and `get_value` on a key whose header slot is `INVALID` returns an empty `Vec` *without* allocating. A test that counts `new_page` calls before and after a lookup on an empty table checks that.

### Allocate a page, then publish it: in that order

`insert_to_new_directory` allocates a directory page, **initialises** it, and only then stores its id in the header slot, so a concurrent reader never follows a header pointer to an uninitialised page. Hold the header's write latch for that whole sequence. The same applies one level down: a new bucket is initialised before the directory slot points at it.

### Guards drop at the end of their scope: use that deliberately

You do not release latches by hand: you control *when* a guard drops by where you declare it and by `drop(guard)`. Write the lookup so the header guard is dropped *after* the directory guard exists and *before* the bucket is touched, and verify with `get_pin_count` that every page is at pin count 0 after the call, including after an early `return` for a missing key.
