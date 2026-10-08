---
title: Moving data across threads: Send, Sync and who owns the buffer
summary: What Send and Sync promise, why a DiskRequest owns its page buffer instead of sharing a pointer, and how ownership hand-off replaces a whole class of data races.
minutes: 9
---
BusTub's `DiskRequest` carries a raw `char *data`. The caller owns the page, the worker reads or fills it, and **nothing in the type says who may touch it when**. The convention is "don't touch it until the promise is set", and a violation is a data race. This page is how Rust turns that convention into a rule the compiler checks.

## The C++ way: a pointer and a promise

```cpp
struct DiskRequest {
  bool is_write_;
  char *data_;                     // shared between the caller and the worker thread
  page_id_t page_id_;
  std::promise<bool> callback_;
};
// caller:  buffer lives in a Page; schedule; ...may touch buffer here by mistake...; future.get();
```

Reuse the buffer too early, free it too early, or read it while the worker writes it, and you have undefined behaviour that shows up once in a thousand runs.

## The Rust way: the request owns the buffer

```rust
pub struct DiskRequest {
    pub is_write: bool,
    pub data: Box<PageData>,                // the request OWNS the 8 KiB page
    pub page_id: PageId,
    pub callback: Promise<DiskResult>,      // DiskResult = io::Result<Box<PageData>>
}
```

A write *moves* the page into the request; a read moves in an empty buffer. When the worker finishes it moves the buffer **back out through the promise**. At every instant exactly one thread owns the buffer; the type system makes "touch it while the worker has it" a compile error (the variable has been moved away).

```svg
caption: The page buffer is owned by exactly one place at a time and moves along the arrows. While it is in the queue or with the worker, the caller no longer has it, so it cannot touch it by mistake.
<svg viewBox="0 0 760 170" role="img" aria-label="A page buffer moving from the caller into a request, the queue, the worker, and back through the future">
<defs><marker id="mv-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<rect class="hot" x="20" y="50" width="130" height="50" rx="4"/><text class="mid t-a" x="85" y="72">caller</text><text class="mid dim sm" x="85" y="90">owns the page</text>
<rect class="box" x="210" y="50" width="130" height="50" rx="4"/><text class="mid fg" x="275" y="72">queue</text><text class="mid dim sm" x="275" y="90">owns the request</text>
<rect class="blue" x="400" y="50" width="130" height="50" rx="4"/><text class="mid t-b" x="465" y="72">worker</text><text class="mid dim sm" x="465" y="90">owns it while I/O runs</text>
<rect class="live" x="590" y="50" width="150" height="50" rx="4"/><text class="mid t-g" x="665" y="72">future</text><text class="mid dim sm" x="665" y="90">hands it back</text>
<path class="ln" d="M150 75 H208" marker-end="url(#mv-a)"/><path class="ln" d="M340 75 H398" marker-end="url(#mv-a)"/><path class="ln" d="M530 75 H588" marker-end="url(#mv-a)"/>
<path class="ln-w dash" d="M665 102 V140 H85 V102" marker-end="url(#mv-a)"/>
<text class="t-w sm" x="250" y="132">future.get() returns the Box: the caller owns the page again</text>
<text class="dim sm" x="20" y="30">schedule(request)</text>
</svg>
```

The cost is that a read allocates (or recycles) a buffer per request and the caller copies out of the returned `Box`. For 8 KiB that is noise next to the I/O, and the buffer pool in module 1f is where you decide when to copy and when to hand ownership on.

## `Send` and `Sync`

Two marker traits, implemented automatically by the compiler, say which values may cross threads:

| trait | meaning | examples |
|---|---|---|
| `Send` | the value may be **moved** to another thread | `Box<PageData>`, `Arc<T>` where `T: Send + Sync`, `Mutex<T>` where `T: Send` |
| `Sync` | a **shared reference** `&T` may be used from several threads at once | `Mutex<T>`, `AtomicUsize`, `File` |
| neither | tied to one thread | `Rc<T>` (non-atomic count), raw pointers, `RefCell<T>` is `Send` but not `Sync` |

`thread::spawn` requires its closure and everything it captures to be `Send`, and `DiskIo: Send + Sync` is what lets an `Arc<dyn DiskIo>` be shared by workers. Break the promise (put an `Rc` in a request) and you get a compile error naming the field, instead of a crash a week later.

## Four ways to share between threads

| need | use | notes |
|---|---|---|
| give a value away | **move** it (`channel.put(request)`) | the sender cannot touch it again |
| many readers of one immutable value | `Arc<T>` | reference-counted, freed when the last owner drops |
| many threads mutate one value | `Arc<Mutex<T>>` / `Arc<RwLock<T>>` | the lock is inside, see the concept on `Mutex` |
| a counter or flag | atomics | see the concept on memory ordering |

> [!WHY] Why not share the page behind a lock?
> A `Mutex<Page>` would work and is what you may build later for *resident* pages (the buffer pool's frames). A request is different: it is a one-way hand-off with a clear end, and ownership transfer needs no lock at all and cannot deadlock.
