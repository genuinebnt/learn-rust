**Where this fits.** The reason it's *extendible* hashing: tables grow one bucket at a time, never rehashing everything.

## The task

In `insert` (and the helper `split_bucket`) in `src/container/disk/hash/disk_extendible_hash_table.rs`: when the key's bucket is **full** (and doesn't have the key):
1. if the bucket's local depth equals the directory's global depth, the directory must grow: if it is already at its **max depth**, `return false` (the table is full here); otherwise `incr_global_depth`;
2. **split**: allocate a new bucket page; the bucket's local depth becomes `d + 1` (set it for **every** directory slot that points at the old bucket); of those slots, the ones with bit `d` set now point at the **new** bucket; move the old bucket's entries whose hash has bit `d` set into the new bucket;
3. try again from the top: the key may land in a bucket that is **still full** (all entries went to the same side), which splits again.

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
