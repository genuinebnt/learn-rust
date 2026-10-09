---
title: The iterator model: init, next, and a tree of executors
summary: How a query plan runs as a tree of pull-based operators, why each call returns a batch, how a parent drives its children, and what holds state between calls.
minutes: 10
---
A plan is a tree; to run it, BusTub builds one **executor** per plan node and connects each to its children's executors. Then the root is asked for a row, over and over, until it says it has no more. This is the **iterator model** (also *Volcano* or *pull-based* execution, after Graefe's 1994 Volcano system). Every operator, from a table scan to a join to a sort, speaks the same two-method protocol:

```text
init()                              get ready (or start over)
next(&mut tuples, &mut rids, n)     fill the batch with up to n tuples; false when there are no more
```

```svg
caption: Executors form a tree like the plan. The engine calls next on the root; each executor calls next on its child, transforms what comes back, and returns it. Data flows up, requests flow down. Nothing is computed that nobody asked for, and nothing is stored between operators.
<svg viewBox="0 0 760 200" role="img" aria-label="Three executors in a chain: projection, filter, scan, with next calls going down and batches coming up">
<defs><marker id="im-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker><marker id="im-b" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--blue)"/></marker></defs>
<rect class="live" x="40" y="20" width="170" height="44" rx="3"/><text class="mid fg" x="125" y="47">Projection</text>
<rect class="live" x="40" y="86" width="170" height="44" rx="3"/><text class="mid fg" x="125" y="113">Filter  a &gt; 3</text>
<rect class="live" x="40" y="152" width="170" height="40" rx="3"/><text class="mid fg" x="125" y="177">SeqScan</text>
<path class="ln" d="M90 64 L90 84" marker-end="url(#im-a)"/><path class="ln" d="M90 130 L90 150" marker-end="url(#im-a)"/>
<path class="ln-b" d="M160 150 L160 132" marker-end="url(#im-b)"/><path class="ln-b" d="M160 84 L160 66" marker-end="url(#im-b)"/>
<text class="dim sm" x="236" y="80">next() ↓</text><text class="t-b sm" x="236" y="98">batch of tuples ↑</text>
<text class="dim sm" x="430" y="47">1. the engine calls Projection.next()</text><text class="dim sm" x="430" y="113">2. which calls Filter.next(), which calls SeqScan.next()</text><text class="dim sm" x="430" y="177">3. the scan fills a batch, the filter keeps some, the projection computes</text>
</svg>
```

## Why pull

