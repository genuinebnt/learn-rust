A table on disk is, in BusTub, the simplest structure that could work: a **linked list of table pages** in the buffer pool. Insert a tuple at the end; when the last page is full, allocate a page and link it after; find a tuple by its record id `(page, slot)`. This stage creates the heap and writes `insert_tuple`, which is where everything from the previous modules meets: the buffer pool's guards, the slotted page's free-space check and the page chain.

**Where this fits.** `TableHeap` is what every executor (module 3b) reads and writes. It is deliberately naive: no free-space map, no reuse of the space of deleted tuples, a lock around every insert. Real systems add those; the interface stays the same.

## The task

In `src/storage/table/table_heap.rs` (the struct is given: the pool, the first page id and a `Mutex<PageId>` holding the last page id):
- `TableHeap::new(bpm)`: allocate the first page (`bpm.new_page()`), format it as a table page (`TablePage::init`) and remember it as both first and last page;
- `insert_tuple(meta, tuple) -> Result<Rid>`:

  `insert_tuple` appends to the last page, and two inserters must not both extend the table (take the heap's lock and write-latch the **last** page). A tuple that does not fit moves on to a freshly allocated, formatted page that is linked from the old one and becomes the last. A tuple that does not fit even in an **empty** page is an error ("tuple is too large, cannot insert"), since no page ever will. The result is `Rid(page_id, slot)`.

> [!ASIDE] The steps, if you would rather not work them out
> 1. take the heap's lock (inserts are one at a time: two inserters could both extend the table) and write-latch the **last** page;
> 2. while the tuple does not fit (`get_next_tuple_offset` is `None`): if the page holds **no tuples**, no page ever will, so return an error ("tuple is too large, cannot insert"); otherwise allocate a new page, link it from this one (`set_next_page_id`), format it, make it the last page, and continue with its guard;
> 3. insert into the page and return `Rid(page_id, slot)`.

## Tests

- A new heap has a formatted, empty first page (not zeros); inserted tuples get consecutive slots of the first page, with their metadata stored.
- 66 tuples fill a page; the 67th starts a second page, linked from the first, slots restarting at 0; a tuple bigger than an empty page is an error and the heap still works afterwards; a tuple that does not fit the rest of the page goes to a new page.
- 5,000 tuples in a pool of 50 frames get distinct rids and read back; four threads inserting at once never share a slot.

## Syntax and methods

```rust
let mut last = self.last_page_id.lock().unwrap();              // MutexGuard<PageId>: the lock is held until it is dropped
let mut page_guard = self.bpm.write_page(*last);
let mut page = TablePage::new(&mut page_guard[..]);            // a view over the guard's bytes
let next = self.bpm.new_page();
page.set_next_page_id(Some(next));
*last = next;
page_guard = self.bpm.write_page(next);                        // assigning a guard drops (unlatches) the previous one
```

## Notes

**Why a lock *and* a page latch.** The page latch protects the bytes of one page; the heap's `Mutex` protects "which page is last". Without it, two threads could both find the last page full, both allocate a successor and link two different pages after the same one, losing one chain of tuples.

**The order of the latches.** The new page is latched *before* the old one is released, so no other thread can find the new page empty and slip in front. With one lock around all inserts there is nothing to deadlock on; BusTub's comment says exactly this: "only allow one insertion at a time; otherwise, it will deadlock."

**Too large is a property of the page, not of this attempt.** A tuple that does not fit a *non-empty* page might fit a fresh one; one that does not fit an *empty* page fits nowhere. That is the test for the error. (BusTub's tuples are bounded by the page size; storing big values across pages, as PostgreSQL does with TOAST, is out of scope.)

**Rids are stable.** A rid is `(page, slot)` and, as module 3b showed, tuples never move within a page, so the rid returned here is a valid address for as long as the table lives.

## In BusTub

`table_heap.cpp`: `TableHeap::TableHeap(BufferPoolManager *bpm)` ("first_page_id_ = bpm->NewPage(); last_page_id_ = first_page_id_; ... first_page->Init();") and `InsertTuple` ("if there's no tuple in the page, and we can't insert the tuple, then this tuple is too large. BUSTUB_ENSURE(page->GetNumTuples() != 0, "tuple is too large, cannot insert");").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::unique_lock<std::mutex> guard(latch_);` | `let mut last = self.last_page_id.lock().unwrap();` (the mutex *holds* the data it protects) |
| `page_guard = std::move(next_page_guard);` | `page_guard = next_guard;` (a move; the old guard drops) |
| `BUSTUB_ENSURE(cond, msg)` (throws) | `return Err(Exception::new(..))` |
| `std::optional<RID>` | `Result<Rid>` (an error for "too large", no `None`) |

**Port rule:** a mutex that guards a variable becomes `Mutex<T>` owning that variable: you cannot touch the variable without the lock.

## Learn more
- [`Mutex`](https://doc.rust-lang.org/std/sync/struct.Mutex.html) · [Heap file organisation](https://en.wikipedia.org/wiki/Heap_(data_structure)) is a different "heap"; for the database one see PostgreSQL's [free space map](https://www.postgresql.org/docs/current/storage-fsm.html) · [`Result`](https://doc.rust-lang.org/std/result/index.html)

## Performance

An insert latches the last page (already in the pool: the last page was just written) and costs `O(1)` plus the tuple copy; a page transition allocates a page, which costs a buffer-pool operation. The heap's lock serialises every insert, so insert throughput does not grow with threads: BusTub accepts that, and a production system would let different threads fill different pages. Because a tuple only ever goes to the *last* page, earlier pages never get new tuples: the space of deleted tuples is never reused.

**Measure it.** Insert 1,000,000 tuples from 1 and 4 threads and compare the rates; then insert tuples of 10, 100 and 1,000 bytes and print pages used.

## Hints

### Hold the lock for the whole insert

The loop reads and may change `last_page_id`; the rid you return names it. Take the lock first and let it drop after you have the slot.

### Which page is "the page that is too small"?

The check for "no tuples" applies to the page you currently hold *after* a failed fit. If it has no tuples, stop with the error; if it has some, a new empty page is worth trying. After allocating, the loop checks the new page too (it will fit unless the tuple is too big, which the next iteration reports).

### Initialise the new page

`new_page()` gives zeros; zeros say "page 0 is my next page". `TablePage::init` writes the invalid next-page id and zero counts. Forgetting it makes a chain loop back to page 0.
