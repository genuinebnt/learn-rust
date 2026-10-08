---
title: Extendible hashing: a hash table that grows one bucket at a time
summary: Global and local depth, the directory of bucket pointers, what a split and a merge do, why the directory sometimes doubles, and the integrity rules the tests check.
minutes: 13
---
A normal hash table resizes by rehashing **everything**: allocate twice the buckets, reinsert every key. On disk that is catastrophic, so extendible hashing (Fagin, Nievergelt, Pippenger and Strong, 1979) grows by **splitting one bucket at a time**, touching only the keys in that bucket. Lookups cost at most two page reads: the directory and the bucket.

## The pieces

- A **bucket** is one page holding up to `bucket_max_size` (key, value) pairs.
- A **directory** is an array of `2^global_depth` pointers to buckets. A key goes to slot `hash(key) & (2^global_depth - 1)`: the **low `global_depth` bits** of its hash.
- Each bucket has a **local depth** `d ≤ global_depth`: the number of low hash bits that all its keys share. A bucket of local depth `d` is pointed to by exactly `2^(global_depth - d)` directory slots (the slots that agree on its `d` bits).

| global depth | directory | |
|---|---|---|
| 0 | 1 slot | one bucket holds everything |
| 1 | 2 slots | buckets by the lowest bit |
| 2 | 4 slots | buckets by the low two bits, but several slots may share a bucket |
| 9 | 512 slots | the maximum in this course (a directory page holds 512 entries) |

```svg
caption: Global depth 2: four directory slots, three buckets. Buckets A and B have local depth 2 (one slot each); bucket C has local depth 1, so two slots (00 and 10) point at it. When C overflows, its local depth (1) is below the global depth (2): it splits without doubling the directory. A is at depth 2 = global: splitting A would double the directory first.
<svg viewBox="0 0 760 270" role="img" aria-label="A directory of four slots pointing to three buckets with local depths">
<defs><marker id="ex-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<text class="dim sm" x="40" y="24">directory (global depth 2)</text>
<rect class="box" x="40" y="34" width="150" height="40" rx="3"/><text class="fg sm" x="52" y="59">00</text><text class="dim sm" x="150" y="59">slot 0</text>
<rect class="box" x="40" y="78" width="150" height="40" rx="3"/><text class="fg sm" x="52" y="103">01</text><text class="dim sm" x="150" y="103">slot 1</text>
<rect class="box" x="40" y="122" width="150" height="40" rx="3"/><text class="fg sm" x="52" y="147">10</text><text class="dim sm" x="150" y="147">slot 2</text>
<rect class="box" x="40" y="166" width="150" height="40" rx="3"/><text class="fg sm" x="52" y="191">11</text><text class="dim sm" x="150" y="191">slot 3</text>
<rect class="live" x="420" y="34" width="250" height="40" rx="3"/><text class="t-g sm" x="432" y="59">bucket C   local depth 1: keys ending in 0</text>
<rect class="blue" x="420" y="100" width="250" height="40" rx="3"/><text class="t-b sm" x="432" y="125">bucket A   local depth 2: keys ending in 01</text>
<rect class="hot" x="420" y="166" width="250" height="40" rx="3"/><text class="t-a sm" x="432" y="191">bucket B   local depth 2: keys ending in 11</text>
<path class="ln-g" d="M190 54 H418" marker-end="url(#ex-a)"/><path class="ln-g" d="M190 142 C300 142 300 62 418 62" marker-end="url(#ex-a)"/>
<path class="ln-b" d="M190 98 C300 98 300 120 418 120" marker-end="url(#ex-a)" style="stroke:var(--fn)"/><path class="ln" d="M190 186 H418" marker-end="url(#ex-a)" style="stroke:var(--acc)"/>
<text class="dim sm" x="40" y="236">slot = hash &amp; 0b11 (the low 2 bits);  slots 00 and 10 differ in bit 1, which bucket C does not look at</text>
<text class="t-w sm" x="40" y="256">split image of A (slot 01, depth 2) = 01 xor (1 &lt;&lt; 1) = 11: B</text>
</svg>
```

## Insert, and what a split does

Find the slot, then the bucket. If the key is already there: refuse. If there is room: insert. If the bucket is **full**, split it:

