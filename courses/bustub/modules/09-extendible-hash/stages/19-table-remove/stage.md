**Where this fits.** Deleting a key. (Merging is the next stage.)

## The task

Implement `remove(&key) -> bool` in `src/container/disk/hash/disk_extendible_hash_table.rs`: read-latch the header, find the directory (return `false` if there is none); **write-latch the directory** and release the header; find the bucket; **write-latch the bucket**; remove the key; return whether it was there. Don't merge anything yet.

## Tests

- Removing a key takes it out; the others stay. Removing from an empty table, a missing key, or the same key twice is `false`. A removed key can be inserted again. Removing every other key from a grown table verifies and leaves the right keys. BusTub's `RemoveTest1`.

## Syntax and methods

```rust
let (removed, now_empty) = { let mut bucket = Bucket::<_, K, V>::new(&mut bucket_guard[..]); (bucket.remove(key, &self.cmp), bucket.is_empty()) };
```

## Notes

Compute `removed` and `now_empty` inside one short scope so the mutable view of the bucket page is dropped before the next step needs the guard. (When a `&mut` view is alive, you can't use the guard it borrows from.) This "do the page work in a block, return plain values out of it" pattern is how you keep borrows short around guards.

## In BusTub

"Remove: ... Return true if the key was removed ... After removing, if the bucket is empty, try to merge it with its split image."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `bool removed = bucket->Remove(key, cmp_); bool empty = bucket->IsEmpty();` with the page pointer valid until the guard dies | the same two calls inside a block that owns the borrow |
| `return false;` early exits leave guards to their destructors | the same: guards drop at scope exit |

## Learn more
- BusTub [extendible_htable_test.cpp](https://github.com/cmu-db/bustub/blob/master/test/container/disk/hash/extendible_htable_test.cpp)
