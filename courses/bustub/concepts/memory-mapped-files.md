---
title: Memory-mapped files: what mmap gives you and why databases avoid it
summary: How `mmap` makes a file look like memory, what a page fault, `msync` and `SIGBUS` mean for a Rust program, and the four reasons a DBMS manages its own buffer pool instead.
minutes: 8
---
`mmap` asks the operating system to make a file's bytes appear at an address range in your process. You read `ptr[i]` and the kernel loads the page from disk on demand (a **page fault**); you write it and the kernel marks the page dirty and writes it back *whenever it likes*. It is the OS's own buffer pool, handed to you as a slice.

| you do | what happens |
|---|---|
| read an address not yet loaded | a page fault; the thread stops until the kernel reads the 4 KiB page |
| write to a `MAP_SHARED` mapping | the page is dirty in the OS page cache; another `read` of the file sees it at once; it reaches disk later |
| `msync` the range | the dirty pages are written back now (`MS_SYNC` waits) |
| the file is truncated by someone else, or the disk fails | the next access raises **`SIGBUS`**, which is not an `Err` and not a panic: it kills the process unless a signal handler is installed |
| `munmap` | the range disappears; a slice that still points there is a dangling reference |

## Why this is `unsafe` in Rust

A `&[u8]` over a mapping promises the bytes do not change while it is borrowed. Another process (or another mapping of the same file) can change them at any moment, and a truncation turns a read into a crash. The compiler cannot see either, so a safe `mmap` API is a lie unless it documents the condition. The `memmap2` crate's `Mmap::map` is `unsafe` for exactly this reason: *the caller guarantees nobody modifies or truncates the file while it is mapped.*

## Why a DBMS does not use it

The paper *Are You Sure You Want to Use MMAP in Your DBMS?* (Crotty, Leis, Pavlo, CIDR 2022; linked from the buffer-pool module) gives four reasons, each of which the buffer pool you build solves:

1. **Transactional safety.** The OS may write a dirty page to disk *before* the transaction commits, and you cannot stop it. A buffer pool pins a page, so a dirty page is written only after its log record is durable (the write-ahead rule; see the *durability and fsync* article).
2. **I/O stalls.** A page fault blocks the thread with no warning; a buffer pool knows a page is absent and can prefetch or run another request.
3. **Error handling.** A failed read is a `SIGBUS` somewhere in the middle of your code instead of an `io::Error` you handle at the call.
4. **Performance.** The kernel's page-table and TLB work happens on every fault and eviction, and with many fast SSDs it becomes the bottleneck; the eviction policy is the OS's, not the one (LRU-K) your workload needs.

mmap is still the right tool when the data is **read-only, fits the working set, and a crash costs nothing**: an index loaded at start-up, a compiled dictionary, a large model file, the executable itself. LMDB builds a whole database on a read-only map plus copy-on-write pages, which sidesteps reasons 1 and 3.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `mmap(NULL, len, PROT_READ, MAP_SHARED, fd, 0)` | the `memmap2` crate (`unsafe { Mmap::map(&file) }`), or `libc::mmap` |
| `munmap(p, len)` in a destructor | `Drop` for the wrapper type |
| `msync(p, len, MS_SYNC)` | `MmapMut::flush()` |
| `boost::interprocess::mapped_region` | `memmap2::MmapMut` |

**Port rule:** the unsafety is the same; Rust lets you put it in one type with a `Drop` and one documented condition.

## In real code

### Using it: a mapping type with `Drop`, on Unix

The standard library has no `mmap`, so this declares the two libc functions it needs (the constants below are the same on Linux and macOS). A real program would use `memmap2`.

```rust test
#[cfg(unix)]
mod map {
    use std::ffi::{c_int, c_void};
    use std::fs::File;
    use std::os::fd::AsRawFd;

    extern "C" {
        fn mmap(addr: *mut c_void, len: usize, prot: c_int, flags: c_int, fd: c_int, offset: i64) -> *mut c_void;
        fn munmap(addr: *mut c_void, len: usize) -> c_int;
    }
    const PROT_READ: c_int = 1;
    const PROT_WRITE: c_int = 2;
    const MAP_SHARED: c_int = 1;

    /// A writable shared mapping of a whole file.
    pub struct MapMut {
        ptr: *mut u8,
        len: usize,
    }

    impl MapMut {
        /// # Safety
        /// Nothing else may truncate the file while the mapping exists; that would make a later access raise SIGBUS.
        pub unsafe fn new(file: &File, len: usize) -> std::io::Result<MapMut> {
            let p = mmap(std::ptr::null_mut(), len, PROT_READ | PROT_WRITE, MAP_SHARED, file.as_raw_fd(), 0);
            if p as isize == -1 {
                return Err(std::io::Error::last_os_error()); // MAP_FAILED
            }
            Ok(MapMut { ptr: p as *mut u8, len })
        }
        pub fn as_slice(&self) -> &[u8] {
            // SAFETY: the mapping is `len` bytes and lives as long as `self`.
            unsafe { std::slice::from_raw_parts(self.ptr, self.len) }
        }
        pub fn as_mut_slice(&mut self) -> &mut [u8] {
            // SAFETY: as above, and `&mut self` makes this the only slice we hand out.
            unsafe { std::slice::from_raw_parts_mut(self.ptr, self.len) }
        }
    }

    impl Drop for MapMut {
        fn drop(&mut self) {
            // SAFETY: `ptr`/`len` are exactly what `mmap` returned, and this runs once.
            unsafe { munmap(self.ptr as *mut c_void, self.len) };
        }
    }

    #[test]
    fn a_write_to_the_mapping_is_a_write_to_the_file() {
        use std::io::Read;
        let path = std::env::temp_dir().join(format!("anneal-mmap-{}", std::process::id()));
        let mut file = std::fs::OpenOptions::new().read(true).write(true).create(true).truncate(true).open(&path).unwrap();
        file.set_len(4096).unwrap(); // a mapping needs the file to be that long already
        {
            // SAFETY: this test is the only user of the file.
            let mut m = unsafe { MapMut::new(&file, 4096).unwrap() };
            m.as_mut_slice()[..5].copy_from_slice(b"hello");
            assert_eq!(&m.as_slice()[..5], b"hello");
        } // unmapped here
        let mut head = [0u8; 5];
        std::fs::File::open(&path).unwrap().read_exact(&mut head).unwrap();
        assert_eq!(&head, b"hello", "the page cache is shared, so a plain read sees the mapped write");
        std::fs::remove_file(&path).unwrap();
    }

    #[test]
    fn a_file_that_cannot_be_mapped_is_an_error_not_a_crash() {
        let file = std::fs::File::open("/dev/null").unwrap();
        // SAFETY: the file is never truncated by anyone.
        let err = unsafe { MapMut::new(&file, 4096) };
        assert!(err.is_err(), "mmap reports a failure through errno, which becomes an io::Error");
    }
}
```

### In the exercises

- **1f-03:** the stage's comparison table says why the buffer pool writes a page itself instead of leaving it to a mapping, and links the paper above.

### Where it is used

- **LMDB** and **BoltDB / bbolt** map the whole database file read-only and use copy-on-write pages for updates.
- **SQLite** offers an optional `mmap_size` for reads; **MongoDB's** first storage engine (MMAPv1) was replaced by WiredTiger, which manages its own cache; the paper discusses that move.
- Loaders for **large read-only files** (language-model weights, the Linux kernel's `vmlinux`, shared libraries) use mmap so that many processes share one copy in the page cache.
