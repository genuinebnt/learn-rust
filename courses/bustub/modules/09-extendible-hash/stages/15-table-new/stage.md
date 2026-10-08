**Where this fits.** The three page types exist; now the table that owns them. `DiskExtendibleHashTable<K, V, C>` is generic over the key, the value and the comparator, holds a reference to the buffer pool, and keeps only **one page id**: the header's. Everything else is found by walking the pages.

## The task

In `src/container/disk/hash/disk_extendible_hash_table.rs`:
- `new(name, bpm, cmp, hash_fn, header_max_depth, directory_max_depth, bucket_max_size)`: allocate a page for the header (`bpm.new_page()`), format it (`init(header_max_depth)` through a write guard), and remember its id and the parameters. The struct and its fields are a starting point.
- `get_value(&key) -> Vec<V>` for the case of an **empty table**: hash the key, read the header; if the slot for that hash has no directory, return an empty vector. (The rest of `get_value` is stage 17.)
- `verify_integrity()`: for every directory the header knows, call the directory page's `verify_integrity`.

## Tests

- A new table has a header with the requested depth and every slot `INVALID`; an empty table has no value for any key; it verifies; the defaults fill a page (1023 `(i32, i32)` pairs, 511 `(GenericKey<8>, Rid)` pairs, depths 9); reading an empty table leaves nothing pinned.

## Syntax and methods

```rust
let header_page_id = bpm.new_page();
ExtendibleHTableHeaderPage::new(&mut bpm.write_page(header_page_id)[..]).init(header_max_depth);   // the guard derefs to the page; `[..]` makes it a slice
let header_guard = self.bpm.read_page(self.header_page_id);                                          // a read latch for the walk
pub struct DiskExtendibleHashTable<'a, K, V, C> { bpm: &'a BufferPoolManager, ... }                   // borrows the pool: it can't outlive it
```

## Notes

**What the table stores, and what it doesn't.** Only `header_page_id`. Every other page id is discovered through the header and the directories, because *those pages are the table*: persist the header id, and the whole table can be reopened (BusTub's catalog stores exactly that). The `'a` lifetime says the table can't outlive the pool it uses, which the C++ code states in a comment ("the BPM must outlive the table") and the compiler here enforces.

## In BusTub

```cpp
DiskExtendibleHashTable(const std::string &name, BufferPoolManager *bpm, const KC &cmp, const HashFunction<K> &hash_fn,
                        uint32_t header_max_depth = HTABLE_HEADER_MAX_DEPTH, uint32_t directory_max_depth = HTABLE_DIRECTORY_MAX_DEPTH,
                        uint32_t bucket_max_size = HTableBucketArraySize(sizeof(std::pair<K, V>)));
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| default arguments in the constructor | no default arguments: pass them, or provide `default_*` functions / a builder |
| `BufferPoolManager *bpm_` (raw pointer, lifetime by convention) | `&'a BufferPoolManager` |
| `auto GetValue(const K &key, std::vector<V> *result, Transaction *txn) const -> bool` | `get_value(&self, key: &K) -> Vec<V>`: return the vector; the `Transaction` parameter arrives in module 4a |
| `HashFunction<K> hash_fn_` copied in (`std::move`) | owned field, moved in |
| `template class DiskExtendibleHashTable<int, int, IntComparator>;` explicit instantiations in the `.cpp` | generics: instantiated wherever used |

## Learn more
- The Rust Book: [lifetimes in structs](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#lifetime-annotations-in-struct-definitions) · BusTub [disk_extendible_hash_table.h](https://github.com/cmu-db/bustub/blob/master/src/include/container/disk/hash/disk_extendible_hash_table.h)
