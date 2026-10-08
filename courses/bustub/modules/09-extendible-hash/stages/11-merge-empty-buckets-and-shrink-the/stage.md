The inverse of a split. When a removal leaves a bucket **empty**, it is merged with its **split image** (the bucket that shares all but its newest bit), provided both have the same local depth: the empty bucket's page is deleted and every directory slot that pointed at it is repointed at the survivor, whose local depth drops by one. The merge may leave the survivor (or its new image) empty too, so it repeats. When no bucket uses the directory's full depth, the directory **halves**.

This is the hardest control flow in the module: a loop with several exit conditions, mutations to the directory and deletion of a page that must not be pinned.

## Part 1 · An empty bucket merges with its split image

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
- CMU 15-445 "Hash Tables" (merge and shrink) · `BufferPoolManager::delete_page` (stage 1f-03 of this course) · [Extendible hashing](https://en.wikipedia.org/wiki/Extendible_hashing)

## Part 2 · Shrink the directory

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

## Performance

A merge deletes one page (`delete_page`: O(1), the disk space is released) and rewrites the directory slots that pointed at it: O(directory size) work, no data moves, because the survivor already holds all the live entries (the empty one held none). The loop can repeat several times (cascading merges), each one touching two buckets, so a pathological removal can cost O(depth) merges: at most 9.

Merging and shrinking are what keep a table *proportional to its contents*: without them, a table that grew to a million keys and was emptied would keep tens of thousands of empty pages and a 512-slot directory.

**Measure it.** Insert 100 000 keys, remove 99 990 of them in random order and print buckets, global depth and allocated pages after each 10 000; then remove all and confirm the table returns to one bucket at depth 0.

## Hints

### When is a merge allowed?

Only when the bucket's **local depth is greater than 0** (there is a split image) **and the image has the same local depth** (if the image was split further, it stands for *several* buckets and cannot absorb this one). After a merge the survivor's depth is one lower, which can enable another merge with *its* new image: that is why it is a loop. State the three exit conditions explicitly: depth 0, image at a different depth, neither bucket empty.

### Delete the page only after nothing points at it

Order matters: first repoint **every** directory slot that referenced the dead bucket to the survivor, then lower the local depth of **every** slot that now references the survivor (there are twice as many as before), and only then call `delete_page`. Deleting first leaves directory slots pointing at a freed page for as long as the function runs, and `delete_page` fails outright if any guard still pins the page: drop all bucket guards before the merge.

### Shrink last, and use `can_shrink`

After the merges, `while directory.can_shrink() { decr_global_depth() }`. A directory can shrink repeatedly after one big merge, so a single `if` is a bug. And re-find the slot you are tracking after every merge: the bucket you started from may now be reached through a different slot. Finish with `verify_integrity` in the test, since a cascade of merges is where reference counts per bucket go wrong.
