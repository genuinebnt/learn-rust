# Porting C and C++ systems code to Rust

The reference for Section K (docs/SYSTEMS.md). It answers one question over and over: *"I have this C or C++ construct.
What does Rust do instead, and why is it different?"* Every row here is a **drill target**: each links to problems in the
K tracks and becomes an idiom card (SYSTEMS.md §8).

Two codebases drive the examples because they are what the owner is porting or will port:

- **BusTub** (CMU's teaching database, `cmu-db/bustub`, C++17, MIT licensed): buffer pool, extendible hash index, B+ tree,
  executors, MVCC, lock manager, WAL.
- **OSDev** (wiki.osdev.org, C and C++ for x86 kernels): paging, GDT/IDT, allocators, scheduler, drivers, file systems, ELF,
  networking.

Rules of thumb that hold everywhere:

1. **Rust makes ownership a type, so every pointer in the C++ must be classified before it is translated.** Owning,
   borrowed, nullable, array-with-length, out-parameter, opaque handle. The class decides the Rust type (§0).
2. **A C++ buffer is `char *buf` plus a length you carry around. A Rust buffer is `&[u8]` or `&mut [u8]`: the length is part
   of the value and every access is checked.** Most `memcpy`/`memset`/pointer-arithmetic code collapses into slice methods.
3. **Rust has no implicit layout.** A struct has no guaranteed field order, padding or endianness unless you say
   `#[repr(C)]` and encode bytes yourself. On-disk and on-wire formats are *encoded*, not *cast*, unless a zero-copy view
   (§1.1) is deliberate.
4. **Locks own their data.** `std::mutex` next to the thing it protects becomes `Mutex<T>`; you cannot touch the data
   without the guard. This is the biggest shape change in concurrent code.
5. **Reach for `unsafe` last, and wrap it once.** Every `unsafe` block needs a `// SAFETY:` comment, and the API around it
   must be impossible to misuse from safe code (the rest of the program is the proof obligation).

---

## 0. How to port a C++ module (the workflow)

Do this before writing any Rust. Each step has a drill in K1.

1. **Inventory the types.** For each class: what does it own, what does it borrow, who frees it, can it be copied or moved.
   C++ answers hide in the destructor, the deleted copy constructor, `std::shared_ptr` vs `std::unique_ptr` vs raw `*`.
2. **Classify every pointer and reference.**
   | In the C++ | Meaning | Rust |
   |---|---|---|
   | `T *` that is deleted by the class | owning | `Box<T>` (one), `Vec<T>`/`Box<[T]>` (array) |
   | `std::unique_ptr<T>` | owning, unique | `Box<T>` |
   | `std::shared_ptr<T>` | shared ownership | `Arc<T>` (threads) / `Rc<T>` (one thread) |
   | `T *` / `T &` that outlives nobody | borrowed | `&T` / `&mut T` with a lifetime |
   | `T *` that may be `nullptr` | optional borrow | `Option<&T>` / `Option<&mut T>` |
   | `T *` + `size_t n` | array view | `&[T]` / `&mut [T]` |
   | `const char *` NUL-terminated | C string | `&CStr` (FFI only); otherwise `&str` or `&[u8]` |
   | `void *` + a type tag | erased value | an enum, a generic, or `Box<dyn Any>` |
   | `T **` / `T &` out-parameter | extra return value | return `(A, B)`, `Option<T>`, or `Result<T, E>` |
   | `T *` that is "the next element" in a list you built | link | an index (`u32`), `Option<Box<T>>`, or `Option<NonNull<T>>` |
   | `std::weak_ptr<T>` | non-owning back-reference | `Weak<T>` (or an index) |
3. **Find the shared mutable state.** Every field touched by two threads, every `static`, every `mutable`, every
   `std::atomic`, every lock. In Rust each becomes `Mutex<T>`/`RwLock<T>`/atomic, and which one you pick is a design
   decision (K12, K13).
4. **List the layout contracts.** Anything written to a file, a socket or a device. These are the places `repr(C)`,
   explicit byte offsets and endianness matter. Write the format down as a table of `(offset, size, name)` first.
5. **List what the C++ relies on being undefined behaviour.** Type punning through `reinterpret_cast`, reading padding,
   signed overflow, out-of-bounds "that always worked", iterator invalidation, use-after-move, uninitialised reads (§4). Each
   has a defined Rust answer.
6. **Write characterization tests first.** Port the C++ test file (BusTub's `test/` is gtest) before the code. Where the
   C++ is a black box, capture golden traces from the real implementation and assert against them (SYSTEMS.md §3.3).
7. **Port bottom-up, behaviour first, performance second.** Leaf types (page layouts, replacer, hash functions), then the
   stateful managers, then the concurrent wrappers. Keep the first version `Vec`/`HashMap`/`Mutex`, then specialise.
8. **Compare with the original on the same inputs** (golden traces, differential tests). Port faithfully; improve only
   after the tests agree.

---

## 1. The Rosetta tables

### 1.1 Bytes, pointers and memory

| C / C++ | Rust | What changes |
|---|---|---|
| `char *buf, size_t n` | `&[u8]` / `&mut [u8]` | length travels with the pointer; indexing is bounds-checked |
| `const char *` read-only view | `&[u8]` | cannot be written through; the compiler enforces it |
| `char buf[4096]` on the stack | `[u8; 4096]` | arrays are values; passing one copies it, so pass `&mut buf` or `&mut buf[..]` |
| `std::vector<char>` | `Vec<u8>` | `Vec` owns; `&v[..]` / `v.as_slice()` borrows |
| `uint8_t`, `unsigned char` | `u8` | `char` in Rust is a 4-byte Unicode scalar, never a byte |
| `memcpy(dst, src, n)` | `dst[..n].copy_from_slice(&src[..n])` | slices must have equal length (panics otherwise); non-overlapping is guaranteed by the borrow rules |
| `memmove(dst+a, dst+b, n)` | `buf.copy_within(b..b+n, a)` | overlap-safe within one slice |
| `memset(p, 0, n)` | `p[..n].fill(0)` | |
| `memcmp(a, b, n)` | `a[..n] == b[..n]` or `a[..n].cmp(&b[..n])` | slices implement `Eq`/`Ord` lexicographically |
| `strlen`, `strchr` | `memchr::memchr(b, hay)`, `iter().position(..)` | |
| `p[i]` with `p` a raw pointer | `slice[i]` (checked) / `slice.get(i)` / `get_unchecked(i)` (unsafe) | decide per hot path; `get` returns `Option` |
| `p + k` pointer arithmetic | `&slice[k..]`, `slice.split_at(k)`, `chunks`, `ptr.add(k)` (unsafe) | prefer subslices; `ptr.add` only inside an unsafe abstraction |
| walking with two pointers `[p, end)` | `slice.iter()`, `chunks_exact(n)`, `windows(n)`, `split_first()` | iterators replace begin/end pairs |
| split a buffer into a header and a body | `let (head, body) = buf.split_at_mut(HEADER);` | two disjoint `&mut` at once, safely |
| `std::span<T>` | `&[T]` / `&mut [T]` | |
| `sizeof(T)` | `size_of::<T>()` | for a slice, `size_of_val(&s)` |
| `alignof(T)` | `align_of::<T>()` | |
| `offsetof(S, f)` | `core::mem::offset_of!(S, f)` (stable 1.77) | works for `repr(C)` and default layout |
| `static_assert(sizeof(X) == 8)` | `const _: () = assert!(size_of::<X>() == 8);` | fails the build |
| `uint32_t x = *(uint32_t*)(buf + 4)` (misaligned, host endian) | `u32::from_le_bytes(buf[4..8].try_into().unwrap())` | explicit endianness, no alignment requirement, no UB |
| `*(uint32_t*)(buf + 4) = x` | `buf[4..8].copy_from_slice(&x.to_le_bytes())` | |
| `memcpy(&x, buf + 4, sizeof x)` | `let x = u32::from_le_bytes(buf[4..8].try_into()?)` | the portable idiom; the compiler emits one load |
| `reinterpret_cast<Header *>(page)` | zero-copy view: `bytemuck::from_bytes::<Header>(&page[..size_of::<Header>()])` or `zerocopy::Ref` | checked size and alignment; `Header` must be `Pod`/`FromBytes`; or decode field by field |
| `reinterpret_cast<T *>(raw)` where `T` has flexible array | a `#[repr(C)]` header plus a *computed* subslice: `bytemuck::cast_slice(&page[HEADER..])` | there is no `T[0]` member; you slice the tail |
| `T arr[0]` / `T arr[]` flexible array member | tail subslice, or a dynamically sized type `struct Page { h: Header, rest: [u8] }` | |
| `union { uint32_t u; float f; }` | `f32::from_bits(u)` / `x.to_bits()`; an `enum` for tagged unions | type punning through a union is `unsafe` and rarely needed |
| `struct { unsigned a:3, b:5; }` bit-field | `bitflags!` or manual `(x >> 3) & 0x1f` helpers in a newtype | field order and packing of C bit-fields is implementation-defined; Rust encodes it explicitly |
| `#pragma pack(1)` / `__attribute__((packed))` | `#[repr(C, packed)]` but **never take a reference to a field** (E0793); copy fields out | or encode/decode by offset, which is usually cleaner |
| `alignas(64)` | `#[repr(align(64))]` | |
| `volatile T *reg` MMIO | `ptr.read_volatile()` / `write_volatile()` on a `*mut T`; or `volatile` crate wrappers | `volatile` in Rust is an operation, not a type qualifier |
| `restrict` | automatic: `&mut` is `noalias` | |
| `new T(args)` / `delete p` | `Box::new(T::new(args))`; drop at scope end | no `delete`; moves are default |
| `new T[n]` / `delete[]` | `vec![T::default(); n]` or `Box<[T]>` (`Vec::into_boxed_slice`) | |
| `malloc(n)` / `free(p)` | avoid; if needed `std::alloc::alloc(Layout)` / `dealloc` (unsafe) | `Layout` carries size and alignment |
| placement new `new (p) T(..)` | `ptr.write(T::new(..))` (unsafe) or `MaybeUninit<T>::write` | |
| explicit destructor call `p->~T()` | `ptr::drop_in_place(p)` (unsafe) | |
| uninitialised array | `[MaybeUninit<T>; N]` then `assume_init` | reading uninitialised memory is UB in Rust too |
| `nullptr` | `None` | `Option<&T>`, `Option<Box<T>>` and `Option<NonNull<T>>` are the same size as the pointer |
| `T *` with arithmetic on a `void *` base | cast to `*mut u8`, then `.add()`; or work on `&[u8]` | |
| `std::launder` | rarely needed; `ptr::read` of a fresh value | |
| `static_cast<T>(x)` numeric | `T::from(x)` (lossless), `T::try_from(x)?` (checked), `x as T` (truncating) | `as` silently wraps and saturates; prefer `try_from` for sizes read from disk |
| `dynamic_cast<Derived*>(p)` | `match` on an enum, or `dyn Any` + `downcast_ref::<Derived>()` | |
| `const_cast` | does not exist; use interior mutability (`Cell`, `Mutex`, atomics) | |
| `sizeof(arr)/sizeof(arr[0])` | `arr.len()` | |
| integer overflow wraps (unsigned) / UB (signed) | debug panic, release wrap; choose `wrapping_*`, `checked_*`, `saturating_*`, `overflowing_*` | overflow is a decision, not an accident |
| `size_t` | `usize` | file offsets and sizes on disk: use explicit `u64`/`u32` |
| `ssize_t` / `off_t` | `isize` / `u64`/`i64` | |
| `uint8_t flags; flags & (1<<3)` | `bitflags!` type, or `flags & MASK != 0` | |
| `__builtin_popcount`, `ctz`, `clz` | `count_ones()`, `trailing_zeros()`, `leading_zeros()` | |
| `__builtin_expect`, `likely` | `#[cold]` on the unlikely function; `std::hint::black_box` is **not** for this | |
| `ntohl` / `htonl` | `u32::from_be_bytes`, `to_be_bytes`, or `u32::from_be(x)` | |
| `__builtin_bswap32` | `x.swap_bytes()` | |
| rounding up to alignment `(n + a - 1) & ~(a - 1)` | `n.next_multiple_of(a)` (a any positive), or `(n + a - 1) & !(a - 1)` for powers of two | `div_ceil` too |
| `is_power_of_two`, next pow 2 | `n.is_power_of_two()`, `n.next_power_of_two()` | |

### 1.2 Ownership, lifetimes and RAII

| C++ | Rust | What changes |
|---|---|---|
| constructor / destructor | `fn new(..) -> Self` / `impl Drop for T` | destructors run at scope exit in reverse declaration order, like C++; moved-from values do **not** run a destructor |
| a constructor that can fail (throws) | `fn new(..) -> Result<Self, E>` | there are no exceptions |
| rule of three/five/zero | derive `Clone` (copy ctor), moves are free and implicit, `Drop` (dtor) | there is no move constructor to write; a moved-from value cannot be used |
| `DISALLOW_COPY_AND_MOVE(T)` | `PhantomPinned` + `Pin` for a value that must not move; or hold it behind `Arc`/`Box` | most "can't be moved" types are just "not `Clone`" in Rust |
| `std::move(x)` | passing `x` by value | a move is the default; use `.clone()` to copy |
| `std::unique_ptr<T>` | `Box<T>` | `Option<Box<T>>` is `nullptr`-able |
| `std::shared_ptr<T>` (atomic refcount) | `Arc<T>` | `Rc<T>` for single-threaded; neither is mutable by default |
| `std::shared_ptr<T>` + mutation | `Arc<Mutex<T>>` / `Arc<RwLock<T>>` / `Arc<T>` with interior atomics | decide *what* is shared and mutable |
| `std::weak_ptr<T>` / `lock()` | `Weak<T>` / `upgrade()` | `upgrade` returns `Option<Arc<T>>` |
| `shared_ptr<const T>` immutable sharing | `Arc<T>` (immutable by default) | persistent structures (BusTub's Trie) are natural |
| `std::enable_shared_from_this` | pass `Arc<Self>` explicitly: `fn start(self: &Arc<Self>)` | |
| copy-on-write via `shared_ptr` + clone | `Arc::make_mut(&mut arc)` clones only if shared | the idiom behind BusTub's `Trie::Put` |
| `friend class BufferPoolManager` | `pub(crate)` fields/methods, or put both types in one module and keep fields private to it | privacy is per-module, not per-class |
| `mutable` member in a `const` method | `Cell<T>` / `RefCell<T>` / `Mutex<T>` / atomic, with `&self` methods | |
| `const` member functions | `&self` methods | |
| `explicit` constructors, conversions | `From`/`TryFrom`/`Into` impls; no implicit conversions | |
| operator overloads | `impl Add`, `Index`, `PartialEq`, `PartialOrd`, `Display` | |
| a reference stored in a struct (`Foo &parent_`) | a lifetime parameter `struct Foo<'a> { parent: &'a Parent }`, or `Arc<Parent>`, or an index | self-referential structs need `Pin`/indices/arenas (K8) |
| object that holds a lock across a function boundary (`std::unique_lock` member) | a guard stored in a struct: `RwLockReadGuard<'a, T>` (with a lifetime) or `parking_lot::ArcRwLockReadGuard` (owns an `Arc`) | the crux of BusTub's `ReadPageGuard` (§2.2) |
| `std::function<R(A)>` | `Box<dyn Fn(A) -> R + Send>` or a generic `F: Fn(A) -> R` | generics are zero cost; `dyn` is a vtable |
| function pointer `void (*)(int)` | `fn(i32)` | |
| lambda capturing by reference `[&]` | closure borrowing; by value `[=]`/`move` | the borrow checker proves the borrow outlives its use |
| `std::thread` capturing locals | `thread::scope(|s| ...)` borrows; `thread::spawn(move || ..)` owns | `'static` bound on spawn |
| RAII scope guard | a struct with `Drop` (`scopeguard` crate for a closure) | |
| `goto cleanup;` | `?` and `Drop` | cleanup is the destructor's job |
| exceptions, `try/catch` | `Result<T, E>`, `?`, `Option`; panics for bugs | `catch_unwind` exists but is not control flow |
| `noexcept` | nothing; `fn` that cannot fail returns `T` | |
| `assert(x)` | `assert!` (always) / `debug_assert!` (debug only) | BusTub's `BUSTUB_ASSERT` = `debug_assert!` |
| `UNREACHABLE` / `__builtin_unreachable` | `unreachable!()` (checked); `unreachable_unchecked` (unsafe, rarely) | |
| `std::exit`, `abort` | `std::process::exit`, `std::process::abort` | |
| `static` local / global | `static X: T` (const-initialised), `static X: OnceLock<T>`, `LazyLock<T>`, `thread_local!` | no static-initialisation-order fiasco: statics are const or lazy |
| `static mut` | avoid: `AtomicUsize`, `Mutex<T>` in a `static`, or `UnsafeCell` behind a `Sync` wrapper | `static mut` references are deny-by-default now |
| `inline`, header-only | `#[inline]`; modules, no headers | |
| `namespace` | `mod` | |
| `#include` order and include guards | `use`/`mod`; no textual inclusion | |
| `extern "C"`, `__attribute__((used))` | `extern "C" fn`, `#[no_mangle]` | K15 |

### 1.3 Containers and algorithms

| C++ | Rust | Notes |
|---|---|---|
| `std::vector<T>` | `Vec<T>` | `push_back` → `push`; `emplace_back` → `push(T::new(..))`; `erase(it)` → `remove(i)` / `swap_remove(i)` / `drain(..)`; `reserve` → `reserve`; `v.data()` → `as_ptr()`/`as_slice()` |
| `std::array<T, N>` | `[T; N]` | `std::array<T, N>::fill` → `fill` |
| `std::list<T>` | usually `VecDeque<T>` or an **index-linked list** in a `Vec`; `LinkedList<T>` rarely | the borrow checker makes pointer lists hard; BusTub's LRU-K uses `list<size_t>` of timestamps, so `VecDeque<u64>` |
| `std::deque<T>` | `VecDeque<T>` | |
| `std::forward_list` | `Option<Box<Node>>` singly linked list | K9 |
| `std::map<K,V>` / `set` | `BTreeMap` / `BTreeSet` | ordered; `lower_bound` → `range(k..)`; `std::multiset` → `BTreeMap<T, usize>` (count), BusTub's `Watermark` |
| `std::unordered_map` / `set` | `HashMap` / `HashSet` | `operator[]` → `entry(k).or_default()`; `find` → `get`; default hasher is SipHash (DoS-resistant, slower): `hashbrown`/`FxHash`/`ahash` for hot paths |
| `std::priority_queue<T>` (max) | `BinaryHeap<T>` (max); `Reverse<T>` for min | no decrease-key |
| `std::queue`, `std::stack` | `VecDeque`, `Vec` | |
| `std::pair`, `std::tuple` | `(A, B)`, `(A, B, C)` | |
| `std::optional<T>` | `Option<T>` | `value_or` → `unwrap_or`; `has_value` → `is_some` |
| `std::variant<A, B>` | `enum E { A(A), B(B) }` | `std::visit` → `match` |
| `std::any` | `Box<dyn Any>` | |
| `std::string` as a byte container | `Vec<u8>` | **a Rust `String` is always UTF-8**; do not use it for arbitrary bytes |
| `std::string_view` | `&str` (text) / `&[u8]` (bytes) | |
| `std::bitset<N>` / `vector<bool>` | `[u64; N/64]`, `Vec<u64>` bitmap, or the `bitvec` crate | K2 |
| `std::sort(v.begin(), v.end(), cmp)` | `v.sort_unstable_by(|a, b| ..)`, `sort_by_key` | stable: `sort_by` |
| `std::lower_bound` / `upper_bound` | `slice.partition_point(|x| x < &k)` | binary search by predicate |
| `std::binary_search` | `slice.binary_search(&k)` → `Result<usize, usize>` | `Err(i)` is the insertion point |
| `std::find`, `find_if` | `iter().position(..)`, `iter().find(..)` | |
| `std::accumulate` | `iter().sum()`, `fold` | |
| `std::copy`, `std::fill`, `std::swap` | `copy_from_slice`/`clone_from_slice`, `fill`, `mem::swap` | |
| `std::move` of a container element out | `mem::take(&mut v[i])`, `mem::replace`, `Option::take()`, `swap_remove` | you cannot move out of an index; replace with something |
| iterator invalidation | impossible: holding an iterator borrows the container | the compiler rejects `v.push(..)` during `for x in &v` |
| `it->second` / structured bindings | `for (k, v) in &map`, `if let Some(v) = map.get(&k)` | |
| `std::hash<K>` | `impl Hash for K` + a `Hasher` | `BuildHasher` for a custom hash function (K10) |
| comparator as a template parameter `Compare` | `K: Ord`, a `Fn(&K, &K) -> Ordering` field, or a trait `trait KeyComparator { fn cmp(&self, a: &[u8], b: &[u8]) -> Ordering; }` | BusTub's `KeyComparator` is the last: keys are raw bytes in a page |
| `std::numeric_limits<T>::max()` | `T::MAX` | |

### 1.4 Strings, text and OS strings

| C / C++ | Rust | Notes |
|---|---|---|
| `const char *s` (NUL-terminated) | `&CStr`, built with `c"literal"` or `CStr::from_bytes_with_nul`; owned `CString` | only needed at the FFI boundary |
| `std::string` for text | `String` / `&str` | UTF-8 guaranteed; index by byte range `&s[a..b]` (panics off a char boundary) |
| `s.size()` | `s.len()` (bytes), `s.chars().count()` (scalars) | |
| `s[i]` character | `s.as_bytes()[i]` (byte), `s.chars().nth(i)` | no O(1) char indexing |
| `std::stoi`, `strtol` | `s.parse::<i32>()?` | returns `Result`, never UB |
| `snprintf`, `std::format` | `format!`, `write!(buf, ..)` into `String` or any `io::Write` | |
| `std::ostringstream` | `String` + `write!` (via `fmt::Write`) | |
| `std::to_string` | `x.to_string()` | |
| `strcmp`, `==` | `==` on `&str`/`&[u8]` | |
| `toupper` | `to_ascii_uppercase()`, `char::to_uppercase()` | |
| `strtok`, split | `split`, `split_whitespace`, `split_once`, `lines` | |
| `wchar_t`, UTF-16 (Windows) | `Vec<u16>`, `OsStrExt::encode_wide`, `OsStringExt::from_wide` | `#[cfg(windows)]` |
| file name / path as `char *` | `&Path` / `PathBuf` (`OsStr` inside) | not UTF-8 on Unix, not even well-formed UTF-16 on Windows; `to_str()` returns `Option` |
| bytes of a path on Unix | `std::os::unix::ffi::OsStrExt::as_bytes` | |
| decode possibly-bad UTF-8 | `String::from_utf8_lossy(&bytes)` (`Cow<str>`), `str::from_utf8(&bytes)?` | |
| `strncpy` into a fixed field | copy bytes, pad with zeros: `field[..n].copy_from_slice(..)` | the on-disk form of a `varchar` |

### 1.5 Concurrency

| C++ | Rust | Notes |
|---|---|---|
| `std::mutex m; T data;` guarded by convention | `Mutex<T>` | the data lives inside; `let g = m.lock().unwrap();` gives `MutexGuard<T>`; `Drop` unlocks |
| `std::lock_guard`, `std::scoped_lock` | the `MutexGuard` itself; drop it early with `drop(g)` or a block | |
| `std::unique_lock` (movable, can unlock) | `MutexGuard` (movable) + `drop` | `Condvar::wait(guard)` consumes and returns it |
| `std::shared_mutex` | `RwLock<T>`; `read()` / `write()` | `parking_lot::RwLock` also has upgradable reads and `*_arc` guards that own an `Arc` |
| `std::condition_variable cv; cv.wait(lk, pred)` | `Condvar`; `cv.wait_while(guard, |s| !ready(s))` | **always wait in a loop or `wait_while`**: spurious wakeups; the predicate state lives inside the `Mutex<T>` |
| `cv.notify_one/all` | `notify_one` / `notify_all` | |
| `cv.wait_for(lk, dur, pred)` | `wait_timeout_while(guard, dur, ..)` | returns `(guard, WaitTimeoutResult)` |
| `std::atomic<T>` | `AtomicU64`, `AtomicBool`, `AtomicPtr<T>`, ... | `load(Ordering)`, `store`, `fetch_add`, `compare_exchange(_weak)`, `swap`, `fetch_update` |
| `std::memory_order_*` | `Ordering::{Relaxed, Acquire, Release, AcqRel, SeqCst}` | same semantics; there is no `consume` |
| `std::atomic_thread_fence` | `std::sync::atomic::fence(Ordering)` | |
| `std::atomic<size_t> pin_count_` | `AtomicUsize` | |
| `std::promise<T>` / `std::future<T>` | `mpsc::channel` of one message, or a oneshot (`mpsc::sync_channel(1)`); `JoinHandle::join()` for thread results | BusTub's `DiskRequest::callback_` |
| `std::async` | `thread::spawn` + `join` | |
| `std::thread t; t.join()` | `let h = thread::spawn(..); h.join()` | dropping a handle detaches |
| thread function with a captured reference | `thread::scope` | borrows locals safely |
| `thread_local T x;` | `thread_local! { static X: RefCell<T> = ... }` | accessed via `.with(|x| ..)` |
| `std::call_once` / function-local static | `Once`, `OnceLock<T>`, `LazyLock<T>` | |
| `std::latch`, `std::barrier` | `Barrier` | |
| `std::counting_semaphore` | build from `Mutex<usize>` + `Condvar` (K12); crates `tokio::sync::Semaphore` for async | std has no semaphore |
| a multi-producer multi-consumer queue (BusTub's `Channel<T>`) | `std::sync::mpsc` (multi-producer, **single consumer**); `crossbeam_channel` for MPMC; or `Mutex<VecDeque<T>>` + `Condvar` | |
| shutdown by sending `std::nullopt` | dropping all senders closes the channel: `recv()` returns `Err`; or an enum message `Job::Stop` | |
| `std::stop_token` | an `AtomicBool`, a channel, or `Condvar`-guarded flag | |
| spinlock with `atomic_flag` | `AtomicBool` + `compare_exchange(false, true, Acquire, Relaxed)` / `store(false, Release)` + `hint::spin_loop()` | K13 |
| hand-over-hand (crab) locking | acquire the child guard, then drop the parent guard; guards must be held in a stack/`Vec` | BusTub B+ tree `Context` (§2.5) |
| lock ordering to avoid deadlock | the same discipline; the type system does not help | |
| `volatile` flag for threads | wrong in C++ too; `AtomicBool` | |
| data race | impossible in safe Rust (`Send`/`Sync`); `unsafe impl Sync` is a proof obligation | |

### 1.6 Files, descriptors and system calls

| POSIX / C / C++ | Rust | Notes |
|---|---|---|
| `open(path, O_RDWR|O_CREAT, 0644)` | `OpenOptions::new().read(true).write(true).create(true).open(p)?` | Unix mode/flags: `std::os::unix::fs::OpenOptionsExt::{mode, custom_flags}` |
| `read(fd, buf, n)` | `file.read(&mut buf)?` (may be short) / `read_exact` | a short read is normal; `read_exact` loops and errors on EOF |
| `write(fd, buf, n)` | `file.write(&buf)?` (may be short) / `write_all` | |
| `pread(fd, buf, n, off)` | `std::os::unix::fs::FileExt::read_at(&buf, off)` / `read_exact_at` | does **not** move the cursor; takes `&File`, so threads can share a file |
| `pwrite` | `FileExt::write_at` / `write_all_at` | |
| Windows `ReadFile` with `OVERLAPPED` offset | `std::os::windows::fs::FileExt::seek_read(buf, off)`, `seek_write` | **moves the cursor** (unlike Unix); behind `#[cfg(windows)]` |
| `lseek` | `file.seek(SeekFrom::Start(off))?` | `stream_position()` for the current offset |
| `ftruncate`, `fallocate` | `file.set_len(n)?`; preallocate with `set_len` | |
| `fsync`, `fdatasync` | `file.sync_all()?`, `file.sync_data()?` | durability needs the directory too: fsync the parent dir after create/rename |
| `rename(a, b)` atomic replace | `fs::rename` | write a temp file in the same directory, `sync_all`, then rename |
| `unlink`, `mkdir`, `rmdir` | `remove_file`, `create_dir_all`, `remove_dir` | |
| `stat` | `fs::metadata(p)?`; `std::os::unix::fs::MetadataExt::{ino, mode, nlink, size, mtime, blocks, dev}` | |
| `readdir` | `fs::read_dir(p)?` yields `DirEntry` (unordered) | `walkdir` crate to recurse |
| `symlink`, `link`, `readlink` | `std::os::unix::fs::symlink`, `fs::hard_link`, `fs::read_link` | |
| `flock`, `fcntl(F_SETLK)` | `File::lock()` / `lock_shared()` / `try_lock()` (std 1.89+), or `fs2`/`fd-lock` | advisory |
| `mmap(NULL, len, prot, flags, fd, off)` | `memmap2::Mmap::map(&file)` / `MmapMut` (`unsafe`: the file may change under you) | `memmap2::MmapOptions::new().offset(..).len(..)`; `libc::mmap` for raw control |
| `madvise`, `msync`, `mprotect`, `mlock` | `Mmap::advise`, `MmapMut::flush()`, `libc::mprotect`, `libc::mlock` | |
| `munmap` | drop the map | |
| `O_DIRECT`, `O_SYNC`, `O_NONBLOCK` | `OpenOptionsExt::custom_flags(libc::O_DIRECT)` | `O_DIRECT` needs aligned buffers: `std::alloc` with `Layout::from_size_align(len, 4096)` |
| `dup`, `dup2`, `close` | `OwnedFd::try_clone`, `drop(fd)`; `libc::dup2` | |
| raw `int fd` | `std::os::fd::{RawFd, OwnedFd, BorrowedFd, AsFd, AsRawFd, FromRawFd, IntoRawFd}` | `OwnedFd` closes on drop; `BorrowedFd<'a>` cannot outlive its owner |
| `pipe`, `socketpair` | `std::io::pipe()` (1.87+), `UnixStream::pair()` | |
| `poll`, `epoll`, `kqueue` | `libc::poll`/`epoll_*`, or `mio` (portable), `rustix::event` | the event loop of a server/kernel |
| `readv`, `writev` | `Read::read_vectored` / `Write::write_vectored` with `IoSlice` | scatter/gather |
| `sendfile`, `splice` | `std::io::copy` (uses `copy_file_range`/`sendfile` on Linux) | zero-copy where the OS allows |
| `errno`, `strerror` | `io::Error`, `e.raw_os_error()`, `e.kind()` (`ErrorKind::NotFound`, `Interrupted`, `WouldBlock`, ...) | retry on `Interrupted`; `read_exact`/`write_all` already do |
| `FILE *`, `fopen`, `fgets` | `File` + `BufReader::new(f).lines()` / `read_line` | `BufWriter` flushes on drop (errors are swallowed: call `flush()`) |
| `std::ifstream`/`ofstream` | `File`, `BufReader`, `BufWriter` | |
| `std::filesystem::path` | `Path`/`PathBuf` | `join`, `parent`, `file_name`, `extension`, `components` |
| `std::filesystem::resize_file` | `File::set_len` | BusTub's `DiskManager` pre-sizes the db file this way |
| `getpid`, `getuid` | `std::process::id()`; `libc::getuid` | |
| `fork` + `exec` | `std::process::Command::new(..).args(..).spawn()?` | `CommandExt::pre_exec` (unsafe) for setup between fork and exec |
| `waitpid` | `child.wait()?` → `ExitStatus`; `ExitStatusExt::signal()` | |
| `pipe` + `dup2` redirection | `Command::stdin(Stdio::piped())`, `.stdout(Stdio::piped())` | |
| signals `sigaction` | `libc::sigaction`, or `signal-hook` | async-signal-safe functions only inside a handler |
| `getenv`/`setenv` | `std::env::var`, `set_var` (unsafe in edition 2024) | |
| `clock_gettime(CLOCK_MONOTONIC)` | `Instant::now()`; `elapsed()` | monotonic, never goes back |
| `clock_gettime(CLOCK_REALTIME)`, `time()` | `SystemTime::now()`; `duration_since(UNIX_EPOCH)` | can go backwards: returns `Result` |
| `nanosleep` | `thread::sleep(Duration)` | |
| `rdtsc` | `core::arch::x86_64::_rdtsc` (unsafe) | |
| `sysconf(_SC_PAGESIZE)` | `rustix::param::page_size()` / `libc::sysconf`; `memmap2` knows it | |
| `socket/bind/listen/accept/connect` | `TcpListener::bind`, `.accept()`, `TcpStream::connect` | `UdpSocket`; `socket2` for options (`SO_REUSEPORT`, buffers) |
| `setsockopt(TCP_NODELAY)` | `stream.set_nodelay(true)` | |
| non-blocking sockets | `set_nonblocking(true)`; `WouldBlock` errors; `mio` | |
| `htons`, byte-order of headers | `u16::from_be_bytes`, `to_be_bytes` | |
| `getaddrinfo` | `ToSocketAddrs` | |

### 1.7 Templates, macros and compile-time

| C++ | Rust |
|---|---|
| `template <typename T>` function/class | generics `fn f<T: Bound>(..)`, `struct S<T>` |
| `template <typename K, typename V, typename Cmp>` | generic params; the comparator as a trait or closure |
| non-type template parameter `template <size_t N>` | const generics `struct Page<const N: usize>`, `[u8; N]` |
| template specialisation | trait impls for concrete types; `impl Trait for u32`; no overlapping specialisation on stable |
| SFINAE, `enable_if`, concepts | trait bounds and `where` clauses |
| CRTP | a generic trait with `Self`, or a trait with an associated type |
| `constexpr` function/variable | `const fn`, `const X: T` (evaluated at compile time) |
| `static constexpr size_t X = ..;` in a class | `const X: usize = ..;` in an `impl` block |
| `#define MAX 100` | `const MAX: usize = 100;` |
| function-like macro `#define PAGE_ALIGN(x) ...` | `const fn page_align(x: usize) -> usize` |
| macros that generate code (X-macros) | `macro_rules!`; derive macros |
| `#ifdef _WIN32` / `__linux__` | `#[cfg(windows)]` / `#[cfg(target_os = "linux")]` / `cfg!(unix)` |
| `#pragma once`, include guards | not needed |
| `typedef`/`using X = Y;` | `type X = Y;` |
| `auto`, `decltype` | type inference; `impl Trait` |
| `namespace` + ADL | modules + traits in scope |
| `static_assert` | `const _: () = assert!(...)` |
| `__attribute__((aligned))`, `packed` | `#[repr(align(N))]`, `#[repr(packed)]` |
| preprocessor-selected struct layout | `#[cfg_attr(..)]` |
| `template <typename... Args>` variadics | tuples + macros; generic closures |

### 1.8 Polymorphism and object-oriented designs

| C++ | Rust |
|---|---|
| abstract base class with virtual methods | `trait Executor { fn next(&mut self) -> Option<Tuple>; }` |
| `std::unique_ptr<AbstractExecutor>` | `Box<dyn Executor>` |
| inheritance used for data sharing | composition: a struct field; or a shared trait with default methods |
| a closed set of subclasses (plan nodes, expression kinds, page types) | `enum PlanNode { SeqScan(SeqScanPlan), Insert(..), .. }` + `match` (usually the best port) |
| `dynamic_cast` to pick a subclass | `match` on the enum; or `as_any()` + `downcast_ref` |
| visitor pattern | `match`; or a trait method that takes `&mut dyn Visitor` |
| `shared_ptr<const AbstractPlanNode>` tree | `Arc<PlanNode>` (enum) with `Vec<Arc<PlanNode>>` children |
| `override`, `final` | implementing the trait method; `final` has no meaning (no inheritance) |
| virtual destructor | `Drop` is automatic for `Box<dyn Trait>` |
| pure virtual interface `DiskManager` with a memory and a file implementation | `trait DiskManager`; `struct MemoryDisk`, `struct FileDisk`; generics `BufferPool<D: DiskManager>` or `Arc<dyn DiskManager>` |
| `Clone()` virtual copy (BusTub's `TrieNode::Clone`) | `trait TrieNode: dyn_clone`; or an `enum Node { Plain, WithValue }` with `#[derive(Clone)]` |
| `std::variant` + `std::visit` | enum + match |
| callbacks / observers | closures `Box<dyn FnMut(..)>`, channels |
| singleton / global | pass a handle (`Arc<Db>`), or `OnceLock` |

### 1.9 Memory-management designs you meet in kernels and databases

| C/C++ pattern | Rust form |
|---|---|
| free list threaded through freed blocks | an intrusive singly linked list of `*mut FreeNode` stored in the freed memory (unsafe, K7), or a `Vec<u32>` of free indices |
| bump allocator | `struct Bump { start: usize, end: usize, next: usize }`; `GlobalAlloc` impl |
| arena + pointers into it | arena `Vec<T>` + typed indices `struct NodeId(u32)`; `bumpalo` for lifetimes-bound references |
| slab allocator | `Vec<Option<T>>` + free list of indices (the `slab` crate) |
| buddy allocator over a bitmap | `struct Buddy { bitmap: Vec<u64>, order_free: [..] }` with explicit address arithmetic |
| frame table + page table (OS/DB buffer pool) | `Vec<Frame>` indexed by `FrameId(u32)`; `HashMap<PageId, FrameId>` |
| LRU list (intrusive doubly linked) | index-based doubly linked list in a `Vec<Node>`, or `LinkedHashMap` |
| reference-counted buffer | `Arc<[u8]>`, `Bytes` (zero-copy slices), `Cow<[u8]>` |
| double buffering | `[Vec<u8>; 2]` with an index, or `mem::swap` of two buffers |
| ring buffer | `Vec<T>` + `head`/`tail` indices with power-of-two mask; SPSC with atomics |
| memory pool of fixed-size objects | `Vec<MaybeUninit<T>>` + free list; or `Box` reuse |
| page-aligned I/O buffers | `Layout::from_size_align(4096, 4096)` + `alloc_zeroed`, wrapped in a struct with `Drop` |
| copy-on-write | `Cow<'a, T>`, `Arc::make_mut` |
| intrusive containers (`container_of`) | store an index/`NonNull` and compute with `offset_of!`; or avoid with indices |
| pointer tagging in the low bits | `usize` newtype with masks; `NonNull::with_addr` (strict provenance) |

---

## 2. BusTub, component by component

For each: what the C++ does, the shape in Rust, and the traps. The K track that drills it is in brackets. The staged
port is the capstone project `bustub-rs` (SYSTEMS.md §6).

### 2.1 Basics: `config.h`, ids, `Page`, `FrameHeader`  [K1, K2]
- `using page_id_t = int32_t; frame_id_t; txn_id_t; lsn_t` and `INVALID_*` sentinels (`-1`): Rust newtypes
  (`struct PageId(u32)`, `FrameId(u32)`) and `Option<PageId>` instead of `-1`. Newtypes stop a `FrameId` being passed where a
  `PageId` is expected, which C++'s `typedef` allows.
- `BUSTUB_PAGE_SIZE = 8192`: `const PAGE_SIZE: usize = 8192;` Frames hold `Box<[u8; PAGE_SIZE]>` or `Box<[u8]>`. BusTub's
  own comment ("in practice `char data_[SIZE]`, we use a vector for ASAN") is irrelevant in Rust: slices are checked.
- `Page`: `std::vector<char> data_`, `std::atomic<size_t> pin_count_`, `std::atomic<bool> is_dirty_`, a `std::shared_mutex
  rwlatch_`, `friend` classes. Rust: `struct Frame { data: RwLock<Box<[u8]>>, pin_count: AtomicUsize, dirty: AtomicBool }`.
  The latch *protects the bytes*, so the bytes go inside the lock.
- `GetLSN() { return *reinterpret_cast<lsn_t *>(GetData() + OFFSET_LSN); }`: decode with `i32::from_le_bytes(data[4..8]...)`.
  `SetLSN` with `memcpy` → `data[4..8].copy_from_slice(&lsn.to_le_bytes())`.
- Trap: BusTub reads native-endian ints straight out of pages. A Rust port should pick an endianness (little-endian) and
  encode explicitly, and add a test that the file format round-trips.

### 2.2 `DiskManager`, `DiskScheduler` and the `Channel`  [K4, K11, K14]
- `DiskManager` uses `std::fstream` with `seekp/write/flush`, a `std::mutex db_io_latch_`, a `pages_` map `page_id → offset`,
  `free_slots_`, and `resize_file` when full. Rust: `File` + `FileExt::read_at/write_at` (no seek, no cursor, no lock needed for
  I/O itself); a `Mutex<Allocation>` only around the page-id to offset map; `File::set_len` to grow. Partial reads past EOF are
  zero-filled (`memset` in C++) → `read_at` returns fewer bytes, then `buf[n..].fill(0)`.
- `DiskManagerMemory` (in-memory) → `struct MemoryDisk(Mutex<HashMap<PageId, Box<[u8]>>>)`; both implement `trait DiskManager`.
  This trait is also your **fault injection point** (SYSTEMS.md §3.4: `SimDisk`).
- `Channel<T>`: `queue + mutex + condition_variable`; `Put` pushes and `notify_all`; `Get` waits with a predicate. Rust:
  `Mutex<VecDeque<T>>` + `Condvar` with `wait_while`, or just `std::sync::mpsc` (single consumer is enough for one worker).
- `DiskScheduler`: a background `std::thread` loops `Get()`; `std::optional<DiskRequest>` where `nullopt` means stop;
  `DiskRequest { bool is_write; char *data; page_id; std::promise<bool> callback }`; the caller keeps a `std::future` to wait.
  Rust: `enum Request { Read{..}, Write{..}, Stop }` or drop the `Sender` to stop; the callback is a one-shot channel
  (`mpsc::sync_channel(1)`) or a `Condvar`-guarded slot; **the data pointer is the interesting part**: `char *data` crossing to
  another thread means either moving a `Box<[u8]>` buffer through the queue and back, or sharing an `Arc<Frame>`. Do not send
  a raw pointer.
- Shutdown: join the worker in `Drop`.

### 2.3 `LRUKReplacer` / `ArcReplacer` / `ClockReplacer`  [K9, K17]
- `std::unordered_map<frame_id_t, LRUKNode>`, `std::list<size_t> history_`, `current_timestamp_`, `curr_size_` (evictable
  count), a `std::mutex latch_`. Algorithm: evict the evictable frame with the largest backward k-distance (`+inf` if fewer than
  `k` accesses, ties by earliest first access).
- Rust: `HashMap<FrameId, Node>` or a `Vec<Node>` indexed by frame id (frames are dense), history as `VecDeque<u64>` capped at
  `k`, the whole replacer behind a `Mutex` in the buffer pool (do not lock twice). `Evict() -> Option<FrameId>`.
- ARC (adaptive replacement cache): four lists (`mru`, `mfu`, `mru_ghost`, `mfu_ghost`) and an adaptive target `p`: `VecDeque`
  or an index-linked list for O(1) removal from the middle. A frame must be removable by id, so a plain `VecDeque` is O(n):
  use `LinkedHashSet`-like structure (a `HashMap<FrameId, usize>` into a slab-linked list).
- CLOCK: a circular buffer of `{ref_bit, evictable}` with a hand index.

### 2.4 `BufferPoolManager` and page guards  [K12, K17]
The central porting problem of BusTub.
- Fields: `frames_` (`vector<shared_ptr<FrameHeader>>`), `page_table_` (`unordered_map<page_id, frame_id>`), `free_frames_`
  (`list`), `replacer_` (`shared_ptr`), `disk_scheduler_` (`shared_ptr`), `bpm_latch_` (`shared_ptr<mutex>`),
  `next_page_id_` (`atomic`).
- `CheckedReadPage(page_id) -> std::optional<ReadPageGuard>`: take `bpm_latch_`; find the frame (or evict one: flush it if
  dirty, read the page from disk); `pin_count++`; `replacer_->RecordAccess` and `SetEvictable(false)`; release the BPM latch;
  **then acquire the frame's read latch** (so I/O does not block the pool); return a guard.
- The guard (`ReadPageGuard`): holds `shared_ptr<FrameHeader>`, `shared_ptr<ArcReplacer>`, `shared_ptr<mutex> bpm_latch_`,
  `shared_ptr<DiskScheduler>`, `bool is_valid_`. Its destructor unlatches the frame, decrements the pin count under the BPM
  latch, and if the count hits 0 marks the frame evictable. Move-only: `ReadPageGuard(const &) = delete`, move constructor
  steals and invalidates the source.
- `As<T>()` returns `const T *` by `reinterpret_cast` of the frame's data. `AsMut<T>()` sets the dirty flag.
- **Rust design.**
  - The pool is `Arc<BufferPool>`; guards hold an `Arc<BufferPool>` (or the `Arc<Frame>`) so they can outlive the borrow of
    the pool: a guard that borrows `&'a BufferPool` would infect every caller with a lifetime; an owning guard does not.
  - The frame latch must be held *inside the guard, across function returns*. A plain `RwLockReadGuard<'a, T>` borrows the
    lock, so a struct holding both the `Arc<Frame>` and the guard is self-referential. Solutions, in order of preference:
    (1) `parking_lot::RwLock::read_arc()` → `ArcRwLockReadGuard<RawRwLock, T>`, an owned guard; (2) use a hand-rolled latch
    (`RawRwLock` from `lock_api`, or an atomics-based latch, K12) so the guard owns an `Arc<Frame>` and calls
    `unlock_shared` in `Drop`; (3) `ouroboros`/`self_cell`; (4) `unsafe` with a documented lifetime extension. Option (1) or (2)
    is the right answer for this project.
  - Move-only comes free: guards are not `Clone`. Moved-from guards cannot be used. `Drop` replaces the manual `Drop()`
    method; keep a `drop(self)` style `fn flush(&self)`.
  - `As<T>()` → `fn as_ref<T: Pod>(&self) -> &T` (via `bytemuck`) or typed page wrappers (`HeaderPage<'a>(&'a [u8])`) with
    accessor methods that decode fields.
  - `std::optional<WritePageGuard>` → `Option<WritePageGuard>`; the "checked" and unchecked variants become `Option`/`Result`
    and `expect`.
  - The BPM latch + pin counts: pin count as `AtomicUsize` per frame, `page_table`/`free_frames`/`replacer` in **one**
    `Mutex<State>` so the invariant "a frame is in exactly one of free list, page table, replacer" is maintained under a single
    lock. This also removes the C++'s `shared_ptr<mutex>` plumbing.
- Traps: holding the BPM mutex across disk I/O (stalls everyone); evicting a frame with pin count > 0; forgetting to flush a
  dirty frame before reuse; a guard dropped *while still holding the BPM mutex* (self-deadlock); `FlushPage` taking the read
  latch while a writer waits (priority inversion); lock ordering page latch vs BPM latch.

### 2.5 Extendible hash table  [K10]
- Three page types: `ExtendibleHTableHeaderPage` (array of directory page ids indexed by the top bits of the hash),
  `DirectoryPage` (`global_depth`, `local_depths[512]`, `bucket_page_ids[512]`), `BucketPage` (`size`, `max_size`,
  `array_[MappingType]` where the array size is computed from `sizeof(MappingType)` at compile time).
- Features: `reinterpret_cast` views of pages; `static_assert` on sizes; `KeyType`/`ValueType`/`KeyComparator` templates over
  fixed-size keys (`GenericKey<8>` ...); bit operations (`GetSplitImageIndex`, local/global depth masks, `IncrGlobalDepth`
  copying the directory half).
- Rust: `#[repr(C)] #[derive(Pod, Zeroable)] struct Header { max_depth: u32, ids: [u32; N] }` and `bytemuck::from_bytes_mut`;
  the bucket's generic array uses a *const-generic* entry type, or stores entries as raw `[u8]` with `K::SIZE + V::SIZE` strides
  and a `trait KeyComparator`. Bit tricks → `u32` methods (`leading_zeros`, `1 << depth`). Splitting buckets = move entries to a
  new bucket and fix directory pointers: a `for` over a range with `step_by`.
- Guard discipline: the table holds a `WritePageGuard` for the header, then the directory, then the bucket, and may *drop the
  earlier ones* once safe (crabbing).

### 2.6 B+ tree  [K18]
- `BPlusTreePage` (type, size, max size), `InternalPage` (`MappingType array_[0]` of `(key, child page id)`), `LeafPage`
  (`next_page_id_`, tombstones, key and rid arrays), `HeaderPage` (root id). All are views over a page's bytes; there are no
  constructors (`= delete`) and no destructors: **the page is the object**.
- Operations: lookup, insert with node split, delete with borrow/merge, range scan via a leaf iterator that holds a read guard,
  concurrent access via latch crabbing with a `Context { header_page: Option<WritePageGuard>, root_page_id, write_set:
  VecDeque<WritePageGuard>, read_set: ... }`.
- Rust shape: typed views `LeafView<'a, K, V>` over `&'a mut [u8]` with `len()`, `key_at(i)`, `insert_at(i, k, v)` (shift with
  `copy_within`), `split_into(&mut other)`; the `Context` holds guards in a `Vec`; "unlatch ancestors when the child is safe"
  = `ctx.write_set.clear()` (drops the guards). The iterator holds a `ReadPageGuard` and the current index; `Iterator::next`
  advances, jumping to `next_page_id`. Tombstones in the leaf: a small fixed array.
- Pre-sizing: slot counts are computed from `PAGE_SIZE`, header size, and `size_of::<K>() + size_of::<V>()`: `const fn`.
- Traps: shifting arrays with overlapping `memmove` (`copy_within`), off-by-one in min sizes (`ceil(max/2)`), iterator
  invalidation across splits (hold the guard), root changes (the header page protects `root_page_id`).

### 2.7 Table heap, tuples and schemas  [K1, K2, K17]
- `TablePage`: `next_page_id`, `num_tuples`, `num_deleted_tuples`, then `TupleInfo tuple_info_[0]` (offset, size, meta) growing
  down from the header while tuple data grows up from the page end: a **slotted page**. `static_assert(sizeof(TablePage) == 8)`.
- `Tuple`: `RID rid_; std::vector<char> data_;` with `GetValue(schema, column_idx)` decoding by column offsets;
  `Value` is a tagged union over INTEGER/BIGINT/VARCHAR/DECIMAL/... with a `TypeId`.
- Rust: `enum Value { Int(i32), BigInt(i64), Varchar(String), Decimal(f64), Boolean(bool), Null(TypeId) }`; `struct Tuple {
  rid: Rid, data: Vec<u8> }` or `Bytes`; slotted page as a typed view with `slot(i) -> SlotInfo`, `insert(&mut self, tuple) ->
  Option<u16>`, free-space arithmetic with `u16`, fixed-width part + variable-width part (offset+length, like Postgres/SQLite).
- `RID`: `struct Rid { page_id: PageId, slot: u32 }`, `Copy + Hash + Ord`, `to_u64`/`from_u64` for key packing.
- `TableHeap` and `TableIterator`: a linked list of table pages; the iterator holds a guard or re-fetches by `Rid` each step
  (simpler, safe against eviction; BusTub project 3 uses the latter).

### 2.8 Expressions, plan nodes, executors, optimizer  [K19]
- A closed hierarchy: `AbstractExpression` (virtual `Evaluate`, `EvaluateJoin`), `ColumnValueExpression`, `ConstantValueExpression`,
  `ComparisonExpression`, `ArithmeticExpression`, `LogicExpression`...; `AbstractPlanNode` with `children_` and `output_schema_`;
  `AbstractExecutor` with `Init()` and `Next(Tuple *, RID *) -> bool` (Volcano / iterator model), `ExecutorContext` with raw
  pointers to catalog, buffer pool, transaction.
- Rust: `enum Expr { Column{..}, Const(Value), Compare{op, l: Box<Expr>, r: Box<Expr>}, ... }` with `fn eval(&self, row: &Tuple,
  schema: &Schema) -> Result<Value>`; `enum Plan { SeqScan{..}, IndexScan{..}, Insert{..}, Update, Delete, Aggregation,
  NestedLoopJoin, HashJoin, Sort, Limit, TopN, Values }` with `Arc<Plan>` children; executors as `Box<dyn Executor>` with `fn
  next(&mut self) -> Result<Option<(Tuple, Rid)>>` (an `Iterator<Item = Result<..>>` is the Rust spelling of Volcano).
  `ExecutorContext` becomes a struct of `Arc`s; **no raw pointers**.
- The "out-parameters + bool" `Next(Tuple *tuple, RID *rid) -> bool` becomes `Option<(Tuple, Rid)>` (and `Result` for errors
  instead of exceptions like `ExecutionException`).
- Optimizer: rule-based rewrites over the plan enum: `fn optimize(plan: Arc<Plan>) -> Arc<Plan>` recursing over children and
  matching shapes (`NestedLoopJoin` with equi-predicate → `HashJoin`; `Sort + Limit` → `TopN`; `SeqScan` with filter on an
  indexed column → `IndexScan`). Pattern matching on `Arc<Plan>` with `if let Plan::NestedLoopJoin { .. } = &*plan`.
- Aggregation, hash join keys: `#[derive(Hash, Eq)]` on a key struct, `HashMap<AggKey, Vec<Value>>`; Sort with a comparator over
  `OrderBy` lists.

### 2.9 Transactions, MVCC, the lock manager  [K12, K19, K20]
- `Transaction` with `undo_logs_` (a vector of `UndoLog`), a `write_set_`, `state_`, `read_ts_`, `commit_ts_`, guarded by
  `std::mutex latch_`; `TransactionManager` with `txn_map_`, `running_txns_` (`Watermark`), `last_commit_ts_`, a commit mutex.
  `Watermark`: a multiset of read timestamps → `BTreeMap<Timestamp, usize>`.
- Version chains: `UndoLink { prev_txn, prev_log_idx }`, tuple meta timestamps, `GetTupleAndUndoLogs`, `ReconstructTuple` by
  applying undo logs. Rust: plain data (`Copy`) links, `Arc<Transaction>` shared between the manager and executors,
  `Mutex<Vec<UndoLog>>` inside the transaction, `RwLock<HashMap<TxnId, Arc<Transaction>>>` in the manager.
- `LockManager` (Fall 2022): per-table and per-row `LockRequestQueue { list<shared_ptr<LockRequest>>, condition_variable cv_,
  mutex latch_, upgrading_ }`, lock modes with a compatibility matrix, 2PL (growing/shrinking), upgrades, deadlock detection with
  a waits-for graph and DFS cycle detection on a background thread.
  Rust: `Mutex<Queue>` + `Condvar` **per queue** (the predicate is "my request is grantable"); compatibility as a `const`
  2D table indexed by `LockMode as usize`; the waits-for graph as `BTreeMap<TxnId, BTreeSet<TxnId>>` (ordered = deterministic
  victim selection); the detector thread with a stop flag and `park_timeout` or `Condvar::wait_timeout`.
- Errors: BusTub throws `TransactionAbortException(txn_id, reason)`: `Err(TxnAbort { id, reason })`, and the transaction state
  is set to `Aborted` before returning.

### 2.10 Logging and recovery  [K16]
- `LogRecord` with a fixed header (`size`, `lsn`, `txn_id`, `prev_lsn`, `type`) and variable payload; serialised into a
  `LogBuffer` (`char *`) via `memcpy`; flushed by a background thread on timeout/full buffer (group commit);
  `LogRecovery` redo pass (scan the log; reapply if page LSN < record LSN) and undo pass (follow `prev_lsn` chains for losers).
- Rust: an `enum LogPayload`, an `encode(&self, out: &mut Vec<u8>)` / `decode(&[u8]) -> Result<(LogRecord, usize)>` pair with
  explicit little-endian fields and a CRC; recovery uses a `trait LogReader`; the log buffer is `Vec<u8>` + `Condvar` for
  flushers. Tests use `SimDisk` crash points to prove atomicity and durability (SYSTEMS.md §3.4).

### 2.11 The primer projects  [K9, K10, K13, K21]
- **COW Trie** (`Trie::Put/Get/Remove` returning a *new* trie sharing structure): nodes are `shared_ptr<const TrieNode>`;
  `Put` clones the nodes on the path (`Clone()` is virtual to preserve `TrieNodeWithValue<T>`), `Get<T>` does a
  `dynamic_cast<const TrieNodeWithValue<T>*>`. Rust: `#[derive(Clone)] struct Node { children: BTreeMap<u8, Arc<Node>>, value:
  Option<Arc<dyn Any + Send + Sync>> }`; `Put` uses `Arc::make_mut` on the path; `Get::<T>` uses `downcast_ref::<T>()`;
  `TrieStore` with a root mutex + write mutex and a `ValueGuard<T>` that keeps the root `Arc` alive: lifetimes tied to a snapshot.
  `MoveBlocked` (a type used in tests to assert move semantics) → a type that is `!Clone` and counts moves via `Drop`.
- **SkipList**: `shared_ptr<SkipNode>` with `vector<shared_ptr>` links, a seeded `std::mt19937`, a `shared_mutex`. Rust:
  `Vec<Node>` arena + indices (avoids `Rc` cycles), or `Option<Arc<..>>` links with the `Drop` problem (recursive drop
  overflow: write an iterative `Drop`). Seeded RNG: `rand_chacha::ChaCha8Rng::seed_from_u64`.
- **Count-min sketch**: `Vec<Vec<AtomicU32>>` rows × cols, hash functions per row (seeded), `fetch_add(Relaxed)`; `merge`; top-k.
- **HyperLogLog**: register array, `leading_zeros`, `harmonic mean` estimator, bit tricks on a 64-bit hash.
- **Robin-hood hash set, OR-set (CRDT)**: open addressing with displacement, `Vec<Option<Entry>>`, back-shift deletion.

### 2.12 Putting it together: what the Rust layout of BusTub should be
```
bustub-rs/
  src/lib.rs
  common/        PageId, FrameId, Rid, Lsn, errors, config consts
  storage/disk/  DiskManager trait, FileDisk, MemoryDisk, SimDisk (tests), DiskScheduler
  buffer/        BufferPool, Frame, guards, replacers (LruK, Arc, Clock)
  storage/page/  typed page views: TablePage, HashHeader/Directory/Bucket, BTreeInternal/Leaf
  container/     ExtendibleHashTable, hash functions
  index/         BPlusTree, IndexIterator
  catalog/       Schema, Column, Catalog, TableInfo, IndexInfo
  types/         Value, TypeId, Tuple
  execution/     Expr, Plan, Executor impls, Optimizer
  concurrency/   Transaction, TransactionManager, Watermark, LockManager
  recovery/      LogRecord, LogManager, Recovery
  primer/        Trie, TrieStore, SkipList, CountMinSketch, HyperLogLog
```
Design rules: no globals (a `Db` struct owns the `Arc`s); `Result<T, DbError>` everywhere with `thiserror`; every `unsafe`
is inside `storage/page` or `buffer` and has a `// SAFETY:`; every page layout has a size test and a round-trip test.

---

## 3. OSDev: the idioms in Rust

**Provenance.** `wiki.osdev.org` returns HTTP 403 to automated clients, so the pages below were read through Internet Archive
copies (2024 snapshots): Memory Allocation, Page Frame Allocation, Paging, Setting Up Paging, Higher Half Kernel, GDT, IDT,
Scheduling Algorithms, System Calls, Spinlock, Ext2, ELF, Multiboot, ATA PIO Mode, Serial Ports, Rust. (The Bump Allocator,
Slab Allocator and Virtual File System pages were not archived; those parts come from general knowledge and are marked.) The
C below is quoted from those pages; the Rust is ours.

### 3.1 What each page teaches, and how it ports

**Memory Allocation: the three layers.** The page's model: RAM is handed out by a **physical memory manager** (page-frame
allocator), pages are mapped into an address space by a **virtual memory manager**, and a **heap allocator** (`malloc` /
`kmalloc`) subdivides mapped pages and asks the VMM for more when it runs out. Steps 3–5 (grow, map, record) are slow, so
allocators minimise them.
- *Watermark allocator* (`freebase`, `freetop`, no free): `struct Bump { next: usize, end: usize }`; `alloc` is a checked add
  (`next.checked_add(size)`); aligned with `next_multiple_of(align)`. It is a `GlobalAlloc` whose `dealloc` is empty.
- *Free-zone list*: "put at the start of the freed zone a descriptor that allows you to insert it in a list of free zones,
  sorted by address so contiguous zones merge". That is the classic **intrusive free list**: the freed memory *is* the list
  node (`#[repr(C)] struct Free { size: usize, next: Option<NonNull<Free>> }`, written in place with `ptr::write`). Rust needs
  `unsafe` exactly at "reinterpret freed bytes as a node"; everything else (sorting, merging adjacent zones) is ordinary
  safe logic on addresses. A safe alternative: a `BTreeMap<usize /*addr*/, usize /*len*/>` of free ranges.
- *Fixed-size allocation*: "treat all free memory as a linked list of nodes; allocate = pop the front; free = push" O(1),
  no fragmentation → `slab`/pool. Rust: `Vec<u32>` free indices (safe) or the intrusive list (unsafe).
- *Hidden header before the block* (so `free(p)` needs no size) and *magic words* ("F R E E", "U S E D", even the requester's
  address) for debugging → a `#[repr(C)] struct Header { size: usize, magic: u32 }` placed at `ptr.sub(size_of::<Header>())`,
  with `debug_assert_eq!(header.magic, USED)` on free (double-free and corruption detection). A K8 Miri problem.
- *Porting an existing allocator*: it needs `alloc_page(n)`, `free_page(ptr, n)` and lock/unlock hooks ("simplest lock:
  disable interrupts; best: spinlock"). Rust: the allocator is generic over a `trait PageSource { fn alloc_pages(n) -> Option<NonNull<u8>>;
  fn free_pages(..) }` and a `lock_api::RawMutex`; `GlobalAlloc` wraps it. "Choosing an allocator": fast, space-efficient, stable
  (low fragmentation), scalable, real-time (TLSF): the same axes as a Rust allocator choice.
- Test advice from the page worth keeping: build the allocator on the host first and compare against the system `malloc` (here:
  compare against `Vec`/`HashMap` models, then run under Miri).

**Page Frame Allocation: five allocators, all portable.** Bitmap (`N/8` bytes, set O(1), allocate O(N), compare a whole word at
once, remember the last-allocated position) · stack/list of free frames (O(1) both ways; cannot answer "is frame X free?") ·
sized portions (split an area into 8 K + 4 K + 4 K chunks to fit sizes closer) · **buddy** (`k` bitmaps, one per order, blocks
`2^i`-sized and aligned; split on allocate, merge buddy on free; "if buddy[0] is empty check buddy[1]…") · hybrid (a small stack
in front of a bitmap) · a **`struct page` array** (one entry per frame: next link, status bits, owner) for copy-on-write and
statistics. Rust: bitmap = `Vec<u64>` + `trailing_zeros`; stack = `Vec<u32>`; buddy = `[Bitmap; MAX_ORDER]` with
`buddy_of(block, order) = block ^ (1 << order)`; frame array = `Vec<FrameInfo>` indexed by `FrameId`. Virtual address allocators
on the same page: **flat list** (first/best fit, kept sorted to merge on free, MS-DOS style) vs **AVL tree** of regions (Linux's
`vm_area` approach) → `BTreeMap<usize, Region>` with `range(..=addr).next_back()` for "which region contains this address".

**Paging / Setting Up Paging.** The page's code: `uint32_t page_directory[1024] __attribute__((aligned(4096)));` initialised
"not present", a `first_page_table[1024]` filled with `(i * 0x1000) | 3`, the directory entry set to the table address `| 3`
(`3` = present + read/write), `mov %eax, %cr3`, then `or $0x80000000, %cr0` (bit 31 enables paging). "A page is not present when
it's not intended to be used; the MMU page-faults, which also implements lazy loading and swapping." Rust:
`#[repr(C, align(4096))] struct Table([Entry; 512 or 1024]);` with `struct Entry(u64)` and `bitflags! { PRESENT, WRITABLE, USER,
... }`; `const fn` index extraction (`(va >> 12) & 0x3ff`); the **assembly stays behind a trait** (`trait Cpu { fn load_cr3(&self, pa:
u64); fn enable_paging(&self); }`), and our simulator implements `Cpu`, so the student's page-table code is checked by
`translate()`. 64-bit: four levels, 9 bits each, 48-bit virtual addresses, PCID, `invlpg`, the `NX` bit, PAT: all expressible as
`bitflags` and shifts. **Higher-half kernel**: the page describes mapping the kernel at a high virtual base with a "small
trampoline running in the lower half that sets up higher-half paging and jumps"; the Rust port is `kernel_virt = phys +
KERNEL_BASE` arithmetic with a `PhysAddr`/`VirtAddr` newtype pair so you cannot confuse them (the single most useful kernel
type-safety idiom).

**GDT / IDT.** GDT: 8-byte segment descriptors (base 32 split in three places, limit 20 split in two, access byte, flags) and
the GDTR (`size - 1`, `offset`). IDT: 256 gates; **32-bit gate = 8 bytes**: `offset_1:u16, selector:u16, zero:u8,
type_attributes:u8, offset_2:u16`; `type_attributes` for DPL 0 is `0x8E` (32-bit interrupt gate, present), `0x8F` (trap gate),
`0x85` (task gate); **64-bit gate = 16 bytes** with an extra `offset_3:u32`, a reserved `u32` and a 3-bit **IST** index; the IDTR
`size` is "one less than the size of the table in bytes"; "an absent entry raises a General Protection Fault". Rust: build each
descriptor as a `u64`/`u128` with `const fn` bit packing and **byte-exact tests against the values printed on the page**; `#[repr(C)]`
structs only for the in-memory table, never for the bit-packed field.

**Spinlock.** The page builds it from `lock bts [lock],0` / `jc .retry` ("basic"), then the **improved test-and-test-and-set**
(spin reading `test [lock],1` without the `LOCK` prefix, then try `bts`), the **`pause`** instruction for hyper-threads, **release
with a plain aligned store** (no `LOCK` needed: "the CPU guarantees writes to an aligned `uint32_t` are atomic"), **cache-line
placement** (a lock sharing a line with hot data ping-pongs; never split a lock across lines/pages), and **lock debugging**
(store an owner id, count failed attempts, detect release-without-acquire, a re-entrant variant). Rust:
`while lock.compare_exchange_weak(false, true, Acquire, Relaxed).is_err() { while lock.load(Relaxed) { hint::spin_loop() } }`
and `lock.store(false, Release)`; `#[repr(align(64))]`; owner id in an `AtomicUsize`. This single page is K12/K13 in miniature.

**Scheduling Algorithms.** Interactive: **round robin** (one queue, quantum of N timer ticks; 20–50 ms is "a frequently chosen
compromise", >100 ms feels laggy), **priority round robin** (4–16 queues; run a higher queue while it is non-empty), the **SVR2
UNIX dynamic priority** (usage factor lowers priority while running, raises it while waiting), **shortest process next** (needs a
predictor), **lottery** (tickets). Batch: **FCFS, SJF, shortest remaining time next, highest response ratio next**. Real-time:
**rate monotonic, earliest deadline first**. Rust: `trait Scheduler { fn add(&mut self, t: TaskId, ..); fn tick(&mut self) ->
Option<Switch>; fn pick(&mut self) -> Option<TaskId>; }`; `VecDeque<TaskId>` per priority; a `BinaryHeap<Reverse<(deadline, id)>>`
for EDF; a seeded RNG for lottery. All gradable **deterministically** by golden tick-by-tick traces on the page's own A/B/C example.

**System Calls.** The page's mechanisms: software **interrupt** (`int 0x80`, function code in `eax`, arguments in registers, a
`pt_regs` frame pushed by an assembly stub), **jump table** (`if eax > NR_syscalls → -ENOSYS; call [table + 4*eax]`, and "if there
is a hole in the table, fill it with a pointer to a function returning an error code"), **`sysenter`/`syscall`** (the saved
user stack/flags, `SFMASK`, "zero the registers that are not preserved so nothing leaks"), a CPU **trap** trick (L4's `lock nop`),
**call gates**; arguments in registers, on the stack, or in memory; "validate pointers: the kernel must not trust user
addresses". Rust: `static SYSCALLS: [fn(&mut Frame) -> isize; N]` with a bounds-checked dispatcher (`.get(nr).copied().unwrap_or(sys_ni)`),
the frame as a `#[repr(C)]` struct, `copy_from_user(src: UserPtr, dst: &mut [u8]) -> Result<(), Fault>` that walks the page tables
and fails instead of faulting, and `-errno` as the C ABI with `Result<usize, Errno>` inside.

**Ext2 (the on-disk format, exactly the maths the page gives).** Superblock at byte offset 1024; block size `1024 << s_log_block_size`;
number of block groups = `ceil(blocks / blocks_per_group)` (and cross-check with inodes); **block group descriptor table** in the
block after the superblock; an inode's **block group = (inode − 1) / INODES_PER_GROUP**, **index = (inode − 1) %
INODES_PER_GROUP**, **containing block = (index × INODE_SIZE) / BLOCK_SIZE**; the inode holds 12 direct block pointers then single,
double and triple indirect; `i_mode` packs file type and permission bits; a **directory entry** is `inode:u32, rec_len:u16,
name_len:u8, type:u8, name[]` with `rec_len` ≥ the entry size (padding / deleted entries live in `rec_len` slack); feature flags
(required vs read-only-if-unknown). "How to read an inode / how to read the root directory (inode 2)" are the page's own
quick summaries and become K6's first problems, graded against fixture images. Rust: field reads with `from_le_bytes` at
`const` offsets, the `rec_len` walk as an `Iterator<Item = DirEntry<'a>>` over a `&'a [u8]` block (zero-copy names).

**ELF.** Header (`e_ident`, `e_type`, `e_machine`, `e_entry`, `e_phoff`, `e_phnum`, ...), **program headers** (`PT_LOAD`:
`p_offset`, `p_vaddr`, `p_filesz`, `p_memsz`, `p_flags` r/w/x; `memsz > filesz` means zero-fill the rest: `.bss`), `PT_INTERP` and
dynamic linking, section headers and relocation. The `objdump -p` output on the page is the exact fixture format. Rust: `repr(C)`
`Pod` headers via `bytemuck::try_from_bytes` (alignment may fail: use `pod_read_unaligned`), `chunks_exact(e_phentsize)` over the
program header table, a loader that returns `Vec<Segment { vaddr, bytes: &[u8], zero_tail, flags }>`; reject `p_filesz > p_memsz`
and offsets past EOF (`checked_add`).

**Multiboot2.** Header: 8-byte-aligned fields `magic = 0xE85250D6`, architecture, total length, checksum (so the four sum to
0 mod 2³²), then **8-byte-aligned tags** ending in a tag of type 0, size 8; the bootloader passes `eax = 0x36D76289` and a
physical pointer in `ebx` to an info struct: `struct multiboot_info { u32 total_size; u32 reserved; struct multiboot_tag
tags[0]; }` with `struct multiboot_tag { u32 type; u32 size; }`. **This is a textbook flexible-array-member port**: Rust decodes the
tag list with a cursor over `&[u8]`: read `type`/`size`, yield `(type, &body[..size-8])`, advance by `size.next_multiple_of(8)`,
stop at type 0. K22's boot-info stage.

**ATA PIO and Serial.** Serial (COM1 = 0x3F8): the init sequence is a fixed list of `outb(PORT + n, value)` writes (disable
interrupts; DLAB on; divisor 3 for 38400 baud; 8N1; FIFO enable and clear with 14-byte threshold; loopback self-test writing `0xAE`
and reading it back); `read` spins on line-status bit 0, `write` spins on line-status bit 5 (transmit empty). ATA PIO (primary
bus base `0x1F0`, control `0x3F6`): the registers, the **400 ns delay by reading the status register 4 times**, `IDENTIFY`,
device-type detection by **signature bytes** (`0x14/0xEB` = PATAPI, `0x69/0x96` = SATAPI, `0/0` = PATA, `0x3C/0xC3` = SATA), 28-bit vs
48-bit LBA, status bits (BSY, DRQ, ERR, DF), software reset, polling vs IRQ. Rust: `trait PortBus { fn inb(&mut self, port: u16) ->
u8; fn outb(&mut self, port: u16, v: u8); fn insw(...) }`; a status `bitflags`; the driver is a state machine that returns `Result`
on `ERR`/timeout; the **simulator provides a scripted UART and an ATA controller** so every sequence is asserted byte for byte.

**Rust on OSDev.** The wiki's Rust page: `std` = `core` + `alloc` + OS parts; "using only `core`" for freestanding kernels; every
Rust compiler is a cross-compiler; libraries: `x86_64`, `spin`, `multiboot`, `slabmalloc`, `bootloader`, `fringe` (context
switching); tutorials: *Writing an OS in Rust*, *Rust Bare Bones*, *Meaty Skeleton*. Our simulated machine means students never
need the toolchain setup, but K22 keeps the same crate boundaries (`core`/`alloc` only; `forbid_paths = ["std::"]`).

### 3.2 The idiom table

| OSDev topic | C/C++ idiom (from the pages) | Rust idiom |
|---|---|---|
| Freestanding setup | no libc, linker script, `kernel_main` | `#![no_std]`, `#![no_main]`, `core`/`alloc`, `#[panic_handler]`, custom target |
| Port I/O | `outb(PORT + 1, 0x00)` | `trait PortBus`; `x86_64::instructions::port::Port<T>` on hardware |
| MMIO / VGA `0xB8000` | `volatile uint16_t *` | `ptr::write_volatile` on a typed `Mmio<T>`; cell = `u16` (char | attr << 8) |
| Global kernel state | globals | `static` + `spin::Mutex<T>` / `AtomicX`; never `static mut` |
| GDT/IDT/TSS | packed structs, `lgdt`/`lidt` | `u64`/`u128` bit packing with `const fn`; `repr(C)` table; byte-exact tests |
| Interrupt handlers | `__attribute__((interrupt))`, `int 0x80` stub | `extern "x86-interrupt"`; a `[Option<fn(&mut Frame)>; 256]` table |
| Spinlock / critical section | `lock bts`, `pause`, `cli`/`sti` | `compare_exchange_weak(Acquire)` + `spin_loop()` + `store(Release)`; RAII interrupt-guard |
| Paging | `uint32_t page_directory[1024] aligned(4096)`; `\| 3`; CR3/CR0 | `#[repr(C, align(4096))] struct Table([Entry; N])`; `bitflags`; `trait Cpu` |
| Frame allocator | bitmap / stack / buddy / frame array | `Vec<u64>` bitmap; `Vec<u32>`; `[Bitmap; ORDERS]`; `Vec<FrameInfo>` |
| Kernel heap | watermark → free list → hidden header → slab | `Bump` → intrusive `Free` list → `Header{size,magic}` → `Slab<T>`; `GlobalAlloc` |
| Scheduler / context switch | task struct, RR queue, asm `switch_to` | `VecDeque<TaskId>` per priority; heap for EDF; `trait Scheduler` |
| System calls | `int 0x80` + jump table, `sysenter`/`syscall` | `[fn(&mut Frame) -> isize; N]` + `copy_from_user -> Result` |
| ELF loading | `Elf32_Ehdr` cast from the buffer | `Pod` headers + `chunks_exact` over `phdr`s; `PT_LOAD` segments |
| Multiboot | `tags[0]` flexible array, 8-byte alignment | cursor over `&[u8]`, `next_multiple_of(8)` |
| Drivers (serial, ATA, PCI, keyboard) | polling loops, status bit masks | `trait PortBus`, status `bitflags`, `Result` + timeouts |
| VFS / ext2 / FAT | block buffers cast to structs, inode maths | `trait BlockDevice`, `from_le_bytes` at offsets, zero-copy `DirEntry` iterator |
| Networking | `struct ip_header` bit-fields, `ntohs`, checksum loop | byte-offset parsers, `from_be_bytes`, one's-complement `u32` accumulator, TCP state `enum` |
| Timers / PIT | `outb`, tick counter | `AtomicU64` ticks, `Relaxed` increments, an `Instant`-like newtype |
| Logging | `printf` to serial | `impl fmt::Write for Serial`; `write!` |
| Testing a kernel | QEMU | user-space simulator (SYSTEMS.md §3.5), `cargo test`; QEMU for the last mile |

---

## 4. Undefined behaviour catalogue: what C/C++ code relies on, and the Rust answer

| C/C++ UB | How it hides | Rust |
|---|---|---|
| Use after free / dangling pointer | returning `&local`, `std::string_view` of a temporary, a `std::vector` reference after `push_back` | borrow checker rejects; `Drop` order is defined |
| Iterator / reference invalidation | `v.push_back` while holding `&v[0]` | rejected at compile time |
| Double free / free of a stack pointer | manual `delete` | ownership: one owner, one `Drop` |
| Out-of-bounds read/write | `buf[i]` past the end, `memcpy` too long | bounds-checked panic; `get(i)` for fallible |
| Uninitialised read | reading a `struct` field never set | `MaybeUninit` required; zero-init is explicit |
| Signed integer overflow | `int` arithmetic that "wraps" | defined: debug panic / release wrap; choose `wrapping_*`/`checked_*` |
| Strict-aliasing violation | `reinterpret_cast<uint32_t*>(char*)` read | use `from_le_bytes`/`bytemuck`; `ptr::read_unaligned` |
| Misaligned access | `*(uint64_t*)(buf + 3)` | `read_unaligned`, `from_le_bytes`, or `bytemuck::try_from_bytes` returning `Err` |
| Reading padding bytes | `memcmp` or `write` of a struct with padding | `Pod` types forbid padding; encode fields |
| Data race | two threads, one plain `int` | impossible in safe Rust: `Send`/`Sync` |
| Order-of-evaluation / sequencing | `i = i++ + i` | defined left-to-right |
| Null dereference | `p->x` with `p == nullptr` | `Option` forces the check |
| Modifying a `const` object via `const_cast` | | no such cast |
| `memcpy` with overlapping ranges | | `copy_within` / `ptr::copy` |
| Shift by ≥ width | `1 << 32` | `checked_shl`, `wrapping_shl`, debug panic |
| Missing `return` | | the compiler requires it |
| Stack overflow from deep recursion | linked list/tree destructor | same; write iterative `Drop` for long chains |
| Exceptions thrown through `noexcept`/C frames | | panics across `extern "C"` abort (`panic = "abort"` or `catch_unwind`) |

---

## 5. Reading lists

- BusTub: `github.com/cmu-db/bustub`, the project handouts on `15445.courses.cs.cmu.edu`, and CMU 15-445 lecture notes (storage,
  buffer pools, hash tables, B+ trees, query execution, concurrency control, recovery). The C++ in this repo's problems is
  quoted with attribution (MIT).
- OSDev: `wiki.osdev.org` (Bare Bones, GDT, IDT, Paging, Memory Allocation, Scheduling Algorithms, ELF, ext2, PCI, ATA PIO),
  Philipp Oppermann's "Writing an OS in Rust" (`os.phil-opp.com`) for the Rust-native versions of the same ideas.
- Rust: the Rustonomicon (unsafe, layout, atomics), "Rust Atomics and Locks" (Mara Bos), the std docs for `std::os::unix`,
  `std::alloc`, `std::sync::atomic`, `core::mem`, `core::ptr`; `crates`: `bytemuck`, `zerocopy`, `memmap2`, `rustix`, `libc`,
  `bitflags`, `parking_lot`, `crossbeam`, `loom`, `bumpalo`, `hashbrown`.
