# Section K · Systems: from C/C++ to Rust (kernels, databases, compilers)

Written 2026-10-08 at the owner's request. **Status: design only; nothing authored yet. The BusTub parts (K17-K20, P6) are superseded by the CodeCrafters-style course in [BUSTUB.md](BUSTUB.md), which is being built first;**
the task board for the rest ([SYSTEMS_TASKS.md](SYSTEMS_TASKS.md)) and the agent prompt ([authoring/write-systems-track.md](authoring/write-systems-track.md)) are still to be written;
the C/C++ → Rust reference every problem leans on is [PORTING.md](PORTING.md).

The owner's brief, kept verbatim in spirit: low-level systems patterns that recur in OS kernels, databases and compilers; learn
to translate C and C++ (BusTub, OSDev) to idiomatic Rust; exercises that are small and specific *or* large and
combined; comprehensive; **innovate; don't be conservative about the existing code or problem set.** The existing curriculum
for the unwritten tracks is therefore rewritten here (§5), and the platform grows the capabilities this needs (§3).

---

## 1. Thesis and scope

**The problem being solved.** Someone who reads C++ fluently, and wants to write Rust, hits a wall that is not the borrow
checker but the *translation dictionary*: C++ code is built from idioms (`char *buf`, `reinterpret_cast`, `friend class`,
`std::condition_variable`, flexible array members, `shared_ptr<FrameHeader>`, `std::promise`, intrusive lists, `volatile`
registers) that each have a Rust answer, sometimes the same shape and often a different one. Knowing the answers is a
vocabulary problem, and vocabulary is best taught by *deliberate, graded, repeated* translation.

**What Section K is.** A systems curriculum organised around the **idioms that kernels, databases and compilers share**,
taught by translating real C and C++ and by building the same machinery from scratch in Rust, with the real code
(BusTub, OSDev examples) as the source text, and with graders that check **behaviour, idiom and robustness** (§3).

