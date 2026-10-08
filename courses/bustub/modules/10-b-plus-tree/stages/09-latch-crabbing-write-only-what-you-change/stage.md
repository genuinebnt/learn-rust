The tree you have is correct and takes an exclusive latch on the header and on every page from the root to the leaf, for every insert and every remove. That serialises all writers (and blocks every reader behind them). This stage makes it fast, by two ideas from the lecture on index concurrency control:

1. **Safe nodes.** While descending with write latches, a page that **cannot** change its parent (an insert into it cannot make it split; a remove from it cannot make it underflow) makes everything above it irrelevant: release all the ancestors the moment you have latched a safe page. Most pages are safe, so a writer ends up holding one or two latches near the leaf.
2. **Optimism.** Assume the leaf is safe. Descend with cheap *read* latches, take a *write* latch on the leaf only, and do the whole operation there. Only if the assumption turns out wrong (the leaf would split or underflow) release it and redo the operation the pessimistic way from stage 3 to 8.

Correctness does not change: everything the tests of stages 2 to 8 check must still pass. What changes is how many pages are write-latched, and the tests count them.

## The task

In `src/storage/index/b_plus_tree.rs`:
- `safe_to_insert(page)`: a leaf is safe if `size + 1 < max_size` (the insert will not reach `max_size`); an internal page if `size < max_size` (it can take another child).
- `safe_to_remove(page, is_root)`: a root leaf is safe if `size > 1`; a root internal page if `size > 2`; any other page if `size > min_size`.
- In `descend_for_write`, after latching a page: `if safe(...) { ctx.release_ancestors() }` (drops the header guard and every guard on the stack), then push the new guard.
- `latch_leaf_for_write(key)`: read-latch the header, then the root and down (crab: latch the child before dropping the parent). When the page just read-latched is a leaf: drop that read guard, take the leaf's **write** latch while the parent's read latch is still held, and return it (with whether it is the root). `None` for an empty tree.
- `insert_optimistic(key, value) -> Option<bool>`: a duplicate is `Some(false)`; if the leaf stays below `max_size` after the insert, insert and `Some(true)`; otherwise `None` (use the pessimistic path).
- `remove_optimistic(key) -> bool`: a missing key (or an empty tree) is done; if the leaf stays at least `min_size` (a root leaf: non-empty), remove it and say done; otherwise `false`.
- `insert` and `remove` call these first (the two `@begin 2c-09` regions at their tops).

## Tests

- An insert into a leaf with room does `reads > 0` and exactly **one** `write_page`; a remove that leaves a leaf at least half full too; an insert that splits writes more than one. (`tree.bpm.get_reads()` and `get_writes()` count them.)
- With the root **read-latched by the test**, an insert into a leaf with room, and a remove that fits, still finish: they only need read latches above the leaf.
- Eight threads inserting disjoint shuffled keys, eight removing them, and nine threads inserting, removing and reading a mixed workload: nothing is lost, the structure is valid, no deadlock (a watchdog fails the test after a timeout), and no page is left pinned.

## Syntax and methods

```rust
fn latch_leaf_for_write(&self, key: &K) -> Option<(WritePageGuard<'a>, bool)> {
    let mut _parent = self.bpm.read_page(self.header_page_id);        // starts as the header; later each internal page
    let mut page_id = Header::new(&_parent[..]).root_page_id();
    if !page_id.is_valid() { return None; }
    let root = page_id;
    loop {
        let guard = self.bpm.read_page(page_id);                       // child latched while the parent is still held
        if Page::new(&guard[..]).is_leaf_page() {
            drop(guard);
            let leaf = self.bpm.write_page(page_id);                   // re-latch for writing; the parent's read latch keeps it in place
            return Some((leaf, page_id == root));                      // `_parent` drops here: only the leaf is held
        }
        let child = Internal::<_, K>::new(&guard[..]).child_for(key, &self.cmp);
        _parent = guard;                                               // the old parent is dropped after the child is held
        page_id = child;
    }
}
```

## Notes

**Why releasing ancestors is safe.** A thread only needs a page's parent latched in order to *change the parent*: add a separator after a split, remove one after a merge. A child that cannot split or underflow will not touch the parent, so the parent is not needed any more; and any other thread that wants the parent is no longer excluded by this one.

**What "safe" means is operation-specific** (and the root is special): safe-for-insert means "will not split", safe-for-remove means "will not underflow" and, for the root, "will not leave a single child or an empty tree". Write the three rules down as comments before the code.

