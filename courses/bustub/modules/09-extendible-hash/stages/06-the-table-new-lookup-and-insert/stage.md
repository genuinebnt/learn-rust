This stage has 3 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

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

In `insert` (and its helpers `insert_to_new_directory`, `insert_to_new_bucket`) in `src/container/disk/hash/disk_extendible_hash_table.rs`:
1. hash the key; **write-latch the header**; find the header slot for the hash;
2. if that slot has no directory (`INVALID`): allocate a page, make it a directory (`init(directory_max_depth)`), record its id in the header slot, compute the directory slot for the hash (`hash_to_bucket_index`), and **insert to a new bucket**: allocate a page, `init(bucket_max_size)`, point the directory slot at it with local depth 0, and insert the pair into it. Return that insert's result.
3. otherwise, for now, `return false` (stage 17).

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

## Part 3 · Lookup and insert into an existing bucket

**Where this fits.** Most operations find an existing bucket with room. This stage is the common path.

### The task

In `src/container/disk/hash/disk_extendible_hash_table.rs`:
- `get_value`: after the header, **read-latch the directory and then release the header** (once you hold the directory's latch, the header slot can't change under you), find the bucket for the hash, **read-latch the bucket and release the directory**, look the key up, return it as a 0- or 1-element `Vec`.
- `insert`, when the header slot already has a directory: **write-latch the directory and release the header**; find the bucket for the hash; **write-latch the bucket**; if it already has the key return `false`; if it has room, insert and return `true`. (A full bucket is stage 18: `return false` for now.)

### Tests

- 8 keys inserted into a bucket of 8, each readable right away. Missing keys have no value. A duplicate key is refused and the old value stays.
- With header depth 2, 40 keys spread across several directories and are all found. Many lookups leave nothing latched or pinned.

### Syntax and methods

```rust
let directory_guard = self.bpm.read_page(directory_page_id);
drop(header_guard);                                    // crabbing: hold the child before releasing the parent
Bucket::<_, K, V>::new(&bucket_guard[..]).lookup(key, &self.cmp).into_iter().collect()     // Option<V> -> Vec<V>
```

### Notes

**Latch crabbing** (also "lock coupling"): to go down a tree under concurrent access, latch the child **before** releasing the parent. Releasing the parent first lets another thread change the parent's pointer to the child (a split, a delete) in the gap, and you would follow a stale pointer. Releasing the parent *as soon as* you hold the child (and the child is safe) keeps the upper levels free for other threads: the header is a bottleneck every operation passes through, so holding it for a few instructions rather than the whole operation matters.

`get_value` uses **read** latches (many readers at once); `insert` and `remove` use **write** latches on the pages they may change. An insert that finds room in a bucket could release the directory early too; this version keeps it until the insert is done (simple and correct).

### In BusTub

Lecture 10 ("Index Concurrency Control") describes this protocol; the project spec says: "you should use the `ReadPageGuard`/`WritePageGuard` ... and release the guards of the parent pages when it is safe to do so".

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto header_guard = bpm_->ReadPage(header_page_id_); auto header = header_guard.As<ExtendibleHTableHeaderPage>(); ... header_guard.Drop();` | `let header_guard = ..; let header = Header::new(&header_guard[..]); ... drop(header_guard);` (the borrow checker stops you using `header` after the drop) |
| `result->push_back(value); return true;` (out-parameter) | `Vec<V>` returned |
| forgetting `Drop()` keeps a latch for the whole function: a performance bug, or a deadlock | the same, but a guard's scope is visible, and `drop` is explicit |
| `std::shared_lock` vs `std::unique_lock` | read guard vs write guard |

### Learn more
- CMU 15-445 "Index Concurrency Control" (latch crabbing) · [`drop`](https://doc.rust-lang.org/std/mem/fn.drop.html) · Rust Atomics and Locks, [locking basics](https://marabos.nl/atomics/building-locks.html)
