Two disks that never touch the file system: a fixed-size one (writing past its capacity must fail loudly, as a full disk does) and an unbounded one (pages appear, zeroed, on first write). They are what makes the buffer pool and the scheduler testable without temporary files.

## Part 1 · DiskManagerMemory: a disk of fixed size

**Where this fits.** Tests want a disk with no files and no waiting. Two in-memory disks live in `src/storage/disk/disk_manager_memory.rs`; this is the first.

### The task

`DiskManagerMemory::new(capacity)` holds `capacity` pages in one byte buffer: page `n` is bytes `n * 8192 .. (n + 1) * 8192`. Implement `new`, `range` (the bounds check and the byte range of a page), `read_page` and `write_page` (which counts the write). Ids outside `0..capacity` **panic** with a message saying the disk ran out of space: that is a bug in the caller, not an I/O error. A fresh disk reads as zeros. `delete_page` is given (it does nothing).

### Tests

- Pages read back and don't overlap; page `capacity`, page 100 on a 4-page disk and `PageId(-1)` panic with "ran out of disk space"; the disk works as `Arc<dyn DiskIo>`.

### Syntax and methods

```rust
vec![0u8; n]                                        // n zero bytes
assert!(cond, "page {} out of range", id);          // panics with the message when cond is false
let at: std::ops::Range<usize> = start..start + BUSTUB_PAGE_SIZE;
buf.copy_from_slice(&memory[at.clone()]);            // both sides must have the same length, or it panics
self.memory.lock().unwrap()[at].copy_from_slice(data);
```

### In BusTub

```cpp
BUSTUB_ASSERT(static_cast<size_t>(page_id) < page_capacity_, "Ran out of disk space for limited memory disk manager implementation");
size_t offset = static_cast<size_t>(page_id) * BUSTUB_PAGE_SIZE;
memcpy(memory_ + offset, page_data, BUSTUB_PAGE_SIZE);
```

BusTub's `ReadPage` doesn't check the bound at all (undefined behaviour). Here both do.

