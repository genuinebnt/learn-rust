BusTub's disks are polymorphic: the real file-backed manager, and in-memory ones for tests. In C++ that is a base class with virtual methods; in Rust it is a trait, and this stage is where you first meet `dyn`: the `DiskIo` trait, its impl for `DiskManager`, and `copy_page`, a function that has to work on any disk.

**Where this fits.** The buffer pool will use *a disk*, not specifically the file one: tests run on in-memory disks. In C++ that is a base class with `virtual` methods. In Rust, a trait.

## The task

`DiskIo` (given) lists what a disk can do: `read_page`, `write_page`, `delete_page`. In `src/storage/disk/disk_manager.rs`:
- implement `DiskIo for DiskManager`: three one-line methods that call the `DiskManager` methods you wrote;
- implement `copy_page(disk, from, to)`: read page `from` into a local buffer, write it as page `to`, through whatever disk was passed in.

## Tests

- A `DiskManager` used as `&dyn DiskIo` writes, reads and deletes for real (its counters move).
- `Arc<dyn DiskIo>` can be handed to four threads that each write a page.
- `copy_page` copies; copying a never-written page writes zeros; it does exactly one read and one write on a test double.

## Syntax and methods

```rust
impl DiskIo for DiskManager {
    fn read_page(&self, page_id: PageId, buf: &mut PageData) -> io::Result<()> {
        DiskManager::read_page(self, page_id, buf)   // the inherent method, named by its path
    }
}
pub fn copy_page(disk: &dyn DiskIo, from: PageId, to: PageId) -> io::Result<()> { /* .. */ }
let mut buf = [0u8; BUSTUB_PAGE_SIZE];               // 8 KiB on the stack is fine
```

## Notes

A struct's own method (`inherent`) wins over a trait method of the same name, so `self.read_page(..)` inside the impl would call the inherent one anyway; writing `DiskManager::read_page(self, ..)` makes that explicit. `&dyn DiskIo` is a reference to *some* disk, chosen at run time (a vtable call). `trait DiskIo: Send + Sync` says every disk can be shared between threads, which `Arc<dyn DiskIo>` needs.

## In BusTub

```cpp
virtual void WritePage(page_id_t page_id, const char *page_data);   // DiskManager's virtual methods
virtual void ReadPage(page_id_t page_id, char *page_data);
virtual void DeletePage(page_id_t page_id);
class DiskManagerMemory : public DiskManager { /* overrides them */ };
```

## The C/C++ way
| C | C++ | Rust |
|---|---|---|
| a struct of function pointers: `struct file_ops { int (*read)(..); int (*write)(..); }` (the Linux VFS does this) | `class Base { virtual void ReadPage(..) = 0; };` + `class Derived : public Base` | `trait DiskIo { fn read_page(..); }` + `impl DiskIo for DiskManager` |
| call through the table: `ops->read(..)` | call through a `Base *` / `Base &` (vtable) | call through `&dyn DiskIo` / `Box<dyn DiskIo>` / `Arc<dyn DiskIo>` (vtable) |
| (none) | `template <class Disk>` compile-time polymorphism | generics: `fn f<D: DiskIo>(d: &D)` (monomorphised, no vtable) |
| (none) | `override`; a virtual destructor, or deleting through a base pointer is UB | `Drop` runs for the concrete type through `Box<dyn Trait>`: no virtual-destructor mistake exists |
| `std::unique_ptr<Base>` / `std::shared_ptr<Base>` | | `Box<dyn Trait>` / `Arc<dyn Trait>` |

**Port rule:** a C++ abstract base class with only pure virtuals is a trait. One with data members and non-virtual helpers is a struct plus a trait (or a generic).
`: Send + Sync` is what C++ leaves to documentation: "this may be used from many threads".

## Learn more
- The Rust Book: [defining shared behaviour with traits](https://doc.rust-lang.org/book/ch10-02-traits.html) and [trait objects](https://doc.rust-lang.org/book/ch18-02-trait-objects.html)

## Performance

Calling through `&dyn DiskIo` is one indirect call through the vtable; it cannot be inlined, and it costs a few nanoseconds more than a direct call. A page I/O costs a syscall (microseconds) or an 8 KiB copy (hundreds of nanoseconds), so the indirection is lost in the noise. A generic `copy_page<D: DiskIo>` would inline and be faster per call, at the price of one copy of the function per disk type and the generic parameter spreading upward (see the concept article).

**Measure it.** Time `copy_page` on a `DiskManagerUnlimitedMemory` through `&dyn DiskIo` and through a generic version over 100 000 pages. Expect the difference to be small next to the 8 KiB copy itself; if it is not on your machine, that is worth understanding before you decide.

## Hints

### Why `&dyn DiskIo` and not a generic parameter

A `BufferPoolManager<D: DiskIo>` would monomorphise and push the disk type into every signature above it. BusTub uses virtual dispatch (`DiskManager` has virtual methods that the memory disks override), and the cost of one indirect call per page I/O is noise next to a syscall. That is why `copy_page` takes `&dyn DiskIo`: it has to work on all three disks. The trait is `Send + Sync` with `&self` methods because each implementation owns its own locking.

### Let the compiler enforce thread safety

`DiskIo: Send + Sync` is a promise every implementation makes, and the compiler holds you to it. Try writing a test double that records its calls in an `Rc<RefCell<Vec<_>>>`: the `impl` is rejected at compile time, because an `Rc` cannot be shared between threads. Fix it with `Arc<Mutex<_>>` and note what you just did: you turned a data race you would have hunted with ThreadSanitizer in C++ into a type error. This is the single biggest thing to take from the trait.
