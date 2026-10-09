---
title: Lifetimes in structs: a value that borrows from another
summary: When a struct holds a reference, what the lifetime parameter promises, the limits of borrowing from a long-lived owner, and the three escape hatches: Arc, owned data and indices.
minutes: 9
---
Until now lifetimes appeared on functions. A struct that stores a reference needs one too: `struct TableIterator<'a> { heap: &'a TableHeap<'a>, ... }`. The `'a` is a promise: *this iterator cannot outlive the heap it points into*. The compiler enforces it: you cannot return the iterator out of the function that owns the heap, drop the heap while the iterator lives, or keep the iterator in a long-lived struct unless that struct is also scoped by `'a`.

```svg
caption: A struct with a lifetime parameter borrows from an owner that must outlive it. The iterator, the heap and the buffer pool form a chain: each borrows the one to its right, so the borrow checker requires them to be dropped in the opposite order they were created.
<svg viewBox="0 0 760 130" role="img" aria-label="Iterator borrows heap borrows pool, with lifetimes nested">
<defs><marker id="ls-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<rect class="blue" x="30" y="40" width="170" height="50" rx="3"/><text class="mid t-b" x="115" y="70">TableIterator&lt;'a&gt;</text>
<rect class="live" x="300" y="40" width="170" height="50" rx="3"/><text class="mid fg" x="385" y="70">TableHeap&lt;'a&gt;</text>
<rect class="box" x="570" y="40" width="160" height="50" rx="3"/><text class="mid fg" x="650" y="70">BufferPoolManager</text>
<path class="ln" d="M200 65 L298 65" marker-end="url(#ls-a)"/><path class="ln" d="M470 65 L568 65" marker-end="url(#ls-a)"/>
<text class="dim sm" x="249" y="55" style="text-anchor:middle">&amp;'a</text><text class="dim sm" x="519" y="55" style="text-anchor:middle">&amp;'a</text>
<text class="dim sm" x="380" y="118" style="text-anchor:middle">dropped in this order: iterator, heap, pool (the reverse of how they were built)</text>
</svg>
```

## What the syntax means

```rust,ignore
struct View<'a> { bytes: &'a [u8] }                 // holds a borrow
impl<'a> View<'a> {
    fn first(&self) -> u8 { self.bytes[0] }
    fn rest(&self) -> &'a [u8] { &self.bytes[1..] } // the result borrows from the *data*, not from the view
}
```

`View<'a>` is not "a View that lives for `'a`"; it is "a View that holds something that is valid for at least `'a`". The second method returns `&'a [u8]`, not `&'_ [u8]` tied to `&self`: the returned slice stays valid even after the `View` itself is gone, because it borrows from the underlying bytes. Choosing between the two is the main design decision.

## Why modules 1 to 3 use them

The buffer pool *owns* pages and hands out guards that borrow it. The table heap and the catalog *borrow* the pool (they cannot own it: many tables share one pool). The iterator borrows the heap. Everything is a view, nothing is copied, and the compiler guarantees no view outlives its source. The cost: structs that hold borrows are tied to a scope, which makes them awkward to store in a global or send to another thread.

## When the borrow is too tight

| situation | symptom | fix |
|---|---|---|
| the struct must be stored in a long-lived place (a global engine, a thread) | `borrowed value does not live long enough` | give it ownership: `Arc<BufferPoolManager>` instead of `&'a BufferPoolManager` |
| the struct needs to point into *itself* (an owner and a view of its own field) | `self-referential struct` is impossible | store an index or an offset; or split into two structs; or an owning crate (`ouroboros`, `self_cell`) |
| many structs share the borrow and a `&mut` is wanted | `cannot borrow as mutable more than once` | interior mutability (`Mutex`, `RefCell`) inside, shared `&` outside, as the table heap does |
| a lifetime parameter spreads through the whole program | `<'a>` on every type | `Arc`, or generics over the owner, once it hurts |

