---
title: Trait objects: BusTub's virtual methods in Rust
summary: How a C++ class hierarchy becomes a trait, what dyn costs and buys, and why the disk is behind &dyn DiskIo instead of a generic parameter.
minutes: 7
---
BusTub has several "disks": the real `DiskManager`, `DiskManagerMemory` (a fixed-size array of pages) and `DiskManagerUnlimitedMemory`. Everything above them (the scheduler, the buffer pool) works with any of the three. That is **polymorphism**, and C++ and Rust spell it differently enough to be worth an explicit comparison.

## The C++ shape

```cpp
class DiskManager {
 public:
  virtual ~DiskManager() = default;
  virtual void ReadPage(page_id_t page_id, char *page_data);
  virtual void WritePage(page_id_t page_id, const char *page_data);
  virtual void DeletePage(page_id_t page_id);
};
class DiskManagerMemory : public DiskManager { void WritePage(...) override; /* ... */ };

BufferPoolManager(size_t pool_size, DiskManager *disk_manager);   // a raw base-class pointer
```

Every call through `disk_manager->WritePage(...)` goes through the object's **vtable**: a hidden pointer in each object leads to a table of function pointers, and the call is an indirect jump. The base class both defines the interface *and* is a concrete implementation, which is why `DiskManagerMemory` has to inherit from the real file-based class and override what it needs.

## The Rust shape

```rust
pub trait DiskIo: Send + Sync {
    fn read_page(&self, page_id: PageId, buf: &mut PageData) -> io::Result<()>;
    fn write_page(&self, page_id: PageId, data: &PageData) -> io::Result<()>;
    fn delete_page(&self, page_id: PageId);
}

impl DiskIo for DiskManager { /* ... */ }
impl DiskIo for DiskManagerMemory { /* ... */ }

pub fn copy_page(disk: &dyn DiskIo, from: PageId, to: PageId) -> io::Result<()> { /* ... */ }
```

A trait is *only* an interface: no data, no inheritance of an implementation. The three disks are unrelated types that each promise the same three methods. `&dyn DiskIo` is a **fat pointer**: two words, a pointer to the value and a pointer to its vtable for `DiskIo`. The vtable is built by the compiler for each `(type, trait)` pair, and a call through it is the same indirect jump as in C++.

| C++ | Rust |
|---|---|
| `class Base { virtual void f(); }` | `trait Base { fn f(&self); }` |
| `class D : public Base { void f() override; }` | `impl Base for D { fn f(&self) { … } }` |
| `Base*` / `Base&` | `&dyn Base` / `Box<dyn Base>` |
| `std::unique_ptr<Base>` | `Box<dyn Base>` |
| `std::shared_ptr<Base>` | `Arc<dyn Base>` (and `Send + Sync` if it crosses threads) |
| a missing `override` silently adds a new method | `impl` blocks list exactly the trait's methods; a typo is a compile error |
| object slicing: `Base b = derived;` copies only the base part | cannot happen: `dyn Trait` has no size, you can only hold it behind a pointer |

## Why `Send + Sync` and `&self`

`DiskIo: Send + Sync` is a promise made by every implementation: it may be moved to another thread (`Send`) and shared by reference between threads (`Sync`). The disk will be called from several scheduler workers at once, so the compiler must be told, and a type that is not thread-safe (say, one holding an `Rc`) is *rejected at the `impl` site* instead of corrupting memory at run time.

The methods take `&self`, not `&mut self`, because there is one shared disk and many callers. That pushes the locking *into* each implementation (the `Mutex` inside `DiskManager`, the one inside `DiskManagerMemory`), which is where it belongs: the caller cannot know what to lock.

## Generic or dynamic?

The other way to write `copy_page` is generic:

```rust
pub fn copy_page<D: DiskIo>(disk: &D, from: PageId, to: PageId) -> io::Result<()> { … }
```

This is **static dispatch**: the compiler makes one copy of the function per concrete `D` (monomorphisation) and the call is direct, so it can be inlined. It is faster per call and bigger in the binary. The real cost is not speed but **spread**: if `BufferPoolManager` holds a `D: DiskIo`, then `BufferPoolManager<D>` exists, so everything that holds a buffer pool is generic over `D`, and so on up the whole system until your `main` names the type. That is called *generic infection*.

For the disk, one indirect call per page I/O is noise next to the system call it leads to, so the course uses `&dyn DiskIo` / `Arc<dyn DiskIo>`: the disk's type disappears at the boundary, as it does in BusTub. Reach for generics instead when the call is in a **hot loop** and cheap (a comparator called per key comparison in the B+ tree is the example you will meet in project 2), and for `dyn` when the call is rare relative to its body and the type should not leak.

> [!WHY] Why the in-memory disks exist
> They are test doubles. A test of the buffer pool should not need a file, a temporary directory and cleanup; it should run in microseconds and be deterministic. Because both implement `DiskIo`, the same buffer-pool test runs against an in-memory disk in every unit test and against the real file in the boss stage. That is the payoff of the seam.

> [!NOTE] Object safety
> A trait can be used as `dyn Trait` only if its methods can be called without knowing `Self`: no generic methods, no `Self` in return position, no `where Self: Sized` methods you rely on. `DiskIo` obeys this by being a plain set of three methods. When you add a generic helper to a trait you plan to use as `dyn`, expect the compiler to refuse.