1. If the bucket's local depth equals the global depth, **double the directory** first (`global_depth += 1`): the new half of the directory is a copy of the old half, so every bucket is now pointed to by twice as many slots. (If `global_depth` is already the maximum, the insert fails: the table is full at that slot.)
2. **Allocate a new bucket** and raise the local depth of the old one by 1 (the new one gets the same).
3. **Redistribute** the old bucket's entries by the *new* bit `d`: those with bit `d` = 1 move to the new bucket.
4. **Repoint the directory slots**: of the slots that pointed at the old bucket, those whose bit `d` is 1 now point at the new one.
5. **Retry the insert**: all keys may have gone to the same side, so the target bucket may still be full, and the split repeats.

Because only one bucket's entries move, a split costs **one new page and one rewritten page**, however large the table is. The directory doubling costs a copy of a 2 KiB array, not a rehash.

## Remove, merge and shrink

After a removal, if a bucket is **empty**, it can be merged with its **split image** (the bucket that shares all but the top local-depth bit), *provided both have the same local depth*. The empty one is deleted; all its slots are repointed to the survivor and the local depths drop by 1. If the survivor (or its new image) is empty too, repeat. Finally, if **no bucket has local depth equal to the global depth**, the directory can **halve**: every pair of slots is a duplicate.

## The invariants (`verify_integrity`)

1. Every directory slot below `2^global_depth` points at a valid bucket page.
2. Every local depth is at most the global depth.
3. A bucket of local depth `d` is referenced by exactly `2^(global_depth - d)` slots.
4. All slots pointing at one bucket have the same local depth, and agree on their low `d` bits.

A bug in any split or merge breaks one of these first, long before a lookup returns the wrong value, which is why the table has a `verify_integrity` the tests call after every operation.

| operation | pages read | pages written |
|---|---|---|
| lookup | header, directory, bucket (3) | none |
| insert, room in bucket | header, directory, bucket | bucket |
| insert, split | + a new page | bucket, new bucket, directory |
| insert, split with doubling | + a new page | the same, and the directory grows |

> [!NOTE] Why three levels here
> BusTub's table has a **header page** above the directories so that one table can use many directory pages (up to 512), each growing independently: the top bits of the hash choose the directory, the low bits the bucket. A single-directory extendible hash table has the same logic with the header removed.

## In real code

### Using it: a complete, runnable extendible hash table

The algorithm in one file, in memory, with the same operations and invariants the course's disk version has (a `Vec` of buckets stands in for pages). Read it next to the diagram above; the stages are this code split across pages.

