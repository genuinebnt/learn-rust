---
title: NULL and three-valued logic
summary: Why a SQL comparison can be true, false or unknown, the truth tables of AND, OR and NOT, what WHERE keeps, how NULL behaves in grouping, and how Option<bool> models it.
minutes: 9
---
In most languages a condition is true or false. In SQL it is **true, false or unknown**. `NULL` means "no value known", so asking whether it equals 5 has no answer: not *no*, but *unknown*. Everything about NULL follows from that one idea.

## Comparisons with NULL are unknown

| expression | result |
|---|---|
| `5 = 5` | true |
| `5 = 6` | false |
| `NULL = 5` | **unknown** |
| `NULL = NULL` | **unknown** (two unknowns are not known to be equal) |
| `NULL <> 5` | **unknown** |
| `x IS NULL` | true or false (the one test that never answers unknown) |

A `WHERE` clause keeps a row only when the condition is **true**. A row whose condition is unknown is dropped, exactly like a false one. That is why `WHERE x <> 5` does not return the rows where `x` is NULL, and why `WHERE x = NULL` returns nothing, ever.

## AND, OR, NOT (Kleene's logic)

| `a` | `b` | `a AND b` | `a OR b` |
|---|---|---|---|
| true | unknown | unknown | **true** |
| false | unknown | **false** | unknown |
| unknown | unknown | unknown | unknown |

`NOT unknown` is unknown. The rule that helps: *if the answer is decided regardless of the unknown, it is decided* (`false AND anything` is false; `true OR anything` is true). Otherwise it stays unknown.

## Where NULL behaves differently

- **Arithmetic**: any operation with a NULL is NULL (`1 + NULL`, `NULL * 0`).
- **Aggregates**: `COUNT(x)` skips NULLs, `COUNT(*)` counts rows, `SUM`/`MIN`/`MAX` ignore NULLs (and are NULL over no values).
- **Grouping and DISTINCT**: NULLs are treated as *equal* to each other (one group of NULLs). That is a different equality from `=`: BusTub's `CompareExactlyEquals`.
- **ORDER BY**: NULLs sort together, first or last depending on the system.
- **Joins**: `a.x = b.y` is unknown for NULLs, so NULLs never match; an outer join pads with NULLs.
- **`NOT IN` with a NULL in the list** is unknown for every row: a famous trap.

## Modelling it in Rust

`Option<bool>` is a three-valued boolean (`Some(true)`, `Some(false)`, `None` = unknown), and BusTub's `CmpBool` is the same thing with names. The tables above are a handful of `match` arms.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `enum class CmpBool { CmpFalse, CmpTrue, CmpNull }` | `enum CmpBool { False, True, Null }` or `Option<bool>` |
| `if (cmp == CmpBool::CmpTrue)` to decide whether a row passes | `cmp == CmpBool::True` (the same: only *true* keeps a row) |
| a nullable column as a sentinel (BusTub) or a bitmap (PostgreSQL) | the same two options; in memory `Option<T>` |

## In real code

### Using it: the logic tables, a filter, and grouping

