**Where this fits.** When the pool is full and a new page is needed, the replacer names the frame to throw out.

## The task

Implement `victim()` in `src/buffer/lru_replacer.rs`: remove and return the frame at the **front** of the list (the one unpinned longest ago), forgetting its handle; `None` if the replacer is empty.

## Tests

- Unpin 3, 1, 2: victims come out 3, 1, 2, then `None`. A victim leaves the replacer (`size` shrinks).
- Unpinning a frame that is already there does **not** refresh it: unpin 1, 2, 1, and 1 is still the first victim.
- A victim can be unpinned again and then goes to the back.

## Syntax and methods

```rust
let frame = self.list.pop_front()?;      // `?`: return None if the list is empty
self.handles.remove(&frame);
Some(frame)
```

## Notes

The map and the list must be kept in step: every frame in one is in the other. Whenever you add a second place that remembers something, ask which operations have to update both. (A pattern that comes back in the buffer pool: the page table and the replacer.)

## In BusTub

```cpp
auto LRUReplacer::Victim(frame_id_t *frame_id) -> bool {
  if (lru_list_.empty()) { return false; }
  *frame_id = lru_list_.front();  lru_list_.pop_front();  pos_.erase(*frame_id);  return true;
}
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `*frame_id = lru_list_.front(); ... return true;` | `Some(frame)` |
| `if (lru_list_.empty()) return false;` guard before `front()` (UB otherwise) | `pop_front()?` |
| two containers to keep in step by discipline | the same, but the types make you write each update |

## Learn more
- LRU in practice: PostgreSQL uses a clock sweep instead ([`freelist.c`](https://github.com/postgres/postgres/blob/master/src/backend/storage/buffer/freelist.c)) because exact LRU needs a lock on every access · [crate `lru`](https://docs.rs/lru) is the ready-made cache
