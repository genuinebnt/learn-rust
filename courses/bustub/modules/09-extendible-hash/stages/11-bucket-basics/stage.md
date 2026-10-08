**Where this fits.** The bottom level: a small **unsorted** array of `(key, value)` pairs.

## The task

`ExtendibleHTableBucketPage<B, K, V>` (`src/storage/page/extendible_htable_bucket_page.rs`) is a view over page bytes laid out as `| size u32 | max_size u32 | (key, value) ... |` (`capacity()` is given). Implement:
- `init(max_size)`: panic ("do not fit") if `max_size` exceeds the page's capacity; size 0, the given max size;
- `size()`, `max_size()`, `is_full()` (`size >= max_size`), `is_empty()`;
- `entry_at(idx)` (panic "past the bucket's size" for `idx >= size`), `key_at(idx)`, `value_at(idx)`. Use a `PageArray` over the bytes after the 8-byte header.

## Tests

- A fresh bucket: size 0, max 10, empty, not full. 511 pairs of `(GenericKey<8>, Rid)` fit; 1023 pairs of `(i32, i32)`. The header bytes sit where BusTub puts them. Reading past `size` panics; `max_size` 512 does not fit.

## Syntax and methods

```rust
fn entries(&self) -> PageArray<&[u8], (K, V)> { PageArray::new(&self.page.as_ref()[HTABLE_BUCKET_PAGE_METADATA_SIZE..]) }
self.entries().get(bucket_idx as usize)
```

## Notes

`B: AsRef<[u8]>` gives `&self` methods a way to see the bytes, `AsMut` for the writers. Because the type parameters `K` and `V` appear only in the impl bounds and in `PhantomData`, the *same page bytes* can be viewed as `(i32, i32)` or `(GenericKey<8>, Rid)` buckets: the page format doesn't record its own key type; the table does (as in BusTub, where it is a template argument).

## In BusTub

```cpp
template <typename KeyType, typename ValueType, typename KeyComparator> class ExtendibleHTableBucketPage { uint32_t size_; uint32_t max_size_; MappingType array_[HTableBucketArraySize(sizeof(MappingType))]; };
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `template <typename K, typename V, typename KC> class ...` | `struct ExtendibleHTableBucketPage<B, K, V>`; the comparator is a method argument |
| `using MappingType = std::pair<KeyType, ValueType>;` | the tuple type `(K, V)` |
| `array_[i].first` returned by value or reference | `entry_at(i).0` (a decoded copy: keys and values are small and `FixedSize`) |
| `static_assert(sizeof(Page) <= BUSTUB_PAGE_SIZE)` | `array_size(..)` computed from `FixedSize::SIZE`; `init` asserts the fit |

## Learn more
- BusTub [extendible_htable_bucket_page.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/page/extendible_htable_bucket_page.h) · [`PhantomData`](https://doc.rust-lang.org/std/marker/struct.PhantomData.html)
