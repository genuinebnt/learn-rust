---
title: FFI: calling C from Rust and being called by C
summary: How `extern "C"` declarations, `repr(C)`, `CString`/`CStr` and callbacks work, who owns memory across the boundary (the `Box::into_raw` / `from_raw` pair), and why a panic must never cross it.
minutes: 9
---
Systems code lives next to C: the operating system's API, `libc`, SQLite, a vendor's driver. Rust talks to it through the **C ABI**, the calling convention every language can reach. Nothing on the other side is checked by the Rust compiler, so every FFI call is `unsafe` and the safe wrapper you write around it is where the contract lives.

## The pieces

| piece | what it is for |
|---|---|
| `extern "C" { fn strlen(s: *const c_char) -> usize; }` | declares a C function; you promise the signature is right (a wrong one is undefined behaviour, not a compile error) |
| `#[repr(C)]` | lays a struct out field by field in order, like C; the default `repr(Rust)` layout is unspecified |
| `extern "C" fn cb(...)` | a Rust function with the C calling convention, so C can call it (a callback) |
| `#[no_mangle]` / `#[unsafe(no_mangle)]` | keeps a Rust function's symbol name so C can link to it |
| `CString` / `CStr` | an owned / borrowed **NUL-terminated** string; a Rust `String` is neither NUL-terminated nor guaranteed free of interior NULs |
| `c_int`, `c_char`, `c_void` | the C types, in `std::ffi` |
| `Box::into_raw` / `Box::from_raw` | hand a Rust value to C as a pointer, and take it back to free it |

Since Rust 2024 an `extern` block is written `unsafe extern "C" { ... }`; the course's other code uses 2021, where the plain form compiles.

## Four rules at the boundary

1. **Wrap the call once, in a safe function** whose argument types make the C contract impossible to break (`&CStr`, `&mut [i32]`), with a `// SAFETY:` comment on the `unsafe` block saying why it holds.
2. **Strings:** keep the `CString` in a variable for as long as C uses the pointer. `CString::new(s).unwrap().as_ptr()` frees the string at the end of the statement and hands C a dangling pointer.
3. **Ownership:** decide who allocates and who frees, and free with the *same allocator*. Memory from Rust's `Box` is freed by `Box::from_raw`, never by C's `free`; memory from `malloc` is freed by `free`, never dropped by Rust.
4. **Never let a panic unwind into C.** Unwinding through a C frame is undefined behaviour (since Rust 1.81 an `extern "C"` function that would unwind aborts instead). Catch it with `std::panic::catch_unwind` and return an error code.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `extern "C" { int abs(int); }` (also to expose C++ to C) | `extern "C" { fn abs(i: c_int) -> c_int; }` (to expose Rust: `#[no_mangle] pub extern "C" fn`) |
| `const char*` and `strlen` | `CStr` (borrowed), `CString` (owned) |
| `std::unique_ptr::release()` / `reset(p)` | `Box::into_raw` / `Box::from_raw` |
| a C++ exception thrown through a C frame is undefined | a Rust panic through a C frame is undefined (or an abort); use `catch_unwind` |
| hand-written headers | `bindgen` makes Rust declarations from a header, `cbindgen` makes a header from Rust |

**Port rule:** treat every `unsafe extern` signature as a promise you must check against the C header; `bindgen` exists so you do not have to check it by eye.

## In real code

### Using it: calling C, with a callback

