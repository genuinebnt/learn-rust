---
title: The Halloween problem: scanning a table you are changing
summary: Why an UPDATE that moves rows can process the same row twice, the three standard fixes, and the one BusTub's iterator uses: remember where the table ended when the scan began.
minutes: 8
---
`UPDATE employees SET salary = salary * 1.1 WHERE salary < 25000`, run with an index on `salary`. The scan visits a row, raises the salary, and the row's index entry *moves further along the scan*. The scan reaches it again, raises it again... Everybody gets the raise until they pass 25,000. The story goes that the IBM System R team found this on 31 October 1976; it is the **Halloween problem**: *a statement that reads and writes the same data can see its own writes*.

```svg
caption: A scan that inserts at the end of the table never terminates if it reads until "no more rows". Fixed by stopping at the last row that existed when the scan began.
<svg viewBox="0 0 760 190" role="img" aria-label="A table with a stop marker before newly inserted rows">
<defs><marker id="hp-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<rect class="live" x="40" y="60" width="64" height="40" rx="2"/><rect class="live" x="106" y="60" width="64" height="40" rx="2"/><rect class="live" x="172" y="60" width="64" height="40" rx="2"/>
<text class="mid fg sm" x="72" y="85">r0</text><text class="mid fg sm" x="138" y="85">r1</text><text class="mid fg sm" x="204" y="85">r2</text>
<rect class="never" x="238" y="60" width="64" height="40" rx="2"/><rect class="never" x="304" y="60" width="64" height="40" rx="2"/><rect class="never" x="370" y="60" width="64" height="40" rx="2"/>
<text class="mid dim sm" x="270" y="85">r0'</text><text class="mid dim sm" x="336" y="85">r1'</text><text class="mid dim sm" x="402" y="85">r2'</text>
<path class="ln-b" d="M237 40 L237 120"/><text class="t-b sm" x="237" y="140" style="text-anchor:middle">stop here</text><text class="t-b sm" x="237" y="158" style="text-anchor:middle">(the end when the scan began)</text>
<text class="dim sm" x="320" y="40" style="text-anchor:middle">rows written by the statement itself</text>
<path class="ln" d="M72 52 C72 20 180 20 204 52" marker-end="url(#hp-a)"/>
</svg>
```

## The three fixes

| fix | how | used by |
|---|---|---|
| **Snapshot the input** | materialise every row to modify first (into memory or a temp table), then modify | simple executors; sort-based plans do it for free; BusTub's update executor pulls the child fully before writing in some plans |
| **Stop at the old end** | the scan records its end position at the start and never goes past | BusTub's `TableIterator` |
| **Versioning** | a statement only sees versions committed before it started (MVCC), so its own new versions are invisible | PostgreSQL, Oracle, MySQL InnoDB (module 4a) |

Optimisers must also know the problem exists: a plan that scans an index on the column being updated is Halloween-prone, and PostgreSQL's planner and SQL Server both add a blocking operator (a spool or a sort) in that case.

## Stopping at the old end

For a heap file the "end" is a record id: the last slot of the last page. When the iterator is created it asks the heap for it and stores it; `advance` compares the next rid with that value. The cost is one extra field and one comparison. Two limits: it assumes the new rows really are appended (an insert into a freed slot *before* the end would still be seen once, harmlessly, but rows rewritten in place could be seen twice if the scan has not reached them), and it sees the table "as of the start" only for rows added, not for changes to rows ahead of the cursor. Versioning handles both.

## Where the rule shows up

- An `INSERT INTO t SELECT * FROM t` must read the old `t`, not the growing one; it is the same problem with a different statement.
- `UPDATE ... SET key = key + 1` on a unique index can collide with a row it has not processed yet (a related ordering problem that databases solve by deferring the uniqueness check to the end of the statement).
- A bank transfer `UPDATE accounts SET balance = balance - 10 WHERE ...` is safe because the update does not move the row in the scan order: the problem needs a write that *changes where the row is found*.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `RID stop_at_rid_; ... if (cursor_ == stop_at_rid_) { is_end_ = true; }` | the same field, stored in the iterator, compared in `advance` |
| `for (auto it = table->MakeIterator(); !it.IsEnd(); ++it) { table->InsertTuple(...); }` | works without end-chasing because `make_iterator()` is a snapshot; `make_eager_iterator()` is the variant that follows the table |
| invalidated iterators after modification (`std::vector`) | the iterator holds a `&TableHeap` shared borrow: legal because the heap uses interior mutability; the *snapshot bound* is what keeps the loop finite |

