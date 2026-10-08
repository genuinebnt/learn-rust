---
title: Const generics: a number in the type
summary: Types that depend on a number (an array length, a buffer capacity), defaults for that number, associated constants computed from it, and why a page layout belongs in the type; the same idea as C++'s non-type template parameters.
minutes: 9
---
Some facts about a data structure are **numbers that never change for a given use**: the length of an array, how many tombstones a leaf can buffer, how many bytes a key takes. If a number is part of the *type*, the compiler knows it: it can compute offsets once, reject mixing two incompatible layouts, and delete code for the case where the number is zero. Rust calls these parameters **const generics**; C++ calls them non-type template parameters (`template <size_t N>`).

## The syntax

```rust
struct Ring<T, const N: usize> { items: [Option<T>; N], head: usize, len: usize }   // N is part of the type

impl<T: Copy, const N: usize> Ring<T, N> {
    const CAPACITY: usize = N;                       // an associated const computed from the parameter
    fn new() -> Self { Ring { items: [None; N], head: 0, len: 0 } }
}

let a: Ring<u32, 4> = Ring::new();                   // Ring<u32, 4> and Ring<u32, 8> are different types
```

`const N: usize` can have a **default** (`const N: usize = 0`), used when a type is written without it (`Ring<u32>` means `Ring<u32, 0>`). A caveat: defaults apply in *type* positions (struct fields, function signatures, aliases) but not when a path in an expression leaves a parameter to inference, so a function that must work for every `N` is itself generic over it.

| in a type | meaning |
|---|---|
| `[T; N]` | an array whose length the compiler knows |
| `Leaf<B, K, V, 0>` | a leaf with no tombstone buffer |
| `Leaf<B, K, V, 3>` | a leaf with a 3-key buffer: a different type, a different layout |
| `where [(); N]:` | (not stable) arithmetic in types: compute with associated consts instead |

## Why a page layout belongs in the type

The leaf's entries start at byte `16 + 4 + 8 * TOMBS` when it has tombstones and at 16 when it has none. Make `TOMBS` a field of the page and every entry access reads it first, a page written with one value can be read with another, and the "no tombstones" case still pays for checks. Make it a type parameter and:

- the offsets are constants (`ENTRIES_AT`), folded by the compiler;
- `if TOMBS == 0 { return ...; }` is decided at compile time, so the zero case has no overhead and no code;
- a mismatch (`Leaf<_, K, V, 2>` where a `Leaf<_, K, V, 3>` is expected) is a **compile error**, not a corrupted page.

> [!WARNING] The price
> Every function that touches the type must carry the parameter: `impl<const TOMBS: usize> ...`, `Leaf::<_, K, V, TOMBS>::new`. Forget it in one place and the default (0) quietly applies: the code compiles, and works, for trees without tombstones only. The tests for the feature use a non-zero value for exactly that reason.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `template <typename K, ssize_t NumTombs = 0> class Leaf` | `struct Leaf<K, const TOMBS: usize = 0>` |
| `size_t tombstones_[LEAF_PAGE_TOMB_CNT];` with a macro | an associated `const TOMB_REGION: usize` and offsets computed from it |
| `if constexpr (N > 0)` | `if N > 0 { ... }` (constant condition, folded; the branch must still type-check) |
| `static_assert(N > 0, "...")` | `const _: () = assert!(N > 0);` inside the impl, or `const { assert!(N > 0) }` in a function |

## In real code

### Using it: a ring buffer that costs nothing at N = 0, and offsets from a parameter

