---
title: Conjunctive predicates: picking a condition apart
summary: A WHERE or ON clause is a tree of AND, OR and comparisons; optimizers split it into conjuncts to find equalities usable for hash joins and index lookups. Splitting, classifying which side a column comes from, and the pitfalls (OR, constants, both sides).
minutes: 8
---
`on a.x = b.y and a.z = b.w and b.k > 10` is one expression, a tree: `AND(AND(a.x = b.y, a.z = b.w), b.k > 10)`. An optimizer rarely cares about the tree as a whole; it cares about its **conjuncts**: the pieces joined by `AND`. Each conjunct is a separate requirement that must hold, so the optimizer can use one of them to find rows fast and check the others afterwards.

## Splitting

Flatten nested `AND`s into a list: `[a.x = b.y, a.z = b.w, b.k > 10]`. An `OR` is *not* split: `p or q` is one conjunct (an alternative). A predicate with no `AND` at all is a list of one.

## Classifying a conjunct

For each conjunct ask what it can be used for:

| conjunct | use |
|---|---|
| `col_of_left = col_of_right` (either order) | an **equi-join key**: hash join, index join |
| `col = constant` (either order) | a **point lookup**: an index on `col` |
| `col = c1 or col = c2` (same column) | a lookup of several keys |
| anything else (`>`, `+`, a function) | a **residual** predicate: check it after |

A hash join needs *all* of the join's conjuncts to be equi-join keys (otherwise the rest must be checked in a filter after the join); an index scan needs only *one* usable conjunct, with the whole predicate re-checked on the rows found.

## Which side is a column on?

In a join predicate each column reference says which input it reads (`#0.i` left, `#1.i` right). `#0.1 = #1.0` is a key pair: left key `#0.1`, right key `#1.0`; `#1.0 = #0.1` is the same pair written the other way round and must be normalised. `#0.1 = #0.2` (both left) or `#0.1 = 5` is not a join key.

## Pitfalls

- **Types.** Comparing an INTEGER column to a VARCHAR column converts one side; a hash of the raw values would not agree. Only use keys whose evaluation yields the same type or hash consistently.
- **NULL.** `col = NULL` is never true; a lookup of the NULL key must find nothing. Hash joins skip NULL keys.
- **Extra conjuncts.** Dropping the residual conjuncts silently changes the result. Either keep them as a filter or do not apply the rule.
- **OR.** `a.x = b.y or a.z = b.w` cannot be a hash join; do not split an `OR`.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `dynamic_cast<const LogicExpression *>(expr.get())` and `logic_type_ == LogicType::And` | `expr.as_any().downcast_ref::<LogicExpression>()` and `.logic_type == LogicType::And` |
| recursion that fills an out-vector | recursion that returns a `Vec<ExprRef>` or pushes to one |
| `expr->GetChildAt(0)` / `GetChildren()` | `expr.child_at(0)` / `expr.children()` |
| `ColumnValueExpression::GetTupleIdx()` | `col.tuple_idx()` |

## In real code

### Using it: conjuncts and equi-join keys

