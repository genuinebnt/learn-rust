---
title: Hashing values and keys: Hash and Eq that mean "the same group"
summary: Why a SQL value cannot simply derive Hash and Eq, how to define equality for grouping and joining (NULLs, floats, strings) and a hash that agrees with it, and the hash/eq contract that a HashMap relies on.
minutes: 8
---
A hash table needs two things from its key type: `Eq` (are these two keys the same?) and `Hash` (a number that is the same for keys that are the same). The contract: **if `a == b` then `hash(a) == hash(b)`**. Break it and a `HashMap` silently loses entries.

A SQL `Value` does not satisfy this out of the box:

- `NULL = NULL` is *unknown*, not true, but `GROUP BY` puts all NULLs in **one** group, so for grouping two NULLs are the same key.
- a `Decimal` holds an `f64`, and `f64` is not `Eq` or `Hash` (`NaN != NaN`, `0.0 == -0.0` but their bits differ).
- `Value::integer(5)` and `Value::bigint(5)` compare equal as SQL values but are different variants.

So grouping and joining need their **own** notion of equality and a hash that agrees with it. Two decisions:

| | for `GROUP BY` | for an equi-join `a.x = b.y` |
|---|---|---|
| NULL vs NULL | same key (one NULL group) | **never** equal (a NULL joins nothing) |
| equal numbers of different types | same key | equal |
| output | one row per key | rows for matching pairs only |

The join rule is the SQL `=`; the grouping rule is "not distinct". A hash join therefore skips rows whose key has a NULL when building and probing, while an aggregation keeps them as a group.

## Making floats and strings hashable

For a key made of integers and strings, `Hash` and `Eq` can be derived on a wrapper enum. For decimals, hash the bit pattern of a *normalised* value (map `-0.0` to `0.0`, one canonical `NaN`) and compare the same normalised bits. For cross-type equality (an `INTEGER` key against a `BIGINT` key), normalise to one representation before hashing: for example hash every integer type as `i64`.

## The hash must use exactly what `Eq` compares

If equality ignores the string's capacity but the hash includes it, equal keys hash differently. If equality is case-insensitive the hash must lowercase first. The simplest way to keep them aligned: implement `Eq` by comparing the same canonical form that `Hash` feeds to the hasher.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `namespace std { template <> struct hash<AggregateKey> { size_t operator()(...) } }` and `operator==` | `impl Hash for AggregateKey` and `impl PartialEq/Eq` |
| BusTub's `AggregateKey::operator==` returns false if `CompareEquals != CmpTrue` (so NULL keys never match) | an explicit rule: grouping treats NULL as equal to NULL |
| `HashUtil::CombineHashes(h1, h2)` to mix per-column hashes | `value.hash(&mut hasher)` for each column in turn (the hasher mixes) |
| `std::unordered_map` | `std::collections::HashMap` (SipHash by default; swap the hasher for speed) |

## In real code

### Using it: a key with grouping equality

```rust test
use std::collections::HashMap;
use std::hash::{Hash, Hasher};

#[derive(Clone, Debug)]
enum V { Null, Int(i64), Dec(f64), Str(String) }

#[derive(Clone, Debug)]
struct Key(Vec<V>);

/// The canonical form used by both Eq and Hash: -0.0 is 0.0, every NaN is one NaN.
fn canon(v: &V) -> (u8, i64, u64, &str) {
    match v {
        V::Null => (0, 0, 0, ""),
        V::Int(i) => (1, *i, 0, ""),
        V::Dec(d) => (2, 0, if *d == 0.0 { 0 } else if d.is_nan() { u64::MAX } else { d.to_bits() }, ""),
        V::Str(s) => (3, 0, 0, s),
    }
}

impl PartialEq for Key {
    fn eq(&self, other: &Key) -> bool {
        self.0.len() == other.0.len() && self.0.iter().zip(&other.0).all(|(a, b)| canon(a) == canon(b))
    }
}
impl Eq for Key {}
impl Hash for Key {
    fn hash<H: Hasher>(&self, state: &mut H) {
        for v in &self.0 {
            canon(v).hash(state);
        }
    }
}

fn key(vs: Vec<V>) -> Key { Key(vs) }

#[test]
fn nulls_group_together_and_equal_keys_hash_alike() {
    let mut counts: HashMap<Key, u32> = HashMap::new();
    for k in [key(vec![V::Null]), key(vec![V::Int(1)]), key(vec![V::Null]), key(vec![V::Int(1)]), key(vec![V::Int(2)])] {
        *counts.entry(k).or_insert(0) += 1;
    }
    assert_eq!(counts[&key(vec![V::Null])], 2);
    assert_eq!(counts[&key(vec![V::Int(1)])], 2);
    assert_eq!(counts.len(), 3);
}

#[test]
fn floats_are_normalised_so_zero_and_negative_zero_are_one_key() {
    assert_eq!(key(vec![V::Dec(0.0)]), key(vec![V::Dec(-0.0)]));
    assert_eq!(key(vec![V::Dec(f64::NAN)]), key(vec![V::Dec(f64::NAN)]));
    let mut m: HashMap<Key, u32> = HashMap::new();
    m.insert(key(vec![V::Dec(-0.0)]), 1);
    assert_eq!(m.get(&key(vec![V::Dec(0.0)])), Some(&1), "equal keys must find each other");
}

#[test]
fn composite_keys_compare_column_by_column() {
    assert_ne!(key(vec![V::Int(1), V::Str("a".into())]), key(vec![V::Int(1), V::Str("b".into())]));
    assert_eq!(key(vec![V::Int(1), V::Str("a".into())]), key(vec![V::Int(1), V::Str("a".into())]));
    assert_ne!(key(vec![V::Int(1)]), key(vec![V::Int(1), V::Null]), "different lengths are different keys");
}
```

### In the exercises

- **3f-02:** the aggregation's `AggregateKey` (group-by values) needs exactly this: NULLs together.
- **3f-05:** the hash join's key is the same idea, with the opposite NULL rule: a NULL key never matches.

### Where it is used

- **PostgreSQL**: `hash_any`, and the *equality operator class* of a type defines both `=` and the hash function (`hashfloat8` normalises `-0.0`).
- **DuckDB / Arrow**: group keys are hashed from normalised bytes; NULL is a validity bit hashed separately.
- **Rust**: `HashMap` requires `Hash + Eq` and documents the `k1 == k2 -> hash(k1) == hash(k2)` rule; `f64` is deliberately not `Eq`.
- **Java**: `equals` and `hashCode` have the identical contract, and breaking it is a classic bug.
