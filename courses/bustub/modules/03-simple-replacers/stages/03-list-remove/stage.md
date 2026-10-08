**Where this fits.** Pinning a frame takes it out of the middle of the line.

## The task

In `src/common/index_list.rs`:
- `remove(handle)`: if the handle still names a live element (`index_of` checks index, generation and that the slot is occupied), unlink it and return the value; otherwise `None`;
- `push_back`: **reuse a freed slot** (from the free list) before growing the `Vec`. A reused node keeps its bumped generation, so handles issued before the reuse stay stale.

## Tests

- Remove from the head, middle and tail; the list stays linked. Removing twice gives `None`.
- After `remove(a)` and a new push (which takes `a`'s slot), `get(a)` is `None`, `remove(a)` is `None`, and the new element is untouched.
- 1000 push-then-remove rounds don't break anything; a model test of 3000 random pushes and removes agrees with a `Vec`.

## Syntax and methods

```rust
let index = self.index_of(handle)?;        // given: Option<usize>, None for a stale or foreign handle
Some(self.unlink(index))
if let Some(free) = self.free.pop() { node.generation = self.nodes[free].generation; self.nodes[free] = node; }
```

## Notes

This is the **ABA problem** in miniature: a handle that names slot 4, then slot 4 is freed and reused for something else; the old handle now points at the wrong element. A generation turns "same index" into "same index *and* same lifetime". Real arenas (`slotmap`, `generational-arena`) do exactly this; C++ programs usually have the bug.

## In BusTub

```cpp
auto it = pos_.find(frame_id);
if (it != pos_.end()) { lru_list_.erase(it->second); pos_.erase(it); }   // O(1): an iterator is a handle
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a dangling iterator/pointer after `erase`: undefined behaviour, often "works" until it doesn't | stale handle → `None` |
| free list threaded through the freed nodes themselves (`struct free_node { struct free_node *next; }`) | `Vec<usize>` of free indices (a separate stack) |
| `malloc`/`free` per node | one `Vec`, grown rarely; nodes are recycled |
| generation counters are what `slotmap`, entity-component systems and Vulkan handles use | `generation: u32` per node |

**Port rule:** any C/C++ API that returns a "pointer into a container" and says "valid until the element is erased" becomes a handle that is *checked* when used.

## Learn more
- [The ABA problem](https://en.wikipedia.org/wiki/ABA_problem) · [`slotmap`](https://docs.rs/slotmap)
- C++ [`std::list::erase`](https://en.cppreference.com/w/cpp/container/list/erase) · [`Vec::swap_remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.swap_remove) (the other way to remove from an arena)
