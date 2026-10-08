**Where this fits.** A frame in use must not be evicted: pinning takes it out of the replacer.

## The task

Implement `pin(frame)` in `src/buffer/lru_replacer.rs`: if the replacer holds the frame, remove it from the list and the map; otherwise do nothing. Everything must be **O(1)**.

## Tests

- A pinned frame is never a victim; pinning an unknown frame, or the same frame twice, changes nothing.
- Unpinning after a pin puts the frame at the back.
- **Speed:** 200,000 unpins, 100,000 pins, 50,000 more unpins and a drain of all victims finish in under 5 seconds (a `Vec`-and-`position` solution takes minutes).

## Syntax and methods

```rust
if let Some(handle) = self.handles.remove(&frame) {   // HashMap::remove returns the removed value
    self.list.remove(handle);
}
```

## Notes

The speed test is the reason for the index list: with a `VecDeque`, `pin` must search for the frame (`O(n)`), and a buffer pool of a million frames pins and unpins on every page access. "Fine for the tests" and "fine for 200,000 frames" are different requirements.

## In BusTub

```cpp
void LRUReplacer::Pin(frame_id_t frame_id) {
  auto it = pos_.find(frame_id);
  if (it == pos_.end()) { return; }
  lru_list_.erase(it->second);  pos_.erase(it);
}
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto it = m.find(k); if (it == m.end()) return; ... m.erase(it);` | `if let Some(h) = m.remove(&k) { ... }` (lookup and erase in one) |
| `std::find(v.begin(), v.end(), x)` on a vector: O(n) | `HashMap` for position, arena for order |
| complexity is a comment ("O(1) amortised") | complexity is a test (`Instant::now()` + an assertion) |

## Learn more
- [`HashMap::remove`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.remove) · Postgres' buffer manager README: [`storage/buffer/README`](https://github.com/postgres/postgres/blob/master/src/backend/storage/buffer/README) (pins, usage counts, the clock sweep)
