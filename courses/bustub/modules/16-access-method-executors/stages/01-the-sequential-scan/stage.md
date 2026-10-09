Until now every query ran on the built-in mock tables. A real table has to be *read from the buffer pool*, and that is the sequential scan's job: walk the table's pages in order and hand the rows upwards in batches. It is the first executor that talks to storage, and the first one with real state between calls: a cursor into the table.

Reading the rows is a loop over module 3c's table iterator. The new things here are the **batch protocol** (fill at most `batch_size` tuples per call, say `false` when there are none left), **skipping deleted rows** (the heap keeps a deleted tuple's slot, flagged), and **where the iterator lives** between calls.

## The task

In `src/execution/executors/seq_scan_executor.rs` (the struct, `new` and the `passes_filter` helper are given; until stage 2 `passes_filter` keeps everything):
- `init`: start a table iterator over the table with `make_iterator()` (the one that stops where the table ended when the scan began) and keep it in `self.iter`;
- `next`: replace the batch with the next up-to-`batch_size` rows: for each tuple the iterator gives, skip it if its metadata says `is_deleted`, otherwise keep it if `passes_filter(..)` says so; push the tuple and its rid; stop at `batch_size` or when the iterator is at the end. Return `true` if the batch is not empty.

## Tests

- An empty table produces no batch at all; a table of 1,000 rows comes back complete and in storage order.
- Batches are at most `batch_size` long and only the last is short (20/20/10, or 7s).
- The rids are the rows' rids; deleted rows are skipped.
- A row stored after `init` is not seen (the scan stops where the table ended); a second `init` starts over and sees it.
- `select * from t` and `select b, a + b from t` through SQL.

## Syntax and methods

```rust
self.iter = Some(self.table_info.table.make_iterator());          // TableIterator<'e>, borrowed from the catalog
let iter = self.iter.as_mut().expect("init is called before next"); // &mut TableIterator
while tuple_batch.len() < batch_size && !iter.is_end() {
    let (meta, tuple) = iter.get_tuple()?;     // (TupleMeta, Tuple)
    let rid = iter.get_rid();
    iter.advance();
}
```

## Notes

**The iterator stays in the struct.** The executor keeps `Option<TableIterator<'e>>`: `None` until `init`, then the cursor that survives from one `next` call to the next. The iterator borrows the table (`&'e TableHeap`), which is why the executor is generic over the lifetime `'e` of the query: it cannot outlive the catalog it reads. (The constructor, given, fetched `&'e TableInfo` with `Catalog::table_info`, which borrows from the catalog instead of cloning an `Arc`.)

**Advance before you decide.** Take the tuple and rid, advance the iterator, *then* decide whether to keep the row. If you only advance for kept rows, a skipped row is looked at forever.

**Deleted rows still occupy slots.** Module 3c's iterator returns every slot including the flagged ones; the scan hides them. That is how a delete (stage 5) can be a one-byte write.

**`make_iterator`, not `make_eager_iterator`.** An update (stage 6) inserts into the very table it scans. The iterator that stops where the table ended when it was created will not meet its own inserts; the eager one would (the Halloween problem).

## In BusTub

`seq_scan_executor.cpp` is a stub in BusTub (`void SeqScanExecutor::Init() { UNIMPLEMENTED("TODO(P3): Add implementation."); }`), with the contract in the comment: "Yield the next tuple batch from the seq scan. @param[out] tuple_batch The next tuple batch produced by the scan @param[out] rid_batch The next tuple RID batch produced by the scan @param batch_size The number of tuples to be included in the batch (default: BUSTUB_BATCH_SIZE) @return `true` if a tuple was produced, `false` if there are no more tuples".

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `TableHeap::MakeIterator()` returning `TableIterator` by value, stored in a `std::optional` or `unique_ptr` | `Option<TableIterator<'e>>` in the struct |
| `tuple_batch->push_back(tuple)` into an out-parameter | `tuple_batch.push(tuple)` on `&mut Vec<Tuple>` |
| `while (!iter->IsEnd()) { auto [meta, tuple] = iter->GetTuple(); ++(*iter); ... }` | the same with `is_end`, `get_tuple()?` and `advance()` |
| a missing `Init()` call is a null dereference | `.expect("init is called before next")` names the mistake |

**Port rule:** an iterator kept between calls becomes an `Option` field that `init` fills; borrow-from-the-owner lifetimes replace "the table outlives the executor, by convention".

## Learn more
- [`Option::as_mut`](https://doc.rust-lang.org/std/option/enum.Option.html#method.as_mut) · [Lifetimes in struct definitions](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html) · [BusTub's executor interface](https://github.com/cmu-db/bustub/blob/master/src/include/execution/executors/abstract_executor.h)

## Performance

A sequential scan reads each page once, in order: the cheapest way to read a lot of data, and the one the buffer pool's prefetching and the disk's read-ahead like best. Its cost is the table's size, whatever the query asks. Each row also costs a `Tuple` copy out of the page; the batch is a `Vec` reused by the caller, so clearing it each call does not allocate.

**Measure it.** Insert 100,000 rows and time `select * from t` with batch sizes 1, 20 and 1000 (`ExecutionEngine` uses 20; call the executor yourself to try others) to see what the batch size buys.

## Hints

### Do not forget to clear

The caller passes in the batch of the *previous* call. The given code clears both vectors at the top of `next`; if you push into non-empty vectors the caller sees old rows twice.

### Check the end *and* the size

The loop condition is both: stop when the batch is full *or* the iterator is at the end. A loop that only checks the size runs off the end of the table; one that only checks the end returns one giant batch.

### Return false only for an empty batch

If the last rows fill a batch exactly, return `true` now; the *next* call finds nothing and returns `false`. Returning `false` together with rows loses them.
