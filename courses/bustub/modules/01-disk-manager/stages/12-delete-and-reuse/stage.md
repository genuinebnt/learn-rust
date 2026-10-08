**Where this fits.** Pages get deleted. Their slots must not be lost, or the file grows forever.

## The task

In `src/storage/disk/disk_manager.rs`:
- `delete_page(page_id)`: remove the page from the page table and push its slot onto `free_slots`. If the page isn't there, do nothing (and free nothing).
- `DbIo::allocate_slot`: *before* anything else, try to reuse a freed slot (`free_slots.pop()`).

`free_slots` is used as a **stack**: the most recently freed slot is reused first.

## Tests

- A deleted page reads as zeros again, and has no slot.
- Delete pages 1 (slot 0) and 3 (slot 2); the next two new pages get slot 2, then slot 0, and only then a fresh slot.
- Deleting an unknown page, or the same page twice, frees at most one slot (a slot freed twice would be given to two pages).
- Writing 40 pages, deleting them all, and writing 40 others leaves the file size unchanged.

## Syntax and methods

```rust
let Some(slot) = io.pages.remove(&id) else { return; };   // let-else: bail out when remove() gives None
io.free_slots.push(slot);                                   // Vec as a stack
if let Some(slot) = self.free_slots.pop() { return Ok(slot); }
```

## Notes

The file never shrinks, it only stops growing; real systems return the space or reorganise (vacuum / compaction). This is why a freed page that is later read must come back as zeros, even though its old bytes are still in the slot until reused: `read_page` goes through the page table, and the deleted page isn't in it.

## In BusTub

```cpp
void DiskManager::DeletePage(page_id_t page_id) {
  std::scoped_lock scoped_db_io_latch(db_io_latch_);
  if (pages_.find(page_id) == pages_.end()) { return; }
  size_t offset = pages_[page_id];
  free_slots_.push_back(offset);
  pages_.erase(page_id);
  num_deletes_ += 1;
}
```

## The C/C++ way
| C++ | Rust |
|---|---|
| `v.push_back(x)` / `v.pop_back()` | `v.push(x)` / `v.pop()` → `Option<T>` |
| `v.back()` on an **empty** vector is undefined behaviour; `if (!v.empty()) { x = v.back(); v.pop_back(); }` | `if let Some(x) = v.pop()`: emptiness is a value you must handle |
| `m.erase(k)` returns how many were erased (0 or 1) | `m.remove(&k)` returns `Option<V>`: the removed value, so you get the slot back in one step |
| `if (m.find(k) == m.end()) return;` early exit | `let Some(slot) = m.remove(&k) else { return };` |
| a "free list" threaded through the freed objects themselves (C: `struct free_block { struct free_block *next; }`) | safe Rust keeps a `Vec<usize>` of indices; an intrusive list is a later module |

**Pitfall in the C++:** double free. Deleting a page twice pushes its slot twice, and two pages then share a slot. The `Option` from `remove` makes the second delete a no-op by construction.

## Learn more
- [`HashMap::remove`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.remove) · [let-else](https://doc.rust-lang.org/rust-by-example/flow_control/let_else.html)
