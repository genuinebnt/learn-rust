**Where this fits.** The reason the pool exists: more pages than frames.

## The task

In `fetch_page` (`src/buffer/buffer_pool_manager.rs`), when the page is not in memory and there is **no free frame**, ask the replacer for a victim. If there is none (every frame is pinned), return `None`. Otherwise forget the victim page (remove it from the page table, clear the frame's metadata) and reuse its frame for the new page exactly as in stage 3.

## Tests

- A full pool of pinned pages refuses another (`None`, and the page is not resident).
- Unpin one and the fetch succeeds; the unpinned page is gone, the pinned ones stay.
- Pinned pages are never the victim. The replacer decides: **least recently accessed first** (not least recently unpinned), and a page accessed twice outlives one accessed once (ARC).
- Clean victims cost no disk writes.

## Syntax and methods

```rust
let frame = inner.replacer.evict()?;                                  // None if nothing is evictable: the fetch fails
let old_page = inner.meta[frame.0].page_id.take().expect("an evicted frame holds a page");
inner.page_table.remove(&old_page);
```

## Notes

**Who is in charge of what.** The replacer says *which*; the pool does the *bookkeeping* around it (page table, metadata). Keep the replacer ignorant of pins and disks: its entire interface is "access / evictable / evict / remove". Everything the pool must remember to undo when it takes a frame back is the list above, and the next stage adds one more item (write the page if it is dirty). When code has a to-do list like this, put it in **one function**.

## In BusTub

```cpp
frame_id_t fid;
if (!free_frames_.empty()) { fid = free_frames_.front(); free_frames_.pop_front(); }
else { auto victim = replacer_->Evict();  if (!victim.has_value()) { return std::nullopt; }  fid = *victim;  /* flush if dirty; erase from page_table_ */ }
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto victim = replacer_->Evict(); if (!victim.has_value()) return std::nullopt; fid = *victim;` | `let frame = inner.replacer.evict()?;` |
| `page_table_.erase(page_id)` | `page_table.remove(&page_id)` |
| `*victim` on an empty optional: undefined behaviour | `?` / `expect` / `match` |
| "the page that was in the frame": looked up by scanning `page_table_` for `fid` (O(n)) | stored in `FrameMeta.page_id` (O(1)), as BusTub's own comment suggests |

## Learn more
- [`Option::take`](https://doc.rust-lang.org/std/option/enum.Option.html#method.take) · CMU 15-445 "Memory Management": eviction, pinning, dirty pages · *PostgreSQL buffer manager*, [README](https://github.com/postgres/postgres/blob/master/src/backend/storage/buffer/README)
