The common path: the table already has a directory, and the key's bucket **has room**. Look the key up through header, directory and bucket, and insert into the bucket: unless the key is already there, in which case refuse. No splitting yet: a full bucket is the next stage's problem.

The substance is the **latching discipline** on this path: which pages are held in which mode, what is held while the bucket is modified, and that the right amount is released on every exit.

**Where this fits.** Most operations find an existing bucket with room. This stage is the common path.

## The task

In `src/container/disk/hash/disk_extendible_hash_table.rs`:
- `get_value`: after the header, **read-latch the directory and then release the header** (once you hold the directory's latch, the header slot can't change under you), find the bucket for the hash, **read-latch the bucket and release the directory**, look the key up, return it as a 0- or 1-element `Vec`.
- `insert`, when the header slot already has a directory: **write-latch the directory and release the header**; find the bucket for the hash; **write-latch the bucket**; if it already has the key return `false`; if it has room, insert and return `true`. (A full bucket is stage 18: `return false` for now.)

## Tests

- 8 keys inserted into a bucket of 8, each readable right away. Missing keys have no value. A duplicate key is refused and the old value stays.
- With header depth 2, 40 keys spread across several directories and are all found. Many lookups leave nothing latched or pinned.

## Syntax and methods

```rust
let directory_guard = self.bpm.read_page(directory_page_id);
drop(header_guard);                                    // crabbing: hold the child before releasing the parent
Bucket::<_, K, V>::new(&bucket_guard[..]).lookup(key, &self.cmp).into_iter().collect()     // Option<V> -> Vec<V>
```

## Notes

**Latch crabbing** (also "lock coupling"): to go down a tree under concurrent access, latch the child **before** releasing the parent. Releasing the parent first lets another thread change the parent's pointer to the child (a split, a delete) in the gap, and you would follow a stale pointer. Releasing the parent *as soon as* you hold the child (and the child is safe) keeps the upper levels free for other threads: the header is a bottleneck every operation passes through, so holding it for a few instructions rather than the whole operation matters.

`get_value` uses **read** latches (many readers at once); `insert` and `remove` use **write** latches on the pages they may change. An insert that finds room in a bucket could release the directory early too; this version keeps it until the insert is done (simple and correct).

## In BusTub

Lecture 10 ("Index Concurrency Control") describes this protocol; the project spec says: "you should use the `ReadPageGuard`/`WritePageGuard` ... and release the guards of the parent pages when it is safe to do so".

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto header_guard = bpm_->ReadPage(header_page_id_); auto header = header_guard.As<ExtendibleHTableHeaderPage>(); ... header_guard.Drop();` | `let header_guard = ..; let header = Header::new(&header_guard[..]); ... drop(header_guard);` (the borrow checker stops you using `header` after the drop) |
| `result->push_back(value); return true;` (out-parameter) | `Vec<V>` returned |
| forgetting `Drop()` keeps a latch for the whole function: a performance bug, or a deadlock | the same, but a guard's scope is visible, and `drop` is explicit |
| `std::shared_lock` vs `std::unique_lock` | read guard vs write guard |

## Learn more
- CMU 15-445 "Index Concurrency Control" (latch crabbing) · [`drop`](https://doc.rust-lang.org/std/mem/fn.drop.html) · Rust Atomics and Locks, [locking basics](https://marabos.nl/atomics/building-locks.html)

## Performance

An insert into a bucket with room reads the header (shared), latches the directory and bucket **exclusively**, does one `lower_bound` and one shift, and marks one page dirty: three page accesses, one page that will need writing back. Latching the directory in write mode for the *whole operation* is coarse: two inserts into the same directory serialise even when they hit different buckets. That is a deliberate simplicity: finer designs latch the bucket first and upgrade only if a split is needed, at the cost of a retry path.

The common case (room in the bucket) holds the directory latch for microseconds; contention appears when many threads insert into one directory, which the header's top-bit routing spreads over up to 512 directories.

**Measure it.** Run 1, 2, 4 and 8 threads inserting disjoint keys into a table with `header_max_depth` 0 (one directory) and 4 (16 directories) and compare throughput: the second should scale better.

## Hints

### Which mode, and for how long?

Insert holds the **directory in write mode** from the moment it is latched until the operation finishes, because a split (next stage) will modify it and there is no safe way to upgrade a read latch. The header is released the moment the directory is held. The bucket is latched in write mode. Draw the three guards on a timeline, mark when each is acquired and dropped, and check no acquisition happens while an *earlier-in-order* page is waited on.

### Duplicate versus full

Both make `insert` return `false`, for different reasons, and the bucket page's own `insert` cannot tell the table which. Check for the key first (`lookup`) and return `false` on a duplicate; then check `is_full()`; and only then call `insert`. The next stage turns "full" into "split and retry", while a duplicate stays a refusal, so conflating them now costs you later.

### A model test finds what the examples miss

Compare the table against a `HashMap<key, value>` over random inserts of a small key range (many duplicates) and `get_value` after every step, with `verify_integrity` called every few operations. Seed the generator, print the seed on failure. This single test covers lookup, duplicates and placement, and it is what you will rerun after the split and merge stages.
