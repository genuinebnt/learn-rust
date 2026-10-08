This stage has 2 parts. Work through them in order; they build on each other, and every test in the stage has to pass.

## Part 1 · IndexList::remove: by handle, and reuse freed slots

**Where this fits.** Pinning a frame takes it out of the middle of the line.

### The task

In `src/common/index_list.rs`:
- `remove(handle)`: if the handle still names a live element (`index_of` checks index, generation and that the slot is occupied), unlink it and return the value; otherwise `None`;
- `push_back`: **reuse a freed slot** (from the free list) before growing the `Vec`. A reused node keeps its bumped generation, so handles issued before the reuse stay stale.

### Tests

- Remove from the head, middle and tail; the list stays linked. Removing twice gives `None`.
- After `remove(a)` and a new push (which takes `a`'s slot), `get(a)` is `None`, `remove(a)` is `None`, and the new element is untouched.
- 1000 push-then-remove rounds don't break anything; a model test of 3000 random pushes and removes agrees with a `Vec`.

### Syntax and methods

```rust
let index = self.index_of(handle)?;        // given: Option<usize>, None for a stale or foreign handle
Some(self.unlink(index))
if let Some(free) = self.free.pop() { node.generation = self.nodes[free].generation; self.nodes[free] = node; }
```

### Notes

This is the **ABA problem** in miniature: a handle that names slot 4, then slot 4 is freed and reused for something else; the old handle now points at the wrong element. A generation turns "same index" into "same index *and* same lifetime". Real arenas (`slotmap`, `generational-arena`) do exactly this; C++ programs usually have the bug.

### In BusTub

```cpp
auto it = pos_.find(frame_id);
if (it != pos_.end()) { lru_list_.erase(it->second); pos_.erase(it); }   // O(1): an iterator is a handle
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| a dangling iterator/pointer after `erase`: undefined behaviour, often "works" until it doesn't | stale handle → `None` |
| free list threaded through the freed nodes themselves (`struct free_node { struct free_node *next; }`) | `Vec<usize>` of free indices (a separate stack) |
| `malloc`/`free` per node | one `Vec`, grown rarely; nodes are recycled |
| generation counters are what `slotmap`, entity-component systems and Vulkan handles use | `generation: u32` per node |

**Port rule:** any C/C++ API that returns a "pointer into a container" and says "valid until the element is erased" becomes a handle that is *checked* when used.

### Learn more
- [The ABA problem](https://en.wikipedia.org/wiki/ABA_problem) · [`slotmap`](https://docs.rs/slotmap)
- C++ [`std::list::erase`](https://en.cppreference.com/w/cpp/container/list/erase) · [`Vec::swap_remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.swap_remove) (the other way to remove from an arena)

## Part 2 · IndexList::move_to_back

**Where this fits.** "Most recently used" means moving an element to the back each time it is touched. The ARC replacer will do it constantly.

### The task

Implement `move_to_back(handle) -> bool` in `src/common/index_list.rs`: if the handle is live, relink its node after the tail **without freeing it** (its handle must stay valid) and return `true`; if it is already the tail, change nothing and return `true`; for a stale handle return `false`.

### Tests

- Head, a middle element and the tail each move correctly (`[1,2,3,4]` → `[2,3,4,1]`, `[1,3,4,2]`, unchanged). A one-element list is fine.
- The handle still works afterwards (`get`, `remove`). A stale handle gives `false` and changes nothing.
- 2000 random moves over 50 elements agree with a `VecDeque` model; popping the whole list afterwards visits all 50 (the links are intact).

### Syntax and methods

```rust
let Some(index) = self.index_of(handle) else { return false };   // let-else
if self.tail == Some(index) { return true; }                     // Option<usize> compares with ==
```

### Notes

Moving is *detach, then attach after the tail*: the same neighbour-joining as `unlink` (without the free-list and generation bookkeeping), then the same linking as `push_back`. Reuse by copying the shapes; resist rewriting it as `remove` + `push_back`, which would give the element a new handle and force every caller to update its map.

### In BusTub

```cpp
lru_list_.splice(lru_list_.end(), lru_list_, it->second);   // O(1) move of one node to the end, iterator stays valid
```

### The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::list::splice(pos, other, it)`: relinks one node, no allocation, iterators stay valid | `move_to_back`: relink by index, handle stays valid |
| `std::rotate`, `std::move_backward` on a vector: O(n) | `Vec::remove` + `push`: O(n); `VecDeque::rotate_*` also O(n) |
| doubly linked list manipulation with raw pointers: four pointer writes, easy to get one wrong | the same four writes, on indices, and a model test to catch the wrong one |

**Port rule:** `splice` is the reason BusTub's replacers use `std::list`. If you see `splice`, you need an O(1) relink: an index list (or `slotmap` + manual links).

### Learn more
- C++ [`std::list::splice`](https://en.cppreference.com/w/cpp/container/list/splice) · [`VecDeque`](https://doc.rust-lang.org/std/collections/struct.VecDeque.html) (what to use when you don't need handles)
