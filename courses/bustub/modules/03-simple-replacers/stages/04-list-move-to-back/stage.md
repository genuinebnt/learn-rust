**Where this fits.** "Most recently used" means moving an element to the back each time it is touched. The ARC replacer will do it constantly.

## The task

Implement `move_to_back(handle) -> bool` in `src/common/index_list.rs`: if the handle is live, relink its node after the tail **without freeing it** (its handle must stay valid) and return `true`; if it is already the tail, change nothing and return `true`; for a stale handle return `false`.

## Tests

- Head, a middle element and the tail each move correctly (`[1,2,3,4]` → `[2,3,4,1]`, `[1,3,4,2]`, unchanged). A one-element list is fine.
- The handle still works afterwards (`get`, `remove`). A stale handle gives `false` and changes nothing.
- 2000 random moves over 50 elements agree with a `VecDeque` model; popping the whole list afterwards visits all 50 (the links are intact).

## Syntax and methods

```rust
let Some(index) = self.index_of(handle) else { return false };   // let-else
if self.tail == Some(index) { return true; }                     // Option<usize> compares with ==
```

## Notes

Moving is *detach, then attach after the tail*: the same neighbour-joining as `unlink` (without the free-list and generation bookkeeping), then the same linking as `push_back`. Reuse by copying the shapes; resist rewriting it as `remove` + `push_back`, which would give the element a new handle and force every caller to update its map.

## In BusTub

```cpp
lru_list_.splice(lru_list_.end(), lru_list_, it->second);   // O(1) move of one node to the end, iterator stays valid
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::list::splice(pos, other, it)`: relinks one node, no allocation, iterators stay valid | `move_to_back`: relink by index, handle stays valid |
| `std::rotate`, `std::move_backward` on a vector: O(n) | `Vec::remove` + `push`: O(n); `VecDeque::rotate_*` also O(n) |
| doubly linked list manipulation with raw pointers: four pointer writes, easy to get one wrong | the same four writes, on indices, and a model test to catch the wrong one |

**Port rule:** `splice` is the reason BusTub's replacers use `std::list`. If you see `splice`, you need an O(1) relink: an index list (or `slotmap` + manual links).

## Learn more
- C++ [`std::list::splice`](https://en.cppreference.com/w/cpp/container/list/splice) · [`VecDeque`](https://doc.rust-lang.org/std/collections/struct.VecDeque.html) (what to use when you don't need handles)