**The 24 tracks** (K1–K24, §4) cover, by design, everything in the owner's list:
reading and writing files, Unix and Windows specifics, disk and memory reading, mmap, file systems, bytes and slicing, strings
and OS strings, ext traits (`FileExt`, `OsStrExt`, `MetadataExt`), low-level primitives, Acquire/Release and their use cases,
pointers and references into byte buffers, pages, byte parsing with offsets, allocators and free lists, data structures,
buffers and ring buffers, queues, concurrency and multithreading, bitmaps and masks, packed flags, state machines, event
loops, producer/consumer and `mpsc`, locking, lock-free, atomics and CAS, reference counting, `Cow`, paging and chunking,
write-ahead logs and journals, batching, double buffering, zero-copy views, I/O, lifetimes, time, syscalls, virtual memory,
file descriptors, demand paging, interrupts, process handling, cache locality, pooling, SIMD, **`Condvar`, semaphores,
barriers, once-cells, thread-locals** (the owner's "things I missed"), worker pools, endianness, alignment and padding, hash
tables and hash functions, linked lists, trees, graphs, raw pointers and `unsafe`, networking and the TCP/IP stack, sockets,
`BufReader`/`BufWriter`, and idiomatic buffer/file/memory patterns.

**Beyond the list (what a kernel/DB/compiler engineer also needs; added on purpose):** crash consistency and fsync ordering
(K16), the buffer pool with page guards (K17, BusTub's hardest Rust problem), latch crabbing (K12/K18), MVCC and 2PL (K20),
checksums and torn writes (K3/K16), varints and framing (K2), `cfg`-portable abstractions over Unix and Windows (K5/K15),
verification: Miri, loom, differential and property testing (K24), reading C declarations ("what is this pointer?") (K1),
undefined-behaviour spotting (K8/K24).

**Not in scope here** (stay elsewhere): async/Tokio (C), web backends (B), DSA interview problems (D), language-level
Rust (L), std collections and iterators (S, except what this section re-teaches at low level).

---

## 2. Problem kinds

Existing kinds stay (*write it*, *fix this*, *project stage*; CURRICULUM §1). Section K adds nine. A problem may combine
several. Each K problem declares its kind(s) in `problem.toml` (`kind = [...]`; SYSTEMS_TASKS INF-5).

| Kind | What you get | What is graded | Example |
|---|---|---|---|
| **Port it** | a **C/C++ excerpt** (quoted with attribution) in a side panel, a Rust skeleton, behaviour tests | behaviour (tests) **and idiom** (rules: no raw pointers where a slice works, etc.) | port BusTub's `DiskManager::ReadPage` (`fstream`, `seekg`, `memset` tail) → `read_at` + `fill` |
| **Fix the transliteration** | a *literal* Rust translation of C++ that compiles but is non-idiomatic, slow, unsound or wrong | the rules and tests force the idiomatic form | `unsafe { *(p as *const u32) }` → `from_le_bytes` (`forbid unsafe`) |
| **Characterize first** | a C++ function with **no tests**; you write Rust tests that pin its behaviour, then port | your tests are run against a hidden *reference port*; they must **fail on the mutants** (`wrong/`) and pass on the reference | port by tests, as a real migration works |
| **Spot the UB** | C++ (or `unsafe` Rust) with undefined behaviour; you write the safe Rust, and an *exploit test* that shows the original's bug | Miri (K8/K24) passes on yours; the exploit test fails on the transliteration | strict-aliasing read of a page header |
| **Trace match** | the C++ implementation's *golden trace* (sequence of observable events) for a scripted workload | your port produces the same trace (§3.3) | LRU-K eviction order on BusTub's own test script |
| **Crash test** | an implementation on a **`SimDisk`** that models what survives a crash (§3.4) | recovery tests at *every* crash point of a scripted workload | WAL append, torn page, rename atomicity |
| **Machine test** | code that manipulates a **simulated machine** (physical memory, MMU, ports, IDT) (§3.5) | byte-exact descriptors, successful translations, correct fault delivery | build a 4-level page table; handle a page fault |
| **Model check** | a concurrent structure; **loom** explores *all* interleavings (§3.6) | every interleaving satisfies the invariant | a spinlock with the wrong ordering fails under loom |
| **Idiom card** | a one-line prompt: "C++ `memmove(dst+a, dst+b, n)` → ?" | typed answer or short code; scheduled by the SRS (§8) | the Rosetta rows in PORTING.md §1 |

Bands keep CURRICULUM's meaning: **Easy = use it**, **Medium = understand it** (invariants, costs, why the compiler says no),
**Hard = build it** (a real component). Add one K-specific rule to every Medium/Hard problem: *the statement names the C/C++ it
descends from* (file and function, or OSDev page), so the owner can read the original.

---

## 3. Grading toolbox

### 3.1 What exists (HANDOFF §5)
`check!` tests, visible/hidden, seeded `Rng`, `wrong/` solutions, `rules` (forbidden methods/types, max changed lines,
`forbid_unsafe`), `[perf]` (release, asm, counting allocator), `anneal_prelude`. Runner: no network, read-only root, `/tmp`
tmpfs (512 MB), 256 pids, capped memory/CPU. **Loopback sockets, threads, files in `/tmp`, `Command` of installed binaries,
`mmap` of `/tmp` files all work**; raw `ptrace`, mounting, privileged ports and `O_DIRECT` on tmpfs do not.

### 3.2 Idiom rules (new; INF-4)
The rules crate learns to enforce *how* a problem is solved, so a literal translation does not pass:
`require_methods = ["copy_from_slice"]`, `forbid_casts = ["*mut", "*const"]` (no pointer casts), `forbid_macros`,
`max_unsafe_blocks = 0|n`, `require_safety_comment = true` (every `unsafe` preceded by `// SAFETY:`), `forbid_paths = ["std::"]`
(a `no_std`-style crate, K22), `forbid_index_expr = true` (force `get`/iterators), `max_clones`, and per-problem **clippy
lint sets** (`clippy = ["ptr_arg", "cast_possible_truncation", "indexing_slicing"]`). These are the graders for "idiomatic".

### 3.3 Golden traces (new; INF-7)
For ports of real C++ (BusTub replacers, hash-table splits, B+ tree shapes, lock-manager grant order), the C++ original is
run once offline by `tools/golden/` on scripted workloads and the **observable trace** is committed as JSON next to the
problem (`tests/golden/*.json`). The Rust port must reproduce it event for event. A trace is data, so no C++ runs in the sandbox.
Traces are generated from BusTub's own `test/` workloads where they exist.

### 3.4 `SimDisk`: crash and fault injection (new; INF-2)
`anneal_prelude::sim::SimDisk` models a block device with: sector-granular writes, a write cache, `flush()` as the fsync
point, **crash at the Nth write** (all later writes lost; cached unflushed writes lost or *torn* at sector boundaries,
configurable and seeded), read errors, and a write log for assertions. `SimFs` models directory-entry durability and `rename`
atomicity (what POSIX actually promises). Tests loop over *every* crash point of a workload and assert the recovery invariant.
This turns "is your WAL correct?" from opinion into proof. Same machine models the BusTub `DiskManager` trait.

### 3.5 `SimMachine`: a user-space x86-64-flavoured machine (new; INF-3)
`anneal_prelude::sim::machine` provides: byte-addressed **physical memory**, a **4-level MMU** (`translate(cr3, vaddr, access)`
→ `Ok(paddr)` or a precise `PageFault { vaddr, error_code }`), a TLB model (hit/miss counters), **port I/O** and **MMIO**
buses with scriptable devices (UART, PIT, PIC, keyboard, a block device, a NIC), an **IDT dispatcher** (`raise(vector)`
invokes your handler through the table you built), and a **CPU context** struct for scheduler tests. Students write the
OSDev code (descriptors, page tables, frame allocator, scheduler, drivers) against traits (`PortBus`, `Mmio`, `PhysMem`) and
the tests assert on **bytes in simulated memory** and on **what the simulated hardware does**. No QEMU, deterministic, fast.
The real-hardware `asm!` lives behind `cfg(target_os = "none")` stubs given in the starter and is never graded.

### 3.6 Model checking, Miri, cross-targets (new; INF-6, INF-9)
- **loom**: `[model_check]` problems run a `loom::model` closure over the student's lock/queue/atomics (built with
  `RUSTFLAGS=--cfg loom`); the student's code uses `crate::sync::{Mutex, Condvar, atomic::*}` aliases that map to loom or std.
  Wrong orderings fail *deterministically* with a minimal schedule printed.
- **Miri**: `[miri]` problems run the unsafe core under `cargo miri test` on a small input (uninitialised reads, aliasing,
  out-of-bounds, misalignment, leaks). Nightly Miri component in the image.
- **Cross-target check**: `[targets = ["x86_64-pc-windows-gnu"]]` runs `cargo check --target` after the tests pass, so
  `#[cfg(windows)]` code is **compile-checked even though it cannot run** (Windows `FileExt::seek_read`, `OsStrExt::encode_wide`,
  `CreateFileW` via `windows-sys`). A `cfg`-portable abstraction problem is graded on Linux behaviour plus a Windows build.

### 3.7 I/O and syscall accounting (new; INF-8)
`anneal_prelude::io::{CountingFile, CountingRead, CountingWrite}` wrap `Read`/`Write`/`FileExt` and count calls and bytes.
"Read a 10 MB file in ≤ 40 syscalls", "write 1000 small records with ≤ 4 `write` calls and 1 `fsync`", "scan a column
with 1 `read_at` per 64 KiB" become **exact, machine-independent** assertions (the same philosophy as the counting allocator).
`getrusage` minor-fault counts (Linux) grade mmap-vs-read behaviour (K7).

### 3.8 Safety net
Every K problem still has ≥ 5 visible and ≥ 8 hidden tests, a seeded random check where a reference is simple, a scale
test where complexity is the point, and 1–3 `wrong/` solutions (CURRICULUM, write-track.md). Systems problems add: a
**boundary test** (empty, one byte, exactly one page, one past a page, `u32::MAX` offsets), an **endianness test**, and, where
bytes are written, a **round-trip** test.

---

## 4. Track map

Notation: `[kind]` marks a problem's graded form when it is not plain tests; `⟵` names the C/C++ origin; `(★)` is the stage
capstone. Counts are targets (an agent may add variations). **Anchors listed are the minimum**; fix-the-transliteration and
spot-the-UB variants of most anchors are expected. Each track's stages are Easy → Medium → Hard.

### K1 · Porting fundamentals: read the C++, classify the pointers · SDE-2 · 24
Drills the §0 workflow of PORTING.md. Output of most problems: a small Rust type or function.
- **Easy · Classify:** out-parameter `bool Parse(const char*, Header*)` → `Result<Header, E>` · nullable `T*` → `Option<&T>` ·
  `T**` out-param → `Option<Box<T>>` · array+length pair → slice · `const char *` read-only view → `&[u8]` · returning
  `&local` (Fix: dangling) · `NULL` sentinel `-1` → `Option` · `size_t` vs `usize` and `as` hazards (Fix: `as u32` truncation).
- **Medium · Own it:** `unique_ptr` → `Box` · `shared_ptr` + `weak_ptr` parent links → `Arc` + `Weak` · copy-on-write via
  `Arc::make_mut` ⟵ BusTub `Trie::Put` · RAII handle with `Drop` that counts closes · move-only guard (no `Clone`), moved-from
  cannot be used · `friend class` → module privacy (the test is `compile_fail` on a doc test) · `std::function` →
  `Box<dyn FnMut>` · `mutable` cache in a `const` method → `Cell`/`RefCell` · exceptions → `Result`/`?` with a custom error enum ·
  `goto cleanup` → `?` + `Drop` · `static` init order → `LazyLock`.
- **Hard · Rewrite the design:** class hierarchy of plan nodes → enum + `match` ⟵ BusTub `AbstractPlanNode` · virtual
  `Clone()` hierarchy → enum with `#[derive(Clone)]` ⟵ BusTub `TrieNode` · a header-only template `Container<K, V, Cmp>` with a
  comparator template parameter → trait/closure · (★) **Port a small C++ class end to end**: BusTub `ReaderWriterLatch` and
  `Channel<T>` (the C++ is shown; Rust must own its data and have no `unsafe`) · characterize-first: `DiskManager::GetFileSize`
  + `AllocatePage` free-slot logic.

### K2 · Bytes, slices and views: the `char *` family · SDE-2 · 28
The owner's headline example: C++ passes `char *buf`, Rust passes slices with methods that do the same job differently.
- **Easy · Slices instead of pointers:** `memcpy`/`memmove`/`memset`/`memcmp` → `copy_from_slice`/`copy_within`/`fill`/`==`
  (Fix: length mismatch panic) · `split_at_mut` to treat one buffer as header and body · `chunks_exact` over fixed records ·
  `windows` · `first_chunk::<4>()`/`split_first_chunk` to read a fixed field · `u32::from_le_bytes(buf[o..o+4].try_into()?)` and a
  `read_u16/u32/u64_le(buf, off) -> Result` helper family · write the same fields · `to_ne_bytes` vs `to_le_bytes` (a Fix:
  that breaks on big-endian) · hexdump · `memchr` newline split.
- **Medium · Reading and writing buffers idiomatically:** `Cursor<&[u8]>`/`Cursor<&mut [u8]>` with `Read`/`Write`/`Seek` ·
  `Read for &[u8]` consuming a slice as it reads · `read_exact` vs `read` vs `read_to_end` · `BufRead::read_until`/`split` ·
  `write!` into a `&mut [u8]` (via `Cursor`) and into `Vec<u8>` · `IoSlice` vectored writes (scatter-gather) · NUL-terminated
  and fixed-width string fields (`varchar(32)` padded) · length-prefixed framing: encode and a **resumable decoder** for partial
  input ⟵ `bytes`/`tokio-util` codecs · varint / LEB128 encode+decode with overflow checks · `bytes::Bytes`-style
  zero-copy `slice`/`split_off` over an `Arc<[u8]>` · `Cow<[u8]>` · `slice::align_to`, `bytemuck::cast_slice`, `try_from_bytes`
  errors on misalignment · `ptr::read_unaligned` and why `*(p as *const u32)` is UB.
- **Hard · Views over pages:** (★) **typed page views**: a `#[repr(C)] Pod` header + trailing records over `&mut [u8; 8192]`
  with `header()`, `slots()`, `insert_at` (shift with `copy_within`) ⟵ BusTub `TablePage`, `BPlusTreeLeafPage` with `key_array_[]` /
  `rid_array_[]` · the flexible-array-member emulation (header + computed tail slice) · a `PageGuard`-like wrapper exposing
  `as_ref::<T>()` / `as_mut::<T>()` with dirty tracking ⟵ BusTub `WritePageGuard::AsMut` · endian-explicit record codec with a
  CRC32 trailer and a corruption test · [Fix the transliteration] `reinterpret_cast` of a page into a struct with padding.

### K3 · Bits, flags, masks and layout · SDE-2 · 26
- **Easy · Bit operations:** set/clear/test/toggle a bit · isolate lowest set bit (`x & x.wrapping_neg()`) · `count_ones`,
  `leading_zeros`, `trailing_zeros` · power-of-two tests and rounding (`next_power_of_two`, `next_multiple_of`) · bit-field
  extraction `(x >> 3) & 0x1f` into a newtype with `const fn` accessors · `bitflags!` for mode bits ⟵ ext2 `i_mode`, POSIX mode ·
  endianness: `swap_bytes`, `from_be`, network byte order ⟵ `htonl`.
- **Medium · Bitmaps and packed data:** a **bitmap allocator** (set, clear, `find_first_zero`, `find_run(n)`, range ops, `u64`
  words, last-word masking) ⟵ OSDev frame allocator, ext2 block bitmap · iterate set bits with `trailing_zeros` ·
  packed header (4-bit version, 4-bit length, flags) ⟵ IPv4 header · TCP flags · PTE flags · `repr(C)` vs `repr(packed)` vs
  `repr(align)` layout quizzes with `size_of`/`align_of`/`offset_of!` · E0793 reference-to-packed-field fix · a hand-written
  `bitflags`-style type via `macro_rules!` · checksums: **Internet (one's-complement) checksum** ⟵ RFC 1071, CRC32 with a table,
  Adler-32, FNV-1a · gray code, parity, bit reversal (`reverse_bits`), `rotate_left`.
- **Hard · Compact structures:** (★) Roaring-lite bitmap (array/bitset/run containers) · rank/select on a bitvector with
  popcount blocks · Bloom filter with `k` hash probes from two hashes (double hashing) ⟵ RocksDB · bit-packed integer array
  (`BitPacked<const BITS: usize>`) · varint-prefix key compression · bitset SIMD-friendly layout (counter-graded).

### K4 · Strings, text and OS strings · SDE-2 · 20
- **Easy:** `String`/`&str`/`&[u8]`/`char` byte vs scalar · `from_utf8` vs `from_utf8_lossy` · char boundaries (Fix: slice panics
  on multibyte) · `CStr`/`CString` round trip, NUL handling ⟵ C strings at an FFI edge · `Path`/`PathBuf`: `join`, `parent`,
  `file_name`, `extension`, `components`.
- **Medium · OS-specific:** `OsStr`/`OsString` and why paths are not UTF-8 · `std::os::unix::ffi::OsStrExt::as_bytes` and
  `from_bytes` · **Windows wide strings**: `OsStrExt::encode_wide` / `OsStringExt::from_wide`, UTF-16 surrogates [cross-target
  check] · `Cow<str>` normaliser (`lossy`, trim, lowercase only when needed) · path normalisation (`.`/`..`) without touching the
  file system ⟵ OSDev VFS lookup, BusTub-free · a **zero-copy tokenizer** (`&'a str` tokens) · string interner returning
  `Symbol(u32)` ⟵ rustc `Symbol`.
- **Hard:** (★) a **cfg-portable path/string layer** (`trait OsPath`) with Unix and Windows implementations, tested on Unix and
  *compiled* for Windows · UTF-8 decoder/validator by hand (state machine over bytes), cross-checked against `std` ·
  `format_args`-free logging into a fixed buffer (`fmt::Write` for `&mut [u8]` that truncates).

### K5 · Files and file descriptors · SDE-2 · 30
- **Easy · Use it:** read a file (`read_to_string`, `read`, `BufReader::lines`) · write (`write_all`, `BufWriter`, flush on drop
  error swallowing: Fix) · `OpenOptions` flag combinations (create, create_new, append, truncate) · `Seek` and `stream_position` ·
  `set_len`/preallocate · directory listing, metadata, `MetadataExt` (`ino`, `nlink`, `mode`) · temp files in `/tmp`.
- **Medium · Understand it:** **short reads/writes**: implement `read_fully`/`write_fully` and prove with a
  `ShortIo` test double · retry on `Interrupted` ⟵ `EINTR` · **`pread`/`pwrite` (`FileExt::read_at`/`write_at`)** vs seek+read,
  and why they are thread-safe on a shared `&File` ⟵ BusTub `DiskManager` · Windows `seek_read` moves the cursor: a cfg-portable
  `read_at` shim [cross-target check] · `OwnedFd`/`BorrowedFd`/`AsFd`: who closes this? (Fix: double close) · `dup`, pipes, and
  `io::pipe` · `File::lock`/`try_lock` (advisory locks), two-process exclusion test via `Command` · atomic file replace:
  temp + `sync_all` + `rename` + directory fsync [io counters, SimFs] · **durability ordering** (Fix: renamed before written)
  · `O_DIRECT` aligned buffers (layout only on tmpfs) · vectored I/O (`write_vectored`) with `IoSlice` and `write_all_vectored` ·
  `copy_file_range`/`io::copy` and a counted `io::copy` adapter · `Read`/`Write` generics: function over `R: Read` tested with
  `&[u8]`, `File`, a chunking double ⟵ S9.
- **Hard · Build it:** (★) **`DiskManager` port** ⟵ BusTub `disk_manager.cpp` (`ReadPage`, `WritePage`, `AllocatePage`,
  `DeletePage`, grow by doubling, zero-fill past EOF, free slots) as `trait DiskManager` with `FileDisk` and `MemoryDisk`, with
  I/O counters asserting one `pread`/`pwrite` per page · `BufReader` and `BufWriter` from scratch (capacity, `fill_buf`, bypass for
  large reads/writes) with syscall-count assertions · `LineWriter` · bounded-memory line reader over a 10 MB file · a **read-ahead
  scanner** with a double buffer (K11) and `posix_fadvise`-like hints as a trait · a file-backed **append-only record log**
  with torn-tail detection.

### K6 · File systems · SDE-3 · 22
All graded on `SimDisk`/fixture images, so they run identically everywhere.
- **Easy · Read an image:** parse a superblock (offsets/endianness) ⟵ ext2 · read inode N (group, index, offset math) · follow
  direct blocks · list a directory (`rec_len`, `name_len`) · FAT12/16: follow a cluster chain, 8.3 names.
- **Medium · Allocate and walk:** block and inode **bitmap allocators** on a `BlockDevice` trait · indirect/double-indirect block
  lookup · path resolution (`/a/b/../c`, symlink limit) · permission check from mode bits and uid/gid · hard links and
  `nlink` accounting · `stat` · a VFS `trait Inode` + `Arc<dyn Inode>` tree with mounts · file offset table (`fd` → open file
  description → inode) ⟵ OSDev VFS, fd table.
- **Hard · Write path:** (★) `create`, `write`, `truncate`, `unlink` on an ext2-lite with correct allocation and **crash tests**
  at every write ⟵ SimDisk · directory growth and entry reuse · a **journal** (physical block journal: begin/commit
  records, replay) · a copy-on-write (log-structured) variant and garbage collection · `fsck` that finds the inconsistencies
  a crashed non-journaled FS leaves.

### K7 · Virtual memory, mmap and paging · SDE-3 · 24
- **Easy · mmap in practice:** read a file via `memmap2::Mmap` and via `read` · `MmapMut` write + `flush` ([unsafe: the file
  can change]: write the safe wrapper) · page size and `align_up`/`align_down` · anonymous map as a buffer · `madvise` hints ·
  count **minor page faults** with `getrusage` for first vs second touch [Linux, counter-graded].
- **Medium · Model the machine:** split a virtual address into level indices and offset (4-level, bit ops) · build a page
  table in simulated physical memory [machine test] · `translate()` with present/writable/user/NX checks and precise fault
  codes · a TLB model with ASID and `invlpg` · **demand paging simulator**: page-fault handler, frame table, backing store ·
  replacement policies **FIFO, LRU, CLOCK, OPT, LRU-K** over reference strings with *golden fault counts* [trace match] ·
  Belady's anomaly demonstration · copy-on-write fork simulation with a frame refcount (`Arc`-like) · working-set and
  thrashing detector.
- **Hard · Build it:** (★) a **user-space pager**: a `Region` that is `mmap`ed `PROT_NONE`, handles faults with `SIGSEGV`
  (`sigaction` + `siginfo`) or userfaultfd-like callbacks, loads from a `BlockDevice` and `mprotect`s (Linux-only, guarded) ·
  a memory-mapped **ring log** (`MmapMut`, atomics for head/tail, wraparound) · huge-page-aware allocator math · a sparse
  array backed by `mmap` with lazily committed pages · NUMA/cache-line notes as a reading (no code).

### K8 · Unsafe Rust and raw pointers · SDE-3 · 28
Replaces Y2. All Hard problems are **Miri-graded** `[miri]`.
- **Easy · Read it:** raw pointer basics (`*const`, `*mut`, `add`, `offset_from`, `read`, `write`) · `unsafe fn` vs `unsafe` block ·
  `NonNull<T>` and why `Option<NonNull<T>>` is pointer-sized · `slice::from_raw_parts(_mut)` and the length/alignment contract ·
  `Box::into_raw`/`from_raw` round trip · (★) write the `// SAFETY:` comment (rules: `require_safety_comment`).
- **Medium · Understand it:** the aliasing rules (Stacked/Tree Borrows) with a Miri failure to fix · `UnsafeCell` and why `&T`
  is not `*mut T` · `MaybeUninit<T>`: uninitialised arrays, `assume_init`, `read_buf`-style fill · `ManuallyDrop`, `mem::forget`,
  leak vs `Box::leak` · `ptr::copy_nonoverlapping` vs `copy` · **provenance**: an integer round trip loses it (Fix) ·
  `addr_of!`/`&raw` on packed and uninitialised fields · `offset_of!` and `container_of` ⟵ Linux `list_head`/`container_of` ·
  spot the **unsound safe API** (returns `&'static mut`, `Send` on a raw pointer) · spot the UB in a transliterated C++
  `reinterpret_cast` read · `Drop` + panic safety in an unsafe `Vec::insert`.
- **Hard · Build it:** (★) **`MiniVec`** with raw allocation (`alloc`/`realloc`, growth, `Drop`, ZSTs) · **`MiniArc`** (refcount with
  the correct orderings; K13) · a doubly linked list with `NonNull` and a safe cursor API · `MiniBox` with `dyn`-capable
  `Layout` · a `SliceDeque`/ring that returns two slices · typed arena that hands out `&'a mut T` soundly · an intrusive list
  with `container_of`.

### K9 · Linked and index-based structures, replacers, skiplists · SDE-2 · 24
- **Easy · Safe lists and arenas:** singly linked list with `Option<Box<Node>>` (iterative `Drop`) · `VecDeque` as the
  default `std::list` · **index-linked** doubly linked list in a `Vec<Node>` with a free list · typed ids (`struct NodeId(u32)`) ·
  generational indices.
- **Medium · The shapes that kernels and databases use:** **LRU cache** on an index-linked list ⟵ BusTub `LRUReplacer` ·
  **LRU-K replacer** (k-distance, `+inf`, evictable flags, `Remove`) ⟵ BusTub `lru_k_replacer.cpp` [trace match] · **CLOCK** ⟵
  `clock_replacer.cpp` [trace match] · **ARC** (four lists, adaptive `p`) ⟵ `arc_replacer.cpp` [trace match] · intrusive freelist
  of fixed blocks · **skiplist** with a seeded RNG ⟵ BusTub `skiplist.h` · a COW **persistent trie** (`Arc::make_mut`) ⟵ BusTub
  `trie.h`, with `TrieStore` and a snapshot `ValueGuard` · adjacency lists in flat arrays (CSR) · union-find with path
  halving · priority queue with `decrease-key` by handle.
- **Hard · Build it:** (★) a **slab allocator** with generation checks and stable handles · a lock-protected LRU-K shared
  across threads that never holds two locks · an **order-statistic tree** or rope for a text buffer · interval tree for VMAs ⟵
  OSDev/Linux `vm_area` · a **B-tree node** in a `[u8; 4096]` (K18 precursor).

### K10 · Hash functions and hash tables · SDE-2 · 22
- **Easy · Hash functions:** FNV-1a, Murmur3-32, a mixer (`splitmix64`), `std::hash::Hash`/`Hasher` and `BuildHasher` ·
  HashDoS and when SipHash matters · identity hasher for dense ints · a `Hasher` that counts calls (graded by counters).
- **Medium · Tables:** open addressing with linear probing (tombstones, resize) ⟵ BusTub `linear_probe_hash_table` · **robin hood** with
  back-shift delete ⟵ BusTub `robin_hood_hash_set` · chained buckets in an arena · **extendible hashing in memory** (directory,
  global/local depth, split, directory doubling) [trace match] ⟵ BusTub `disk_extendible_hash_table.cpp` · linear hashing ·
  consistent-hash ring with virtual nodes (add/remove moves ≤ 1/N keys) · count-min sketch with `AtomicU32` rows ⟵ BusTub
  `count_min_sketch` · **HyperLogLog** (leading zeros, bias correction) ⟵ BusTub `hyperloglog` · OR-set CRDT ⟵ BusTub `orset`.
- **Hard · Build it:** (★) **SwissTable-style control bytes** (SWAR group probing on `u64`) ⟵ hashbrown, counter-graded ·
  a **concurrent sharded map** ⟵ dashmap · a **disk-resident extendible hash table** over the buffer pool (K17 stage) · cuckoo
  with a stash · perfect hash for a fixed keyword set (compiler, K21).

### K11 · Buffers, rings and queues · SDE-2 · 24
- **Easy:** `VecDeque` as a queue and ring · a fixed-capacity **byte ring buffer** (`head`, `tail`, power-of-two mask, two
  slices out) · peek/consume/`make_contiguous` · double buffer with `mem::swap` · reuse a `Vec` buffer (`clear` not realloc;
  counter-graded) · `BufWriter` batching (counter-graded).
- **Medium · Producer/consumer:** **`Mutex<VecDeque<T>>` + `Condvar` bounded blocking queue**: `wait_while`, `notify_one` vs
  `notify_all`, close semantics ⟵ BusTub `Channel<T>`, then fix the lost wakeup and the missed close [model check] ·
  `mpsc::channel` vs `sync_channel(0/1/N)` semantics and disconnect · MPMC with `crossbeam_channel` and a worker pool · a
  **log buffer with group flush** (accumulate, flush on size/timeout, wake waiters) ⟵ BusTub `log_manager` · write-behind
  cache · a **bip-buffer** for contiguous writes · batching and **coalescing** (sort+merge adjacent writes) ⟵ OSDev disk
  scheduling, BusTub `DiskScheduler`.
- **Hard · Build it:** (★) **SPSC lock-free ring** with Acquire/Release [model check] ⟵ Linux `kfifo`, K13 · MPSC queue
  (Vyukov) · a **channel from scratch** (`Mutex`+`Condvar`, bounded, select-ish) · a **disk elevator** (SCAN/C-SCAN) scheduler
  in simulated seek time [trace match] · `io_uring`-style submission/completion rings (simulated).

### K12 · Locks, `Condvar` and blocking synchronisation · SDE-3 · 34
Replaces C1's lock half and the Condvar items the owner flagged. Concurrency problems are **model-checked with loom** when the
state space is small, and use deadline-bounded stress otherwise (a hang fails with the last known state).
- **Easy · Use it:** `Mutex<T>` guard scope (drop early) · `RwLock` for read-mostly data · `Arc<Mutex<T>>` counters · `thread::scope`
  borrowing · `try_lock` · poisoning and `into_inner` · `Once`/`OnceLock`/`LazyLock` · `thread_local!` ⟵ `static`/`thread_local` ·
  `Barrier`.
- **Medium · `Condvar` properly:** wait in a loop vs `wait_while` · spurious wakeups (Fix: `if` → `while`) · lost wakeup (Fix:
  notify before wait without state) · `notify_one` vs `notify_all` and the **thundering herd** (counter-graded wakeups) ·
  `wait_timeout_while` and timed waits ⟵ BusTub lock waits · **semaphore from `Mutex`+`Condvar`** · a **latch / countdown**
  (`CountDownLatch`) · a **bounded buffer** (the classic) · a **read-write lock from scratch** (reader-preferring, then
  writer-preferring, then fair; starvation tests) ⟵ BusTub `rwlatch.h` · a **ticket lock** and a **spinlock with exponential
  backoff** · lock ordering and a **deadlock detector** (waits-for graph, DFS cycle) ⟵ BusTub `LockManager::RunCycleDetection` ·
  `parking_lot`: upgradable read, `lock_arc`/`read_arc` owned guards.
- **Hard · Build it:** (★) **`LockManager` with 2PL**: table/row locks, five modes (S, X, IS, IX, SIX), compatibility matrix
  as a `const` table, upgrade rules, FIFO grant, `Condvar` per queue, abort on illegal transitions ⟵ BusTub `lock_manager.cpp`
  [trace match] · **hand-over-hand (crab) locking** on a linked list and a tree, with guards stored in a `Vec` ⟵ BusTub B+ tree
  `Context` · a **page latch + pin protocol**: guard types that hold a latch across function returns without
  self-referential borrows ⟵ BusTub `ReadPageGuard`/`WritePageGuard` · a **sharded lock table** · priority-inheritance mutex
  (simulated scheduler) · a **writer-preferring RwLock** that passes loom.

### K13 · Atomics, memory ordering and lock-free · SDE-3 · 30
Replaces C3. Every Medium/Hard problem has a **wrong-ordering `wrong/` solution that loom rejects**.
- **Easy · Counters and flags:** `AtomicUsize::fetch_add(Relaxed)` counter and when it is enough · `AtomicBool` stop flag ·
  `compare_exchange` vs `compare_exchange_weak` loops · `fetch_update` · `Ordering` cheat sheet drills (idiom cards).
- **Medium · Orderings with use cases:** **Release/Acquire publication** (flag + data; Fix: `Relaxed` publishes stale data) ·
  `AcqRel` RMW · `SeqCst` where it is required (Dekker/IRIW-style example) · fences · a **spinlock** with `Acquire`/`Release`
  [model check] · a **seqlock** for a multi-word snapshot ⟵ Linux `seqlock_t` · one-time init flag (double-checked locking done
  right) · **reference counting**: `MiniArc` with `Release` decrement + `Acquire` fence before drop ⟵ `Arc` · `AtomicPtr` swap
  (RCU-like publish) · atomic bitmap allocator (`fetch_or`/`fetch_and`) · a lock-free **stack (Treiber)** and the **ABA problem**
  (Fix with tagged pointers) · hazard-pointer/epoch idea via `crossbeam-epoch`.
- **Hard · Build it:** (★) **Michael–Scott queue** with epoch reclamation · **SPSC ring** (K11) with cached head/tail to avoid
  cache-line ping-pong, `CachePadded` [counter-graded] · MPSC queue · a lock-free **freelist/slab** · a **concurrent LRU-K
  access counter** with atomics (BusTub `pin_count_`) · a lock-free `Watermark` (multiset of read timestamps) ⟵ BusTub MVCC ·
  work-stealing deque (Chase–Lev, sketch under loom).

### K14 · Threads, pools, event loops and state machines · SDE-2 · 26
- **Easy · Threads:** `spawn`/`join`, `move` closures, return values · `thread::scope` fork-join · `Send`/`Sync` errors (Fix:
  `Rc` across threads) · parallel chunked sum · `thread::park`/`unpark` · `Instant` (monotonic) vs `SystemTime` (wall) ·
  timeouts with `recv_timeout`/`park_timeout`.
- **Medium · Pools and loops:** **worker pool** with graceful shutdown and no lost jobs ⟵ BusTub `DiskScheduler` thread ·
  a pool that returns results (oneshot per job) ⟵ `std::promise` · a **pipeline** (stages over channels, backpressure) ·
  an **actor** · pub/sub · **single-threaded event loop** over `poll` (`libc::poll`) with timers and a ready queue ·
  `epoll` via `libc` or `mio`, level vs edge trigger · **self-pipe trick** for signal-driven shutdown (SIGTERM via `libc`) ·
  **state machines**: enum + `match` transition table, illegal transitions are unrepresentable (typestate) · a deadline
  scheduler (min-heap of timers) with a fake clock injected (`trait Clock`) · a debouncer/rate limiter · simulated
  **round-robin and MLFQ scheduler** with a tick loop [machine test] ⟵ OSDev Scheduling Algorithms.
- **Hard · Build it:** (★) **mini reactor**: nonblocking sockets (K23), readiness queue, timers, wakers ⟵ mio/libevent ·
  work-stealing pool (sketch, loom-checked core) · a **thread-per-core** server skeleton with shard routing · **disk-request
  scheduler with futures** (promise/oneshot, batching) ⟵ BusTub `DiskScheduler` full port · an async-free `Future`
  poller (hand-rolled waker) as the bridge to C5.

### K15 · Processes, syscalls, signals, FFI · SDE-3 · 26
Replaces S10 and Y3. Unix-first with Windows contrasts compile-checked.
- **Easy · Processes:** `Command`: args, env, cwd, status, `output()` · pipes `Stdio::piped` and feeding stdin without a
  deadlock (write and read concurrently) · exit codes, `ExitStatusExt::signal` · `env::args`/`var` · a CLI with exit
  codes · `process::exit` vs return from `main` (destructors).
- **Medium · The syscall layer:** `libc` basics: `getpid`, `pipe2`, `fcntl(F_GETFL/SETFL)`, `read`/`write` on raw fds with the
  `-1`/`errno` convention → `io::Result` · `rustix` safe wrappers vs raw `libc` · `Command` with `pre_exec` (setup between fork
  and exec), `exec` replacing the process · **`fork`-safety rules** (why not in a multithreaded program) · **signals**:
  `sigaction`, `signal-hook`, async-signal-safe rules, handler sets an `AtomicBool` only · `SIGPIPE` and broken pipes ·
  `kill`/`waitpid` and zombies · resource limits (`setrlimit`) · **interrupts as an analogy**: top-half/bottom-half with a
  ring buffer filled by a handler and drained by a loop [machine test]; spurious IRQ handling.
- **Hard · FFI and the boundary:** `extern "C"`, `#[repr(C)]` structs, `CString`/`CStr` ownership ("who frees this?") ·
  callbacks from C with a `*mut c_void` user-data trampoline · panics across `extern "C"` (abort vs `catch_unwind`) · a **safe
  wrapper over a small C library** compiled in the image (`cc` build script: `qsort`-style callback API and an opaque handle
  with create/destroy) · `windows-sys` `CreateFileW`/`ReadFile` sketch [cross-target check] · (★) a portable `trait Sys` with a
  Linux, a macOS-stub and a Windows implementation behind `cfg`, tested on Linux, compiled for Windows.

### K16 · Durability: WAL, journals, checkpoints, crash consistency · SDE-3 · 28
All **Crash tests** on `SimDisk`. The track the owner named "write-ahead log, journal, batching".
- **Easy · The failure model:** what survives a crash (write cache, `fsync`, torn sector) · append a record and fsync ·
  checksummed records (CRC32 + length) · detect and truncate a **torn tail** on recovery · atomic replace by rename · the
  directory-fsync bug (Fix).
- **Medium · The log:** **WAL**: begin/update/commit records, **redo-only** recovery with idempotent replay · force-at-commit vs
  **group commit** (batch N commits per fsync; counter-graded) ⟵ Postgres, BusTub `log_manager` · LSNs and `page_lsn` ("apply
  if page_lsn < record_lsn") ⟵ BusTub `Page::GetLSN` · **checkpoint** and log truncation · **double-write buffer** vs full-page
  writes for torn pages · undo logging and **steal/no-force** with a dirty-page table · a **journaled key-value file**
  (metadata/ordered/data modes) ⟵ ext3/4.
- **Hard · Build it:** (★) **ARIES-lite**: analysis, redo, undo with CLRs, on a toy page store; crash at every write and
  after every recovery step (nested crash) · an **LSM**: memtable (skiplist K9) → SST with index and Bloom filter (K3/K10) →
  manifest → compaction, with crash tests at each step ⟵ RocksDB/LevelDB · a **copy-on-write B-tree** with atomic root swap
  (shadow paging) · `LogRecord` encode/decode ⟵ BusTub `log_record.h` as the wire format for all of the above.

### K17 · Storage engine: disk manager, buffer pool, page guards · SDE-3 · 24  ← **BusTub Project 1**
Capstone track for the buffer pool; ports the real BusTub design (PORTING.md §2.1–§2.4). Stages are cumulative: the project
`bustub-rs` (§6) carries the repo forward.
- **Easy:** `PageId`/`FrameId`/`Rid` newtypes and `Option<PageId>` for `INVALID_PAGE_ID` · `Frame { data: RwLock<Box<[u8]>>,
  pin_count: AtomicUsize, dirty: AtomicBool }` · `MemoryDisk` and `FileDisk` behind `trait DiskManager` (K5) · **disk
  scheduler**: worker thread, request queue, completion by oneshot, drop to shut down.
- **Medium:** **LRU-K / ARC replacer** wired in (K9) [trace match] · the **`BufferPool`**: `page_table`, `free_frames`, `replacer`
  under one `Mutex<State>`, `new_page`, `fetch`, `unpin`, `flush`, `flush_all`, `delete`, with eviction and write-back ·
  pin-count invariants checked by tests that try to evict a pinned frame · **page guards**: `ReadPageGuard`/`WritePageGuard`
  as owned guards (`parking_lot::read_arc` or a hand-rolled latch) that unlatch, unpin and mark evictable in `Drop`;
  `drop(guard)`, `into_dirty`, `flush` ⟵ BusTub `page_guard.cpp` · **no I/O under the pool mutex** (Fix) · concurrent
  fetch/unpin stress under deadline.
- **Hard · Build it:** (★) the **full BusTub P1 test suite** ported (`buffer_pool_manager_test`, `disk_scheduler_test`,
  `page_guard_test`, `lru_k_replacer_test`/`arc_replacer_test` traces) · **readahead** (sequential scan prefetch) · a pool with
  **per-shard locks** and a global replacer interface · **scan resistance** (LRU-K vs LRU, hit-rate counter-graded) · a
  **`SimDisk`-backed** pool test that crashes mid-flush.

### K18 · Indexes: extendible hashing and the B+ tree · SDE-3 · 28  ← **BusTub Project 2**
(PORTING.md §2.5–§2.7.) All pages live in the K17 buffer pool and are accessed through typed views (K2).
- **Easy:** the three extendible-hash page types as `repr(C)` views (header, directory, bucket) with `const fn` capacity ·
  bucket `lookup`/`insert`/`remove` over a key comparator trait · directory depth masks and split-image index (`u32` bit tricks).
- **Medium:** **extendible hash index on pages**: insert with bucket split, directory growth, shrink on remove, merging
  empty buckets [trace match] · **B+ tree pages**: internal/leaf views, `key_at`, `insert_at` with `copy_within`, `split`,
  `min_size` rules · B+ tree **insert** with leaf/internal splits and root creation · **lookup** and **range scan** with an iterator
  that holds a read guard and hops `next_page_id` · B+ tree **remove**: borrow from sibling, merge, root shrink [trace match,
  tree shape golden] · duplicate-key and tombstone variants ⟵ BusTub tombstone leaf.
- **Hard · Build it:** (★) **concurrent B+ tree with latch crabbing** (`Context` holding the header and ancestor write guards,
  release ancestors when the child is *safe*, optimistic read descent) [loom on a miniature, stress on the real one] ·
  bulk-load from a sorted run · variable-length keys with an indirection array (slotted internal pages) · a leaf iterator that
  survives concurrent splits · prefix-compressed keys.

### K19 · Query execution: values, expressions, executors, optimizer · SDE-3 · 30  ← **BusTub Project 3**
(PORTING.md §2.7–§2.8.)
- **Easy:** `Value` enum with typed comparison and `Null` semantics · `Schema`/`Column` and **tuple (de)serialisation** with
  fixed and variable parts (offsets) · `RID` packing · expression `enum Expr` + `eval` (column, const, comparison, arithmetic,
  logic with three-valued logic).
- **Medium:** the **Volcano executor** trait and `Iterator<Item = Result<Tuple>>` · `SeqScan` over the table heap · `Insert`/
  `Update`/`Delete` with index maintenance · `Filter`, `Projection`, `Limit` · `Aggregation` with a hash table keyed by a derived
  `Hash` key (`COUNT/SUM/MIN/MAX`, group by, empty-input rules) · `NestedLoopJoin` (inner/left) · `HashJoin` with
  equi-key extraction and multi-column keys · `Sort` with multi-key ordering · `TopN` (bounded heap) · `IndexScan` ⟵ K18 ·
  window functions (rank, running sum).
- **Hard · Build it:** (★) **plan rewrite rules** over `Arc<Plan>`: NLJ → HashJoin, Sort+Limit → TopN, SeqScan+predicate →
  IndexScan, constant folding, predicate pushdown, join reordering by cardinality [plan-shape golden traces] · sort-merge
  join · external merge sort with a memory budget (spills to `SimDisk`) · vectorised executors over column batches (SIMD hooks,
  K25-perf) · a mini **SQL front end** (K21 parser reused) feeding the planner.

### K20 · Transactions, MVCC, serialisability · SDE-3 · 22  ← **BusTub Project 4**
(PORTING.md §2.9.)
- **Easy:** `Transaction` state machine (running, tainted, committed, aborted) with typestate-ish methods · `Watermark` with a
  `BTreeMap<Timestamp, usize>` multiset ⟵ BusTub `watermark.cpp` · timestamps and `TxnManager` (begin, commit, abort).
- **Medium:** **tuple meta + undo logs + version chains**: `UndoLink`, `GetTupleAndUndoLogs`, `ReconstructTuple` ⟵ BusTub
  `transaction_manager` · **snapshot-isolation reads** (visible if `ts ≤ read_ts` or own writes) · write-write conflict
  detection and `Tainted` · MVCC `Insert/Update/Delete` executors · **garbage collection** below the watermark · index
  maintenance under versions · **isolation anomaly litmus tests** (dirty read, non-repeatable, write skew, phantom): scripted
  interleavings with a deterministic scheduler.
- **Hard · Build it:** (★) **serializable validation** (OCC-style or SSI rw-antidependency tracking) with predicate logs ⟵
  BusTub `scan_predicates_` · a **history checker** (Elle-style: build the dependency graph from a recorded history and detect
  cycles) · 2PL strict and **deadlock victim selection** (youngest transaction) with the K12 lock manager integrated ·
  **MVCC + WAL** recovery of version chains (K16 integration).

### K21 · Compilers: lexing, parsing, IR, VM, codegen · SDE-3 · 34
- **Easy · Front end on bytes:** a **zero-copy lexer** (`&'a str` tokens, `peekable` over `char_indices`, spans) · escape
  sequences and numeric literal parsing (checked overflow) · a **string interner** (`Symbol(u32)`, `Vec<String>` + `HashMap`) ⟵ rustc ·
  recursive-descent expression parser with precedence climbing / **Pratt** · AST in a **typed-index arena** (`ExprId`) and `bumpalo`
  ⟵ rustc `IndexVec`.
- **Medium · Middle and back end:** symbol tables and scopes (stack of `HashMap`, or a persistent map) · type checker for a small
  language · **bytecode design**: instruction set with operand packing in `u32`/`u64` words, encode/decode, a disassembler ⟵
  Lua/CPython · **stack VM** and **register VM** · constant folding and dead-code elimination · **basic blocks + CFG** (graph in a
  `Vec`) · **liveness analysis** with a bitset dataflow fixed point (K3) · **graph-colouring register allocation** (interference
  graph, simplify/select) · **regex → NFA (Thompson) → DFA** (subset construction) as bitset state machines · a hand-written
  **assembler for an x86-64 subset** with byte-exact encodings checked against a table (`mov`, `add`, `jmp rel32`, `call`, `ret`)
  [machine test: executes on a tiny emulator] · relocation patching: forward jumps with a fix-up list.
- **Hard · Build it:** (★) **end-to-end**: a statically typed expression language → AST (arena) → CFG → register allocation →
  bytecode **and** x86-64 bytes → run on the `SimMachine` CPU or the VM, with an **IR verifier** · a **mark-sweep GC** over an
  index-based heap with a root stack and a `Drop`-aware finaliser list ⟵ OSDev/CS: raw-pointer-free · a **linker** for object
  files you define (symbols, relocations, sections) · a **parser generator** fragment (LL(1) tables from a grammar) · an **interning
  + incremental recompute** layer (salsa-like memoisation, sketch).

### K22 · Kernel patterns on the simulated machine · SDE-3 · 36  ← **OSDev**
Each stage cites the OSDev page it ports (read via archive copies, PORTING.md §3). Everything runs on `SimMachine` (§3.5). `no_std`-style: solution crates are compiled with `#![no_std]` + `alloc`
(`forbid_paths = ["std::"]`).
- **Easy · Hardware vocabulary:** port I/O and MMIO through `trait PortBus`/`Mmio` · **UART driver**: the page's exact init
  sequence (`PORT+1=0`, DLAB, divisor 3, 8N1, FIFO `0xC7`, loopback self-test `0xAE`), `read` spinning on LSR bit 0, `write` on bit 5,
  `fmt::Write` ⟵ OSDev Serial Ports · **VGA text buffer** writer at `0xB8000` in simulated memory (cell encoding, scrolling with
  `copy_within`, cursor) · PIT divisor and tick counter · keyboard scancode set 1 → keys with a state machine (shift/ctrl) ·
  `static` kernel state with `spin`-style lock and an **interrupt-disabling guard**.
- **Medium · Descriptors, memory, interrupts:** **GDT** entries (base/limit/access/flags encoding, byte-exact against the
  page's tables) · **IDT** gate descriptors: the 8-byte 32-bit gate and the 16-byte 64-bit gate with IST, `type_attributes` `0x8E`
  / `0x8F` / `0x85`, `IDTR.size = len - 1`; `raise(vector)` dispatch, absent gate → general-protection fault ⟵ OSDev IDT/GDT · **TSS** · exception handlers (page
  fault error-code decoding, double-fault stack) · **PIC/APIC** remapping and EOI protocol · **physical frame allocator**: bitmap with
  word-at-a-time scan and a last-allocated hint, stack of free frames, sized portions, then **buddy** (`k` bitmaps, `block ^ (1 << order)`)
  and the `struct page` array ⟵ OSDev Page Frame Allocation · **virtual address allocator**: sorted flat list with merge, then
  `BTreeMap` region tree ⟵ same page · **page table construction** (map/unmap/identity/higher-half) and
  a recursive/direct-map accessor [machine test] · **kernel heap**: watermark → address-sorted free-zone list with merge →
  **hidden size header with `FREE`/`USED` magic** (double-free detection) → fixed-size pools/**slab** → `GlobalAlloc` over a simulated
  region, with `alloc_page`/`free_page`/lock hooks behind traits (porting an existing allocator) ⟵ OSDev Memory Allocation · **scheduler**: task struct, context switch via
  the simulated register file; the page's algorithms with golden tick traces: round robin (quantum), priority RR (4–16 queues),
  SVR2 dynamic priority, lottery, FCFS/SJF/SRTN/HRRN, rate-monotonic, EDF; sleep queue with the PIT ⟵ OSDev Scheduling Algorithms · **syscalls**: the page's jump table with the bound check and **holes filled with an
  error handler**, `pt_regs`-style frame, `syscall`/`sysenter` register discipline (zero what is not preserved), `copy_from_user`
  returning `Result` on unmapped pointers ⟵ OSDev System Calls · **ELF loader**: parse headers with offsets, map `PT_LOAD` (zero-fill `memsz > filesz`), set up a stack ⟵
  OSDev ELF · **Multiboot2** header checksum and **tag-list walk** (8-byte aligned, type-0 end tag) ⟵ OSDev Multiboot · process table, **fd table**, **pipes** with blocking via the scheduler · signals (pending mask, delivery on
  return to user).
- **Hard · Build it:** (★) **mini kernel in a box**: boot-info parse (Multiboot2 structure with tags) → memory map → frame
  allocator → page tables → heap → IDT/PIC/PIT → scheduler → syscalls (`write`, `fork`-lite, `exec`-lite) → runs two
  "user programs" (byte arrays for the simulator CPU) with a deterministic transcript · **ATA PIO block driver** against the
  simulated disk, feeding K6's file system via `BlockDevice` · **ext2 mount + `exec` from disk** · **SMP-lite** simulation with
  per-CPU data and a ticket lock under loom · **copy-on-write fork** with page-fault handling · a **demand-paged ELF** loader.

### K23 · Networking: sockets, protocols and a TCP/IP stack · SDE-3 · 32
- **Easy · Sockets with `std::net`:** echo server/client over loopback (`TcpListener`/`TcpStream`) · **partial reads/writes**
  and `read_exact` · length-prefixed and delimiter framing (K2) · `UdpSocket` request/response · `set_nodelay`,
  `set_read_timeout`, `shutdown(Write)` half-close · `BufReader` over a socket · a thread-per-connection server with a pool.
- **Medium · Parse and build packets:** **Ethernet / ARP / IPv4 / IPv6 / UDP / TCP** header parsers returning typed
  views, builders, and the **Internet checksum** with pseudo-header (K3) · IP fragmentation and **reassembly** with holes
  (interval set) · **DNS** message parse including **compression pointers** ⟵ RFC 1035 · an **HTTP/1.1 request parser**
  (httparse-style, incremental, no allocation, `Status::Partial`) · chunked decoding · **non-blocking sockets + `poll`
  loop** with per-connection state machines and write buffering (`WouldBlock`) · TLS-free "protocol framing" of a toy KV protocol ·
  `socket2` options (`SO_REUSEPORT`, buffer sizes) [loopback-only].
- **Hard · Build it:** (★) **a TCP stack over a simulated NIC** (`SimNet`: delay, loss, reorder, duplicate, seeded): three-way
  handshake, sequence numbers with wraparound (`wrapping_sub` comparisons), sliding window, retransmission timeout, fast
  retransmit, `FIN` close, the TCP **state machine** as an enum ⟵ OSDev TCP · congestion control (Reno) with a throughput
  assertion on a lossy link · **ARP cache + routing table** (longest prefix match with a trie) · a **DHCP**/DNS client against
  scripted servers · a **userspace "tun" echo** pipeline from NIC ring → IP → UDP socket API · an **epoll-style readiness API**
  on top of the stack.

### K24 · Verifying systems code · SDE-3 · 24  (replaces Y5)
- **Easy · Test it:** unit, integration, doc tests; `#[should_panic]` vs `Result` · `proptest` strategies for byte buffers ·
  differential test against a reference (`HashMap` vs your table) · `debug_assert!` invariants and `cfg(debug_assertions)`.
- **Medium · Find the bug:** run an unsafe function under **Miri** and fix the finding (uninit read, OOB, aliasing, misaligned,
  leak) · **loom** a broken lock and read the schedule · a **fuzz-style harness** (`proptest` + corpus) for a parser: find the
  panic; add the regression test · round-trip and **model-based** testing (state machine vs reference model) · check
  `size_of`/layout contracts in CI (`const` asserts) · "**what would the sanitizer say?**": classify C++ UB cases and
  their Rust fate (idiom cards).
- **Hard · Build it:** (★) a **linearizability checker** for a concurrent map/queue (history recorder + Wing–Gong search) ·
  a **deterministic simulation test** harness (seeded scheduler, fake clock, `SimDisk`, `SimNet`) in the FoundationDB style, run
  against the K17–K20 engine · crash-point exploration framework · a **sanitiser-lite** that detects use-after-free in your
  arena via generations · coverage-guided mutation for a binary format.

**Totals:** 24 tracks, **~640 anchors** at the minimums above (extra variants will take it past 700), plus the capstone
projects (§6). It is the largest section by design; the SDE-3 path takes all of it, the SDE-2 path takes K1–K5, K9–K11, K14 (Easy
and Medium) only.

---

## 5. What this replaces (rewrite, not patch)

CURRICULUM.md is updated by SYSTEMS_TASKS DOC-1. Nothing below is written except F2 (kept, it becomes a prerequisite
of K2/K3), so nothing is lost.

| Old (unwritten) | Now | Why |
|---|---|---|
| S9 I/O & filesystem | **K5**, K2 | the I/O track was a std tour; it is now graded on syscall counts and durability |
| S10 Time, env & processes | **K15**, K14 (time) | processes, signals and syscalls belong together |
| S11 mem, ptr & alloc | **K8**, K7, F3 → K9/K7 | raw pointers, mmap, allocators are one story |
| C1 Threads & shared state | **K12**, K14 | locks and `Condvar` are systems primitives and are now model-checked |
| C2 Message passing | **K11**, K14 | queues and channels are buffers; `mpsc` is a layer |
| C3 Atomics & lock-free | **K13** | |
| C4–C6 | renumbered **C1–C3** (Async & Tokio; Async internals; Data parallelism) | the Tokio-facing half of C stays a backend topic |
| Y2 Unsafe, Y3 FFI, Y5 Testing | **K8**, **K15**, **K24** | |
| F3 Memory & allocation, F4 Hashing & structures, F6 Concurrency perf | **K7/K9/K10**, **K12/K13** | the *performance grading* ideas (counting allocator, asm, relative timing) are kept as capabilities and used inside K |
| F1 Measure, F2 Data layout (written), F5 CPU tricks, F7 Serialization | **stay in F** | F becomes the focused performance section; K tracks reference F2 and F5 |
| D14 Data-structure design, D13 Matrix/bits | unchanged | interview-shaped; K9/K3 cross-link |
| P (projects) | + **P6 `bustub-rs`**, **P7 `kernel-rs`**, **P8 `minic`**, **P9 `sqlite-lite`** (§6) | capstones |

Anything in the old plan that this table does not mention is kept as is.

---

## 6. Capstone projects (Section P additions)

Project stages carry the repo forward (CURRICULUM "project stage"). Each stage's tests are the *ported* C++ test suite
where one exists, plus golden traces.

- **P6 · `bustub-rs`** (≈ 38 stages): Project 0 primer (trie, trie store, skiplist, count-min sketch, HyperLogLog) → **P1**
  disk manager/scheduler, replacers, buffer pool, guards (= K17) → **P2** extendible hash, B+ tree (= K18) → **P3** executors and
  optimizer (= K19) → **P4** MVCC, lock manager (= K20) → P5 logging and recovery (K16) → SQL front end (K21). Source of truth:
  PORTING.md §2; the C++ is in `cmu-db/bustub` (MIT). A student who finishes P6 has a working relational engine.
- **P7 · `kernel-rs`** (≈ 30 stages): the K22 mini kernel grown into a small OS on `SimMachine`: memory, interrupts,
  scheduler, syscalls, VFS+ext2, ELF exec, pipes/signals, TCP/IP stack (K23), a shell program.
- **P8 · `minic`** (≈ 20 stages): the K21 compiler as a repo: lexer → parser → typecheck → IR → optimisations → register
  allocation → x86-64 → loader on the machine, with a test corpus of programs.
- **P9 · `sqlite-lite`** (≈ 18 stages): a single-file B-tree database with a page cache, a journal (K16), a VDBE-like
  bytecode, and `PRAGMA integrity_check`; reuses K17–K21 ideas on a single-writer design.

---

## 7. Order of work and dependencies

1. **Infrastructure first** (SYSTEMS_TASKS INF-1…INF-12). INF-1 (crates, image) and INF-4 (idiom rules) unblock K1–K5;
   INF-2 (`SimDisk`) unblocks K5/K6/K16/K17; INF-3 (`SimMachine`) unblocks K7/K21/K22; INF-6 (loom) unblocks K11–K13;
   INF-9 (Miri, Windows target) unblocks K8/K24/K4/K15.
2. **Foundation tracks:** K1, K2, K3, K4, K5 (SDE-2 path, no heavy infra).
3. **Structures and concurrency:** K9, K10, K11, K14, then K12, K13 (needs loom).
4. **Durability and storage:** K16, K17, K18, K19, K20 (= `bustub-rs`).
5. **Memory and OS:** K7, K8, K6, K22, K23, K15.
6. **Compilers:** K21 (any time after K2/K3).
7. **Verification:** K24 last; its Easy stage can ship with K2.

Authoring is **one agent per track at a time** (owner's standing rule, HANDOFF §6.0), but different tracks can run in
parallel when they touch disjoint paths (`tools/author/<track>.py`, `content/tracks/<track>/`). Infra tasks touch shared
crates and run **one at a time**.

---

## 8. Idiom cards and the Library

PORTING.md §1 is not just reading. Every table row becomes an **idiom card** (`content/idioms/*.toml`: `front` = the
C/C++ construct, `back` = the Rust idiom and one-line why, `drills` = problem ids that practise it, `tags`). The app shows
them in the **Library** (nav item currently "designed, not built") as a searchable Rosetta stone, and the SRS schedules them
(same FSRS as problems; "solved" = recalled the idiom). Each K problem lists the cards it teaches, so a missed card
resurfaces the right problem. Build tasks: INF-10 (card format and loader), INF-11 (Library page; mockup first, per the
owner's rule), DOC-3 (extract ~400 cards from PORTING.md).

---

## 9. Open questions for the owner

1. **Windows depth.** Plan: `cfg(windows)` code is *compile-checked*, never run. If real Windows behaviour matters more, a
   Windows runner is a separate project. Accept?
2. **Real syscalls.** Plan: tests use `libc`/`rustix` for real Linux syscalls inside the container, so a few problems
   (`getrusage` faults, `fcntl`) are Linux-only and skip elsewhere. macOS-specific (kqueue) is read-only content. Accept?
3. **C++ in the sandbox.** Plan: the C++ is quoted and its behaviour captured as golden traces; **no C++ compiles in the
   runner**. An optional later step is a `cc`-built C library for the K15 FFI problems. Accept?
4. **License.** BusTub is MIT, OSDev wiki code is CC0/public; excerpts are quoted with attribution in problem statements.
5. **Scope pacing.** ~700 problems is a year of authoring. Suggested first release: INF-1/2/4/6 + K1, K2, K3, K5, K11, K12
   (~170 problems) then K17 stage by stage.
