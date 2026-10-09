A sequential scan visits every tuple of a table: slot after slot, page after page along the chain. The iterator is a cursor holding a `Rid`; "next" is slot + 1, or slot 0 of the next page, or the end. That is simple. The subtle part is **when it ends**.

Consider `UPDATE t SET salary = salary * 2` implemented as "for each row: delete it and insert the updated row". The insert appends to the table; the scan, still running, finds the new row at the end and doubles it again, and again, forever. This is the **Halloween problem** (found, the story goes, on 31 October 1976, in IBM's System R). The fix BusTub uses: an iterator **records where the table ended when it started and stops there**.

> [!CHECK] An `UPDATE` appends the new version of each row at the end of the table (delete, then insert). A scan feeds it and simply walks to the end of the table. What happens to a row whose new value still passes the filter, and what does stopping at the table's end *when the scan began* change?
> ||The new version is found again at the end of the table, updated again, appended again, and so on: rows are updated more than once, or forever. Stopping at the rid that was last when the scan began means rows added during the scan are never visited.||
>
> - Where does the new version of the row end up?
> - Does the scan know the new version is not an original row?
> - What number could you remember when the scan starts?

## The task

In `src/storage/table/table_iterator.rs` and `table_heap.rs`:
- `TableIterator::new(heap, rid, stop_at_rid)`: remember them; if `rid` does not name an existing tuple (an empty table: slot 0 of a page with no tuples) the iterator starts **at the end** (a rid in an invalid page);
- `is_end()`, `get_rid()`, `get_tuple()` (an error at the end), and `advance()` (does nothing at the end): next slot of this page; if that equals `stop_at_rid` the iterator is at the end; else if the page has more tuples, stay; else move to slot 0 of the **next page**, or to the end if there is none;
- `impl Iterator`: `next()` returns the current `(TupleMeta, Tuple)` and advances;
- `TableHeap::make_iterator()`: start at `(first page, 0)`, stop at `(last page, the number of tuples that page has right now)`;
- `TableHeap::make_eager_iterator()`: start the same way with **no** stopping point (an invalid rid): it runs to the table's end whenever that is.

The iterator returns **every** tuple, deleted ones too, with their meta; filtering is the caller's (module 3b's `SeqScan`).

## Tests

- An empty table's iterators are at the end; a scan of 3,000 tuples returns them in insertion order with the rids that `insert` returned; a cursor can be driven by hand (`is_end`, `get_rid`, `advance`); deleted tuples come back with `is_deleted`.
- The snapshot iterator ignores tuples inserted while it runs (also when the stopping point is the very end of a full page); the eager one sees them.

## Syntax and methods

```rust
impl Iterator for TableIterator<'_> {
    type Item = (TupleMeta, Tuple);
    fn next(&mut self) -> Option<(TupleMeta, Tuple)> {
        if self.is_end() { return None; }
        let item = self.get_tuple().ok()?;
        self.advance();
        Some(item)
    }
}
pub struct TableIterator<'a> { heap: &'a TableHeap<'a>, rid: Rid, stop_at_rid: Rid }   // borrows the heap for 'a
```

## Notes

**The stopping point is a rid, not a count.** "Stop after N tuples" would be wrong if tuples were removed; "stop at this exact slot of this exact page" is stable because tuples never move. `make_iterator` reads the last page's tuple count under a latch and keeps `(last_page, count)`: the first rid that did not exist yet.

**The iterator borrows the heap.** `TableIterator<'a>` holds a reference to the `TableHeap` for the iterator's life; the compiler therefore forbids dropping or moving the heap while a scan is running. In C++ that is a convention (`TableHeap *table_heap_`) and a dangling-pointer bug if broken.

**No latch is held between steps.** Like module 2c's index iterator, each `get_tuple` and each `advance` latch a page briefly. Tuples can be added concurrently (that is what the stopping point guards against for the *same* statement); a concurrent writer's deletes are seen as flags.

**Eager is for tests.** BusTub provides `MakeEagerIterator` so that module 4's tests can check an update executor really is a pipeline breaker: if it were not, the eager scan would see the new versions.

## In BusTub

`table_heap.cpp` (`MakeIterator`: "When this iterator is created, it will record the current last tuple in the table heap, and the iterator will stop at that point, in order to avoid halloween problem.") and `table_iterator.cpp` (`operator++`: "if (rid_ == stop_at_rid_) { rid_ = RID{INVALID_PAGE_ID, 0}; } else if (next_tuple_id < page->GetNumTuples()) { // that's fine } else { auto next_page_id = page->GetNextPageId(); rid_ = RID{next_page_id, 0}; }").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `TableIterator` with `operator++`, `IsEnd()`, `GetTuple()`, `DISALLOW_COPY` | `advance`, `is_end`, `get_tuple`, plus `impl Iterator` so `for` loops work; no `Clone` |
| `TableHeap *table_heap_` (a raw pointer) | `&'a TableHeap<'a>` (a checked borrow) |
| `RID{INVALID_PAGE_ID, 0}` as "end" | the same, internally; `is_end()` hides it |

**Port rule:** an iterator holding a raw pointer to its container becomes a struct with a lifetime parameter borrowing it.

## Learn more
- [`Iterator`](https://doc.rust-lang.org/std/iter/trait.Iterator.html) · [Lifetimes in structs](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#lifetime-annotations-in-struct-definitions) · [Halloween Problem](https://en.wikipedia.org/wiki/Halloween_Problem)

## Performance

A scan latches each page once per tuple here (each `get_tuple` and `advance` is a short latch), `O(1)` per tuple plus the copy; the pages are read sequentially along the chain, which the buffer pool and the disk like (the next page is the next one allocated, so usually adjacent). The scan's cost is the page count, `tuples / tuples_per_page`, not the tuple count: a table of narrow tuples scans faster per tuple.

The snapshot costs one latch at creation. The eager iterator has no stopping point to check but can run forever against a writer that keeps inserting.

**Measure it.** Scan a million-tuple table and print tuples per second; then scan it from a second thread while the first inserts, with `make_iterator` and `make_eager_iterator`, and compare how many tuples each returns.

## Hints

### Think of the end as a rid

A rid in an invalid page is "the end". Everything that moves the cursor produces either a valid rid or that. `is_end` is then one comparison, and `get_tuple` at the end must be an error, not a read of page -1.

### Compare before you move on

After `slot + 1`, first check whether you reached the stopping rid, then whether the page has that slot, then take the next page. The order matters when the stopping point is slot 0 of the next page (a page boundary): the first check ends the scan before the next page is read.

### What does an empty table's first rid mean?

`(first page, 0)` names a tuple that does not exist: `num_tuples` is 0. The constructor checks that and starts at the end; otherwise the first `get_tuple` returns an out-of-range error.