```rust test
use std::collections::HashMap;

struct Bucket { depth: u32, items: Vec<(u32, u32)> }                  // (key, value); local depth

struct Table {
    global_depth: u32,
    dir: Vec<usize>,                                                  // slot -> index into `buckets`
    buckets: Vec<Bucket>,
    max_size: usize,                                                  // entries per bucket
}

fn hash(key: u32) -> u32 { key.wrapping_mul(2654435761) ^ (key >> 7) }    // any decent hash; the real one is MurmurHash3

impl Table {
    fn new(max_size: usize) -> Table {
        Table { global_depth: 0, dir: vec![0], buckets: vec![Bucket { depth: 0, items: vec![] }], max_size }
    }
    fn slot(&self, h: u32) -> usize { (h & ((1u32 << self.global_depth) - 1)) as usize }      // the LOW global_depth bits

    fn get(&self, key: u32) -> Option<u32> {
        let b = &self.buckets[self.dir[self.slot(hash(key))]];
        b.items.iter().find(|(k, _)| *k == key).map(|(_, v)| *v)
    }

    fn insert(&mut self, key: u32, value: u32) -> bool {
        loop {
            let slot = self.slot(hash(key));
            let b = self.dir[slot];
            if self.buckets[b].items.iter().any(|(k, _)| *k == key) { return false; }          // duplicate
            if self.buckets[b].items.len() < self.max_size {
                self.buckets[b].items.push((key, value));
                return true;
            }
            self.split(slot);                                          // full: split, then retry (it may still be full)
        }
    }

    fn split(&mut self, slot: usize) {
        let old = self.dir[slot];
        if self.buckets[old].depth == self.global_depth {              // no spare bit: double the directory (copy the first half)
            let copy = self.dir.clone();
            self.dir.extend(copy);
            self.global_depth += 1;
        }
        let d = self.buckets[old].depth;                               // the bit that has just become significant
        let new = self.buckets.len();
        self.buckets.push(Bucket { depth: d + 1, items: vec![] });
        self.buckets[old].depth = d + 1;
        let moved: Vec<(u32, u32)> = std::mem::take(&mut self.buckets[old].items);
        for (k, v) in moved {                                          // redistribute by bit d of the HASH
            let target = if hash(k) & (1 << d) != 0 { new } else { old };
            self.buckets[target].items.push((k, v));
        }
        for s in 0..self.dir.len() {                                   // repoint: slots that referenced `old` and have bit d set
            if self.dir[s] == old && (s & (1 << d)) != 0 { self.dir[s] = new; }
        }
    }

    /// The invariants the course's verify_integrity checks.
    fn verify(&self) {
        let mut refs: HashMap<usize, usize> = HashMap::new();
        for &b in &self.dir { *refs.entry(b).or_default() += 1; }
        for (b, n) in refs {
            let d = self.buckets[b].depth;
            assert!(d <= self.global_depth, "local depth above global");
            assert_eq!(n, 1 << (self.global_depth - d), "bucket {b}: wrong number of directory slots");
        }
    }
}

#[test]
fn grow_one_bucket_at_a_time() {
    let mut t = Table::new(2);
    for k in 0..100 {
        assert!(t.insert(k, k * 10));
        t.verify();                                                    // after EVERY operation
    }
    assert!(!t.insert(5, 0));                                          // duplicates are refused
    for k in 0..100 {
        assert_eq!(t.get(k), Some(k * 10));
    }
    assert_eq!(t.get(1000), None);
    assert!(t.global_depth >= 5);                                      // 100 keys in buckets of 2 need at least 50 buckets
    assert!(t.buckets.len() >= 50);
}

#[test]
fn the_directory_only_doubles_when_a_full_bucket_has_no_spare_bit_and_matches_a_hashmap() {
    let mut t = Table::new(2);
    assert_eq!((t.global_depth, t.dir.len()), (0, 1));
    // find three keys whose hashes share bit 0 pattern so the first split is forced: just insert until the first doubling
    let mut k = 0;
    while t.global_depth == 0 { t.insert(k, k); k += 1; }
    assert_eq!((t.global_depth, t.dir.len()), (1, 2), "the first split doubles the directory exactly once");
    t.verify();
    // a split of a bucket whose local depth is below the global depth does NOT double the directory
    let before = t.global_depth;
    let mut model = HashMap::new();
    for key in 0..500u32 { if t.insert(key, key + 1) { model.insert(key, key + 1); } }
    for (&key, &value) in &model { assert_eq!(t.get(key), Some(value)); }
    assert!(t.global_depth >= before);
    t.verify();
    // some bucket must still have a local depth below the global depth: the directory has shared slots
    assert!(t.buckets.iter().any(|b| b.depth < t.global_depth) || t.buckets.len() == t.dir.len());
}
```

### In the exercises

- **2b-02 to 2b-04:** the directory's `slot` (low bits), `global_depth`, doubling (`dir.extend(copy)`) and `verify` are the directory page's methods over bytes.
- **2b-05:** `Bucket` is the bucket page: sorted, with `max_size`, `insert` refusing duplicates and a full page.
- **2b-09:** `split` above: the order is *double if needed, allocate, bump depths, redistribute by bit `d` of the hash, repoint slots*, and `insert`'s `loop` is the retry.
- **2b-11:** the inverse: merge an empty bucket with its split image `slot ^ (1 << (d - 1))` when both have the same depth, repoint, lower depths, then shrink while no bucket has depth equal to the global depth.

### Where it is used

- **Disk-based hash indexes**: extendible hashing is the textbook design (Berkeley DB's hash access method is in this family; PostgreSQL's hash index uses the sibling technique, *linear hashing*), and ext3/ext4's HTree directory index is a hash-indexed tree for the same reason: grow by local splits, not by rehashing everything.
- **Distributed systems**: *consistent hashing* and Cassandra's token ranges share the "split a range when it is too full" idea.
- **Why not a B+ tree?** A hash index answers equality in one or two page reads and has no ordering; B+ trees (module 2c) also answer ranges and are the default index almost everywhere.
