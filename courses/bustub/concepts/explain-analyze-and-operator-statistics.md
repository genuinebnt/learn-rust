---
title: EXPLAIN ANALYZE: measuring a plan while it runs
summary: EXPLAIN shows the plan the optimizer chose; EXPLAIN ANALYZE runs it and reports, per operator, rows, batches, loops and inclusive time. A decorator around each executor does the counting; reading the numbers is the skill.
minutes: 9
---
`EXPLAIN` answers "what will the database do?". It does not answer "was that a good idea?", because it only knows what the optimizer *believed*. A plan that expects ten rows from a filter and gets ten million is wrong in a way no amount of staring at the plan text reveals. `EXPLAIN ANALYZE` closes the gap: it **runs the query** and prints the same tree with what each operator actually did.

## What is measured

Four numbers per operator are enough to find most problems:

- **rows**: tuples the operator produced, over its whole life. Compare with what its parent consumed and with what the optimizer estimated.
- **batches**: calls to `next` that returned something. BusTub passes tuples in batches of 20; `rows / batches` tells you how full they run.
- **loops**: calls to `init`. A nested loop join starts its inner side again for every outer tuple, so the inner scan shows `loops` equal to the outer row count, and `rows` equal to loops times the inner table. That one number explains most slow joins.
- **time**: wall-clock time spent inside the operator's `init` and `next`, **including its children**. Subtracting the children's time gives the operator's own ("exclusive") time.

Laziness shows up too. In `select * from big limit 5` the scan reports a few dozen rows, not the table's size: the limit stopped asking. A plan that reads everything to return five rows is the one to worry about.

## How it is built: a decorator

The executors of the Volcano model all speak one interface: `init`, `next`, `output_schema`. Anything that implements that interface and holds another executor can sit **between** an operator and its parent without either noticing. A *profiling executor* does exactly that: it forwards `init` and `next`, and around each call it reads a clock and adds to counters that belong to the plan node it wraps. Nothing in a real executor knows it is being measured, which is why the feature costs nothing when it is off (the wrapper is simply never created).

Two design decisions follow:

- **Where the counters live.** They belong to the *plan node*, not the executor, because the output is the plan tree and because one node can be started many times (a nested loop's inner side). A map from node identity to counters, created per execution, is enough.
- **The clock.** Reading a clock costs tens of nanoseconds; for an operator that handles twenty tuples per call that is noticeable, and `EXPLAIN ANALYZE` is known to slow queries down for this reason. The measured times are honest about relative cost and a little pessimistic about absolute cost.

## Reading a result

```text
Limit { limit=3 } (rows=3, batches=1, loops=1, time=0.042ms)
  ExternalMergeSort { ... } (rows=3, batches=1, loops=1, time=0.040ms)
    SeqScan { table=t } (rows=1000, batches=50, loops=1, time=0.031ms)
```

The sort produced only 3 rows because the limit asked for 3, but it had to read all 1000 to find the smallest: the scan's rows are the cost, the sort's rows are the answer. A top-N operator would show the same scan and the same 3 rows with far less memory.

Things to look for: a **filter** whose rows are close to its child's (it filters nothing: is the predicate useful?); a **join** whose output is far larger than both inputs (a missing predicate); an inner side with a large `loops` (a candidate for a hash join or an index); a **sort** under a limit (a candidate for top-N).

## What EXPLAIN ANALYZE must not do

It *executes* the statement. For a `select` that is harmless; for an `update` or `delete` it changes the data, which is why PostgreSQL tells people to wrap it in a transaction and roll back. A teaching engine can simply refuse data-changing statements.

## C++ comparison

| C / C++ | Rust |
|---|---|
| a wrapper class deriving from `AbstractExecutor` | a struct that holds `Box<dyn Executor>` and implements the same trait |
| `std::chrono::steady_clock::now()` | `std::time::Instant::now()` and `.elapsed()` |
| `std::atomic<uint64_t>` counters shared through a `shared_ptr` | `AtomicUsize` / `AtomicU64` inside an `Arc` |
| a `std::map<const PlanNode *, Stats>` | a `HashMap` keyed by `Arc::as_ptr(plan) as usize` |

## In real code

### Using it: a decorator that counts and times

```rust test
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

trait Exec {
    fn init(&mut self);
    /// Fills `out` with up to `n` items; false when there are no more.
    fn next(&mut self, out: &mut Vec<i32>, n: usize) -> bool;
}

struct Scan {
    data: Vec<i32>,
    pos: usize,
}

impl Exec for Scan {
    fn init(&mut self) {
        self.pos = 0;
    }
    fn next(&mut self, out: &mut Vec<i32>, n: usize) -> bool {
        out.clear();
        out.extend(self.data.iter().skip(self.pos).take(n));
        self.pos += out.len();
        !out.is_empty()
    }
}

/// Passes at most `limit` items on and then stops asking its child.
struct Limit {
    child: Box<dyn Exec>,
    limit: usize,
    seen: usize,
}

impl Exec for Limit {
    fn init(&mut self) {
        self.seen = 0;
        self.child.init();
    }
    fn next(&mut self, out: &mut Vec<i32>, n: usize) -> bool {
        if self.seen >= self.limit {
            return false;
        }
        let want = n.min(self.limit - self.seen);
        if !self.child.next(out, want) {
            return false;
        }
        out.truncate(want);
        self.seen += out.len();
        true
    }
}

#[derive(Default)]
struct Stats {
    rows: AtomicUsize,
    batches: AtomicUsize,
    loops: AtomicUsize,
}

struct Profiled {
    inner: Box<dyn Exec>,
    stats: Arc<Stats>,
}

impl Exec for Profiled {
    fn init(&mut self) {
        self.stats.loops.fetch_add(1, Ordering::Relaxed);
        self.inner.init();
    }
    fn next(&mut self, out: &mut Vec<i32>, n: usize) -> bool {
        let more = self.inner.next(out, n);
        if more {
            self.stats.batches.fetch_add(1, Ordering::Relaxed);
            self.stats.rows.fetch_add(out.len(), Ordering::Relaxed);
        }
        more
    }
}

fn drain(e: &mut dyn Exec) -> Vec<i32> {
    e.init();
    let (mut all, mut batch) = (vec![], vec![]);
    while e.next(&mut batch, 4) {
        all.extend(&batch);
    }
    all
}

#[test]
fn counts_rows_batches_and_loops_per_operator() {
    let (scan_stats, limit_stats) = (Arc::new(Stats::default()), Arc::new(Stats::default()));
    let scan = Profiled { inner: Box::new(Scan { data: (0..100).collect(), pos: 0 }), stats: scan_stats.clone() };
    let limit = Limit { child: Box::new(scan), limit: 6, seen: 0 };
    let mut root = Profiled { inner: Box::new(limit), stats: limit_stats.clone() };
    assert_eq!(drain(&mut root), vec![0, 1, 2, 3, 4, 5]);
    assert_eq!(limit_stats.rows.load(Ordering::Relaxed), 6);
    assert_eq!(limit_stats.batches.load(Ordering::Relaxed), 2, "4 + 2");
    assert_eq!(scan_stats.rows.load(Ordering::Relaxed), 6, "the scan was not read to the end: the limit stopped asking");
    assert_eq!(scan_stats.loops.load(Ordering::Relaxed), 1, "wrapped nodes are initialised through their parent: the scan's loops count its own init");
}

#[test]
fn restarting_an_operator_counts_a_loop_each_time() {
    let stats = Arc::new(Stats::default());
    let mut inner = Profiled { inner: Box::new(Scan { data: vec![1, 2, 3], pos: 0 }), stats: stats.clone() };
    for _ in 0..3 {
        assert_eq!(drain(&mut inner), vec![1, 2, 3]);
    }
    assert_eq!(stats.loops.load(Ordering::Relaxed), 3, "the inner side of a nested loop join, started once per outer row");
    assert_eq!(stats.rows.load(Ordering::Relaxed), 9);
}
```

### In the exercises

- **3i-06:** `ProfilingExecutor` is `Profiled` with a clock added; `render_analysis` prints the tree with the counters; `create_executor` wraps every executor when the execution is an `EXPLAIN ANALYZE`.

### Where it is used

- **PostgreSQL**: `EXPLAIN (ANALYZE, BUFFERS)`; the `Instrumentation` struct (`InstrStartNode`, `InstrStopNode`) is wrapped around every plan node, with `nloops` and `ntuples` exactly as here.
- **MySQL 8**: `EXPLAIN ANALYZE` prints `actual time=... rows=... loops=...` per iterator.
- **DuckDB / ClickHouse**: `EXPLAIN ANALYZE` and the query profiler give per-operator timings and cardinalities.