**Why the optimistic path can re-latch the leaf.** Between dropping the leaf's read guard and taking its write guard, the leaf could be split or merged away *unless* someone prevents it. What prevents it is the **parent's read latch**: any thread that would restructure the leaf must have the parent write-latched (its separator changes), and cannot while we hold it. A thread that holds only the leaf (itself optimistic) changes the leaf's contents but never its identity. After the write latch is held the parent can be released.

**Why the lock order is deadlock-free.** Everyone takes latches strictly top-down, and among siblings left-to-right. A thread holding page P only ever waits for pages below P or to its right, never for an ancestor or a left neighbour; so a cycle cannot form.

**The header.** The header page is the parent of the root: read-latched on the optimistic path, write-latched on the pessimistic one until the root is known to be safe (or the operation is done). It is the first ancestor released when the root is safe.

## In BusTub

The Project 2 design document asks for exactly this: "Briefly describe the order in which you acquire and release latches, and when it becomes safe to release an ancestor." `b_plus_tree.h`'s `Context` has the pieces: `header_page_`, `write_set_`, `read_set_`. The tests `OptimisticInsertTest` and `OptimisticDeleteTest` (the boss) assert `EXPECT_GT(new_reads - base_reads, 0); EXPECT_EQ(new_writes - base_writes, 1);` through the traced pool.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `ctx.write_set_.clear()` / `ctx.header_page_ = std::nullopt` to release ancestors | `ctx.release_ancestors()`: assigning `None` and clearing the `Vec` drop (unlatch) the guards |
| `std::shared_mutex` upgrade (not supported) | drop the read guard, take the write guard while the parent is held; no upgrade primitive exists, in C++ or Rust |
| `bpm_->ReadPage` vs `bpm_->WritePage` counted by `TracedBufferPoolManager` | `tree.bpm.get_reads()` / `get_writes()` |
| `std::thread` + `join` | `std::thread::scope` (borrowed data, joined at the end) |

**Port rule:** a lock guard stored in a variable lives until that variable is reassigned, moved or dropped; "release this lock early" is `drop(guard)` or assigning a new guard over it, never an explicit `unlock()`.

## Learn more
- CMU 15-445 "Index Concurrency Control" (latch crabbing, optimistic crabbing) · [Bayer & Schkolnick, "Concurrency of operations on B-trees" (1977)](https://link.springer.com/article/10.1007/BF00263762) · [`std::thread::scope`](https://doc.rust-lang.org/std/thread/fn.scope.html)

## Performance

With `h` levels, the pessimistic path takes `h + 1` exclusive latches per write and serialises all writers at the header. The optimistic path takes `h + 1` *shared* latches and one exclusive one on the leaf. Two writers conflict only if they touch the same leaf (or one of them has to restructure, which is rare: about 1 insert in `capacity / 2`), so throughput scales with the number of leaves rather than staying flat.

The cost model to hold in mind: `writes_per_insert` is 1 for the common case and `h` or more for a split. Measuring the fraction of operations that fall back to the pessimistic path tells you whether the optimism pays: with 255 pairs per leaf it is below 1%.

**Measure it.** Run the same 8-thread insert workload with the optimistic path disabled (comment out the two early-return regions) and enabled, on a tree with 255-pair leaves, and compare operations per second. Print the fallback rate. Then rerun with `leaf_max_size = 3` (every other insert splits) and see the optimistic path stop paying.

## Hints

### How do you know a node is safe before you have changed anything?

By looking at its size *now* and asking whether the operation, applied to it, would change what its parent holds. Insert: would the page reach (leaf) or exceed (internal) `max_size`? Remove: would it fall below `min_size`, or (the root) have too few? A page is only inspected after it is latched, so decide safety when you have its guard, before pushing it on the stack.

### What exactly gets released, and what must stay?

Everything *above* the safe page: the header guard and all guards already in `write_set`. The safe page's own guard is pushed afterwards and stays. Later steps (`insert_into_parent`, `rebalance`) pop from the stack; if the safe page is where the stack ends, they never reach for a parent that has been released, because a safe page never needs one.

### Optimistic means assume, check, and redo

The optimistic function must return enough for the caller to know whether it *did* the operation. If it did anything before deciding it could not (a partial insert), the pessimistic redo would see a half-done state. Check the leaf first, change it only when you are sure. And a duplicate key or a missing key is a complete answer in both paths: it must not fall through to the slow path.