## In real code

### Using it: the loop that never ends, and the bound that ends it

```rust test
/// A growing table of numbers; a "statement" re-inserts each row doubled.
struct Table { rows: Vec<u32> }

fn double_all_naive(t: &mut Table, limit: usize) -> usize {
    // read until "no more rows": each insert gives the scan another row to read
    let mut i = 0;
    while i < t.rows.len() && i < limit {
        let v = t.rows[i];
        t.rows.push(v.wrapping_mul(2));
        i += 1;
    }
    i
}

fn double_all_bounded(t: &mut Table) -> usize {
    let stop = t.rows.len();                // remember the end when the scan began
    let mut i = 0;
    while i < stop {
        let v = t.rows[i];
        t.rows.push(v.wrapping_mul(2));
        i += 1;
    }
    i
}

#[test]
fn the_naive_scan_runs_until_something_else_stops_it() {
    let mut t = Table { rows: vec![1, 2, 3] };
    let visited = double_all_naive(&mut t, 1000);
    assert_eq!(visited, 1000, "it only stopped because of the safety limit");
    assert!(t.rows.len() > 1000);
}

#[test]
fn the_bounded_scan_visits_each_original_row_once() {
    let mut t = Table { rows: vec![1, 2, 3] };
    assert_eq!(double_all_bounded(&mut t), 3);
    assert_eq!(t.rows, vec![1, 2, 3, 2, 4, 6]);
}
```

```rust test
/// The same fix on a chain of pages: the bound is a (page, slot) position, compared lexicographically.
fn visit(pages: &mut Vec<Vec<u32>>, cap: usize) -> Vec<u32> {
    let stop = (pages.len() - 1, pages.last().unwrap().len()); // one past the last row: (page, slot)
    let mut seen = vec![];
    let (mut p, mut s) = (0usize, 0usize);
    while (p, s) < stop {
        let v = pages[p][s];
        seen.push(v);
        // the "statement" appends a derived row
        if pages.last().unwrap().len() == cap { pages.push(vec![]); }
        pages.last_mut().unwrap().push(v + 100);
        s += 1;
        if s == pages[p].len() && p + 1 < pages.len() { p += 1; s = 0; }
    }
    seen
}

#[test]
fn a_position_bound_works_across_pages() {
    let mut pages = vec![vec![1, 2], vec![3]];
    assert_eq!(visit(&mut pages, 2), vec![1, 2, 3]);
    assert_eq!(pages.iter().flatten().count(), 6, "three originals and three derived rows");
}

#[test]
fn an_empty_scan_returns_nothing_and_inserts_nothing() {
    let mut pages = vec![vec![]];
    assert_eq!(visit(&mut pages, 2), Vec::<u32>::new());
    assert_eq!(pages, vec![Vec::<u32>::new()]);
}
```

### In the exercises

- **3c-02:** `make_iterator` records the heap's last rid in `stop_at_rid`; `advance` ends the scan when it passes it. `make_eager_iterator` leaves the bound out for callers that want the live end.
- **Module 4b** (the update executor): a pipeline `Update <- Seq Scan` over the same table depends on this bound to terminate.
- **Module 4a** (MVCC): the same guarantee comes from timestamps instead.

### Where it is used

- **System R / DB2**: where it was first found.
- **PostgreSQL**: snapshots (statement-level visibility) make the new row versions invisible to the statement that wrote them; the planner adds a `Materialize` when needed.
- **SQL Server**: the optimizer inserts a *Halloween Protection* spool operator.
- **SQLite**: collects the rowids to modify first (a "one-pass" optimisation is only used when it is provably safe).
