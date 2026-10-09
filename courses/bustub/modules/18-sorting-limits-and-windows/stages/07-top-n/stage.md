`order by score desc limit 10` is the most common use of sorting. The obvious plan is `Limit ← Sort ← Scan`: sort everything, return ten rows. A **top-N** executor does it in one pass with memory for ten rows: keep the best ten seen so far in a heap, and for each new row compare it with the worst of the ten. BusTub's optimizer rewrites `Limit(Sort(x))` to `TopN(x)` (that rule is yours in module 3h); here you write the executor and test it with plans built by hand.

## The task

In `src/execution/executors/topn_executor.rs` (`HeapEntry`, a wrapper whose `Ord` makes the **worst** kept tuple the greatest, `new`, `get_num_in_heap` and the check executor are given):
- `init`: initialise the child; read all its batches; for each tuple make its sort key (`generate_sort_key`) and a `HeapEntry { entry: (key, tuple), seq, cmp }` (`seq` counts arrivals); push it while the heap holds fewer than `n`; otherwise, if the new entry is smaller than the heap's greatest (`heap.peek()`), pop that one and push the new one. After each tuple store `heap.len()` in `self.num_in_heap`. At the end pop the heap into `self.result` in **output order** (best first). An `n` of 0 reads nothing;
- `next`: hand out the next at most `batch_size` tuples of `self.result` (a default rid with each).

## Tests

- The best 3 of 7 rows, descending and ascending; `n` larger than the input returns everything sorted; `n = 0` and an empty table return nothing.
- Ties keep the **earlier** rows (five rows with `a = 1`, `n = 3` gives tags 0, 1, 2 after the single 0).
- Several keys with NULLs; 5,000 rows against a reference sort.
- After `init` the heap holds exactly `n` tuples (`get_num_in_heap() == 7`); the `+ensure:topn` check, which asserts that the heap never exceeds `n`, passes.
- The executor can be initialised again.

## Syntax and methods

```rust
let mut heap: BinaryHeap<HeapEntry> = BinaryHeap::new();         // a max-heap: the greatest = the worst kept
heap.push(e);  heap.pop();  heap.peek();  heap.len();
candidate < *worst                                               // HeapEntry: PartialOrd, comes from Ord
while let Some(e) = heap.pop() { best.push(e.entry.1); }  best.reverse();
```

## Notes

**Why the worst is the greatest.** The heap must give the *worst* kept row cheaply, to decide whether a newcomer beats it. `HeapEntry`'s `Ord` is the query's order (so "greater" means "comes later in the output") with ties broken by arrival: a later arrival is greater. The greatest element is then the row to evict, and among equal rows the latest arrival goes first, so earlier rows win ties.

**Bounded.** The heap never holds more than `n` entries, so the memory is `n` tuples whatever the input. The check executor (`TopNCheckExecutor`, wrapped around the child by the factory when a test says `+ensure:topn`) asserts this on every pull; a sort-then-limit implementation would fail it.

**Pop order.** `BinaryHeap::pop` returns the greatest first, i.e. the worst of the best, so popping everything gives the output *reversed*; reverse it once at the end.

**Why materialise in `init`.** The answer cannot be known before the last input row, so top-N is blocking, like sort; `init` does the work and `next` hands out the result.

## In BusTub

`topn_executor.h` (`TopNExecutor` with `GetNumInHeap()` and `SetChildExecutor`), `topn_check_executor.cpp` ("`BUSTUB_ASSERT(topn_executor_->GetNumInHeap() <= plan_->GetN(), "Cannot store more than N elements");`"), `sort_limit_as_topn.cpp` (the rule, a stub), and `p3.17-topn.slt` (`+ensure:topn`).

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::priority_queue<SortEntry, std::vector<SortEntry>, TupleComparator>` | `BinaryHeap<HeapEntry>` where `HeapEntry: Ord` calls the comparator |
| `pq.top()`, `pq.pop()`, `pq.push()` | `heap.peek()`, `heap.pop()`, `heap.push()` |
| a `TupleComparator` object that the queue copies | an `Rc<TupleComparator>` shared by the entries |
| `GetNumInHeap()` read through a pointer by the check executor | an `Arc<AtomicUsize>` both executors share |

**Port rule:** a priority queue with a runtime comparator is a `BinaryHeap` of a wrapper type whose `Ord` calls it.

## Learn more
- [`BinaryHeap`](https://doc.rust-lang.org/std/collections/struct.BinaryHeap.html) · [`Reverse`](https://doc.rust-lang.org/std/cmp/struct.Reverse.html) · PostgreSQL [top-N heapsort](https://www.postgresql.org/docs/current/using-explain.html)

## Performance

`O(rows · log n)` time and `O(n)` memory against the sort's `O(rows · log rows)` and `O(rows)`. For `n = 10` the heap operations are trivial and the cost is reading and evaluating the keys. Most rows are rejected by one comparison with the worst kept row.

**Measure it.** `order by a desc limit 10` over 1,000,000 rows as a hand-built `TopN` and as `Limit ← Sort`: compare time and peak memory.

## Hints

### Compare before you push

When the heap is full, compare the candidate with `peek()` first. Pushing then popping works but does a log-n operation for every row, most of which lose.

### Ties

A candidate equal to the worst kept entry is *not* better: it arrived later, so `HeapEntry`'s ordering already says it is greater. `candidate < *worst` is false and the candidate is dropped.

### Update the counter inside the loop

The check reads `num_in_heap` between pulls from the child. Store it after every tuple (or at least every batch), not once at the end.
