Removal in its simplest form: find the key through header, directory and bucket, remove it from the bucket, and report whether it was there. The directory is latched for writing from the start (a merge may follow, next stage), and the bucket is the only page modified.

The stage is short on purpose. Its job is to put the **removal path** in place with the right latching and the right return value, so that the next stage can add merging as one clearly separated step rather than as a rewrite.

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

## Performance

`remove` costs what `insert` into a bucket with room costs: three page accesses, one `lower_bound`, one shift (about half the array on average), the bucket marked dirty. A removal of an **absent** key still latches the directory and bucket (the directory in write mode, as a merge cannot be ruled out until you have looked), so a stream of failed removals serialises on the directory latch like a stream of inserts.

A removal does **not** free memory: the bucket keeps its page even when it becomes empty (until a merge in the next stage), so a table that inserts and removes the same keys repeatedly does not leak pages or grow, but a table emptied by removals keeps all its buckets until merged.

**Measure it.** Insert 10 000 keys, remove them all, and count the pages the buffer pool has allocated (`bpm.new_page` count) at the end: with no merge it stays at the high-water mark. Re-run after the next stage and watch it fall.

## Hints

### Return false without changing anything for an absent key

A `remove` of a key that is not there must leave the table byte-for-byte unchanged and return `false`: no dirty page, no merge attempt. Check with a counting disk that a failed removal causes no write after the pool flushes. This also tells you where the "empty bucket" test belongs: *only after a removal that succeeded*, because a bucket that was already empty and from which nothing was removed has not changed.

### Which guards survive past the removal?

To merge you will need the **directory** (still latched) and the *page ids* of the bucket and its image, but **not** the bucket guard: a merge deletes the bucket's page, and `delete_page` refuses a pinned page, which a live guard keeps. Structure the function so the bucket guard is released (or goes out of scope) *before* the code that merges, and so the directory guard is not.

### Test remove against the model, not only by example

Extend the random model test with `remove` operations: after every step compare `get_value` for a sample of keys with the `HashMap` model and call `verify_integrity`. Include removals of absent keys and removals followed immediately by re-insertion of the same key. The bug this finds is the one where `remove` leaves a bucket in a state `insert` does not expect.