```rust test
type Tri = Option<bool>;           // Some(true), Some(false), None = unknown

fn and(a: Tri, b: Tri) -> Tri {
    match (a, b) {
        (Some(false), _) | (_, Some(false)) => Some(false),   // false decides it, whatever the other is
        (Some(true), Some(true)) => Some(true),
        _ => None,
    }
}
fn or(a: Tri, b: Tri) -> Tri {
    match (a, b) {
        (Some(true), _) | (_, Some(true)) => Some(true),
        (Some(false), Some(false)) => Some(false),
        _ => None,
    }
}
fn not(a: Tri) -> Tri { a.map(|b| !b) }

fn eq(a: Option<i32>, b: Option<i32>) -> Tri { Some(a? == b?) }   // `?` on Option: unknown if either side is

#[test]
fn the_truth_tables() {
    let (t, f, u) = (Some(true), Some(false), None);
    assert_eq!((and(t, u), and(f, u), and(u, u)), (u, f, u));
    assert_eq!((or(t, u), or(f, u), or(u, u)), (t, u, u));
    assert_eq!((not(t), not(f), not(u)), (f, t, u));
    assert_eq!(and(or(t, u), not(u)), u, "(true OR unknown) AND (NOT unknown) = true AND unknown = unknown");
    assert_eq!((eq(Some(5), Some(5)), eq(Some(5), Some(6)), eq(None, Some(5)), eq(None, None)), (t, f, u, u));
}

#[test]
fn where_keeps_only_true_so_not_equal_misses_the_nulls() {
    let column = [Some(4), Some(5), None, Some(6), None];
    let equal_five: Vec<_> = column.iter().filter(|x| eq(**x, Some(5)) == Some(true)).collect();
    let not_five: Vec<_> = column.iter().filter(|x| not(eq(**x, Some(5))) == Some(true)).collect();
    assert_eq!(equal_five.len(), 1);
    assert_eq!(not_five.len(), 2, "4 and 6: the two NULLs are neither = 5 nor <> 5");
    let is_null = column.iter().filter(|x| x.is_none()).count();
    assert_eq!(equal_five.len() + not_five.len() + is_null, column.len(), "IS NULL is what finds them");
}
```

```rust test
use std::collections::HashMap;

#[test]
fn aggregates_skip_nulls_and_grouping_treats_them_as_one_group() {
    let column = [Some(3), None, Some(3), None, Some(7)];
    let count_star = column.len();
    let count_x = column.iter().flatten().count();
    let sum: Option<i32> = column.iter().flatten().copied().reduce(|a, b| a + b);
    let min = column.iter().flatten().min();
    assert_eq!((count_star, count_x, sum, min), (5, 3, Some(13), Some(&3)));
    let none_at_all: [Option<i32>; 2] = [None, None];
    assert_eq!(none_at_all.iter().flatten().copied().reduce(|a, b| a + b), None, "SUM over no values is NULL, not 0");

    // GROUP BY x: for grouping, NULL equals NULL (Option's own == does exactly that)
    let mut groups: HashMap<Option<i32>, usize> = HashMap::new();
    for x in column { *groups.entry(x).or_default() += 1; }
    assert_eq!(groups[&None], 2);
    assert_eq!(groups[&Some(3)], 2);
    assert_eq!(groups.len(), 3);
}

#[test]
fn not_in_with_a_null_is_never_true() {
    let list = [Some(1), None, Some(3)];
    // x IN (1, NULL, 3) is x = 1 OR x = NULL OR x = 3, and `x = NULL` is unknown
    let tri_in = |x: i32| list.iter().fold(Some(false), |acc, y| {
        let e = y.map(|y| x == y);                        // unknown if the list item is NULL
        match (acc, e) { (Some(true), _) | (_, Some(true)) => Some(true), (Some(false), Some(false)) => Some(false), _ => None }
    });
    assert_eq!(tri_in(1), Some(true), "1 IS in the list");
    assert_eq!(tri_in(2), None, "2 NOT IN (1, NULL, 3) is unknown, not true: the row is dropped");
}
```

### In the exercises

- **3a-01, 3a-03, 3a-04:** a NULL is a value of a type (`is_null`, the typed NULL constructors); `CmpBool` and the comparisons answer `Null` for any NULL; arithmetic with a NULL is a NULL of the result type.
- **Module 3b:** the filter executor passes a row when the predicate is `True`; aggregation skips NULLs; the group-by hash table uses `compare_exactly_equals`.

### Where it is used

- **Every SQL database** (the SQL standard defines it); the three-valued rules are why `LEFT JOIN ... WHERE right.x <> 1` silently turns into an inner join.
- **Rust**: `Option<bool>`, `Option::and`/`or`/`xor`/`zip`, and `f64`'s `partial_cmp` returning `None` for NaN (a comparison that has no answer) are the same idea.
- **Other languages**: JavaScript's `NaN !== NaN`, Kleene logic in Lua-like `nil`, and Prolog's three outcomes.