```rust test
use std::ffi::{c_char, c_int, c_void, CStr, CString};

extern "C" {
    fn strlen(s: *const c_char) -> usize;
    fn abs(i: c_int) -> c_int;
    fn qsort(base: *mut c_void, n: usize, size: usize, cmp: extern "C" fn(*const c_void, *const c_void) -> c_int);
}

/// Safe wrapper: a `&CStr` is guaranteed NUL-terminated and valid for the call.
fn c_len(s: &CStr) -> usize {
    // SAFETY: `s.as_ptr()` points to a NUL-terminated string that outlives the call.
    unsafe { strlen(s.as_ptr()) }
}

extern "C" fn compare_i32(a: *const c_void, b: *const c_void) -> c_int {
    // SAFETY: qsort passes pointers to two elements of the slice we gave it, each a valid, aligned i32.
    let (a, b) = unsafe { (*(a as *const i32), *(b as *const i32)) };
    a.cmp(&b) as c_int
}

/// Sorts with C's `qsort`; the element size and count come from the slice, so they cannot disagree.
fn sort_with_qsort(v: &mut [i32]) {
    // SAFETY: the pointer and length describe exactly `v`; `compare_i32` reads only i32s.
    unsafe { qsort(v.as_mut_ptr() as *mut c_void, v.len(), std::mem::size_of::<i32>(), compare_i32) }
}

#[test]
fn c_string_length_counts_up_to_the_nul() {
    let s = CString::new("buffer pool").unwrap();
    assert_eq!(c_len(&s), 11);
    assert!(CString::new("a\0b").is_err(), "an interior NUL cannot be passed to C");
}

#[test]
fn a_rust_callback_runs_inside_c() {
    let mut v = [5, -2, 9, 0, 3];
    sort_with_qsort(&mut v);
    assert_eq!(v, [-2, 0, 3, 5, 9]);
    assert_eq!(unsafe { abs(-7) }, 7);
}
```

### Using it: ownership across the boundary, and a panic that stays inside

```rust test
use std::ffi::c_int;
use std::panic::catch_unwind;
use std::sync::atomic::{AtomicUsize, Ordering};

static LIVE: AtomicUsize = AtomicUsize::new(0);

struct Counter {
    n: u64,
}
impl Counter {
    fn new() -> Counter {
        LIVE.fetch_add(1, Ordering::SeqCst);
        Counter { n: 0 }
    }
}
impl Drop for Counter {
    fn drop(&mut self) {
        LIVE.fetch_sub(1, Ordering::SeqCst);
    }
}

// What a C library would see: an opaque pointer with a create / use / destroy trio.
#[no_mangle]
pub extern "C" fn counter_new() -> *mut Counter {
    Box::into_raw(Box::new(Counter::new())) // ownership moves to the caller
}

#[no_mangle]
pub extern "C" fn counter_add(c: *mut Counter, by: u64) -> c_int {
    // Never unwind into C: turn a panic into an error code.
    let result = catch_unwind(|| {
        // SAFETY: the caller passes a pointer from `counter_new` that it has not destroyed.
        let c = unsafe { c.as_mut() }.expect("null counter");
        c.n = c.n.checked_add(by).expect("overflow");
    });
    if result.is_ok() { 0 } else { -1 }
}

#[no_mangle]
pub extern "C" fn counter_destroy(c: *mut Counter) {
    if !c.is_null() {
        // SAFETY: the pointer came from `Box::into_raw` in `counter_new` and is freed exactly once.
        drop(unsafe { Box::from_raw(c) });
    }
}

#[test]
fn create_use_destroy_frees_exactly_once_and_errors_are_codes() {
    let c = counter_new();
    assert_eq!(LIVE.load(Ordering::SeqCst), 1);
    assert_eq!(counter_add(c, 5), 0);
    assert_eq!(counter_add(c, u64::MAX), -1, "an overflow panic became an error code, not an unwind into C");
    assert_eq!(counter_add(std::ptr::null_mut(), 1), -1, "a null pointer is an error, not undefined behaviour");
    counter_destroy(c);
    assert_eq!(LIVE.load(Ordering::SeqCst), 0);
    counter_destroy(std::ptr::null_mut()); // destroying null is a no-op, as `free(NULL)` is
}
```

### In the exercises

No stage in this course crosses into C. The `unsafe` you meet in 1g-01 (page guards) and 2a-01 (typed values in raw page bytes) follows the same rule as rule 1 above: a safe type around a small `unsafe` block with a `// SAFETY:` comment. Read the *`unsafe` and its contracts* article first; this one adds the boundary to another language.

### Where it is used

- **SQLite, zlib, OpenSSL, libgit2** are C libraries Rust programs link through `-sys` crates (`libsqlite3-sys`, `libz-sys`), with a safe crate on top (`rusqlite`, `flate2`).
- **The Linux kernel**'s Rust support and **Firefox** (Stylo, WebRender) expose Rust to C and C++ through `extern "C"` and `cbindgen`-style headers.
- **PyO3** and **Neon** are FFI too: they turn a Rust function into one Python or Node can call.
