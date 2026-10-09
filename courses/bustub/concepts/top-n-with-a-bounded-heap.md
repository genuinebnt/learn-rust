---
title: Top-N with a bounded heap
summary: How ORDER BY ... LIMIT N avoids sorting everything: keep only the best N seen so far in a heap, evict the worst when a better one arrives, and why that bounds memory and time.
minutes: 7
---
`select * from t order by score desc limit 10` can be run as a full sort followed by a limit: sort a billion rows, throw away all but ten. Or it can be run as a **top-N**: scan the rows once and keep only the ten best seen so far. Memory is `N` rows, not a billion, and the time is `O(rows · log N)` instead of `O(rows · log rows)`.

## The bounded heap

Keep a heap of at most `N` rows ordered so that its **top is the worst of the N kept**. For each incoming row:

- fewer than `N` kept: push it;
- otherwise compare it with the worst kept: if the new row is better, pop the worst and push the new one; if not, drop the new row.

At the end the heap holds exactly the `N` best rows; pop them all (worst first) and reverse for the final order. Equal rows: the rule "keep the earlier one" matches what a stable sort followed by a limit returns.

```text
N = 3, descending by score:  stream 5 9 1 7 8
heap holds the 3 best so far; the top is the smallest of them
 5      → [5]
 9      → [5 9]
 1      → [1 5 9]
 7      → 7 > 1: evict 1  → [5 7 9]
 8      → 8 > 5: evict 5  → [7 8 9]
result:  9 8 7
```

## Why it needs a *max-heap of the worst*

To decide whether a new row belongs you only need the worst row you are keeping; a heap gives that in `O(1)` and replaces it in `O(log N)`. In a max-heap keyed by "badness" the top is the worst. Rust's `BinaryHeap` is a max-heap on `Ord`; to make the *worst under the query's order* the maximum, make the element's `Ord` the query's order itself ("greater = comes later in the output").

## N = 0, N larger than the input

`limit 0` returns nothing without reading anything. If `N` exceeds the number of rows the heap never fills and the result is the whole input, sorted.

## A check for the implementation

The test runner can verify that an implementation really is bounded (`+ensure:topn` turns on a check executor that asserts the heap never holds more than N rows). A sort-then-limit passes the result tests but fails that check; this is how BusTub keeps the cheat out.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::priority_queue<SortEntry, std::vector<SortEntry>, TupleComparator>` | `BinaryHeap<HeapEntry>` where `HeapEntry: Ord` calls the comparator |
| `heap.top()` and `heap.pop()` | `heap.peek()` and `heap.pop()` |
| a min-heap by flipping the comparator | `std::cmp::Reverse(x)` |
| `std::partial_sort` / `std::nth_element` | not needed: the heap is explicit |

## In real code

### Using it: the best N of a stream

```rust test
use std::collections::BinaryHeap;

/// The `n` largest values, largest first. Keeps at most `n` in memory.
fn top_n(stream: impl IntoIterator<Item = i32>, n: usize) -> (Vec<i32>, usize) {
    // a max-heap of Reverse(x) has the SMALLEST kept value on top
    let mut heap: BinaryHeap<std::cmp::Reverse<i32>> = BinaryHeap::new();
    let mut max_size = 0;
    if n == 0 {
        return (vec![], 0);
    }
    for x in stream {
        if heap.len() < n {
            heap.push(std::cmp::Reverse(x));
        } else if heap.peek().is_some_and(|worst| x > worst.0) {
            heap.pop();
            heap.push(std::cmp::Reverse(x));
        }
        max_size = max_size.max(heap.len());
    }
    let mut out: Vec<i32> = heap.into_iter().map(|r| r.0).collect();
    out.sort_by(|a, b| b.cmp(a));
    (out, max_size)
}

#[test]
fn keeps_the_best_n_in_order() {
    let (best, _) = top_n([5, 9, 1, 7, 8], 3);
    assert_eq!(best, vec![9, 8, 7]);
}

#[test]
fn memory_is_bounded_by_n_however_long_the_stream() {
    let (best, max_size) = top_n(0..100_000, 5);
    assert_eq!(best, vec![99_999, 99_998, 99_997, 99_996, 99_995]);
    assert_eq!(max_size, 5);
}

#[test]
fn edge_cases() {
    assert_eq!(top_n([3, 1, 2], 10).0, vec![3, 2, 1], "n larger than the input returns everything, sorted");
    assert_eq!(top_n([3, 1, 2], 0).0, Vec::<i32>::new());
    assert_eq!(top_n(std::iter::empty(), 3).0, Vec::<i32>::new());
    assert_eq!(top_n([4, 4, 4, 4], 2).0, vec![4, 4]);
}
```

### In the exercises

- **3g-06:** the `LimitExecutor` is the simple cousin: pass on the first N and stop.
- **3g-07:** the `TopNExecutor` is this heap over `(sort key, tuple)` entries, with the query's comparator.
- **Module 3h:** the optimizer rule that turns `Limit(Sort(x))` into `TopN(x)`.

### Where it is used

- **PostgreSQL**: a "top-N heapsort" (`Sort Method: top-N heapsort  Memory: 25kB` in `EXPLAIN ANALYZE`) when `ORDER BY ... LIMIT` is small.
- **Search engines**: Lucene's `PriorityQueue` collects the top-k hits.
- **DuckDB**: a "top-N" operator with a heap; ClickHouse and others have the same.
- **Rust**: `BinaryHeap` with `Reverse` is the idiom for "k largest of a stream".
