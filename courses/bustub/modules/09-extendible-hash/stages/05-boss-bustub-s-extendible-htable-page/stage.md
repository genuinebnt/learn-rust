**Where this fits.** Header, directory and bucket pages are done. BusTub's own test exercises all three through real buffer pool pages.

## The task

Nothing new. Run the ported `tests/extendible_htable_page_test.rs`:

| BusTub | here | checks |
|---|---|---|
| `ExtendibleHTableTest.BucketPageSampleTest` | `bucket_page_sample_test` | 10 pairs fill a bucket; the 11th is refused; lookups; removing the odd keys, then every key, empties it |
| `ExtendibleHTableTest.HeaderDirectoryPageSampleTest` | `header_directory_page_sample_test` | the header's four directory indexes by top bits; a directory grown 0 → 3 with four buckets, `verify_integrity` at each step, then shrunk |

## Tests

- `s2b_14_the_bucket_sample_end_to_end`: the same bucket sequence through a `WritePageGuard`'s bytes.
- The two BusTub tests.

## Syntax and methods

```rust
let mut guard = bpm.write_page(page_id);
let mut bucket = ExtendibleHTableBucketPage::<_, GenericKey<8>, Rid>::new(&mut guard.get_data_mut()[..]);   // a view over the guard's bytes
```

## Notes

Everything below the hash table is now tested. When the table misbehaves, the first suspects are *its* use of these pages, not the pages: you have a test for each of their methods. (BusTub's comment on its own test: "uncommenting this code line below should cause an 'Assertion failed'": Rust spells that `#[should_panic]`, which the stage tests carry.)

## In BusTub

```cpp
auto directory_page = directory_guard.AsMut<ExtendibleHTableDirectoryPage>();   directory_page->Init(3);
directory_page->SetBucketPageId(0, bucket_page_id_1);   directory_page->VerifyIntegrity();
```

## The C/C++ way

| gtest / C++ | Rust |
|---|---|
| `guard.AsMut<Page>()` returns `Page *` into the frame | a view struct built from `guard.get_data_mut()` |
| `header_guard.Drop();` | `drop(header_guard);` |
| `GenericKey<8> index_key; index_key.SetFromInteger(i); RID rid; rid.Set(i, i);` | `key(i)` helper, `Rid::new(PageId(i), i)` |
| `ParseCreateStatement("a bigint")` builds a schema for the comparator | `GenericComparator::<8>` (until module 3a introduces schemas) |

## Learn more
- BusTub's [page test](https://github.com/cmu-db/bustub/blob/master/test/storage/extendible_htable_page_test.cpp) · [`#[should_panic]`](https://doc.rust-lang.org/book/ch11-01-writing-tests.html#checking-for-panics-with-should_panic)
