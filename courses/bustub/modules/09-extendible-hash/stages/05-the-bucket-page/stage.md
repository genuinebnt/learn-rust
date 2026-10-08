This stage has 3 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · The bucket page: init and accessors

**Where this fits.** The bottom level: a small **unsorted** array of `(key, value)` pairs.

### The task

`ExtendibleHTableBucketPage<B, K, V>` (`src/storage/page/extendible_htable_bucket_page.rs`) is a view over page bytes laid out as `| size u32 | max_size u32 | (key, value) ... |` (`capacity()` is given). Implement:
- `init(max_size)`: panic ("do not fit") if `max_size` exceeds the page's capacity; size 0, the given max size;
- `size()`, `max_size()`, `is_full()` (`size >= max_size`), `is_empty()`;
- `entry_at(idx)` (panic "past the bucket's size" for `idx >= size`), `key_at(idx)`, `value_at(idx)`. Use a `PageArray` over the bytes after the 8-byte header.

### Tests

- A fresh bucket: size 0, max 10, empty, not full. 511 pairs of `(GenericKey<8>, Rid)` fit; 1023 pairs of `(i32, i32)`. The header bytes sit where BusTub puts them. Reading past `size` panics; `max_size` 512 does not fit.

### Syntax and methods

```rust
fn entries(&self) -> PageArray<&[u8], (K, V)> { PageArray::new(&self.page.as_ref()[HTABLE_BUCKET_PAGE_METADATA_SIZE..]) }
self.entries().get(bucket_idx as usize)
```

### Notes

`B: AsRef<[u8]>` gives `&self` methods a way to see the bytes, `AsMut` for the writers. Because the type parameters `K` and `V` appear only in the impl bounds and in `PhantomData`, the *same page bytes* can be viewed as `(i32, i32)` or `(GenericKey<8>, Rid)` buckets: the page format doesn't record its own key type; the table does (as in BusTub, where it is a template argument).

### In BusTub

```cpp
template <typename KeyType, typename ValueType, typename KeyComparator> class ExtendibleHTableBucketPage { uint32_t size_; uint32_t max_size_; MappingType array_[HTableBucketArraySize(sizeof(MappingType))]; };
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `template <typename K, typename V, typename KC> class ...` | `struct ExtendibleHTableBucketPage<B, K, V>`; the comparator is a method argument |
| `using MappingType = std::pair<KeyType, ValueType>;` | the tuple type `(K, V)` |
| `array_[i].first` returned by value or reference | `entry_at(i).0` (a decoded copy: keys and values are small and `FixedSize`) |
| `static_assert(sizeof(Page) <= BUSTUB_PAGE_SIZE)` | `array_size(..)` computed from `FixedSize::SIZE`; `init` asserts the fit |

### Learn more
- BusTub [extendible_htable_bucket_page.h](https://github.com/cmu-db/bustub/blob/master/src/include/storage/page/extendible_htable_bucket_page.h) · [`PhantomData`](https://doc.rust-lang.org/std/marker/struct.PhantomData.html)

## Part 2 · Bucket lookup and insert

**Where this fits.** What a bucket does: find a key, add a pair.

### The task

In `src/storage/page/extendible_htable_bucket_page.rs`:
- `lookup(key, cmp) -> Option<V>`: scan the entries for a key that **compares equal** under the comparator (not `==` on bytes);
- `insert(key, value, cmp) -> bool`: `false` (nothing changes) if the bucket is full or already has the key; otherwise append the pair at slot `size` and count it.

### Tests

- Insert then lookup of 5 keys; entries at the slots the accessors say; a full bucket refuses; a duplicate key is refused and the old value stays; `i32` buckets with 1023 pairs.
- **Keys compare through the comparator**: two `GenericKey<16>` whose bytes differ beyond the first 8 are equal to `GenericComparator<16>`, so the second insert is a duplicate.

### Syntax and methods

```rust
(0..self.size()).map(|i| self.entry_at(i)).find(|(k, _)| cmp.compare(k, key).is_eq()).map(|(_, v)| v)    // Ordering::is_eq
self.entries_mut().set(size as usize, &(key.clone(), value.clone()));
```

### Notes

The bucket is **unsorted** and scanned linearly: with buckets of tens of pairs a scan of one page is dominated by the page fetch, and keeping it unsorted makes insert and split trivial. (The B+ tree's leaves *are* sorted; compare the costs there.) Uniqueness is enforced here, at the lowest level, so no caller can break it.

### In BusTub

"Lookup/Insert/Remove ... Insert returns false if the bucket is full or the key already exists" (header comments); `KeyComparator` is a function object returning -1/0/1.

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `if (cmp(array_[i].first, key) == 0) { value = array_[i].second; return true; }` (out-parameter + bool) | `Option<V>` |
| `std::find_if(array_, array_ + size_, pred)` | `Iterator::find` |
| `array_[size_++] = {key, value};` | `set(size, &(key, value))` then store `size + 1` |
| `const KeyType &key` copied into the page with `=` (trivially copyable) | `key.clone()` then `encode` |

### Learn more
- [`Iterator::find`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.find) · [`Ordering::is_eq`](https://doc.rust-lang.org/std/cmp/enum.Ordering.html#method.is_eq)

## Part 3 · Bucket remove

**Where this fits.** The last bucket operation.

### The task

In `src/storage/page/extendible_htable_bucket_page.rs`:
- `remove_at(idx)`: panic ("past the bucket's size") for `idx >= size`; shift later entries down (keeping order) and count one fewer. (`PageArray::remove_at` does the shifting.)
- `remove(key, cmp) -> bool`: find the key, `remove_at` it, say whether it was there.

### Tests

- Remove takes a pair out; the rest keep their order; a missing key is `false`; removing twice finds nothing; `remove_at` by slot; a bucket can be emptied and refilled.

### Syntax and methods

```rust
self.entries_mut().remove_at(bucket_idx as usize, size as usize);
write_u32(self.page.as_mut(), SIZE_OFFSET, size - 1);
```

### Notes

BusTub's bucket doesn't promise to keep entries ordered, so a "swap with the last" removal (O(1)) is also valid; this port shifts (O(n)) because the shifting helper exists and a stable order makes tests and debugging simpler. For small `n` it doesn't matter.

### In BusTub

```cpp
auto Remove(const KeyType &key, const KeyComparator &cmp) -> bool;   void RemoveAt(uint32_t bucket_idx);
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::move(array_ + i + 1, array_ + size_, array_ + i); --size_;` | `copy_within` + `size - 1` |
| swap-with-last: `array_[i] = array_[size_ - 1]; --size_;` | the same, `Vec::swap_remove` |
| return `true`/`false` after `find` | `match`/`map` over the `Option<usize>` |

### Learn more
- [`Vec::swap_remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.swap_remove) vs [`Vec::remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.remove)
