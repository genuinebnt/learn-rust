---
title: unsafe: what it promises and why this course has none
summary: What the unsafe keyword allows, the obligations the programmer takes on, how to write and review a SAFETY comment, and where a database might need it (and how miri checks it).
minutes: 6
---
`unsafe` does not turn the borrow checker off; it unlocks **five extra abilities** the compiler cannot check: dereferencing a raw pointer, calling an `unsafe fn`, accessing a `static mut`, implementing an `unsafe trait` (such as `Send` or `Sync`), and accessing fields of a `union`. Everything else is still checked. The block means: *"I have verified the conditions the compiler cannot."*

## The contract

Each `unsafe` operation has a precondition (a raw pointer is non-null, aligned, points to an initialised value that nobody else mutates meanwhile; a `transmute` target accepts every bit pattern of the source; an `unsafe impl Send` type really can move between threads). Violating one is **undefined behaviour**: not a crash you can debug but a program that the compiler was allowed to compile into anything.

A good `unsafe` block is therefore tiny, wrapped in a safe function whose signature makes misuse impossible, and carries a `// SAFETY:` comment naming each condition and why it holds. An `unsafe fn` documents what the caller must guarantee under `# Safety`. The review checklist from the `rust-skills` unsafe guide: every block has a SAFETY comment; pointers are valid, aligned and initialised; no aliasing of `&mut`; no data races; `Send`/`Sync` impls are really sound; no uninitialised memory (use `MaybeUninit`); no invalid bit patterns.

## Why this course has none

The reference crate has no `unsafe` at all, on purpose: pages are `[u8]` slices read and written with `from_le_bytes`/`to_le_bytes`; shared state is behind `Mutex`/`RwLock`/atomics; linked structures are arenas with index links rather than raw pointers; type punning is `as` or `TryFrom`, not `transmute`. The things a C++ buffer pool does with pointer casts (`reinterpret_cast<Page *>`) become byte-slice reads with explicit endianness, at the cost of a copy or a little bounds checking.

Where a real system reaches for `unsafe`: zero-copy views of page memory (`&[u8]` reinterpreted as a struct, guarded by `#[repr(C)]` and alignment checks: see the repr(C) article), intrusive lock-free lists, memory-mapped files, SIMD, FFI. Even there, the usual advice is to prefer a vetted crate (`bytemuck` for plain-old-data casts, `zerocopy`, `memmap2`) over writing the `unsafe` yourself.

## miri keeps unsafe honest

`cargo +nightly miri test` runs your tests in an interpreter that tracks every pointer and flags out-of-bounds reads, use after free, uninitialised reads, misaligned access, invalid values and data races. If you ever add `unsafe` to this codebase, run the affected tests under miri before anything else (see the *testing concurrent code* article).

## C++ comparison

| C / C++ | Rust |
|---|---|
| every pointer operation is "unsafe" | only raw pointer dereference and a few others are, inside marked blocks |
| `reinterpret_cast<T *>(buffer)` | `T::from_le_bytes(buffer[..].try_into().unwrap())`, or `unsafe` with a SAFETY comment |
| `std::launder`, `volatile` | rarely needed; atomics and `MaybeUninit` |
| sanitizers find UB at run time | miri finds it in an interpreter; safe Rust cannot have it |

**Port rule:** replace a cast of bytes to a struct with explicit field reads; keep `unsafe` for the one place that proves it is needed in a profile.

## In real code

### Using it: the safe version of a pointer cast

```rust test
fn read_header(page: &[u8]) -> (u32, u16) {
    // reading fields at fixed offsets: bounds-checked, endian-explicit, no unsafe
    let magic = u32::from_le_bytes(page[0..4].try_into().unwrap());
    let count = u16::from_le_bytes(page[4..6].try_into().unwrap());
    (magic, count)
}

fn write_header(page: &mut [u8], magic: u32, count: u16) {
    page[0..4].copy_from_slice(&magic.to_le_bytes());
    page[4..6].copy_from_slice(&count.to_le_bytes());
}

#[test]
fn fields_round_trip_through_bytes() {
    let mut page = vec![0u8; 16];
    write_header(&mut page, 0xB057_AB, 42);
    assert_eq!(read_header(&page), (0xB057_AB, 42));
    assert_eq!(&page[0..4], &[0xAB, 0x57, 0xB0, 0x00], "little-endian, whatever the machine");
}

#[test]
fn a_short_slice_is_a_panic_not_a_wild_read() {
    let short = vec![0u8; 3];
    assert!(std::panic::catch_unwind(|| read_header(&short)).is_err());
}
```

### Using it: a tiny unsafe wrapper with its SAFETY comment

```rust test
/// Swaps two distinct elements of a slice without cloning (what `slice::swap` does for you; shown to practise the contract).
fn swap_distinct<T>(v: &mut [T], i: usize, j: usize) {
    assert!(i != j && i < v.len() && j < v.len(), "indexes must be distinct and in range");
    let ptr = v.as_mut_ptr();
    // SAFETY: i and j are distinct and both < v.len(), so `ptr.add(i)` and `ptr.add(j)` are valid, aligned,
    // initialised and do not alias each other; we hold the only &mut to the slice.
    unsafe {
        std::ptr::swap(ptr.add(i), ptr.add(j));
    }
}

#[test]
fn the_wrapper_swaps_and_checks_its_own_preconditions() {
    let mut v = vec![String::from("a"), String::from("b"), String::from("c")];
    swap_distinct(&mut v, 0, 2);
    assert_eq!(v, vec!["c", "b", "a"]);
    assert!(std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| swap_distinct(&mut vec![1, 2], 0, 0))).is_err());
}

#[test]
fn the_safe_standard_function_does_the_same() {
    let mut v = vec![1, 2, 3];
    v.swap(0, 2);
    assert_eq!(v, vec![3, 2, 1]);
}
```

### In the exercises

- **2a-01:** typed values read from page bytes through `from_le_bytes`, the safe alternative to casting.
- **3b:** tuples and table pages as byte layouts.
- **1a:** positional I/O into byte buffers.

### Where it is used

- **The standard library** (`Vec`, `Arc`, `Mutex` are built on small audited `unsafe`), **`bytemuck`/`zerocopy`** for casts, **`memmap2`** for mapped files, and every FFI binding.
- The Rustonomicon is the reference for what unsafe code must uphold.
