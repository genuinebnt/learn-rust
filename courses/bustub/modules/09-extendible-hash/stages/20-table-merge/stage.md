**Where this fits.** Tables shrink as well as grow: otherwise a table that had a million keys keeps its million-key directory forever.

## The task

In `remove` (and the helper `merge_empty_buckets`) in `src/container/disk/hash/disk_extendible_hash_table.rs`: after a removal leaves the bucket **empty**, release the bucket's latch and, holding the directory's write latch, repeat:
1. if the bucket's local depth is 0, stop;
2. find its **split image** slot; if the image's local depth differs, stop (the sibling has split further and can't absorb this bucket);
3. if neither bucket is empty, stop. Otherwise keep the non-empty one (either, if both are empty): point **all** the slots of the other at the survivor, **decrease the local depth** of all the survivor's slots, and delete the dropped page from the pool (`bpm.delete_page`);
4. continue with a slot that points at the survivor (it may be empty too, or its new split image may be).

## Tests

- Emptying buckets reduces the number of distinct bucket pages; every page that left the directory has been **deleted from the pool** (`get_pin_count` is `None`).
- 300 keys, two thirds removed: the survivors are all found and the directory verifies. A table emptied completely is one bucket. Repeating insert-all/remove-all three times works.

## Syntax and methods

```rust
self.bpm.delete_page(drop_id);                            // only after every guard on that page is gone
bucket_idx = (0..directory.size()).find(|&s| directory.get_bucket_page_id(s) == keep).expect("the survivor has a slot");
```

## Notes

**Pin before delete.** `delete_page` refuses (returns `false`) if the page is pinned. Make sure no guard on the dropped page is alive when you call it: release the bucket guard before the merge, and don't hold a guard on the image bucket while deleting it. A merge that "works" but leaves pages undeleted is a leak you only see in file size.

**Why the loop.** After merging two depth-3 buckets into one depth-2 bucket, the survivor may itself be empty (if both were), and its new split image (depth 2) may now be mergeable. Merging cascades.

**Merging is optional for correctness**, mandatory for space. A table that never merges gives right answers.

## In BusTub

"If the bucket is empty after the removal, merge it with its split image. ... You must merge repeatedly if possible ... and you must delete the empty bucket page."

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `bpm_->DeletePage(page_id)` returns `bool` and nobody checks it | check it, or `debug_assert!` it |
| the dropped bucket's `WritePageGuard` still alive in an outer scope: the delete silently fails | scope the guard in a block |
| `std::vector<page_id_t> to_delete;` collected and deleted later | the same pattern if deleting inside the loop gets awkward |

## Learn more
- CMU 15-445 "Hash Tables" (merge and shrink) · `BufferPoolManager::delete_page` (stage 1f-09 of this course) · [Extendible hashing](https://en.wikipedia.org/wiki/Extendible_hashing)
