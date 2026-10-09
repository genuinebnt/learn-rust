Databases delete pages all the time: a table is dropped, an index shrinks, a page is merged away. If the file only ever grew, a long-running database would be mostly holes. This stage makes space come back.

> [!CHECK] Pages A, B and C are written, then B is deleted and then A. Two new pages are written. In a design that reuses space, which places do the new pages get, and does the file grow? What if the file had no reuse at all: what would the third new page cost?
> ||The two new pages take the places A and B had (the most recently freed place first, if your free space is a stack, but any order satisfies the test), and the file does not grow. With no reuse every new page would be appended: after n deletes and n new pages the file would be n pages longer than the live data needs, forever.||
>
> - What does delete_page leave behind that write_page can use?
> - Does the order in which freed places are reused matter to the tests? Look at what they measure.
> - What is the file's length after 100 pages are written and 100 others come and go one at a time?

## The task

Implement `delete_page(page_id)` and make `write_page` use the space it frees.

- `delete_page(id)`: the page is forgotten and its space becomes available to later pages. Deleting an id that was never written, or was already deleted, does nothing (and costs nothing).
- After a delete, the same id may be written again; it is a new page. What a *read* of a deleted page returns is **unspecified**: do not rely on zeros, and do not promise them.
- **Space is reused.** The file does not keep growing when pages come and go. Precisely: after any sequence of operations, if at most `p` pages were ever live at the same moment, `get_db_file_size()` is at most the initial room, or twice `p` pages, whichever is larger, plus BusTub's one spare page (`(max(16, 2p) + 1) × 8 192` bytes). Growing the file by doubling meets this; so do other designs.

The tests check the bound after every operation of random sequences, and BusTub's own `DeletePageTest` shape: 100 live pages, then 200 more come and go one at a time, and the file must not grow at all.

## Your freedom

How freed space is remembered (a stack, a queue, a set, a bitmap), the order it is reused in, how the file grows (by doubling, by a fixed step, by exactly what is needed) and what you do with the bytes of a deleted page. The tests only measure the file's size and the read-what-you-wrote rule.

## The Rust toolbox

**A `Vec` is a stack.** `v.push(x)` and `v.pop()` (which returns `Option<T>`: `None` when empty) are `O(1)`, so a `Vec<usize>` of freed places is a free list that costs one word per hole.

**`let ... else` for the early exit.** `let Some(place) = pages.remove(&id) else { return; };` removes the page, or returns at once if there was none. It keeps the happy path unindented.

**`HashMap::remove` returns the old value.** `map.remove(&k)` gives `Option<V>`: both "was it there?" and "where was it?" in one call.

**Growing a file.** `file.set_len(n)` sets the length; growing it fills the new region with zeros without writing it (a *sparse file* on most filesystems), which is why doubling costs address space, not disk blocks. If `set_len` fails with `?`, the *bookkeeping* must not already claim the room: do the fallible step first.

**An invariant checker.** Write a `fn check(&self)` guarded by `#[cfg(debug_assertions)]` that asserts what must always be true (every place is live or free, never both, never neither) and call it at the end of each method that changes state. It costs nothing in a release build and finds corruption at the operation that caused it, which is worth more than any test.

**`usize` and `u64`.** Page counts are `usize`; file offsets and lengths are `u64`. Convert with `as u64` *before* multiplying by the page size, so a big count cannot overflow `usize` arithmetic on a narrow platform.

## If this is new

- **S3 Vec & slices**, the `push`/`pop` problems: `Vec` as a stack.
- **S1 Option & Result**, the `?` and `ok_or` problems, and `let ... else` (search the track for "else").
- **S4 Maps & sets**: `remove` and `entry`.

## Tests

- Deleting an unknown page does nothing; a deleted id can be written again; deleting one page leaves all others intact.
- Random sequences of writes, reads and deletes agree with a model (reads of deleted pages are not checked).
- The file never exceeds the bound in the contract, after every operation, and stays exactly the same length while the number of live pages does not grow (BusTub's `DeletePageTest`).

## Hints

### What does a delete leave behind?

Deleting a page must make *something* available to a later write. Think about what a write needs: a place. What do you have to keep so that the next new page can be given a place that is no longer in use?

### Reuse before you grow

When a new page needs a place, there are two sources: space freed earlier, and fresh space at the end of the file. Which should come first, and what makes the file grow only when it has to? Decide when the file is allowed to get longer, and make that the only place it does.

### The invariant, written down

Every place the file has is in exactly one of two states: used by a page, or free. State it in one sentence, and write the check. A place in neither state is a leak (the file grows with nothing to show); a place in both is two pages overwriting each other. Neither failure makes a small test fail.

## Performance

A delete is a table update and a push: no I/O at all. A write that reuses a place costs the same as any write; a write that grows the file adds one `set_len`. Growing by one page per allocation makes `n` allocations cost `n` calls; doubling costs `log₂ n` of them, because the total of `c + 2c + 4c + …` is under twice the last term: the usual amortised `O(1)` argument for `Vec::push`, applied to a file.

**Measure it.** Allocate 100 000 pages while counting `set_len` calls (wrap the call, or run under `strace -c -e trace=ftruncate`). Compare growth by one, by doubling and by a fixed 64 pages, and sketch calls against pages. Which one would you pick if `set_len` took a millisecond?

## Experiment

Optional. Predict first, then run.

1. **A leak, on purpose.** Remove the free-list push in your delete. Which tests fail, and with what message? Now put it back but pop from a *queue* instead of a stack: which tests notice, if any?
2. **Fragmentation.** Write 1 000 pages, delete every other one, then write 500 new pages. How long is the file? What would a design that always uses the *lowest* free place do differently, and when would you want that (hint: truncating the file)?

## Other designs

- **Stack (LIFO), BusTub's.** The most recently freed place is reused first: `O(1)`, and the recently touched place is likely still in the operating system's cache.
- **Queue (FIFO).** Places age before reuse; gentler on flash wear and on bugs where something still holds a stale reference.
- **Lowest place first** (a `BTreeSet`). `O(log n)`, but the file stays dense at the front, so the tail can be truncated and the space returned to the operating system.
- **Bitmap.** One bit per place: compact and cache-friendly, the form most real engines store on disk; finding a free bit is a scan unless you keep a hint.

## In BusTub

```cpp
std::filesystem::resize_file(db_file_name_, (page_capacity_ + 1) * BUSTUB_PAGE_SIZE);   // grow when page_capacity_ is exceeded
...
free_slots_.push_back(slot);                                                              // DeletePage
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::vector<size_t> free_slots_; free_slots_.back(); free_slots_.pop_back();` | `Vec<usize>`; `free.pop()` returns `Option<usize>` |
| `std::filesystem::resize_file(path, n)` | `file.set_len(n)?` |
| `assert(...)` in every build unless `NDEBUG` | `debug_assert!` (debug builds only) and `#[cfg(debug_assertions)]` |

**Port rule:** `pop_back()` on a possibly empty vector is undefined behaviour in C++ and an `Option` you must handle in Rust.

## Learn more

- [`File::set_len`](https://doc.rust-lang.org/std/fs/struct.File.html#method.set_len) · [`fs::metadata`](https://doc.rust-lang.org/std/fs/fn.metadata.html) · [`Vec::pop`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.pop)
- Rust by Example: [`let ... else`](https://doc.rust-lang.org/rust-by-example/flow_control/let_else.html)
