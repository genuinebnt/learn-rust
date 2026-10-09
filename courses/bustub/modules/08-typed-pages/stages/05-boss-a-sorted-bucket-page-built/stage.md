**Where this fits.** The toolkit assembled on a real page, before the hash table and the B+ tree use it.

## The task

Nothing new to write. The test builds, with only what you implemented, a page that is a bucket page in all but name: a `u32` length at offset 0, a `u32` capacity at offset 4, then `(GenericKey<8>, Rid)` entries from offset 8, **kept sorted** with `lower_bound` + `insert_at`, in a `WritePageGuard` from your buffer pool. It inserts 200 pseudo-random keys (skipping duplicates), pushes the page out of the pool by using the other frames, reads it back through a `ReadPageGuard`, and checks every entry.

## Tests

- `s2a_13_a_sorted_bucket_built_from_the_pieces_survives_the_buffer_pool`.

## Syntax and methods

```rust
let mut guard = bpm.write_page(page);
let data = guard.get_data_mut();                                       // &mut PageData
let mut array = PageArray::<_, (GenericKey<8>, Rid)>::new(&mut data[HTABLE_BUCKET_PAGE_METADATA_SIZE..]);
let at = array.lower_bound(len, |(k, _)| cmp.compare(k, &target));
array.insert_at(at, len, &(key, rid));
```

## Notes

You now have every primitive the next two modules use: ints at offsets, optional page ids, `Rid`, fixed-size keys and entries, a comparator, an array view with insert/remove/search, and a layout checked at compile time. The extendible hash table pages are *thin wrappers* over these; the B+ tree pages add sibling pointers and splits.

BusTub never tests these pieces on their own (its tests exercise the finished pages), which is why this module has its own tests: when something goes wrong in the B+ tree, you will want to know that the page primitives aren't the culprit.

## In BusTub

```cpp
auto bucket_page = guard.AsMut<ExtendibleHTableBucketPage<GenericKey<8>, RID, GenericComparator<8>>>();
bucket_page->Init(10);   bucket_page->Insert(index_key, rid, comparator);
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `guard.AsMut<T>()` returns `T *` into the page | `guard.get_data_mut()` returns `&mut [u8; 8192]`; a `PageArray` view over a sub-slice |
| the page class has `Init()`, because the constructor is deleted (the object is "placed" onto existing bytes) | the view is built from bytes each time; `init` writes the header fields |
| `DISALLOW_COPY_AND_MOVE` so nobody copies a "page object" | there is no page object to copy: only bytes and short-lived views |

## Experiment

Optional. Predict first, then run it.

1. **Linear versus binary.** Replace `lower_bound` with a linear scan and time the insert of 200 keys into one page, then compute the same for the largest page you can build. At what number of entries does binary search start to win on your machine? Does that number depend on the key size?
2. **How full is a page?** With 8-byte keys, `Rid` values and an 8-byte header, how many entries does `capacity` report for a page of 8 192 bytes? Work it out on paper first.

## What you built

A safe, typed view layer over raw pages: no `unsafe`, no `reinterpret_cast`, explicit byte order, checked layouts. Next: the **extendible hash table**.

## Learn more
- CMU 15-445 "Database Storage II" (slotted pages and page layout) and "Hash Tables" (linked below) · Postgres [page layout](https://www.postgresql.org/docs/current/storage-page-layout.html) · SQLite [B-tree pages](https://www.sqlite.org/fileformat2.html#b_tree_pages)
