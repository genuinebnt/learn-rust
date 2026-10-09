---
title: Heap files: a table as a chain of pages
summary: The simplest way to store a table: unordered pages linked in a list, an append point, record ids that name a row, and why every real database starts here.
minutes: 8
---
A **heap file** stores a table's rows in no particular order. The file is a sequence of pages; each page is a slotted page (module 3b) holding some rows; rows are found by their **record id** `(page, slot)`. "Heap" here means *unordered pile*, not the memory heap. It is the default table storage of PostgreSQL, SQLite (the table b-tree aside), Oracle and BusTub.

```svg
caption: A heap file as a singly linked chain of pages. The table remembers its first page (where scans start) and its last page (where inserts go). When the last page is full a new page is allocated, linked from the old last page, and becomes the append point.
<svg viewBox="0 0 760 170" role="img" aria-label="Three linked pages with a first and a last pointer">
<defs><marker id="hf-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<rect class="live" x="60" y="50" width="170" height="60" rx="3"/><text class="mid fg" x="145" y="76">page 4</text><text class="mid dim sm" x="145" y="97">full · next = 9</text>
<rect class="live" x="300" y="50" width="170" height="60" rx="3"/><text class="mid fg" x="385" y="76">page 9</text><text class="mid dim sm" x="385" y="97">full · next = 2</text>
<rect class="blue" x="540" y="50" width="170" height="60" rx="3"/><text class="mid t-b" x="625" y="76">page 2</text><text class="mid dim sm" x="625" y="97">room left · next = none</text>
<path class="ln" d="M230 80 L298 80" marker-end="url(#hf-a)"/><path class="ln" d="M470 80 L538 80" marker-end="url(#hf-a)"/>
<text class="dim sm" x="145" y="30">first_page_id: scans start here</text><path class="ln" d="M145 36 L145 48" marker-end="url(#hf-a)"/>
<text class="t-b sm" x="625" y="30">last_page_id: inserts go here</text><path class="ln-b" d="M625 36 L625 48" marker-end="url(#hf-a)"/>
<text class="dim sm" x="60" y="145">The page ids are not consecutive: the buffer pool hands out ids, the chain is what links them.</text>
</svg>
```

## The operations

| operation | how it works | cost |
|---|---|---|
| **insert** | try the last page; if the row does not fit, allocate a page, link it, retry | O(1) pages touched |
| **get** `(page, slot)` | fetch that page, read the slot | O(1) |
| **delete** | set a flag in the slot (space is reclaimed later by compaction or vacuum) | O(1) |
| **scan** | start at the first page, read every slot, follow `next` | O(pages) |
| **find by value** | a scan, or an index (module 3c) | O(pages) without an index |

All the fast paths work by record id; everything *by value* is a scan, which is exactly why indexes exist: a B+ tree maps a key to the record id and the heap does the rest.

## Design choices

