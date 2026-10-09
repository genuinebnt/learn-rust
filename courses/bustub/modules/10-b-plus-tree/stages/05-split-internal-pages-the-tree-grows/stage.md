Splitting a leaf adds one child to its parent. When the parent is already full, **it** splits too, its parent gets a child, and so on: a split can cascade all the way to the root, and a root split is the only thing that makes the tree taller. This stage finishes the insert path: `insert_into_parent` becomes a loop that climbs while pages are full.

Internal splits differ from leaf splits in one way that is worth getting right, and the tests check it exactly: the **middle key moves up** instead of being copied. Internal keys are signposts, not data, so the key that separates the two new halves is no longer needed inside either of them.

**Where this fits.** With internal pages of 3 children, five keys already make a three-level tree. These small sizes are the point: they force every case in a few dozen inserts.

> [!CHECK] An internal page has `max_size` 4 and is full: slot 0 has no key, then keys 10, 20, 30 with children c0..c3. The child `new` with key 25 must be inserted. After the split, which pairs does each page hold, and which key moves up to the parent? Does the right page still store that key?
> ||Five pairs after the insert: (_, c0), (10, c1), (20, c2), (25, new), (30, c3). The left page keeps the first ceil(5 / 2) = 3; the right page gets (25, new) and (30, c3). The key 25 moves up as the separator. The right page's slot 0 still holds 25, but nothing reads the key of slot 0.||
>
> - Do the insert on a list first, then cut it.
> - How many pairs stay on the left when there are `max_size + 1`?
> - What does a child's slot 0 key mean in an internal page?

## The task

Complete `insert_into_parent` in `src/storage/index/b_plus_tree.rs`. When the popped parent is **full** (`size == max_size`).
A full parent is split too. Its `max_size` pairs plus the new `(key, right_id)` (at its sorted place, after slot 0, which has no key) are divided: the old page keeps the first `ceil((max_size + 1) / 2)`, a new internal page gets the rest. The key of the new page's slot 0 is the one that **moves up**: it is the separator for the next level, and nothing in the new page reads it. The insert then continues one level up with `left_id = the old parent`, `key = the key that moved up` and `right_id = the new page`, until a parent has room or there is none and a new root is made.

> [!ASIDE] The steps, if you would rather not work them out
> 1. collect its `(key, child)` pairs in a `Vec` and insert the new `(key, right_id)` at its sorted position (after slot 0, which has no key): `max_size + 1` pairs;
> 2. the left page keeps the first `ceil((max_size + 1) / 2)`; write them back into the existing page and `set_size`;
> 3. allocate a new internal page, `init` it, and write the rest into its slots `0..`; the key of its slot 0 is the one that **moves up**: it is the separator for the next level, and nothing in the new page reads it;
> 4. repeat with `left_id = parent_id`, `key = the key that moved up`, `right_id = the new page's id` — the loop either finds a parent with room, or pops `None` and makes a new root.

## Tests

- Keys 1..=4 with `(leaf 2, internal 3)` give `{3 {2 [1] [2]} {4 [3] [4]}}`: the root split, 3 moved up. Keys 1..=9 give a known 4-level tree.
- The height never grows by more than one per insert, and the structure checker passes after inserts in ascending, descending and shuffled order for eight (leaf, internal) size pairs, 150 keys each.
- 2,000 shuffled keys in a pool of only **20 frames** are all found: a deep tree must not pin more than its path.
- BusTub's `InsertTest1NoIterator`; duplicates in a deep tree are refused and change nothing.

## Syntax and methods

```rust
let mut entries: Vec<(K, PageId)> = (0..parent.size()).map(|i| parent.entry_at(i)).collect();
let at = 1 + entries[1..].partition_point(|(k, _)| self.cmp.compare(k, &key).is_le());   // where the new pair goes: after the last key <= key
entries.insert(at, (key.clone(), right_page_id));
let keep = entries.len().div_ceil(2);                       // the left page keeps the extra one
let moves_up = entries[keep].0.clone();                     // the first key of the right half
for (i, (k, child)) in entries[keep..].iter().enumerate() { right.set_entry_at(i as u32, k, *child); }
```

