A sort that works for tables bigger than memory has to put its intermediate results somewhere: on pages of the buffer pool, which spills to disk when memory is short. The building block is the **run**: a sorted sequence of tuples stored on a list of pages. This stage writes the storage format and the reader and writer; the next stages generate and merge runs.

A run page is `[count: u32][tuple][tuple]...`, each tuple as `Tuple::serialize_to` writes it (a 4-byte length and the bytes). A run is just the list of its page ids.

## The task

In `src/execution/executors/external_merge_sort_executor.rs`:
- `RunBuilder::flush_page(&mut self)`: if the buffer holds tuples, allocate a page with `bpm.new_page()`, write the count (4 bytes, little-endian) and then the buffered bytes into it through a write guard (`bpm.write_page(id)`, `guard.get_data_mut()`), remember the page id, and empty the buffer;
- `RunBuilder::push(&mut self, tuple)`: a tuple that cannot fit even in an empty page is an `Execution` error; if it does not fit in what is left of the current page, flush the page first; then append the tuple's serialized bytes to the buffer and count it;
- `MergeSortRun::read_page(&self, index) -> Vec<Tuple>`: read the page's count and that many tuples (`Tuple::deserialize_from`; each occupies `4 + length` bytes);
- `RunIterator::next`: the next tuple of the current page; when the page is used up, load the next one with `read_page`; `None` after the last page.

(`finish` and `from_tuples`, the constructor shapes and `delete_pages` are given.)

## Tests

- A few tuples fit one page and read back equal and in order; an empty run has no pages and an empty iterator.
- A full page starts the next: 1000-byte tuples give 8 per page (`4 + 8 × 1004 ≤ 8192`), so 20 give 8 + 8 + 4 over 3 pages.
- A tuple too large for a page is an `Execution` error; one that exactly fills a page is fine.
- 5,000 tuples written through a 24-frame pool come back complete.
- Reading page by page and iterating agree.

## Syntax and methods

```rust
let page_id = self.bpm.new_page();                       // PageId
let mut guard = self.bpm.write_page(page_id);            // WritePageGuard: pinned + latched
guard.get_data_mut()[..4].copy_from_slice(&count.to_le_bytes());
let guard = self.bpm.read_page(id); let data = guard.get_data();       // &[u8; 8192]
tuple.serialize_to(&mut buf[at..]);  Tuple::deserialize_from(&data[at..])
u32::from_le_bytes(data[..4].try_into().unwrap())
```

## Notes

**Format: the simplest that works.** Tuples are variable-length and only read front to back, so no slot array is needed (unlike a table page): a count, then the tuples packed one after another. The reader walks the bytes: after each tuple the next starts `4 + len` bytes later.

**Buffer first, page second.** The builder accumulates a page's worth of bytes in a `Vec<u8>` and writes the page once when it is full. Allocating the page earlier would hold a pinned frame for the whole fill, and pin pressure is exactly what a spilling sort must avoid.

**Pages are the only memory a run uses.** A run is a `Vec<PageId>`; its tuples live in the buffer pool and, when the pool is full, on disk. `delete_pages` returns them (stage 4 does it after a merge).

**Guards are released at the end of the scope.** A page guard unpins on drop; hold it as briefly as you can (`read_page` decodes the tuples and returns, so no guard escapes the function).

## In BusTub

`external_merge_sort_executor.h`: `class MergeSortRun { std::vector<page_id_t> pages_; BufferPoolManager *bpm_; class Iterator {... operator++ operator* operator== operator!= (all "TODO(P3): Add implementation.")} Begin() End() }`. BusTub leaves the page format to you; this port fixes the one described above so that the tests can check page counts.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `auto page = bpm->WritePage(pid); memcpy(page.GetDataMut(), ...)` | `let mut g = bpm.write_page(pid); g.get_data_mut()[..n].copy_from_slice(..)` |
| `class Iterator { operator++, operator*, operator!= }` and `Begin()/End()` | `impl Iterator for RunIterator` with `next() -> Option<Tuple>` |
| reinterpret the page bytes as a struct | explicit little-endian reads and writes |
| manual `bpm->DeletePage(pid)` for each page | `delete_pages(self)` consumes the run |

**Port rule:** a C++ iterator class with `++`, `*`, `!=` is one `Iterator::next`.

## Learn more
- [`u32::to_le_bytes`](https://doc.rust-lang.org/std/primitive.u32.html#method.to_le_bytes) · [`slice::copy_from_slice`](https://doc.rust-lang.org/std/primitive.slice.html#method.copy_from_slice) · [External sorting](https://en.wikipedia.org/wiki/External_sorting)

## Performance

Each page is written once and read once per pass. With 8 KiB pages a run of a million 8-byte tuples is about 1,500 pages. Writing through the buffer pool means pages stay in memory while the pool has room and are flushed when it does not, so small sorts never touch the disk.

**Measure it.** Write 1,000,000 tuples into a run with a 24-frame pool and time the write and the read; the pool's eviction is doing the spilling.

## Hints

### Count first, tuples after

The count lives in the first 4 bytes, so the tuples start at offset 4 and the buffer you accumulate holds only tuples. Do not write the count until you flush.

### The capacity check includes the count

A page holds `8192 - 4` bytes of tuples. A tuple fits an empty page iff `4 + size ≤ 8192`; it fits the current page iff `4 + buffer.len() + size ≤ 8192`.

### Do not hold a guard across calls

`RunIterator::next` calls `read_page`, which reads, decodes and releases. Keeping a read guard alive in the iterator would pin a frame per open run: a K-way merge would pin K frames for nothing.
