The leaves of a B+ tree form a sorted linked list, and that is the whole point of the design: finding the first key of a range costs a tree descent, and the rest of the range costs one page after another with no tree walking. This stage adds the cursor: `begin()` (the smallest key), `begin_at(key)` (the first key not less than `key`) and `end()`.

The cursor remembers a *position* (a leaf and a slot in it) and holds **no latch between calls**: each step latches the leaf, copies the pair out and lets go. That keeps a slow consumer from blocking writers, at the price that a scan racing a writer may see the tree change under it (BusTub's own iterator makes the same trade).

## Part 1 · The cursor

**Where this fits.** `IndexIterator` is the first type in the course that implements Rust's `Iterator` for a data structure backed by pages.

### The task

In `src/storage/index/index_iterator.rs`:
- the struct is given: the pool, `page_id: Option<PageId>` (`None` is the end) and `index` (a slot in that leaf);
- `end(bpm)`: no leaf;
- `at(bpm, page_id, index)`: the position, then `skip_past_the_end_of_leaves`;
- `skip_past_the_end_of_leaves()`: while the position is past the last pair of its leaf, move to slot 0 of the next leaf (or become the end if there is none); latch each leaf with `read_page` just long enough to look;
- `is_end()`, `Iterator::next` (copy the current pair out, advance, normalise, return it) and `PartialEq` (same leaf, same slot).

### Tests

- Iterators compare by position: two `begin()`s are equal, `begin()` differs from `end()`, `begin_at(k)` after one `next` equals `begin_at(k + 1)`, a finished iterator equals `end()`.
- Nothing stays pinned between calls (the iterator holds no latch), writers are not blocked by a live iterator, and it carries on afterwards.

### Syntax and methods

```rust
impl<K: FixedSize + Clone, V: FixedSize + Clone> Iterator for IndexIterator<'_, K, V> {
    type Item = (K, V);
    fn next(&mut self) -> Option<(K, V)> {
        let page_id = self.page_id?;                                   // None: already at the end
        let pair = { let guard = self.bpm.read_page(page_id); Leaf::<_, K, V>::new(&guard[..]).entry_at(self.index) };   // latch, copy, unlatch
        self.index += 1;
        self.skip_past_the_end_of_leaves();
        Some(pair)
    }
}
```

### Notes

**Keep the position normalised.** After every move, the cursor points at a pair that exists, or is the end. Then `is_end` is a field check, equality is a field comparison, and `begin_at(k)` for a `k` larger than every key in its leaf (which `lower_bound` reports as slot `size`) just works because `at` moves on to the next leaf.

**A `for` loop over a tree.** Implementing `Iterator` is all it takes for `for (key, rid) in tree.begin()`, `.take(10)`, `.filter(..)`, `.collect()` and every other adapter to work on an index, with no more code. BusTub's `operator*`, `operator++` and `operator!=` become `next`, `==` and `is_end`.

### In BusTub

`index_iterator.h`: "// you may define your own constructor based on your member variables ... auto IsEnd() -> bool; auto operator*() -> std::pair<const KeyType &, const ValueType &>; auto operator++() -> IndexIterator &;". BusTub's tests loop `for (auto iter = tree.Begin(); iter != tree.End(); ++iter)`.

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `operator*` returning a reference into the page (valid only while the page guard lives) | `next()` returns the pair **by value**: nothing borrows the page after the call |
| `operator++`, `operator!=`, `IsEnd()` | `Iterator::next`, `PartialEq`, `is_end` |
| an iterator that keeps a `ReadPageGuard` member | a position only, latching per step (the C++ tests accept both) |

**Port rule:** a C++ iterator that hands out references into a buffer becomes a Rust iterator that hands out copies (or owns the guard); a reference into a page that may be evicted cannot outlive the latch.

### Learn more
- [`std::iter::Iterator`](https://doc.rust-lang.org/std/iter/trait.Iterator.html) · [Implementing `Iterator`](https://doc.rust-lang.org/rust-by-example/trait/iter.html) · C++ [named requirements: LegacyInputIterator](https://en.cppreference.com/w/cpp/named_req/InputIterator)

## Part 2 · begin, begin_at, end

**Where this fits.** The tree turns "where do I start" into a cursor.

### The task

In `src/storage/index/b_plus_tree.rs`:
- `begin()`: `find_leaf(None)` (the leftmost leaf, from stage 2); `IndexIterator::at(bpm, leaf_page_id, 0)`; an empty tree has no leaf, so its `begin()` is `end()`;
- `begin_at(key)`: `find_leaf(Some(key))`, the slot of `lower_bound(key)` in it, then `IndexIterator::at`; `end()` for an empty tree;
- `end()`: `IndexIterator::end(bpm)`.

### Tests

- An empty tree begins at its end; `begin()` visits every pair, in key order, with each value next to its key (200 shuffled keys).
- `begin_at` of an existing key starts there; of a missing key starts at the next one; below the smallest starts at the first; above the largest is the end. A scan from every starting key of a 40-key, 3-pairs-per-leaf tree reaches the last key (every leaf boundary is crossed).
- A scan after 500 random inserts equals a `BTreeMap`'s range for several probes.

### Syntax and methods

```rust
match self.find_leaf(Some(key)) {
    Some(leaf_guard) => {
        let at = Leaf::<_, K, V>::new(&leaf_guard[..]).lower_bound(key, &self.cmp);
        IndexIterator::at(self.bpm.inner(), leaf_guard.get_page_id(), at)          // `inner()` is the plain pool (the iterator's reads are not traced)
    }
    None => self.end(),
}
```

### Notes

`find_leaf` returns a read guard; the cursor needs only the page id. Take it, read what you need (`lower_bound`) while the guard is held, and let it drop *before* the cursor starts latching on its own, or the cursor's first `read_page` would be a second read latch on the same page (legal, but pointless).

**Range queries.** `begin_at(low)` followed by `take_while(|(k, _)| k < high)` is a complete range scan: one descent, then sequential leaf reads. This is why a B+ tree can answer `WHERE x BETWEEN a AND b` and a hash index cannot.

### In BusTub

`b_plus_tree.cpp`: "Begin() ... find the leftmost leaf page first, then construct index iterator"; "Begin(const KeyType &key) ... find the leaf page that contains the input key first, then construct index iterator"; "End() ... construct an index iterator representing the end of the key/value pair in the leaf node".

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `for (auto it = tree.Begin(); it != tree.End(); ++it) { auto [k, v] = *it; }` | `for (k, v) in tree.begin() { }` |
| `std::map::lower_bound(key)` returning an iterator | `tree.begin_at(&key)` |
| `std::map::equal_range` / two iterators for a range | `begin_at(&low)` plus `take_while` |

### Learn more
- [`Iterator::take_while`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.take_while) · C++ [`std::map::lower_bound`](https://en.cppreference.com/w/cpp/container/map/lower_bound) · CMU 15-445 "Tree Indexes" (range scans)

## Performance

A scan of `m` pairs costs one descent (`h` page reads) plus `m / (pairs per leaf)` sequential page reads; with 255 pairs per leaf (about half full) that is one page read per 255 pairs. The cost per pair is dominated by the per-step latch (an uncontended `RwLock` read: tens of nanoseconds) and the 16-byte copy.

Latching per step rather than per leaf costs about one extra lock operation per pair compared with holding a guard for the whole leaf, and buys the freedom to never block a writer for longer than one copy. For a bulk scan you can have both by reading a whole leaf's worth of pairs per latch (a `Vec<(K, V)>` buffer in the iterator); that is a worthwhile exercise once the tests pass.

**Measure it.** Scan 1,000,000 pairs with `begin()` and time pairs per second; then scan the same range by calling `get_value` for each key and compare (the descent per key is why a scan exists). Try the buffered variant.

## Hints

### Where exactly should the cursor point?

At a pair that exists, or nowhere. `begin_at` may produce "slot `size` of this leaf" (every key here is smaller than the target): that is not a position, it is the first slot of the *next* leaf. One function that normalises a position, called by the constructor and by `next`, removes all the special cases.

### What does the iterator own, and what does it borrow?

The buffer pool (a shared reference) and a position (two small values). No guard. If your `next` keeps a `ReadPageGuard` in a field, a long-lived iterator pins a frame and read-latches a leaf for as long as it lives; the nothing-stays-pinned test catches it.

### Equality and the end

Two iterators are equal when `(page_id, index)` match, and every finished iterator has `page_id == None`, `index == 0`. If `next` leaves a stale `index` after becoming the end, `it == tree.end()` will be false for an iterator that is plainly done.