The course keeps `'a` because the structures are scoped to one test or one query. An engine that outlives a request would switch to `Arc` at the top and keep `'a` below.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `class TableIterator { TableHeap *table_heap_; ... }` (a raw pointer; dangling if the heap is deleted) | `struct TableIterator<'a> { heap: &'a TableHeap<'a> }`, checked at compile time |
| `std::shared_ptr<BufferPoolManager>` stored in every object | `&'a BufferPoolManager` (free) or `Arc<...>` (counted), your choice |
| iterator invalidation by documentation | iterator validity by the type system: you cannot mutate the borrowed owner while it lives (unless it uses interior mutability) |

## In real code

### Using it: a view and a result that outlives it

```rust test
struct Tokens<'a> { text: &'a str, pos: usize }

impl<'a> Tokens<'a> {
    fn new(text: &'a str) -> Tokens<'a> { Tokens { text, pos: 0 } }
}

impl<'a> Iterator for Tokens<'a> {
    type Item = &'a str; // the token borrows from the text, not from the iterator
    fn next(&mut self) -> Option<&'a str> {
        let rest = &self.text[self.pos..];
        let rest_trim = rest.trim_start();
        if rest_trim.is_empty() { return None; }
        let start = self.pos + (rest.len() - rest_trim.len());
        let end = rest_trim.find(' ').map(|i| start + i).unwrap_or(self.text.len());
        self.pos = end;
        Some(&self.text[start..end])
    }
}

fn first_two(text: &str) -> (Option<&str>, Option<&str>) {
    let mut it = Tokens::new(text);
    let a = it.next();
    let b = it.next();
    (a, b) // the iterator is dropped here, the tokens are still valid: they borrow from `text`
}

#[test]
fn an_iterator_over_borrowed_text_yields_borrowed_pieces() {
    let words: Vec<&str> = Tokens::new("select  a from  t").collect();
    assert_eq!(words, ["select", "a", "from", "t"]);
}

#[test]
fn the_items_outlive_the_iterator() {
    let text = String::from("insert into people");
    let (a, b) = first_two(&text);
    assert_eq!((a, b), (Some("insert"), Some("into")));
}
```

```rust test
use std::sync::Arc;

/// The same shape with `Arc` instead of a borrow: the iterator owns a share of the data and can be sent anywhere.
struct OwnedIter { data: Arc<Vec<u32>>, pos: usize }

impl Iterator for OwnedIter {
    type Item = u32;
    fn next(&mut self) -> Option<u32> { let v = self.data.get(self.pos).copied(); self.pos += 1; v }
}

fn make(data: &Arc<Vec<u32>>) -> OwnedIter { OwnedIter { data: data.clone(), pos: 0 } }

#[test]
fn an_arc_iterator_can_be_returned_and_sent_to_another_thread() {
    let it = {
        let data = Arc::new(vec![1, 2, 3]);
        make(&data) // `data` goes out of scope; the iterator keeps its own share alive
    };
    let sum = std::thread::spawn(move || it.sum::<u32>()).join().unwrap();
    assert_eq!(sum, 6);
}

#[test]
fn the_data_is_freed_when_the_last_owner_goes() {
    let data = Arc::new(vec![1, 2]);
    let it = make(&data);
    assert_eq!(Arc::strong_count(&data), 2);
    drop(it);
    assert_eq!(Arc::strong_count(&data), 1);
}
```

### In the exercises

- **3c-02:** `TableIterator<'a>` holds `&'a TableHeap<'a>`; `get_tuple` returns owned `(TupleMeta, Tuple)`, so nothing borrowed leaves the iterator.
- **3c-03:** `BPlusTreeIndex<'a, N>` borrows the buffer pool the same way; the catalog stores `Box<dyn Index + 'a>`, so the `'a` is part of the catalog's type too.
- **Everywhere since 1g:** a guard is `PageGuard<'a>`, borrowed from the pool.

### Where it is used

- **Parsers and tokenisers** (`nom`, `logos`, `sqlparser`'s tokenizer) return `&'a str` slices of the input to avoid copying.
- **`std`**: `Chars<'a>`, `Iter<'a, T>`, `MutexGuard<'a, T>` are all structs borrowing from their source.
- **Embedded and kernel code**: borrowed views over buffers (`&'a mut [u8]`) so no allocation is needed.
