---
title: Traits with associated constants: sizing things at compile time
summary: How FixedSize gives every storable type a SIZE known to the compiler, how generics use it for array capacities, and what const fn can and cannot compute, against C++ templates and sizeof.
minutes: 9
---
An index page holds an array of entries, and how many fit depends on the entry's size. In C++ that is `sizeof(MappingType)` inside a template. In Rust it is an **associated constant** on a trait, and the compiler knows it at compile time.

## The trait

```rust
pub trait FixedSize: Sized {
    const SIZE: usize;                         // the number of bytes of one value in a page
    fn encode(&self, out: &mut [u8]);          // write exactly SIZE bytes
    fn decode(bytes: &[u8]) -> Self;           // read exactly SIZE bytes
}

impl FixedSize for i32 { const SIZE: usize = 4; /* encode, decode via to_le_bytes */ }
impl FixedSize for Rid { const SIZE: usize = 8; /* ... */ }
```

`T::SIZE` is a *constant of the type*, like `sizeof(T)` but defined by you, not by the compiler's layout: it is the size in the **page format**, which need not equal `size_of::<T>()` (a `Rid` struct might have padding; its encoding does not).

## Composing: a pair of fixed-size values is fixed-size

```rust
impl<A: FixedSize, B: FixedSize> FixedSize for (A, B) {
    const SIZE: usize = A::SIZE + B::SIZE;     // computed at compile time from the two parts
    fn encode(&self, out: &mut [u8]) { let (a, b) = out.split_at_mut(A::SIZE); self.0.encode(a); self.1.encode(b); }
    fn decode(bytes: &[u8]) -> (A, B) { let (a, b) = bytes.split_at(A::SIZE); (A::decode(a), B::decode(b)) }
}
```

So `(GenericKey<8>, Rid)` has `SIZE == 16` with no code written for that case. The C++ equivalent is a `std::pair<KeyType, ValueType>` with `sizeof` and a reinterpret cast: shorter, and it bakes the *compiler's* padding into the file format.

## Const fn and array sizes

```rust
pub const fn array_size(metadata_size: usize, entry_size: usize) -> usize {
    (BUSTUB_PAGE_SIZE - metadata_size) / entry_size
}
const BUCKET_CAP: usize = array_size(HTABLE_BUCKET_PAGE_METADATA_SIZE, <(GenericKey<8>, Rid)>::SIZE);   // 8184 / 16 = 511
```

A `const fn` can be evaluated by the compiler, so the result can size an array or appear in a `const` item. **What it cannot do (today)**: use generic parameters in an array length (`[u8; T::SIZE]` for a generic `T` is not allowed on stable Rust), call non-`const` functions, or allocate. That is why page views compute offsets at run time from `T::SIZE` instead of declaring `[T; N]` fields: the **capacity** is a method, `bytes.len() / T::SIZE`.

| C++ | Rust |
|---|---|
| `sizeof(T)` | `size_of::<T>()` (layout) or `T::SIZE` (your page format) |
| `template <typename K, typename V> class Bucket { std::pair<K,V> array_[]; }` | `struct Bucket<B, K, V>` with `K: FixedSize, V: FixedSize` |
| `constexpr size_t N = (PAGE_SIZE - 8) / sizeof(MappingType);` | `const N: usize = array_size(8, <(K, V)>::SIZE);` |
| `static_assert(sizeof(X) <= PAGE_SIZE)` | `const _: () = assert!(size_of::<X>() <= PAGE_SIZE);` |
| duck-typed templates: errors are pages long | trait bounds: `K: FixedSize` is checked at the call site |

## Why a trait and not a macro or an enum

A **trait bound** says what a generic type must provide, once, and the compiler checks it where the type is used; an error is "the trait `FixedSize` is not implemented for `String`". The alternative, a macro that pastes `sizeof`, has no check and no name for the idea. And unlike an enum of known types, a trait is **open**: the B+ tree and the table heap can add their own storable types without touching this module.

> [!NOTE] Limits worth knowing
> `const SIZE` has no default that varies with a generic parameter in an array length (yet), and a trait with an associated `const` is not object safe: you cannot write `&dyn FixedSize`. Neither matters here, because the page views are generic and monomorphised.
