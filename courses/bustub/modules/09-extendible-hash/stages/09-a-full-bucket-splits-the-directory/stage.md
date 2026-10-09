The heart of extendible hashing: **splitting a full bucket**. When the target bucket is full, allocate a new one, raise the local depth, redistribute the entries by the *new* hash bit, repoint the directory slots between the two buckets, and **retry**: all the entries may have gone to the same side, so the bucket may still be full and the split repeats. When the bucket's local depth already equals the global depth, the directory **doubles** first; at the maximum depth the insert simply fails.

Everything earlier was preparation for this stage: bit arithmetic, directory growth, bucket lifecycle and latching all appear in one function.

**Where this fits.** The reason it's *extendible* hashing: tables grow one bucket at a time, never rehashing everything.

## The task

In `insert` (and the helper `split_bucket`) in `src/container/disk/hash/disk_extendible_hash_table.rs`: when the key's bucket is **full** (and doesn't have the key).
A full bucket that does not already hold the key is split until the key has room. When `insert` returns, `verify_integrity` holds. The directory has doubled only if the bucket's local depth equalled the global depth; if it is already at its **max depth**, `insert` returns `false` (the table is full here). Every directory slot that referenced the old bucket now has local depth `d + 1`; those whose hash has bit `d` set point at a new bucket, which holds exactly the old entries whose hash has bit `d` set. If the key's bucket is *still* full afterwards (all entries went to the same side), it splits again.

> [!ASIDE] The steps, if you would rather not work them out
> 1. if the bucket's local depth equals the directory's global depth, the directory must grow: if it is already at its **max depth**, `return false` (the table is full here); otherwise `incr_global_depth`;
> 2. **split**: allocate a new bucket page; the bucket's local depth becomes `d + 1` (set it for **every** directory slot that points at the old bucket); of those slots, the ones with bit `d` set now point at the **new** bucket; move the old bucket's entries whose hash has bit `d` set into the new bucket;
> 3. try again from the top: the key may land in a bucket that is **still full** (all entries went to the same side), which splits again.

## Tests

- 8 keys chosen to spread two per low-2-bit class fit in a table with directory depth 2 and buckets of 2; a ninth is refused. With BusTub's literal keys 0..8 (four of them share their low bits) exactly 5 fit.
- A split moves entries by the new bit and the directory still verifies; 400 keys survive many splits; with max depth 3 and buckets of 2 at most 16 keys fit and the directory reaches depth 3; a 600-operation model test against a `HashMap`; no pins leak.

## Syntax and methods

```rust
let new_bit = 1u32 << new_depth.saturating_sub(1);
for i in (0..old_bucket.size()).rev() {                  // walk backwards: remove_at shifts later entries, which we've already passed
    let (k, v) = old_bucket.entry_at(i);
    if self.hash(&k) & new_bit != 0 { new_bucket.insert(&k, &v, &self.cmp); old_bucket.remove_at(i); }
}
for slot in 0..directory.size() {
    if directory.get_bucket_page_id(slot) == old_page_id { directory.set_local_depth(slot, new_depth as u8); if slot & new_bit != 0 { directory.set_bucket_page_id(slot, new_page_id); } }
}
```

## Notes

**Why every slot, not just one.** With global depth 3 and a bucket of local depth 1, **four** slots point at it (`2^(3-1)`). Splitting it to depth 2 leaves two slots for each half: the directory update must visit all four. Forgetting the others is the classic bug: `verify_integrity` catches it immediately ("bucket has the wrong number of pointers").

**Why loop.** If a full bucket's entries all share the next hash bit, one split leaves one empty bucket and one still-full one; the key still has no room. Splitting again is correct: it's what the paper does, and it stops at the max depth (return `false`).

**Borrow checker note.** `split_bucket` takes `&mut` views of the directory page and the old bucket *and* allocates a new page (a new guard). They are different pages, so there are no conflicts; keep each guard alive only as long as needed, and re-read the directory slot at the top of every loop iteration.

## In BusTub

The project spec: "Insert: ... If the bucket is full, you must split it. If the local depth equals the global depth, increment the global depth first (the directory doubles). ... Reinsert the entries of the old bucket ... it's possible that a split does not make room, so you may need to split repeatedly." The helper names in the header: `UpdateDirectoryMapping`, `MigrateEntries`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `MigrateEntries(old_bucket, new_bucket, new_bucket_idx, local_depth_mask)` iterating `old_bucket->Size()` while calling `RemoveAt`: a classic skip-an-element bug | iterate indices **backwards** when removing |
| `if (hash & (1 << d))` or `hash & mask == 0`: in C and C++ `==` binds **tighter** than `&`, so `hash & mask == 0` means `hash & (mask == 0)` | in Rust `&` binds tighter than `==`: `hash & mask == 0` is `(hash & mask) == 0`. Parenthesise anyway when you port |
| `bpm_->NewPage()` failing returns `INVALID_PAGE_ID` | `new_page()` always returns an id; fetching may panic when the pool is full |

**Port rule:** bitwise operators have different precedence relative to comparisons in C/C++ and Rust; when porting a bit test, add the parentheses explicitly and check the expression's meaning rather than copying it.

## Learn more
- Fagin et al., [Extendible Hashing](https://en.wikipedia.org/wiki/Extendible_hashing) · CMU 15-445 "Hash Tables" · BusTub [disk_extendible_hash_table.cpp](https://github.com/cmu-db/bustub/blob/master/src/container/disk/hash/disk_extendible_hash_table.cpp) (the stubs and their doc comments are the spec)

## Performance

A split costs **one new page** (allocation plus one write), a rewrite of the old bucket, and an update of the directory slots that pointed at it: roughly 3 page writes and O(bucket size) work to rehash and move entries (about 255 key hashes). It does not touch any other bucket, so the cost is independent of table size; a **doubling** adds a copy of the directory (a few hundred bytes).

Splitting is *amortised*: for a bucket of `B` entries, one split happens per about `B/2` inserts after steady state, so the average insert pays about 6 to 12 extra entry moves. The pathological case is **many keys with equal low bits**: if more than `B` keys share their low `max_depth` bits, the bucket cannot split further and the insert fails: a property of the hash and `max_depth`, not a bug.

**Measure it.** Insert 100 000 sequential keys and print the global depth, the number of buckets and the average fill after every 10 000 (expect fill around 69%, `ln 2`); count page writes per insert. Then insert keys crafted to share low bits and watch the failure at `max_depth`.

## Hints

### Which bit decides who moves?

After the split, the old bucket has local depth `d + 1`; the entry belongs in the **new** bucket iff its hash has bit `d` set (the bit that has just become significant). Entries with the bit clear stay. Compute `new_bit = 1 << d` from the local depth you read *before* incrementing, and apply it to the **full 32-bit hash of each key**, not to the directory index (which has fewer bits).

### Repoint every slot that referenced the old bucket

A bucket at local depth `d` in a directory of global depth `g` is referenced by `2^(g - d)` slots. After the split, each of those slots gets local depth `d + 1`, and the ones whose index has bit `d` set point at the **new** bucket. Iterate over all slots comparing the *page id* to the old one, rather than computing which slots by formula: it is slower by nothing that matters and impossible to get off by one.

### Retry, and the termination condition

After a split the key may still hash to a full bucket (all entries moved to one side), so loop: re-resolve the slot, check for room, split again. The loop ends when there is room or when the bucket's local depth equals the directory's **maximum** depth and it is full: the table cannot subdivide further, and `insert` returns `false`. Do not let the loop double the directory past its maximum. Test a pathological key set that forces the failure, and test that after it the table still passes `verify_integrity`.
