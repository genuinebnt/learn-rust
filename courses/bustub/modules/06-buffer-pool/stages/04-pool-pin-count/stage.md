**Where this fits.** Most fetches hit: the page is already in memory.

## The task

In `src/buffer/buffer_pool_manager.rs`:
- in `fetch_page`, when the page is **already resident**: add one pin, tell the replacer about the access, keep it non-evictable, return its frame. **No disk read.**
- `get_pin_count(page_id) -> Option<usize>`: the page's pin count, or `None` if it isn't in memory.

## Tests

- A page not in memory has no pin count; a fetched page has 1; fetched twice, 2 and the same frame, with only one disk read.
- Pin counts are per page. An unsaved change to a resident page is still there after another fetch.

## Syntax and methods

```rust
if let Some(&frame) = inner.page_table.get(&page_id) { /* copy the FrameId out of the reference */ }
inner.meta[frame.0].pin_count += 1;
let frame = inner.page_table.get(&page_id)?;     // in get_pin_count: `?` returns None when absent
```

## Notes

A pin count is a **reference count with a different job**: it doesn't free anything when it reaches zero; it makes the frame *eligible* for eviction. When you see `Arc::strong_count` and a pin count side by side you are looking at the same idea, one managed by the compiler and one by you.

## In BusTub

```cpp
auto BufferPoolManager::GetPinCount(page_id_t page_id) -> std::optional<size_t>   // nullopt if the page is not in the pool
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::optional<size_t>` | `Option<usize>` |
| `std::atomic<size_t> pin_count_` in `FrameHeader` (read without the pool latch by guards) | a plain `usize` inside `Mutex<Inner>`: guards go through the lock |
| `if (page_table_.find(id) != page_table_.end())` then `page_table_[id]` (two lookups) | `if let Some(&frame) = page_table.get(&id)` (one) |

## Learn more
- [`Option::?`](https://doc.rust-lang.org/book/ch09-02-recoverable-errors-with-result.html#a-shortcut-for-propagating-errors-the--operator) · *The Internals of PostgreSQL*, [buffer descriptors and refcount](https://www.interdb.jp/pg/pgsql08.html)
