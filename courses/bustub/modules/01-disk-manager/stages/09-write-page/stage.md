**Where this fits.** Callers know pages by id (`PageId(1000)`); the file is slots. The page table connects them.

## The task

`DbIo::pages: HashMap<PageId, usize>` maps a page id to its slot. Implement `write_page(page_id, data)` in `src/storage/disk/disk_manager.rs` (the invalid-id check is given):

- if the page has a slot, overwrite that slot;
- otherwise get a fresh slot from `io.allocate_slot()`, **remember it in the page table**, then write.

## Tests

- Pages 1000 then 3 get slots 0 then 1 (ids needn't be dense): `slot_of` says so.
- Rewriting a page keeps its slot; the next fresh slot is still the next one.
- Each page's bytes are in the file at its slot's offset.
- `PageId::INVALID` panics (given code).

## Syntax and methods

```rust
io.pages.get(&id)               // Option<&usize>
io.pages.insert(id, slot);      // Option<usize>: the old value, if there was one
match io.pages.get(&id) {
    Some(&slot) => slot,        // `&slot` copies the usize out of the reference
    None => { /* you need io.allocate_slot()? here */ }
}
write_slot(&io.file, slot, data)?;
```

## Notes

**The borrow trap.** `io.pages.get(&id)` borrows `io.pages`; `io.allocate_slot()` needs `&mut io`. If the shared borrow is still alive in the `None` arm, the compiler refuses. Matching `Some(&slot)` copies the number out, so the borrow ends. If you hit E0502, copy first: `let found = io.pages.get(&id).copied();`.

## In BusTub

```cpp
if (pages_.find(page_id) != pages_.end()) { offset = pages_[page_id]; }   // exists: overwrite in place
else { offset = AllocatePage(); }                                           // new: take a slot
...
pages_[page_id] = offset;
```

## The C/C++ way
| C++ (`std::unordered_map`) | Rust (`HashMap`) |
|---|---|
| `m.find(k) != m.end()` | `m.contains_key(&k)` / `m.get(&k).is_some()` |
| `m[k]` **inserts a default value** if `k` is missing; `m.at(k)` throws | `m[&k]` panics if missing; `m.get(&k)` → `Option<&V>`; nothing is inserted unless you say so |
| `m[k] = v;` / `m.emplace(k, v)` / `m.insert({k, v})` | `m.insert(k, v)` returns the old value; `m.entry(k).or_insert(v)` |
| iterator invalidation: inserting while holding an iterator or reference is **undefined behaviour** | the borrow checker rejects it (the "borrow trap" in this stage's notes) |
| `size_t offset = pages_[page_id];` copies a value out | `let slot = *io.pages.get(&id)?` or `Some(&slot)`: copy out so the borrow ends |

**Pitfall in the C++:** `pages_[page_id]` on a missing key quietly creates an entry with offset `0`, a classic source of "phantom page 0" bugs.

## Learn more
- [`HashMap`](https://doc.rust-lang.org/std/collections/struct.HashMap.html) · [`Option::copied`](https://doc.rust-lang.org/std/option/enum.Option.html#method.copied)
- The Rust Book: [references and borrowing](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html)