```rust test
/// A fixed-capacity buffer of the last N values, oldest first (the shape of the tombstone buffer).
struct Last<T, const N: usize = 0> { items: [Option<T>; N], len: usize }

impl<T: Copy, const N: usize> Last<T, N> {
    const CAPACITY: usize = N;
    fn new() -> Self { Last { items: [None; N], len: 0 } }

    /// Adds `value` as the newest; if the buffer is full the oldest falls out and is returned.
    fn push(&mut self, value: T) -> Option<T> {
        if N == 0 { return Some(value); }                    // a constant condition: with N = 0 the rest is dead code
        let mut evicted = None;
        if self.len == N {
            evicted = self.items[0];
            self.items.copy_within(1.., 0);
            self.len -= 1;
        }
        self.items[self.len] = Some(value);
        self.len += 1;
        evicted
    }
    fn to_vec(&self) -> Vec<T> { self.items[..self.len].iter().map(|x| x.unwrap()).collect() }
}

#[test]
fn the_capacity_is_part_of_the_type_and_the_oldest_falls_out() {
    let mut last: Last<u32, 3> = Last::new();
    assert_eq!(Last::<u32, 3>::CAPACITY, 3);
    assert_eq!((last.push(1), last.push(2), last.push(3)), (None, None, None));
    assert_eq!(last.push(4), Some(1), "full: the oldest is returned");
    assert_eq!(last.to_vec(), vec![2, 3, 4]);
}

#[test]
fn n_equal_to_zero_is_a_buffer_that_keeps_nothing_and_takes_no_room() {
    let mut none: Last<u32> = Last::new();                  // the default N = 0
    assert_eq!(none.push(7), Some(7), "nothing is kept: the value comes straight back");
    assert_eq!(std::mem::size_of::<Last<u32, 0>>(), std::mem::size_of::<usize>(), "no items array: just the length");
    assert!(std::mem::size_of::<Last<u32, 8>>() > std::mem::size_of::<Last<u32, 0>>());
}
```

```rust test
/// A page layout that depends on how many tombstone keys it can buffer.
struct Layout<const TOMBS: usize>;

impl<const TOMBS: usize> Layout<TOMBS> {
    const HEADER: usize = 16;
    const KEY: usize = 8;
    /// Bytes between the header and the entries: nothing for TOMBS = 0, otherwise a 4-byte count and the keys.
    const TOMB_REGION: usize = if TOMBS == 0 { 0 } else { 4 + TOMBS * Self::KEY };
    const ENTRIES_AT: usize = Self::HEADER + Self::TOMB_REGION;
    const fn capacity(page: usize, entry: usize) -> usize { (page - Self::ENTRIES_AT) / entry }
}

// a compile-time check, like BusTub's static_assert on the page struct: this would not compile if the layout outgrew a page
const _: () = assert!(Layout::<8>::ENTRIES_AT < 8192);

#[test]
fn offsets_and_capacities_are_constants_computed_from_the_parameter() {
    assert_eq!(Layout::<0>::ENTRIES_AT, 16, "no tombstones: the old layout, byte for byte");
    assert_eq!(Layout::<1>::ENTRIES_AT, 28);
    assert_eq!(Layout::<2>::ENTRIES_AT, 36);
    assert_eq!(Layout::<0>::capacity(8192, 16), 511);
    assert_eq!(Layout::<2>::capacity(8192, 16), 509);
    assert_eq!(Layout::<3>::capacity(8192, 16), 509);
    assert_eq!(Layout::<4>::capacity(8192, 16), 508);
}

#[test]
fn different_parameters_are_different_types() {
    fn takes_three(_: &Layout<3>) {}
    takes_three(&Layout::<3>);
    // takes_three(&Layout::<2>);   // does not compile: expected `Layout<3>`, found `Layout<2>`
    assert_ne!(std::any::type_name::<Layout<2>>(), std::any::type_name::<Layout<3>>());
}
```

### In the exercises

- **2d-01:** `BPlusTreeLeafPage<B, K, V, const TOMBS: usize = 0>`, `TOMB_REGION` and `ENTRIES_AT` are the second test's constants; the first test is the buffer's behaviour (`add_tombstone` returning the evicted key is `remove_logically`'s "remove the oldest" step).
- **2d-02, 2d-03:** `Leaf::<_, K, V, TOMBS>::new` everywhere in your tree and iterator; `if TOMBS > 0 { leaf.remove_logically(..) } else { leaf.remove(..) }` is the `if N == 0` of the first test.
- **Tests:** `new_tree_t::<2>(..)`, `IndexLeaves::<2>::with_tombstones(..)` pass the parameter explicitly.

### Where it is used

- **`[T; N]` and `std::array`**: every fixed-size array in Rust is a const generic type; `impl<T, const N: usize> Default for [T; N]`-style impls, `array::map`, `<[T; N]>::try_from(slice)`.
- **`arrayvec`, `smallvec`, `heapless`**: containers with an inline capacity `N` known at compile time: no allocation until it is exceeded (or never).
- **Matrices and SIMD** (`nalgebra`'s `SMatrix<T, R, C>`, `std::simd::Simd<T, N>`): dimensions in the type, so a 3x3 times a 4x4 does not compile.
- **Embedded and kernel code**: buffer sizes, page sizes and register counts as type parameters, checked with `const` assertions.
