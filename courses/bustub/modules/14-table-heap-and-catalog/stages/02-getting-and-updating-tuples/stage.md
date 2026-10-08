The other half of the heap's interface: read a tuple by its rid, read just its metadata, change the metadata (mark it deleted), and overwrite a tuple in place under a caller's condition. Each is "latch the right page, call the page function". The interest is in *which latch* and in what happens to errors.

## The task

In `src/storage/table/table_heap.rs`:
- `get_tuple(rid) -> Result<(TupleMeta, Tuple)>`: **read**-latch the rid's page and read the slot; the tuple carries its rid;
- `get_tuple_meta(rid) -> Result<TupleMeta>`;
- `update_tuple_meta(meta, rid) -> Result<()>`: **write**-latch the page and replace the slot's metadata;
- `update_tuple_in_place(meta, tuple, rid, check: Option<&dyn Fn(&TupleMeta, &Tuple, Rid) -> bool>) -> Result<bool>`: write-latch the page, read the old tuple, and if there is no check or the check says yes, overwrite the tuple and its metadata and return `true`; otherwise `false` and change nothing. The tuple must have the old tuple's length (an error otherwise).

An out-of-range slot (or a page that is not part of the table) is an `Err`, never a panic.

## Tests

- A tuple and its meta by rid; marking deleted changes only the meta; bad slots are errors for all four functions.
- The check runs against the *old* tuple, meta and rid: a refusing check changes nothing, an approving one updates, and the same check can approve once and refuse the next time; a wrong length is an error; 2,000 tuples across many pages are all found by rid.

## Syntax and methods

```rust
let guard = self.bpm.read_page(rid.page_id());                  // shared latch: many readers at once
TablePage::new(&guard[..]).get_tuple(rid)
let mut guard = self.bpm.write_page(rid.page_id());             // exclusive latch
check.map_or(true, |check| check(&old_meta, &old_tuple, rid))   // Option<&dyn Fn> : "no check" means yes
```

## Notes

**Reader or writer?** A read latch lets any number of threads read the same page at once; a write latch excludes everyone. `get_tuple` takes the cheaper one; the updates take the exclusive one for the whole read-check-write, which is what makes the check meaningful: nothing can change the tuple between the check and the write.

**Why `get_tuple` returns the meta *and* the tuple.** Reading them in two calls would take two latches, and a writer could change the meta in between (a tuple deleted after you read its bytes). One call, one latch: a consistent pair. BusTub's header says the same: "if you want to get tuple and meta together, use `GetTuple` instead to ensure atomicity."

**The check is a closure.** `Option<&dyn Fn(...) -> bool>` lets a caller pass "update only if the tuple has not been touched since I read it" (module 4 uses this for write-write conflict detection). A closure that captures what it needs replaces C++'s `std::function` argument.

**In-place update is not used in this project.** BusTub's own comment: "Should NOT be used in project 3. Implement your project 3 update executor as delete and insert." It exists for module 4's multi-version tuples.

## In BusTub

`table_heap.cpp`: `GetTuple` ("auto page_guard = bpm_->ReadPage(rid.GetPageId()); auto page = page_guard.As<TablePage>(); auto [meta, tuple] = page->GetTuple(rid); tuple.rid_ = rid;"), `UpdateTupleMeta` and `UpdateTupleInPlace` ("if (check == nullptr || check(old_meta, old_tup, rid)) { page->UpdateTupleInPlaceUnsafe(meta, tuple, rid); return true; } return false;").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::function<bool(const TupleMeta &, const Tuple &, RID)> &&check = nullptr` | `Option<&dyn Fn(&TupleMeta, &Tuple, Rid) -> bool>` |
| `page_guard.As<TablePage>()` (a reinterpret cast of the page) | `TablePage::new(&guard[..])` (a view) |
| `std::pair<TupleMeta, Tuple>` | `(TupleMeta, Tuple)` |

**Port rule:** a nullable callback becomes `Option<&dyn Fn..>` (or a generic `impl Fn`); `nullptr` is `None`.

## Learn more
- [`Option::map_or`](https://doc.rust-lang.org/std/option/enum.Option.html#method.map_or) · [Closures](https://doc.rust-lang.org/book/ch13-01-closures.html) · [`RwLock`](https://doc.rust-lang.org/std/sync/struct.RwLock.html) (what a page latch is)

## Performance

Each call is one latch acquisition (shared for reads) and an `O(1)` slot lookup, plus the tuple copy for `get_tuple`. A page already in the pool costs tens of nanoseconds; a page that must be fetched from disk costs a disk read, which dominates everything: scans (next stage) therefore visit pages in order so each is fetched once. `get_tuple_meta` is cheaper than `get_tuple` (no copy): a scan that checks `is_deleted` first and reads only live tuples saves the copy for dead ones.

**Measure it.** Read 10 million random rids from a table that fits the pool and from one that does not; the ratio is the cost of a buffer pool miss.

## Hints

### Errors come for free

The page functions already return `Err` for a slot out of range; if you return their `Result` unchanged, the "bad rid" tests pass. A rid naming a page that is not in the table gives a zero page: its `num_tuples` is 0, so every slot is out of range too.

### Do the check while you hold the latch

Read the old tuple through the same write guard you will write through; do not drop it and re-latch between the check and the write.

### `None` means yes

`check.map_or(true, |c| c(&old_meta, &old_tuple, rid))`: no check, always update.
