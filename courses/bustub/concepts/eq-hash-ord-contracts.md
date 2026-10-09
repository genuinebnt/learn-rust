---
title: Eq, Hash and Ord: the contracts a map key must keep
summary: What equality, hashing and ordering promise each other, what breaks a HashMap or BTreeMap when they disagree, why floats are not keys, and how to derive or write them for a key type.
minutes: 6
---
Keys of a `HashMap` need `Eq + Hash`; keys of a `BTreeMap`/`BTreeSet` need `Ord`. Those traits are **contracts**: the collection's correctness depends on you keeping them, and the compiler cannot check them.

| trait | promise |
|---|---|
| `PartialEq` / `Eq` | `==` is symmetric and transitive; `Eq` adds **reflexive** (`a == a`) |
| `Hash` | **equal values hash equally**: `a == b` implies `hash(a) == hash(b)` (the converse is not required) |
| `PartialOrd` / `Ord` | a **total order**: any two values compare, consistently with each other and with `Eq` (`a.cmp(b) == Equal` exactly when `a == b`) |

## What breaks

- `Hash` and `Eq` disagree (two equal keys hash differently): `get` misses keys that are there.
- `Ord` and `Eq` disagree: a `BTreeMap` may hold two "equal" keys, or lose one.
- A key **changes while it is in the map** (through interior mutability): it is now in the wrong place; lookups fail. Keys must not mutate.
- **`f32`/`f64` are not `Eq`/`Ord`**: `NaN != NaN` and `NaN` has no order. Wrap floats with a total-order key (`f64::total_cmp`, or convert to bits) before using them as keys. This is why SQL values need their own comparison and NULL handling (the *sort keys and NULL ordering* and *hashing values* articles).

## Derive when you can

`#[derive(PartialEq, Eq, Hash, PartialOrd, Ord)]` compares **field by field in declaration order** (for enums, by variant order first). That is exactly right for `PageId(i32)` or `(T, Uid)` pairs. Write the traits by hand only when equality is not field-wise (case-insensitive strings, a comparator chosen at run time) and then implement them **together** so they agree.

## Tuples and ordering

`(a, b)` orders by `a` then `b`: this course's `BTreeSet<(T, Uid)>` in the OR-Set keeps all pairs of one element adjacent, and the replacers' `BTreeSet<(priority, id)>` gives "smallest first" for free.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `operator==` plus `std::hash<T>` specialisation that must agree | `PartialEq`/`Eq` plus `Hash`, normally derived together |
| `operator<` strict weak ordering | `Ord` (total order) |
| `std::set` with a custom comparator type | a wrapper type implementing `Ord`, or `BTreeMap` with a `Reverse<T>` key |
| `float` as `std::map` key (NaN breaks it) | not allowed: `f64` is not `Ord` |

**Port rule:** `std::hash` + `operator==` becomes `#[derive(Hash, PartialEq, Eq)]`; a comparator functor becomes an `Ord` impl on a wrapper.

## In real code

### Using it: derive and a hand-written case-insensitive key

```rust test
use std::collections::{BTreeSet, HashMap, HashSet};
use std::hash::{Hash, Hasher};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
struct PageId(i32);

#[derive(Debug, Clone)]
struct CaseInsensitive(String);

impl PartialEq for CaseInsensitive {
    fn eq(&self, other: &Self) -> bool {
        self.0.eq_ignore_ascii_case(&other.0)
    }
}
impl Eq for CaseInsensitive {}
impl Hash for CaseInsensitive {
    fn hash<H: Hasher>(&self, state: &mut H) {
        // equal keys (ignoring case) must hash equally: hash the lower-cased bytes
        for b in self.0.bytes() {
            state.write_u8(b.to_ascii_lowercase());
        }
    }
}

#[test]
fn derived_ordering_follows_the_fields() {
    let set: BTreeSet<PageId> = [PageId(3), PageId(1), PageId(2)].into_iter().collect();
    assert_eq!(set.into_iter().collect::<Vec<_>>(), vec![PageId(1), PageId(2), PageId(3)]);
    let pairs: BTreeSet<(&str, i64)> = [("b", 1), ("a", 9), ("a", 2)].into_iter().collect();
    assert_eq!(pairs.into_iter().collect::<Vec<_>>(), vec![("a", 2), ("a", 9), ("b", 1)]);
}

#[test]
fn hash_must_agree_with_eq() {
    let mut m: HashMap<CaseInsensitive, i32> = HashMap::new();
    m.insert(CaseInsensitive("Select".into()), 1);
    assert_eq!(m.get(&CaseInsensitive("SELECT".into())), Some(&1));
    let set: HashSet<CaseInsensitive> = ["A", "a", "b"].iter().map(|s| CaseInsensitive(s.to_string())).collect();
    assert_eq!(set.len(), 2);
}
```

### Using it: floats need a total order

```rust test
use std::cmp::Ordering;
use std::collections::BTreeSet;

#[derive(Debug, Clone, Copy)]
struct F(f64);
impl PartialEq for F {
    fn eq(&self, o: &F) -> bool { self.0.total_cmp(&o.0) == Ordering::Equal }
}
impl Eq for F {}
impl PartialOrd for F {
    fn partial_cmp(&self, o: &F) -> Option<Ordering> { Some(self.cmp(o)) }
}
impl Ord for F {
    fn cmp(&self, o: &F) -> Ordering { self.0.total_cmp(&o.0) }
}

#[test]
fn nan_has_a_place_under_total_cmp() {
    let set: BTreeSet<F> = [F(2.0), F(f64::NAN), F(-1.0), F(2.0)].into_iter().collect();
    assert_eq!(set.len(), 3);
    assert!(f64::NAN != f64::NAN, "plain f64 equality is not reflexive, so f64 cannot be Eq");
}

#[test]
fn reverse_gives_a_descending_set() {
    use std::cmp::Reverse;
    let set: BTreeSet<Reverse<i32>> = [1, 3, 2].into_iter().map(Reverse).collect();
    assert_eq!(set.into_iter().map(|r| r.0).collect::<Vec<_>>(), vec![3, 2, 1]);
}
```

### In the exercises

- **2b:** hash table keys and `GenericKey` comparators.
- **3f-01 / 3f-06:** group-by and hash-join keys: equality with NULLs as one group.
- **0a-01:** `BTreeMap<char, ..>` children; **0c-01:** the key hash trait; **0d-06:** `BTreeSet<(T, Uid)>`.
- **1d:** `BTreeSet` of eviction candidates ordered by a tuple.

### Where it is used

- Every `HashMap`/`BTreeMap` in Rust; `ordered-float` and the standard `f64::total_cmp` exist for the float problem.