### The C/C++ way
| C / C++ | Rust |
|---|---|
| `new char[n]` ... `delete[] p` (manual; BusTub's destructor does this) | `vec![0u8; n]`: freed by `Drop` |
| `malloc(n)` is uninitialised; `calloc(1, n)` is zeroed | `vec![0; n]` is always initialised: no "uninitialised read" bug class |
| `memcpy(dst + off, src, size)`: no bounds check; overlapping ranges are UB | `dst[a..b].copy_from_slice(src)`: panics on a length mismatch; `copy_within` for overlap (`memmove`) |
| `BUSTUB_ASSERT(cond, "msg")` (aborts in debug builds) | `assert!(cond, "msg {}", x)` (a panic; in every build unless you use `debug_assert!`) |
| `assert(x)` from `<assert.h>` vanishes with `-DNDEBUG` | `assert!` always runs; `debug_assert!` is the vanishing one |

**Pitfall in the C++:** `DiskManagerMemory::ReadPage` has no bounds check at all, so reading past the end is undefined behaviour. Rust slices make that a panic.

### Learn more
- [`copy_from_slice`](https://doc.rust-lang.org/std/primitive.slice.html#method.copy_from_slice) · [`assert!`](https://doc.rust-lang.org/std/macro.assert.html) · [`Range`](https://doc.rust-lang.org/std/ops/struct.Range.html)

## Part 2 · DiskManagerUnlimitedMemory: pages on demand

**Where this fits.** Most of BusTub's tests use this disk: no capacity to choose, pages appear when first written.

### The task

Pages live in a `Vec<Option<Box<PageData>>>` indexed by page id; `None` means "never written". In `disk_manager_memory.rs`, `DiskManagerUnlimitedMemory`:
- `write_page`: grow the `Vec` to length `id + 1` (filled with `None`), create the page if it is `None`, copy the data in, count the write;
- `read_page`: copy the page out if it exists, otherwise zero the buffer. Reading never creates a page;
- `get_memory_usage`: the number of existing pages times `BUSTUB_PAGE_SIZE`.

### Tests

- Pages 0, 1, 500 and 5000 read back and gaps read as zeros; `get_memory_usage` counts only pages that exist; eight threads writing 25 pages each all read back.

### Syntax and methods

```rust
pages.resize_with(at + 1, || None);                  // grow, filling new slots with the closure's result
let page = pages[at].get_or_insert_with(|| Box::new([0u8; BUSTUB_PAGE_SIZE]));   // &mut Box<PageData>
page.copy_from_slice(data);                           // a Box<[u8; N]> derefs to the array
match pages.get(at) { Some(Some(page)) => buf.copy_from_slice(&**page), _ => buf.fill(0) }
pages.iter().filter(|p| p.is_some()).count()
```

### Notes

Why `Option<Box<..>>` and not `Option<PageData>`? A `PageData` is 8 KiB, so a `Vec` of them reserves 8 KiB for every id up to the highest written. `Option<Box<T>>` is **one pointer wide** (the null pointer means `None`, a "niche"), so empty ids cost 8 bytes.

### In BusTub

```cpp
if (page_id >= static_cast<int>(data_.size())) { data_.resize(page_id + 1); }
if (data_[page_id] == nullptr) { data_[page_id] = std::make_shared<ProtectedPage>(); }
memcpy(ptr->first.data(), page_data, BUSTUB_PAGE_SIZE);
```

BusTub's version also has a **latency simulator** (sleeping 1 ms per random access, 0.1 ms for nearby pages) so tests can see a buffer pool hide disk latency. It comes in with the buffer pool module.

### The C/C++ way
| C++ | Rust |
|---|---|
| `std::vector<std::shared_ptr<Page>> data_; data_.resize(n);` | `Vec<Option<Box<PageData>>>`; `resize_with(n, \|\| None)` |
| a null pointer means "no page": `if (data_[i] == nullptr)` | `None`; `Option<Box<T>>` is the same size as a pointer, and `None` *is* the null pointer |
| `std::make_shared<T>()` | `Box::new(..)` for sole ownership; `Arc::new(..)` only if it is really shared |
| `std::optional<T>` | `Option<T>` |
| `std::shared_mutex` per page (BusTub's `ProtectedPage`) | `RwLock<..>`: a later stage when pages are shared |
| `std::this_thread::get_id()` | `std::thread::current().id()` |

**Port rule:** `shared_ptr` is the *last* resort in Rust, not the default. Ask "who owns this?": one owner means `Box`, many means `Arc`. BusTub uses `shared_ptr` liberally because C++ has no other cheap way to say "keep this alive".

### Learn more
- [`Option::get_or_insert_with`](https://doc.rust-lang.org/std/option/enum.Option.html#method.get_or_insert_with) · [`Vec::resize_with`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.resize_with) · [niche optimisation](https://doc.rust-lang.org/std/option/index.html#representation)

## Performance

`DiskManagerMemory` is one flat `Vec<u8>`: a page I/O is an O(1) range computation and one 8 KiB `memcpy` under a `Mutex`. `DiskManagerUnlimitedMemory` is a `Vec<Option<Box<PageData>>>` indexed by page id: O(1) as well, but it holds one 8-byte slot for *every id up to the largest written*, whether or not the page exists. For ids from the buffer pool, which are dense, that is fine. For an id like 1 000 000 000 the vector would be 8 GB of `None`s, which is why `get_memory_usage` counts pages that exist rather than the vector's size.

A `HashMap<PageId, Box<PageData>>` has no such cliff but pays a hash and a pointer chase per access. Knowing which one your workload needs is the lesson.

**Measure it.** Write pages 0, 1, 500 and 5000 and print `get_memory_usage()` (four pages) next to the process's resident size. Write one page with id 50 000 000 and watch what happens to memory.

## Hints

### An in-memory disk still has to say no

`DiskManagerMemory` has a fixed capacity: writing page `capacity` is the in-memory version of a full disk, and the tests expect a loud failure rather than a silent write somewhere else. The unlimited disk has the opposite contract: pages appear, zeroed, on first write, and a page never written reads as zeros. Decide what each stores (one flat buffer versus one allocation per page), and what `get_memory_usage` should count. It should not count pages that were never written.

### Panic or `Err`?

The real disk returns `io::Result` because the environment can fail (the disk is full, the file vanished). The fixed in-memory disk panics when a page id is out of range, as BusTub's `BUSTUB_ASSERT` does, because that is a caller bug rather than an environmental failure. Decide the line you draw between a precondition violation (panic) and an operational error (`Err`), and say it in a comment: the buffer pool code above will rely on it.
