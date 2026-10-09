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

```svg
caption: A &dyn DiskIo is two words: a pointer to the value and a pointer to the vtable the compiler built for (DiskManager, DiskIo). A method call loads the function pointer from the vtable and jumps through it.
<svg viewBox="0 0 760 320" role="img" aria-label="A fat pointer with a data pointer to a DiskManager value and a vtable pointer to a table of function pointers">
<defs><marker id="vt-a" markerWidth="9" markerHeight="9" refX="7" refY="4.5" orient="auto"><path d="M0 0 L9 4.5 L0 9 z" style="fill:var(--dim)"/></marker></defs>
<text class="dim sm" x="20" y="34">disk: &amp;dyn DiskIo</text>
<rect class="hot" x="20" y="44" width="200" height="40" rx="4"/><text class="mid fg" x="120" y="69">data ptr</text>
<rect class="violet" x="20" y="84" width="200" height="40" rx="4"/><text class="mid fg" x="120" y="109">vtable ptr</text>
<rect class="box" x="290" y="30" width="220" height="74" rx="4"/><text class="t-a" x="304" y="54">DiskManager</text>
<text class="dim sm" x="304" y="74">db_io: Mutex&lt;DbIo&gt;</text><text class="dim sm" x="304" y="90">log_io, counters ...</text>
<path class="ln" d="M220 64 H288" marker-end="url(#vt-a)"/>
<path class="ln" d="M220 104 H254 V155 H288" marker-end="url(#vt-a)"/>
<text class="t-v sm" x="290" y="130">vtable for (DiskManager, DiskIo)</text>
<rect class="box" x="290" y="142" width="220" height="26"/><text class="dim" x="304" y="160">drop_in_place</text><rect class="box" x="290" y="168" width="220" height="26"/><text class="dim" x="304" y="186">size</text><rect class="box" x="290" y="194" width="220" height="26"/><text class="dim" x="304" y="212">align</text><rect class="blue" x="290" y="220" width="220" height="26"/><text class="t-b" x="304" y="238">read_page</text><rect class="blue" x="290" y="246" width="220" height="26"/><text class="t-b" x="304" y="264">write_page</text><rect class="blue" x="290" y="272" width="220" height="26"/><text class="t-b" x="304" y="290">delete_page</text>
<text class="big" x="548" y="168">disk.write_page(id, &amp;buf)</text>
<text class="dim sm" x="548" y="192">1. load the vtable pointer</text><text class="dim sm" x="548" y="208">2. load write_page from it</text><text class="dim sm" x="548" y="224">3. call it with the data ptr</text>
<text class="dim sm" x="548" y="256">the layout is a compiler</text><text class="dim sm" x="548" y="272">detail, not a promise</text>
</svg>
```

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

## In real code

### The API you will use

| syntax | meaning | when |
|---|---|---|
| `trait DiskIo: Send + Sync { fn read_page(&self, ..) -> io::Result<()>; }` | an interface; `Send + Sync` are supertraits | defining the seam |
| `impl DiskIo for DiskManager { .. }` | one implementation | each concrete disk |
| `&dyn DiskIo` / `Box<dyn DiskIo>` / `Arc<dyn DiskIo>` | a trait object: any implementor, dispatched at run time | when the type must not spread |
| `fn f<D: DiskIo>(d: &D)` / `impl DiskIo` | static dispatch: one copy of `f` per type | hot paths |
| `dyn Any` + `downcast_ref::<T>()` | recover the concrete type | rare: tests and plugins |
| `Box::new(x) as Box<dyn Trait>` | coerce a concrete value | building a collection of mixed types |

```rust test
use std::io;
use std::sync::{Arc, Mutex};

trait Disk: Send + Sync {
    fn write(&self, page: usize, data: &[u8]) -> io::Result<()>;
    fn read(&self, page: usize) -> io::Result<Vec<u8>>;
}

struct MemoryDisk { pages: Mutex<Vec<Vec<u8>>> }

impl Disk for MemoryDisk {
    fn write(&self, page: usize, data: &[u8]) -> io::Result<()> {
        let mut pages = self.pages.lock().unwrap();
        if pages.len() <= page { pages.resize(page + 1, Vec::new()); }
        pages[page] = data.to_vec();
        Ok(())
    }
    fn read(&self, page: usize) -> io::Result<Vec<u8>> {
        Ok(self.pages.lock().unwrap().get(page).cloned().unwrap_or_default())
    }
}

// Works for ANY disk: the function never names a concrete type.
fn copy_page(disk: &dyn Disk, from: usize, to: usize) -> io::Result<()> {
    let data = disk.read(from)?;
    disk.write(to, &data)
}

#[test]
fn one_function_every_disk() {
    let disk: Arc<dyn Disk> = Arc::new(MemoryDisk { pages: Mutex::new(Vec::new()) });
    disk.write(0, b"hello").unwrap();
    copy_page(&*disk, 0, 3).unwrap();
    assert_eq!(disk.read(3).unwrap(), b"hello");
}
```

```rust test
use std::fmt::Debug;

trait Replacer { fn victim(&mut self) -> Option<u32>; fn name(&self) -> &'static str; }
struct Fifo(Vec<u32>);
struct Lifo(Vec<u32>);
impl Replacer for Fifo { fn victim(&mut self) -> Option<u32> { if self.0.is_empty() { None } else { Some(self.0.remove(0)) } } fn name(&self) -> &'static str { "fifo" } }
impl Replacer for Lifo { fn victim(&mut self) -> Option<u32> { self.0.pop() } fn name(&self) -> &'static str { "lifo" } }

// Static dispatch: the compiler writes one copy per concrete type. Dynamic dispatch: one copy, one indirect call.
fn evict_all_static<R: Replacer>(mut r: R) -> Vec<u32> { std::iter::from_fn(|| r.victim()).collect() }
fn evict_all_dyn(r: &mut dyn Replacer) -> Vec<u32> { std::iter::from_fn(|| r.victim()).collect() }

#[test]
fn static_versus_dynamic_dispatch() {
    assert_eq!(evict_all_static(Fifo(vec![1, 2, 3])), vec![1, 2, 3]);
    let mut policies: Vec<Box<dyn Replacer>> = vec![Box::new(Fifo(vec![1, 2, 3])), Box::new(Lifo(vec![1, 2, 3]))];
    let out: Vec<(&str, Vec<u32>)> = policies.iter_mut().map(|p| (p.name(), evict_all_dyn(p.as_mut()))).collect();
    assert_eq!(out, vec![("fifo", vec![1, 2, 3]), ("lifo", vec![3, 2, 1])]);
}
```

### In the exercises

- **1a-04:** `DiskIo` has three methods and is `Send + Sync`; `DiskManager` implements it by forwarding to its own methods, and `copy_page` works through any of them.
- **1a-04:** `DiskManagerMemory` and `DiskManagerUnlimitedMemory` are two more `impl DiskIo` blocks; one test runs the same operations against all three and compares them with a model.
- **1b-02:** the scheduler stores an `Arc<dyn DiskIo>` and the worker's closure clones it; this is why the disk's concrete type never appears in the scheduler's signature.

### Where it is used

- **Plug-in architectures**: a database's storage engine, a logging backend or a filesystem driver behind one trait (MySQL's storage-engine API, `log::Log`, `std::io::Write`).
- **Test doubles**: swap the real network or disk for an in-memory fake that records calls.
- **Heterogeneous collections**: a `Vec<Box<dyn Executor>>` is the shape of a query plan, a tree of operators with different types (module 3).
- **Where not**: tight inner loops (use generics so the call can be inlined).