- **Append only to the last page.** Remembering only the last page makes insert constant-time and keeps the table clustered by arrival; the price is that the space freed by deletions in earlier pages is not reused until something (vacuum, a free-space map) tells the heap about it. PostgreSQL keeps a *free space map* for exactly this reason.
- **A row never moves.** Because an index stores the record id, the heap must not relocate rows on update. BusTub updates in place when the new row is the same size and otherwise does *delete + insert* (a new rid, so every index must be updated too); PostgreSQL's *HOT updates* and tuple chains exist to soften this cost.
- **The last-page pointer is shared state.** Two threads inserting at once both want the same page; the heap guards the pointer (and the page it names) with a lock, covered in `coarse-and-fine-grained-locking`.
- **A row must fit one page.** A row larger than a page cannot be stored by this design; real systems *overflow* big values to separate pages (PostgreSQL's TOAST). BusTub returns an error.

## Heap vs. clustered tables

A heap is *unordered*: the primary key is just another index. A **clustered** table (InnoDB, SQLite's rowid tables, SQL Server clustered indexes) stores the rows *inside* the leaves of the primary-key B+ tree. The trade-off: clustered tables answer primary-key range queries from one sequential read, but every secondary index must store the primary key (not a position) and rows may move when the tree splits. Heap files keep record ids stable and make every index equal.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `page_id_t first_page_id_; page_id_t last_page_id_; std::mutex latch_;` | `first_page_id: PageId` and `last_page: Mutex<PageId>` (the data the lock protects lives inside it) |
| `TablePage *page = reinterpret_cast<TablePage *>(guard.GetDataMut());` | `TablePageMut::new(&mut guard[..])`, a view checked by the borrow checker |
| `INVALID_PAGE_ID` as the end of the chain | `PageId::INVALID` (or `Option<PageId>` in your own code) |

## In real code

### Using it: a heap of tiny pages

```rust test
struct Heap {
    pages: Vec<Vec<String>>, // a page holds up to CAP rows
    next: Vec<Option<usize>>,
    first: usize,
    last: usize,
}
const CAP: usize = 2;

impl Heap {
    fn new() -> Heap { Heap { pages: vec![vec![]], next: vec![None], first: 0, last: 0 } }
    fn insert(&mut self, row: &str) -> (usize, usize) {
        if self.pages[self.last].len() == CAP {
            self.pages.push(vec![]);
            self.next.push(None);
            let new = self.pages.len() - 1;
            self.next[self.last] = Some(new);
            self.last = new;
        }
        self.pages[self.last].push(row.to_string());
        (self.last, self.pages[self.last].len() - 1)
    }
    fn get(&self, rid: (usize, usize)) -> Option<&str> {
        self.pages.get(rid.0)?.get(rid.1).map(|s| s.as_str())
    }
    fn scan(&self) -> Vec<&str> {
        let mut out = vec![];
        let mut page = Some(self.first);
        while let Some(p) = page {
            out.extend(self.pages[p].iter().map(|s| s.as_str()));
            page = self.next[p];
        }
        out
    }
}

#[test]
fn rows_get_record_ids_and_the_chain_grows_at_the_end() {
    let mut h = Heap::new();
    assert_eq!(h.insert("a"), (0, 0));
    assert_eq!(h.insert("b"), (0, 1));
    assert_eq!(h.insert("c"), (1, 0), "page 0 is full: a new page is linked and becomes the append point");
    assert_eq!(h.last, 1);
    assert_eq!(h.next[0], Some(1));
    assert_eq!(h.get((0, 1)), Some("b"));
    assert_eq!(h.get((5, 0)), None);
}

#[test]
fn a_scan_follows_the_chain_in_insertion_order() {
    let mut h = Heap::new();
    let rids: Vec<_> = ["a", "b", "c", "d", "e"].iter().map(|r| h.insert(r)).collect();
    assert_eq!(h.scan(), vec!["a", "b", "c", "d", "e"]);
    assert_eq!(rids, vec![(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)]);
    for (rid, want) in rids.iter().zip(["a", "b", "c", "d", "e"]) {
        assert_eq!(h.get(*rid), Some(want), "a record id keeps naming its row");
    }
}
```

### In the exercises

- **3c-01:** `TableHeap::new` allocates the first page; `insert_tuple` is `insert` (with a real page, a lock around the last-page pointer and an error when the tuple can never fit).
- **3c-01:** `get_tuple` and `get_tuple_meta` are `get`; the rid is the address.
- **3c-02:** the iterator is `scan`, turned inside out so it can pause between rows.

### Where it is used

- **PostgreSQL**: heap files of 8 KiB pages; a row is addressed by its `ctid = (block, line pointer)`; a *free space map* and `VACUUM` reclaim deleted space.
- **SQLite**: tables are b-trees keyed by rowid, but `WITHOUT ROWID` tables and indexes show the clustered alternative.
- **MySQL InnoDB**: the clustered alternative; every table is a B+ tree on the primary key.
- **Oracle**: heap-organised tables are the default, with index-organised tables as the clustered option.
