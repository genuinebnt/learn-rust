---
title: Iterators and closures: the loop vocabulary of Rust
summary: How iterator adapters (map, filter, zip, windows, filter_map) and consumers (collect, sum, any, fold) replace index loops, how closures capture, and why the chain costs no more than the loop.
minutes: 8
---
An **iterator** produces values one at a time; **adapters** (`map`, `filter`, `zip`, `enumerate`, `take`, `skip`, `windows`, `filter_map`) wrap one iterator in another and do nothing until a **consumer** (`collect`, `sum`, `count`, `any`, `all`, `find`, `fold`, `for`) pulls on the end. Adapters take **closures**: small anonymous functions that can capture variables from where they are written.

Prefer the chain to an index loop: it cannot go out of bounds, says what it does ("keep the live keys, map them to buckets"), and compiles to the same machine code (iterators are zero-cost abstractions: the adapters are inlined and fuse into one loop). An index-based `for i in 0..v.len()` is a code smell when you only read `v[i]`; clippy's `needless_range_loop` says so.

## The vocabulary this course uses

| need | write |
|---|---|
| transform each | `.map(f)` |
| keep some | `.filter(pred)`; drop `None`s and unwrap `Some`s at once with `.filter_map(f)` |
| position and value | `.enumerate()` |
| two sequences together | `.zip(other)` |
| neighbouring pairs | `slice.windows(2)` |
| fixed-size groups | `slice.chunks(n)` |
| any / all / count | `.any(p)`, `.all(p)`, `.count()` |
| smallest / largest | `.min()`, `.max()`, `.min_by_key(f)` |
| collect into a container | `.collect::<Vec<_>>()`, `HashMap`, `String`, `Result<Vec<_>, E>` |
| in-place filter | `vec.retain(pred)`; sort with `vec.sort_by(cmp)` (stable) |

`collect::<Result<Vec<_>, _>>()` is worth remembering: it stops at the first `Err` and returns it, or returns all the `Ok` values: the iterator form of "parse every field, fail if any fails".

## Closures capture

A closure borrows what it uses (`Fn`), mutates it (`FnMut`) or takes it (`FnOnce`); `move` forces it to take ownership, which `thread::spawn` requires. Two consequences you meet in this code: a closure passed to `retain` or `sort_by` must not use the vector it is changing (the borrow checker says so), and a `check` callback given to `update_tuple_and_undo_link` borrows the transaction for the duration of the call.

## Laziness and allocation

Adapters allocate nothing; `collect` does, once. A chain that only needs to know "is any element bad?" should end in `any`, not in `collect` then `len`. Conversely, collecting into a `Vec` before iterating twice is correct when the source is consumed (a child executor's batch): see the *allocation and cache* article.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::transform`, `std::copy_if` | `.map(..)`, `.filter(..)` |
| `std::accumulate` | `.fold(init, f)` or `.sum()` |
| `std::any_of` / `all_of` / `find_if` | `.any(..)` / `.all(..)` / `.find(..)` |
| `std::sort` with a lambda | `v.sort_by(..)` (stable) or `sort_unstable_by` |
| range-for over `v` with an index | `for (i, x) in v.iter().enumerate()` |

**Port rule:** an algorithm call with two iterators becomes a method chain starting from one; the second sequence enters with `zip`.

## In real code

### Using it: chains in place of loops

```rust test
#[test]
fn filter_map_and_collect_replace_a_loop_with_pushes() {
    let raw = ["7", "x", "12", "", "30"];
    let numbers: Vec<i32> = raw.iter().filter_map(|s| s.parse().ok()).collect();
    assert_eq!(numbers, vec![7, 12, 30]);
}

#[test]
fn windows_zip_and_enumerate_see_neighbours_and_positions() {
    let ts = [1, 3, 3, 8];
    let gaps: Vec<i32> = ts.windows(2).map(|w| w[1] - w[0]).collect();
    assert_eq!(gaps, vec![2, 0, 5]);
    let sorted = ts.windows(2).all(|w| w[0] <= w[1]);
    assert!(sorted);
    let weighted: i32 = ts.iter().zip([1, 2, 3, 4]).map(|(a, b)| a * b).sum();
    assert_eq!(weighted, 1 + 6 + 9 + 32);
    let (best_i, best) = ts.iter().enumerate().max_by_key(|(_, v)| **v).unwrap();
    assert_eq!((best_i, *best), (3, 8));
}
```

### Using it: collect into a Result, retain, sort_by

```rust test
#[test]
fn collecting_into_a_result_stops_at_the_first_error() {
    let ok: Result<Vec<i32>, _> = ["1", "2", "3"].iter().map(|s| s.parse::<i32>()).collect();
    assert_eq!(ok.unwrap(), vec![1, 2, 3]);
    let bad: Result<Vec<i32>, _> = ["1", "oops", "3"].iter().map(|s| s.parse::<i32>()).collect();
    assert!(bad.is_err());
}

#[test]
fn retain_and_a_stable_sort_by_keep_ties_in_order() {
    let mut rows = vec![("b", 2), ("a", 2), ("c", 1), ("d", 9)];
    rows.retain(|r| r.1 < 9);
    rows.sort_by(|x, y| y.1.cmp(&x.1)); // by count, descending; ties keep their order
    assert_eq!(rows, vec![("b", 2), ("a", 2), ("c", 1)]);
}
```

### In the exercises

- **3e-01:** scans and filters are the iterator model in SQL form; the Rust iterator is the same idea in the language.
- **3g:** `sort_by` and the comparator; stable ties.
- **4b-05:** `retain` on the transaction map.
- **0d-01:** `top_k` sorts candidates with a stable `sort_by`.

### Where it is used

- Everywhere; the standard library's `Iterator` trait has about 75 methods, and `rayon` turns many of the same chains parallel by changing `iter()` to `par_iter()`.
