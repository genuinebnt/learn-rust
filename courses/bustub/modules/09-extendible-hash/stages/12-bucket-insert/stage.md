**Where this fits.** What a bucket does: find a key, add a pair.

## The task

In `src/storage/page/extendible_htable_bucket_page.rs`:
- `lookup(key, cmp) -> Option<V>`: scan the entries for a key that **compares equal** under the comparator (not `==` on bytes);
- `insert(key, value, cmp) -> bool`: `false` (nothing changes) if the bucket is full or already has the key; otherwise append the pair at slot `size` and count it.

## Tests

- Insert then lookup of 5 keys; entries at the slots the accessors say; a full bucket refuses; a duplicate key is refused and the old value stays; `i32` buckets with 1023 pairs.
- **Keys compare through the comparator**: two `GenericKey<16>` whose bytes differ beyond the first 8 are equal to `GenericComparator<16>`, so the second insert is a duplicate.

## Syntax and methods

```rust
(0..self.size()).map(|i| self.entry_at(i)).find(|(k, _)| cmp.compare(k, key).is_eq()).map(|(_, v)| v)    // Ordering::is_eq
self.entries_mut().set(size as usize, &(key.clone(), value.clone()));
```

## Notes

The bucket is **unsorted** and scanned linearly: with buckets of tens of pairs a scan of one page is dominated by the page fetch, and keeping it unsorted makes insert and split trivial. (The B+ tree's leaves *are* sorted; compare the costs there.) Uniqueness is enforced here, at the lowest level, so no caller can break it.

## In BusTub

"Lookup/Insert/Remove ... Insert returns false if the bucket is full or the key already exists" (header comments); `KeyComparator` is a function object returning -1/0/1.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `if (cmp(array_[i].first, key) == 0) { value = array_[i].second; return true; }` (out-parameter + bool) | `Option<V>` |
| `std::find_if(array_, array_ + size_, pred)` | `Iterator::find` |
| `array_[size_++] = {key, value};` | `set(size, &(key, value))` then store `size + 1` |
| `const KeyType &key` copied into the page with `=` (trivially copyable) | `key.clone()` then `encode` |

## Learn more
- [`Iterator::find`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.find) · [`Ordering::is_eq`](https://doc.rust-lang.org/std/cmp/enum.Ordering.html#method.is_eq)
