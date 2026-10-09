**Where this fits.** Columns, schemas, tuples and a table page used together, the way the table heap of module 3c will use them: fill a page, start another when it is full, link them, read every row back by its record id.

> [!CHECK] A table is a chain of pages, and a row's address is `(page id, slot)`. A page is copied byte for byte, as the buffer pool does when it evicts and re-reads. Which of your design decisions must hold for the copy to read back the same rows? Name one thing a page could do that would break this.
> ||Every piece of state the page needs must be inside its 8 KiB: the tuple count, the slots, the next-page link. A page that kept a count in a Rust field, a cached "free space" in the struct, or a pointer into another page would lose it when only the bytes were copied. Record ids stay valid across the copy because they name a page and a slot, not a memory address.||
>
> - Where is the next page's id stored?
> - What would happen to a cached value in the `TablePage` struct after eviction?
> - What do the page ids in a record id refer to?

## The task

Nothing new to design.

- **A chain of pages.** For random schemas and rows (1 to 7 columns, every type, NULLs, text): insert 20 to 79 rows, starting a new page and linking it when the current one is full; copy every page's bytes; follow the chain from page 0 counting tuples; read every row back by its record id and compare it value by value.
- **Values after the trip.** A value compared after a trip through bytes still compares like the original.
- **The course's page test** (`table_page_test.rs`): a page of tuples comes back value by value, deleting marks without moving, an in-place update, and a table as a chain of pages.

## Your freedom

None new.

## The Rust toolbox

**Copying a page.** `let copied = pages.clone();` clones a `Vec<[u8; 8192]>`; `TablePage::new(&copied[i][..])` reads a copy.

**Reading a failure.** A property failure prints the schema (`to_string(true)`) and the column, the value put in and the value that came out.

## If this is new

- Everything is in the earlier stages of this module.

## Tests

- Rows survive a chain of pages copied byte for byte (random schemas and rows).
- Values compare equally after a trip through bytes.
- The course's table page tests.

## Hints

### The chain breaks after the first page

If rows on later pages are wrong, the link or the slot numbering is: check `get_next_page_id` after `set_next_page_id`, and that `init` is called on the new page.

## Performance

A table's scan reads pages in chain order: one page latch and a loop over its slots per page. The page's overhead decides how many pages the same data needs; the earlier experiment (a smaller slot) shows the effect.

## Experiment

Optional. Predict first, then run.

1. **Wasted space.** Compute the fraction of each page not holding tuple bytes for your layout and a typical schema.
2. **A delete-heavy page.** Mark half the tuples deleted. How much of the page is garbage, and what would reclaim it?

## Other designs

None for this stage. The *Other designs* sections of 3b-01 to 3b-04 list the alternatives to compare with yours.

## In BusTub

BusTub has no unit test for `TablePage` alone; it is exercised through `TableHeapTest` (module 3c's boss). This stage's test file is the course's own.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::vector<char *> pages` | `Vec<[u8; BUSTUB_PAGE_SIZE]>` |
| `memcpy(copy, page, BUSTUB_PAGE_SIZE)` | `let copy = page;` (an array is `Copy`) |

**Port rule:** a page buffer is a fixed-size array, which Rust copies by assignment.

## Learn more

- [Arrays are `Copy`](https://doc.rust-lang.org/std/primitive.array.html) when their elements are
