---
title: Set operations and bag arithmetic
summary: UNION, INTERSECT and EXCEPT with and without ALL as arithmetic on row counts, why two NULLs are the same row here, how precedence and parentheses group a chain of them, and what ORDER BY and LIMIT apply to.
minutes: 9
---
A join combines rows side by side. A **set operation** combines two whole result sets one on top of the other: the customers who ordered in March, plus the customers who ordered in April; the products we sell that nobody ordered. The two queries must produce the same number of columns, of matching types, and the result is named after the first one.

## Sets and bags

SQL tables are not sets: a table may hold the same row twice. A collection that may repeat its members is a **bag** (or multiset), and the clean way to define the operations is by *counting*. Let `na` be the number of times a row appears in the left result and `nb` the number of times in the right. Then the row appears in the output this many times:

| operation | with `ALL` | without `ALL` |
|---|---|---|
| `UNION` | `na + nb` | 1 if `na + nb > 0` |
| `INTERSECT` | `min(na, nb)` | 1 if both are positive |
| `EXCEPT` | `max(na - nb, 0)` | 1 if `na > 0` and `nb = 0` |

Without `ALL` the result is also a set: duplicates are removed from the inputs, so every row appears once or not at all. With `ALL` the counts are carried through. `UNION ALL` is the cheapest of all: no comparison, no memory, the left rows followed by the right rows. That is why query writers use it whenever they know the sides cannot overlap, and why a `UNION` that could have been `UNION ALL` is a classic performance bug: it sorts or hashes everything to remove duplicates that were never there.

A worked count. Left has the row `(1)` three times and `(2)` once; right has `(1)` twice and `(3)` once. `INTERSECT ALL` gives `(1)` twice (the smaller count). `EXCEPT ALL` gives `(1)` once, because 3 - 2 = 1, and `(2)` once; `(3)` is not in the left, and counts never go below zero. Plain `EXCEPT` gives `(2)` only: it removes every row that appears on the right at all, so `(1)` is gone entirely.

## Two NULLs are one row

In a `WHERE` clause `NULL = NULL` is unknown. Set operations compare rows differently: two rows are the same if each pair of columns is **not distinct**, and two NULLs are not distinct. So `select null union select null` is one row, and `select null intersect select null` returns it. A set operation that implemented "same row" with the join predicate would get all of these wrong. The same convention is used by `GROUP BY` and `DISTINCT`, which is why the executor can reuse the grouping key.

## Precedence

`INTERSECT` binds tighter than `UNION` and `EXCEPT`, as multiplication binds tighter than addition. `a UNION b INTERSECT c` means `a UNION (b INTERSECT c)`. `UNION` and `EXCEPT` have equal rank and group from the left: `a EXCEPT b UNION c` is `(a EXCEPT b) UNION c` and `a EXCEPT b EXCEPT c` is `(a EXCEPT b) EXCEPT c`, which is not `a EXCEPT (b EXCEPT c)`. Parentheses override all of it, and a parenthesised operand is a complete query, so it can carry its own `ORDER BY` and `LIMIT`.

A parser handles this with the same *precedence climbing* it uses for arithmetic: read an operand, look at the next operator, and if the operator after the right operand binds tighter, let that operand take it first.

## ORDER BY and LIMIT apply to the whole

`select x from a union all select x from b order by x limit 3` sorts and limits the *union*, not `b`. The clause belongs to the outermost query. To limit one side you parenthesise it: `(select x from a order by x limit 1) union all (...)`. In `ORDER BY` you can name only the columns of the result, which are named after the first query: an alias on the first select works, an alias on the second does not.

## Try it

Predict the result of the three-row example above for all six operators before running it. Then find a query where `UNION` and `UNION ALL` give the same rows and say what the database does extra for `UNION`.

## In real code

### Using it: the six operations as arithmetic on counts

```rust test
use std::collections::BTreeMap;

fn counts(rows: &[i32]) -> BTreeMap<i32, usize> {
    let mut m = BTreeMap::new();
    for r in rows {
        *m.entry(*r).or_insert(0) += 1;
    }
    m
}

/// `op` is "union", "intersect" or "except"; the answer is sorted.
fn set_op(op: &str, all: bool, left: &[i32], right: &[i32]) -> Vec<i32> {
    let (a, b) = (counts(left), counts(right));
    let keys: std::collections::BTreeSet<i32> = a.keys().chain(b.keys()).copied().collect();
    let mut out = vec![];
    for k in keys {
        let (na, nb) = (a.get(&k).copied().unwrap_or(0), b.get(&k).copied().unwrap_or(0));
        let n = match (op, all) {
            ("union", true) => na + nb,
            ("union", false) => (na + nb > 0) as usize,
            ("intersect", true) => na.min(nb),
            ("intersect", false) => (na > 0 && nb > 0) as usize,
            ("except", true) => na.saturating_sub(nb),
            ("except", false) => (na > 0 && nb == 0) as usize,
            _ => unreachable!(),
        };
        out.extend(std::iter::repeat(k).take(n));
    }
    out
}

#[test]
fn the_six_operations_on_the_worked_example() {
    let (l, r) = ([1, 1, 1, 2], [1, 1, 3]);
    assert_eq!(set_op("union", false, &l, &r), vec![1, 2, 3]);
    assert_eq!(set_op("union", true, &l, &r).len(), 7);
    assert_eq!(set_op("intersect", false, &l, &r), vec![1]);
    assert_eq!(set_op("intersect", true, &l, &r), vec![1, 1]);
    assert_eq!(set_op("except", false, &l, &r), vec![2]);
    assert_eq!(set_op("except", true, &l, &r), vec![1, 2]);
}

#[test]
fn except_is_not_symmetric_and_intersect_is() {
    let (l, r) = ([1, 1, 1, 2], [1, 1, 3]);
    assert_eq!(set_op("intersect", true, &l, &r), set_op("intersect", true, &r, &l));
    assert_ne!(set_op("except", true, &l, &r), set_op("except", true, &r, &l));
}
```

### In the exercises

- **3j-04:** `UNION ALL` is the loop over both inputs; the planner's check that the sides agree.
- **3j-05:** `SetOpExecutor::compute` is `set_op` with a row key in place of `i32` (two NULLs are one key).
- **3j-06:** precedence between `INTERSECT` and the other two, and `ORDER BY` / `LIMIT` on the whole result.
- **3j-07:** the boss checks the identities that link `UNION`, `INTERSECT` and `EXCEPT`.

### Where it is used

Every SQL database has `UNION`, `INTERSECT` and `EXCEPT` (Oracle spells the last one `MINUS`; MySQL added `INTERSECT` and `EXCEPT` only in version 8.0.31, and SQLite has had all three for years). PostgreSQL executes `UNION` with a hash aggregate or a sort, and `INTERSECT` and `EXCEPT` with its `SetOp` node (hashed or sorted); the plan of a `UNION ALL` is an `Append` node with no work of its own, which is why partitioned tables are scanned with it.
