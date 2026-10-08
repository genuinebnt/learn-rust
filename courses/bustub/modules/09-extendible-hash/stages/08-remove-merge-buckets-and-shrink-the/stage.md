This stage has 3 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · remove

**Where this fits.** Deleting a key. (Merging is the next stage.)

### The task

Implement `remove(&key) -> bool` in `src/container/disk/hash/disk_extendible_hash_table.rs`: read-latch the header, find the directory (return `false` if there is none); **write-latch the directory** and release the header; find the bucket; **write-latch the bucket**; remove the key; return whether it was there. Don't merge anything yet.

### Tests

- Removing a key takes it out; the others stay. Removing from an empty table, a missing key, or the same key twice is `false`. A removed key can be inserted again. Removing every other key from a grown table verifies and leaves the right keys. BusTub's `RemoveTest1`.

### Syntax and methods

```rust
let (removed, now_empty) = { let mut bucket = Bucket::<_, K, V>::new(&mut bucket_guard[..]); (bucket.remove(key, &self.cmp), bucket.is_empty()) };
```

### Notes

Compute `removed` and `now_empty` inside one short scope so the mutable view of the bucket page is dropped before the next step needs the guard. (When a `&mut` view is alive, you can't use the guard it borrows from.) This "do the page work in a block, return plain values out of it" pattern is how you keep borrows short around guards.

### In BusTub

"Remove: ... Return true if the key was removed ... After removing, if the bucket is empty, try to merge it with its split image."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `bool removed = bucket->Remove(key, cmp_); bool empty = bucket->IsEmpty();` with the page pointer valid until the guard dies | the same two calls inside a block that owns the borrow |
| `return false;` early exits leave guards to their destructors | the same: guards drop at scope exit |

### Learn more
- BusTub [extendible_htable_test.cpp](https://github.com/cmu-db/bustub/blob/master/test/container/disk/hash/extendible_htable_test.cpp)

## Part 2 · An empty bucket merges with its split image

**Where this fits.** Tables shrink as well as grow: otherwise a table that had a million keys keeps its million-key directory forever.

### The task

In `remove` (and the helper `merge_empty_buckets`) in `src/container/disk/hash/disk_extendible_hash_table.rs`: after a removal leaves the bucket **empty**, release the bucket's latch and, holding the directory's write latch, repeat:
1. if the bucket's local depth is 0, stop;
2. find its **split image** slot; if the image's local depth differs, stop (the sibling has split further and can't absorb this bucket);
3. if neither bucket is empty, stop. Otherwise keep the non-empty one (either, if both are empty): point **all** the slots of the other at the survivor, **decrease the local depth** of all the survivor's slots, and delete the dropped page from the pool (`bpm.delete_page`);
4. continue with a slot that points at the survivor (it may be empty too, or its new split image may be).

### Tests

- Emptying buckets reduces the number of distinct bucket pages; every page that left the directory has been **deleted from the pool** (`get_pin_count` is `None`).
- 300 keys, two thirds removed: the survivors are all found and the directory verifies. A table emptied completely is one bucket. Repeating insert-all/remove-all three times works.

### Syntax and methods

```rust
self.bpm.delete_page(drop_id);                            // only after every guard on that page is gone
bucket_idx = (0..directory.size()).find(|&s| directory.get_bucket_page_id(s) == keep).expect("the survivor has a slot");
```

### Notes

**Pin before delete.** `delete_page` refuses (returns `false`) if the page is pinned. Make sure no guard on the dropped page is alive when you call it: release the bucket guard before the merge, and don't hold a guard on the image bucket while deleting it. A merge that "works" but leaves pages undeleted is a leak you only see in file size.

**Why the loop.** After merging two depth-3 buckets into one depth-2 bucket, the survivor may itself be empty (if both were), and its new split image (depth 2) may now be mergeable. Merging cascades.

**Merging is optional for correctness**, mandatory for space. A table that never merges gives right answers.

### In BusTub

"If the bucket is empty after the removal, merge it with its split image. ... You must merge repeatedly if possible ... and you must delete the empty bucket page."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `bpm_->DeletePage(page_id)` returns `bool` and nobody checks it | check it, or `debug_assert!` it |
| the dropped bucket's `WritePageGuard` still alive in an outer scope: the delete silently fails | scope the guard in a block |
| `std::vector<page_id_t> to_delete;` collected and deleted later | the same pattern if deleting inside the loop gets awkward |

### Learn more
- CMU 15-445 "Hash Tables" (merge and shrink) · `BufferPoolManager::delete_page` (stage 1f-02 of this course) · [Extendible hashing](https://en.wikipedia.org/wiki/Extendible_hashing)

## Part 3 · Shrink the directory

**Where this fits.** The last piece of remove.

### The task

At the end of `merge_empty_buckets` in `src/container/disk/hash/disk_extendible_hash_table.rs`: while the directory `can_shrink()`, `decr_global_depth()`.

### Tests

- A table emptied completely returns to global depth 0. After removing three quarters of 64 keys the depth is **lower** (the directory shrank *as buckets merged*, not only at the very end) and the survivors are still there.
- A directory that can't shrink keeps its depth. **A model test**: 2000 random inserts and removes against a `HashMap`, checking `insert`'s and `remove`'s result at every step and `verify_integrity` every 100 steps.

### Syntax and methods

```rust
while directory.can_shrink() { directory.decr_global_depth(); }
```

### Notes

**The model test is the real safety net.** The table has so many interacting cases (split with and without growth, merge with and without shrink, cascades) that hand-written examples can't cover them. A random workload against a trivially correct model (`HashMap`) plus the page-level invariant checker finds the rest. This is *property-based testing*, and it works on every data structure in this course: B+ trees next.

### In BusTub

The spec: "Shrink the directory if possible: while `CanShrink()`, `DecrGlobalDepth()`".

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `while (dir->CanShrink()) { dir->DecrGlobalDepth(); }` | the same |
| `std::unordered_map<K, V>` as the reference model in tests | `HashMap<K, V>` |
| `rand()` seeded by time: failures you can't reproduce | a fixed-seed LCG: every failure is replayable |

### Learn more
- [Property-based testing](https://en.wikipedia.org/wiki/Software_testing#Property_testing) · the [`proptest`](https://docs.rs/proptest) crate (shrinks failing inputs automatically) · [`quickcheck`](https://docs.rs/quickcheck)
