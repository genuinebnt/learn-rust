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
