This stage has 2 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · set_evictable: which frames may go

**Where this fits.** A frame in use (pinned) must not be evicted. The buffer pool tells the replacer with `set_evictable(frame, false/true)`.

### The task

Implement `set_evictable(frame, evictable)` in `src/buffer/lru_k_replacer.rs`: change the frame's flag and keep `curr_size` (the number of evictable frames) correct. A frame the replacer has never seen is ignored. Setting a flag to the value it already has changes nothing (and must not skew the count).

### Tests

- Of frames 1..6 with 1..5 set evictable and 6 not, `size()` is 5.
- Setting `true` twice counts once; toggling goes up and down; an unknown frame is ignored; further accesses keep the flag.

### Syntax and methods

```rust
let Some(node) = self.node_store.get_mut(&frame) else { return };   // get_mut: Option<&mut V>
if node.is_evictable != evictable { /* update flag and count together */ }
```

### Notes

`curr_size` is **derived state**: it could be computed by counting nodes. Keeping a counter is faster (`size()` is called often) but means *every* place that changes a flag, or removes a node, must update it. The two classic bugs: counting a no-op change, and forgetting it in `evict`/`remove`. When you feel the urge to cache a count, write the test that checks the cache against a recount (stage 6's model test does).

### In BusTub

"Set the evictable status of a frame. Note that replacer's size is the number of evictable frames. If a frame was previously evictable and is to be set to non-evictable, then size should decrement. If a frame was previously non-evictable and is to be set to evictable, then size should increment." (`SetEvictable` comment)

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto it = node_store_.find(id); if (it == node_store_.end()) return; it->second.is_evictable_ = ...` | `let Some(node) = self.node_store.get_mut(&id) else { return };` |
| `size_t curr_size_` decremented below zero: wraps to 18446744073709551615 | `usize` underflow panics in debug builds (use the invariant, not `wrapping_sub`) |
| `bool` flags mutated through public members | private fields + methods |

### Learn more
- [`HashMap::get_mut`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.get_mut) · [let-else](https://doc.rust-lang.org/rust-by-example/flow_control/let_else.html)

## Part 2 · evict: the least recently used among the infinite

**Where this fits.** The point of the whole module: choosing a victim.

### The task

In `src/buffer/lru_k_replacer.rs`, implement `evict()` and the pieces it needs (`pick_victim` and `remove_node` are the suggested helpers):
- among the **evictable** frames, choose the victim: for now, treat every frame as if it had fewer than `k` accesses, so the victim is the frame whose **first** (oldest kept) access is oldest: LRU;
- remove its node (history gone, `curr_size` down by one) and return it;
- `None` if no frame is evictable (and change nothing).

### Tests

- One access each: victims in order of access. Frames not made evictable are skipped, and `evict` on them gives `None`.
- `evict` lowers `size`; a failed `evict` does not.
- **An evicted frame starts over:** when it is recorded again it is a new frame, not evictable until marked.
- With `k = 3`, frames with 1 and 2 accesses are both "infinite": the older **first** access goes first, not the older latest one.

### Syntax and methods

```rust
self.node_store.values().filter(|n| n.is_evictable()).min_by_key(|n| n.first_timestamp()).map(|n| n.frame_id())
let victim = self.pick_victim()?;                         // `?` on Option: return None if there is no victim
self.node_store.remove(&victim)                           // HashMap::remove -> Option<V>
```

### Notes

`Iterator::min_by_key` scans everything: this is O(n) per eviction, which is fine for the tests and wrong for a pool of a million frames (stage 8 fixes that). Write the obviously-correct version first; the test suite then protects the fast one.

### In BusTub

"Find the frame with largest backward k-distance and evict that frame. Only frames that are marked as 'evictable' are candidates for eviction. ... Successful eviction of a frame should decrement the size of replacer and remove the frame's access history."

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::min_element(first, last, comp)` returns an iterator; `end()` when empty (dereferencing it is UB) | `min_by_key(..)` returns `Option` |
| a hand-written loop with a "best so far" variable and a `bool found` | `filter` + `min_by_key` + `map` |
| `std::optional<frame_id_t> Evict()` | `Option<FrameId>` |
| `node_store_.erase(it)` | `node_store.remove(&k)` |

### Learn more
- [`Iterator::min_by_key`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.min_by_key) · [`Iterator::filter`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.filter) · C++ [`std::min_element`](https://en.cppreference.com/w/cpp/algorithm/min_element)