```rust test
#[derive(Debug, Clone, PartialEq)]
enum E {
    Col(u8, usize),   // (side 0 or 1, column index)
    Const(i32),
    Eq(Box<E>, Box<E>),
    Gt(Box<E>, Box<E>),
    And(Box<E>, Box<E>),
    Or(Box<E>, Box<E>),
}
use E::*;

fn b(e: E) -> Box<E> { Box::new(e) }

/// Flattens nested ANDs; anything else is a single conjunct.
fn conjuncts(e: &E, out: &mut Vec<E>) {
    match e {
        And(l, r) => { conjuncts(l, out); conjuncts(r, out); }
        other => out.push(other.clone()),
    }
}

/// If EVERY conjunct is `left column = right column` (either way round), the (left key, right key) pairs.
fn equi_join_keys(e: &E) -> Option<Vec<(usize, usize)>> {
    let mut parts = vec![];
    conjuncts(e, &mut parts);
    parts.iter().map(|p| match p {
        Eq(l, r) => match (l.as_ref(), r.as_ref()) {
            (Col(0, a), Col(1, c)) => Some((*a, *c)),
            (Col(1, c), Col(0, a)) => Some((*a, *c)),
            _ => None,
        },
        _ => None,
    }).collect()
}

/// `col = const` / `const = col` / an OR of those on the SAME column: (column, keys).
fn point_lookup(e: &E) -> Option<(usize, Vec<i32>)> {
    match e {
        Eq(l, r) => match (l.as_ref(), r.as_ref()) {
            (Col(_, c), Const(k)) | (Const(k), Col(_, c)) => Some((*c, vec![*k])),
            _ => None,
        },
        Or(l, r) => {
            let ((c1, mut k1), (c2, k2)) = (point_lookup(l)?, point_lookup(r)?);
            if c1 != c2 { return None; }
            k1.extend(k2);
            Some((c1, k1))
        }
        _ => None,
    }
}

#[test]
fn conjuncts_flatten_nested_ands_but_not_ors() {
    let e = And(b(And(b(Eq(b(Col(0, 1)), b(Col(1, 0)))), b(Gt(b(Col(1, 2)), b(Const(10)))))), b(Or(b(Const(1)), b(Const(2)))));
    let mut out = vec![];
    conjuncts(&e, &mut out);
    assert_eq!(out.len(), 3);
    assert!(matches!(out[2], Or(..)), "an OR stays whole");
}

#[test]
fn equi_join_keys_need_every_conjunct_to_be_a_cross_side_equality() {
    let k1 = Eq(b(Col(0, 1)), b(Col(1, 0)));
    let k2 = Eq(b(Col(1, 3)), b(Col(0, 2))); // written the other way round
    assert_eq!(equi_join_keys(&And(b(k1.clone()), b(k2))), Some(vec![(1, 0), (2, 3)]));
    assert_eq!(equi_join_keys(&And(b(k1.clone()), b(Gt(b(Col(1, 2)), b(Const(10)))))), None, "a residual conjunct: no hash join");
    assert_eq!(equi_join_keys(&Eq(b(Col(0, 1)), b(Col(0, 2)))), None, "both sides on the left: not a join key");
    assert_eq!(equi_join_keys(&Or(b(k1.clone()), b(k1))), None);
}

#[test]
fn point_lookups_come_from_equalities_with_a_constant() {
    assert_eq!(point_lookup(&Eq(b(Col(0, 4)), b(Const(7)))), Some((4, vec![7])));
    assert_eq!(point_lookup(&Eq(b(Const(7)), b(Col(0, 4)))), Some((4, vec![7])), "either order");
    let two = Or(b(Eq(b(Const(4)), b(Col(0, 0)))), b(Eq(b(Col(0, 0)), b(Const(7)))));
    assert_eq!(point_lookup(&two), Some((0, vec![4, 7])));
    let different_columns = Or(b(Eq(b(Col(0, 0)), b(Const(4)))), b(Eq(b(Col(0, 1)), b(Const(7)))));
    assert_eq!(point_lookup(&different_columns), None);
    assert_eq!(point_lookup(&Gt(b(Col(0, 0)), b(Const(1)))), None);
}
```

### In the exercises

- **3h-01:** `extract_equi_join_keys` is `equi_join_keys` over BusTub's expression tree.
- **3h-04:** `extract_point_lookup` is `point_lookup`, with the constant a `ConstantValueExpression`.

### Where it is used

- **PostgreSQL**: `extract_actual_join_clauses`, `get_equivalence_classes`; "Hash Cond", "Index Cond" and "Filter" in `EXPLAIN` are the classified conjuncts.
- **Calcite / DataFusion**: `split_conjunction`, `extract_join_filters`.
- **SQLite**: the `WHERE` clause is split into `WhereTerm`s on `AND`, and each term is matched against indexes.
- **Datalog / constraint solvers**: conjunctions are lists of goals.