## Notes

**Why use a `Vec` here?** The overflowing page would need `max_size + 1` slots, which the page may not have (a page at full capacity has none to spare). Building the sequence in memory, then writing both halves, sidesteps it and makes the arithmetic obvious. It allocates once per internal split, which is rare; the hot path (a leaf with room) never reaches this code.

**Leaf vs internal, once more.**

| | leaf split | internal split |
|---|---|---|
| separator | **copied** up: the key stays in the right leaf | **moved** up: the key leaves both halves |
| halves | `ceil(n/2)` and the rest | `ceil((n+1)/2)` and the rest, counted in children |
| chain | next-leaf pointers updated | none |

**Terminates.** Each iteration moves one level up the stack; the stack holds the path from the topmost page you may change, so the loop ends at a parent with room or at the root.

## In BusTub

`b_plus_tree_internal_page.h`: "Store `n` indexed keys and `n + 1` child pointers (page_id) within internal page. ... the first key in key_array_ always remains invalid." The slot-0 key of the new right page is exactly that invalid key. This course's rule: an internal page splits when a child is added to a page that already holds `max_size` children.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a temporary `std::vector<std::pair<KeyType, page_id_t>>` or oversize array to hold `max_size + 1` pairs | `Vec<(K, PageId)>` |
| `std::upper_bound` to find the insertion point | `partition_point` on the keys after slot 0 |
| recursion `InsertIntoParent(...)` calling itself | a `loop` that reassigns `left_id`, `key`, `right_id` (no stack growth, same logic) |

**Port rule:** a recursive "propagate to the parent" becomes a loop over a stack of guards when the guards are already in a `Vec`.

## Learn more
- CMU 15-445 "Tree Indexes" · [B+ tree (Wikipedia)](https://en.wikipedia.org/wiki/B%2B_tree) · [`slice::partition_point`](https://doc.rust-lang.org/std/primitive.slice.html#method.partition_point)

## Performance

A cascade of `k` internal splits writes `2k + 1` pages and happens with probability about `1 / fan-out^k`, so the expected extra cost per insert is tiny: with leaves of ~500 pairs and 340-way internal pages, a leaf splits about once every 250 inserts and an internal page about once every 40,000. The *height* grows by one when the root splits, i.e. about every time the number of keys is multiplied by the fan-out.

Everything above the leaf level stays small: a completely full tree of 237 million pairs has 1 root, 681 pages below it and 463,761 below those. The upper levels are why the buffer pool makes a B+ tree fast: the top two levels (about 700 pages = 5.6 MB) are always in memory, so a lookup costs one or two disk reads however large the table is.

**Measure it.** Insert 1,000,000 shuffled keys with leaf size 255 and internal size 340 and print the height after each power of two of keys; confirm it increases by one about every time the key count is multiplied by ~340. Count `get_writes()` per insert and find the inserts that write more than one page.

## Hints

### Collect, insert, split: the arithmetic is on a list, not on a page

Build the full `Vec` of `max_size + 1` pairs first, with the new pair already in its sorted place. Then the split is two slices: `entries[..keep]` (written back to the old page) and `entries[keep..]` (written to the new one). Every off-by-one in this stage comes from doing the arithmetic on the page instead.

### What exactly moves up, and what does the right page's slot 0 hold?

`entries[keep].0`. It becomes the next level's separator. The right page stores that pair as its slot 0, and slot 0's key is never read, so storing it there is harmless and storing garbage would be too. After inserting 1..=4 with `(leaf 2, internal 3)` the root has the single key 3 and its right child `{4 [3] [4]}` has the key 4, not 3.

### The loop's state is three variables

`left_id`, `key` and `right_id`. After a split they become `(parent_id, moved_up_key, new_page_id)`. If the next `write_set.pop()` returns `None`, the page that just split was the root: a new root with `left_id` and `right_id` as its children and `key` between them, and the header gets the new root's id.