- **Composable.** An operator needs only its children's `next`; it neither knows nor cares what they are. `Filter` works over a scan, a join or another filter.
- **Lazy.** `select ... limit 1` stops pulling after one row, so the scan below reads one page, not the table.
- **Pipelined.** A row can flow from the scan to the root without being stored anywhere. Operators that must see all their input first (a sort, a hash join's build side, an insert) are **pipeline breakers**: their first `next` drains the child.

## Why batches

A call per row crosses a virtual-call boundary per row per operator. BusTub's `next` fills a *batch* (20 tuples by default) so the overhead is paid once per batch; production engines use batches of thousands of values stored by column (*vectorised* execution, DuckDB, Velox). The contract: after the call both vectors hold the batch, at most `batch_size` long; `false` means "no more", and the vectors are empty.

## State between calls

The executor is an ordinary struct: its fields are the cursor. A scan keeps its table iterator; an insert keeps "I have already answered"; a projection keeps the leftover part of a child batch it could not fit. `init` resets the fields so that a parent that needs the same output twice (a nested loop join re-reads its inner side for every outer row) can call it again.

## Lifetimes

Executors borrow the catalog and the buffer pool for the duration of the query. In Rust that is a lifetime on the struct (`SeqScanExecutor<'e>`) and `Box<dyn Executor + 'e>` for children; nothing can outlive the query that created it. C++ keeps raw pointers and a convention.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `virtual void Init() = 0; virtual bool Next(vector<Tuple> *, vector<RID> *, size_t) = 0;` | `trait Executor { fn init(&mut self) -> Result<()>; fn next(&mut self, &mut Vec<Tuple>, &mut Vec<Rid>, usize) -> Result<bool>; }` |
| `std::unique_ptr<AbstractExecutor> child_executor_` | `child: Box<dyn Executor + 'e>` |
| out-parameters `std::vector<Tuple> *tuple_batch` | `&mut Vec<Tuple>` (also an out-parameter, with a checked lifetime) |
| `throw` on error from anywhere inside `Next` | `Result<bool>` and `?` |

## In real code

### Using it: a pull-based pipeline

```rust test
trait Exec {
    fn init(&mut self);
    /// Fills `batch` with at most `n` values; false when there are no more.
    fn next(&mut self, batch: &mut Vec<i64>, n: usize) -> bool;
}

struct Scan { data: Vec<i64>, pos: usize }
impl Exec for Scan {
    fn init(&mut self) { self.pos = 0; }
    fn next(&mut self, batch: &mut Vec<i64>, n: usize) -> bool {
        batch.clear();
        while batch.len() < n && self.pos < self.data.len() { batch.push(self.data[self.pos]); self.pos += 1; }
        !batch.is_empty()
    }
}

struct Filter<'a> { child: Box<dyn Exec + 'a>, keep: fn(i64) -> bool, pending: Vec<i64>, offset: usize }
impl<'a> Filter<'a> {
    fn new(child: Box<dyn Exec + 'a>, keep: fn(i64) -> bool) -> Filter<'a> { Filter { child, keep, pending: vec![], offset: 0 } }
}
impl Exec for Filter<'_> {
    fn init(&mut self) { self.child.init(); self.pending.clear(); self.offset = 0; }
    fn next(&mut self, batch: &mut Vec<i64>, n: usize) -> bool {
        batch.clear();
        let mut child_batch = vec![];
        while batch.len() < n {
            if self.offset == self.pending.len() {
                if !self.child.next(&mut child_batch, n) { break; }
                self.pending = std::mem::take(&mut child_batch);
                self.offset = 0;
            }
            let v = self.pending[self.offset];
            self.offset += 1;
            if (self.keep)(v) { batch.push(v); }
        }
        !batch.is_empty()
    }
}

fn drain(e: &mut dyn Exec, n: usize) -> Vec<Vec<i64>> {
    e.init();
    let (mut batches, mut batch) = (vec![], vec![]);
    while e.next(&mut batch, n) { batches.push(batch.clone()); }
    assert!(batch.is_empty(), "the last call leaves an empty batch");
    batches
}

#[test]
fn a_parent_pulls_batches_from_its_child() {
    let mut f = Filter::new(Box::new(Scan { data: (1..=10).collect(), pos: 0 }), |v| v % 2 == 0);
    assert_eq!(drain(&mut f, 2), vec![vec![2, 4], vec![6, 8], vec![10]]);
}

#[test]
fn batches_are_filled_with_matches_not_with_scanned_rows() {
    let mut f = Filter::new(Box::new(Scan { data: (1..=100).collect(), pos: 0 }), |v| v % 10 == 0);
    let sizes: Vec<usize> = drain(&mut f, 4).iter().map(|b| b.len()).collect();
    assert_eq!(sizes, vec![4, 4, 2], "10 matches in batches of 4, though the child sent 100 rows");
}

#[test]
fn init_starts_the_whole_pipeline_over() {
    let mut f = Filter::new(Box::new(Scan { data: vec![1, 2, 3], pos: 0 }), |_| true);
    assert_eq!(drain(&mut f, 10), vec![vec![1, 2, 3]]);
    assert_eq!(drain(&mut f, 10), vec![vec![1, 2, 3]], "a second init gives the same rows again");
}
```

### In the exercises

- **3e-01:** the sequential scan is the leaf: it owns a table iterator and fills batches from it.
- **3e-02 to 3e-06:** the scan with a predicate, and the insert, delete and update executors, which are pipeline breakers over a child.
- **3e-07, 3e-08:** the index scan is another leaf.
- **Module 3f onwards:** joins call `init` on their inner child once per outer row; aggregation and sort drain their child first.

### Where it is used

- **PostgreSQL**: `ExecProcNode` on a tree of `PlanState` nodes, one tuple per call.
- **SQLite**: not a tree of objects but bytecode, but `OP_Next` loops are the same pull.
- **DuckDB / Velox / DataFusion**: batches of column vectors flowing through operators (vectorised pull or push).
- **Rust**: `Iterator::next` composes the same way (`iter.filter(..).map(..)`), one item per call.
