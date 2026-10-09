---
title: Allocation and cache: where Rust programs spend their time
summary: Measure first, then look for the usual three costs (allocation, copying, scattered memory); how to read a flamegraph, how with_capacity and borrowing help, and what a profile of this course's MVCC scan showed.
minutes: 8
---
The performance guide in the `rust-skills` set gives an order of attack: **algorithm** (10x to 1000x), **data structure** (2x to 10x), **allocation** (2x to 5x), **cache behaviour** (1.5x to 3x), and one rule above all: **measure first, in release mode**. Debug-build timings are not evidence.

## The three usual costs

1. **Allocation.** Every `Vec::new()` that grows, every `String`, every `Box`, every `.clone()` of a heap value asks the allocator. In a hot loop that is the cost. Fixes: `Vec::with_capacity(n)` when you know the size; reuse a buffer across iterations (`clear()` keeps the capacity); avoid `format!` in loops; iterate instead of collecting into a temporary.
2. **Copying.** Hidden `.clone()`s of big values; passing `String` where `&str` would do; returning `Vec` when an iterator would do. Cloning an `Arc` is cheap (a counter bump); cloning what it points to is not.
3. **Scattered memory.** A `Vec<T>` is contiguous and the CPU prefetches it; a `HashMap`, a linked list or a `Vec<Box<T>>` chases pointers, each a likely cache miss. For small collections a linear search in a `Vec` beats a hash map; for large ones the hash map wins. A flat array indexed by integer (an arena, a `Vec<AtomicU32>` matrix) beats nested vectors.

## A worked profile: the MVCC scan

The course's own numbers (release mode, 20 000 rows): a reader at the newest snapshot scans in about 5 ms; a reader that began before ten updates of every row takes about 37 ms. A flamegraph of the old reader (commands in the *performance tests and measuring* article) says: roughly half of all samples are `malloc` and `free`, and the largest piece of the code's own time after `collect_undo_logs` is `Schema::new`, called by `get_undo_log_schema` for every log of every tuple. The chain walk is not slow; **allocating a partial schema, a `Vec<Value>` and a `Tuple` per log is**. The remedies the profile suggests, in order of payoff: cache the partial schema per `modified_fields` pattern; reconstruct into one reusable value buffer; apply several logs to one buffer before building the tuple (the reference already builds the tuple once at the end). None changes the algorithm; all reduce allocations.

## Workflow

1. Write the workload as a release-mode binary or benchmark (`criterion` for micro-benchmarks).
2. Time it. If it is fast enough, stop.
3. Profile it (`perf` on Linux, `sample` on macOS, or `cargo flamegraph`) and read the widest boxes.
4. Change one thing. Re-measure. Keep the change only if the number moved.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `std::vector::reserve` | `Vec::with_capacity`, `reserve` |
| pass `const std::string &` | pass `&str` |
| `std::move` to avoid a copy | a move is the default; clone is explicit |
| `perf`, `valgrind --tool=callgrind`, `heaptrack` | the same tools work on Rust binaries (symbols need `debug = 1` in the release profile) |

**Port rule:** an explicit `.clone()` in a loop is the Rust equivalent of an accidental copy in C++: look at it first in a profile.

## In real code

### Using it: with_capacity, reuse and borrowing

```rust test
#[test]
fn with_capacity_allocates_once() {
    let mut v: Vec<u64> = Vec::with_capacity(1000);
    let cap = v.capacity();
    for i in 0..1000 {
        v.push(i);
    }
    assert_eq!(v.capacity(), cap, "no reallocation while filling");
}

fn join_lines(lines: &[&str], buf: &mut String) {
    buf.clear(); // keeps the allocation
    for l in lines {
        buf.push_str(l);
        buf.push('\n');
    }
}

#[test]
fn a_reused_buffer_keeps_its_capacity_between_calls() {
    let mut buf = String::new();
    join_lines(&["a", "b"], &mut buf);
    let cap = buf.capacity();
    join_lines(&["c"], &mut buf);
    assert_eq!(buf, "c\n");
    assert_eq!(buf.capacity(), cap);
}

fn count_long(words: &[String]) -> usize {
    words.iter().filter(|w| w.len() > 3).count() // borrows: no String is copied
}

#[test]
fn counting_by_reference_copies_nothing() {
    let words: Vec<String> = ["tree", "ab", "forest"].iter().map(|s| s.to_string()).collect();
    assert_eq!(count_long(&words), 2);
}
```

### Using it: contiguous beats scattered (a measurement you can repeat)

```rust test
use std::time::Instant;

#[test]
fn summing_a_flat_vec_is_not_slower_than_chasing_boxes() {
    let flat: Vec<u64> = (0..200_000).collect();
    let boxed: Vec<Box<u64>> = (0..200_000).map(Box::new).collect();
    let t = Instant::now();
    let a: u64 = flat.iter().sum();
    let flat_time = t.elapsed();
    let t = Instant::now();
    let b: u64 = boxed.iter().map(|x| **x).sum();
    let boxed_time = t.elapsed();
    assert_eq!(a, b);
    // timing assertions are flaky; we only record that both finished and the answers agree (run with --release --nocapture to compare)
    let _ = (flat_time, boxed_time);
}

#[test]
fn a_small_vec_search_is_a_fine_map_for_a_handful_of_entries() {
    let pairs = vec![("a", 1), ("b", 2), ("c", 3)];
    let find = |k: &str| pairs.iter().find(|(key, _)| *key == k).map(|(_, v)| *v);
    assert_eq!(find("b"), Some(2));
    assert_eq!(find("z"), None);
}
```

### In the exercises

- **4a-04 / 4a-08:** the old-reader scan, and the allocation profile above.
- **0c-02:** random keys versus sequential keys: the lesson that a benchmark input can hide the behaviour.
- **3g:** batches reuse their `Vec`s across `next` calls.
- **0b-01:** an arena instead of per-node allocations.

### Where it is used

- `criterion` for benchmarks, `cargo flamegraph`, `perf`, `samply`, `dhat` for heap profiles; the Rust Performance Book (`nnethercote.github.io/perf-book`) covers each of these in depth.
