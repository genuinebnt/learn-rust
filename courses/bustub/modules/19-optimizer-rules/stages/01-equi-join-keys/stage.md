A nested loop join compares every pair of rows. If the join condition is an *equality between a column of the left input and a column of the right input* (`a.x = b.y`), only rows with the same value can match, and a hash join can find them without comparing all pairs. Before the optimizer can use a hash join it has to **recognise** such a condition inside an expression tree: `a.x = b.y and a.z = b.w` is an `AND` of two comparisons, each between two column references, one reading the left tuple and one the right. This stage writes that recogniser; the next uses it.

## The task

In `src/optimizer/optimizer.rs` (`Optimizer::conjuncts(expr, &mut out)`, which splits nested `AND`s into a list, is given):

`extract_equi_join_keys(predicate: &ExprRef) -> Option<(Vec<ExprRef>, Vec<ExprRef>)>`:
- split the predicate into conjuncts;
- **every** conjunct must be a `ComparisonExpression` of type `Equal` whose two children are both `ColumnValueExpression`s, one with `tuple_idx() == 0` (the left input) and the other with `tuple_idx() == 1` (the right input), in either order;
- return `(left keys, right keys)`: the left columns and the right columns in the same order, each rebuilt as `ColumnValueExpression::new(0, col_idx, return_type)` (each key will be evaluated on a tuple of its own side, so both read "tuple 0");
- anything else makes the whole answer `None`: another operator, an `OR`, a constant, both columns on one side, a non-column expression.

## Tests

- One equality gives one key pair; written the other way round (`b.y = a.x`) it gives the same pair with the left column first.
- Several equalities, however nested, give the keys in order.
- A single conjunct that is not such an equality rules it out: a residual condition (`and b.q > 10`), a constant, `<`, `!=`.
- Both columns on one side, an `OR`, or a bare constant are not join keys.
- `conjuncts` flattens `AND`s and keeps an `OR` whole.

## Syntax and methods

```rust
expr.as_any().downcast_ref::<ComparisonExpression>()?         // Option: None if the node is something else
cmp.comp_type == ComparisonType::Equal
cmp.children()[0].as_any().downcast_ref::<ColumnValueExpression>()?
(a.tuple_idx(), b.tuple_idx())                                 // (0, 1) or (1, 0)
Arc::new(ColumnValueExpression::new(0, left.col_idx(), left.return_type().clone()))
```

## Notes

**Why every conjunct.** A hash join checks *only* key equality. If the condition also had `and a.y > 5`, hashing would lose that check and return wrong rows. The rule is therefore all-or-nothing here. (A smarter optimizer would hash on the equalities and keep the remaining conjuncts as a filter above the join; that is the natural extension, and it needs a `Filter` node built by the rule.)

**`?` in a function returning `Option`.** `downcast_ref` returns an `Option`; with `?` the function returns `None` as soon as a node is not what you expect, which is exactly the intended behaviour. The rule reads as a checklist.

**Normalising the sides.** In the join predicate `#1.0 = #0.2` the right column is written first. The pair `(left, right)` you return must not depend on that; the executor evaluates `left_keys[i]` on left tuples and `right_keys[i]` on right tuples.

**Both read tuple 0.** In the join a column says which input it reads (`#0.i` or `#1.i`). A hash join evaluates each key expression on a tuple of one side, with that side's schema, with plain `evaluate`; for that the column index is what matters, so the keys are rebuilt with tuple index 0.

## In BusTub

`nlj_as_hash_join.cpp`: "optimize nested loop join into hash join. In the starter code, we will check NLJs with exactly one equal condition. You can further support optimizing joins with multiple eq conditions." Its tests `p3.14-hash-join.slt` and `p3.15-multi-way-hash-join.slt` include conditions like `on t1.colC = t2.colB and t2.colC = t1.colB` (two keys, written in both orders).

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `dynamic_cast<const ComparisonExpression *>(expr.get())`, then `if (cmp == nullptr)` | `expr.as_any().downcast_ref::<ComparisonExpression>()?` |
| a recursive helper that fills two out-vectors and returns bool | build the vectors in a loop over the conjuncts; `None` on the first bad one |
| `expr->GetChildAt(0)` / `GetChildren()` | `expr.children()[0]` / `expr.children()` |
| `std::make_shared<ColumnValueExpression>(0, idx, type)` | `Arc::new(ColumnValueExpression::new(0, idx, type))` |

**Port rule:** a chain of `dynamic_cast` + null checks is a chain of `downcast_ref()?`.

## Learn more
- [`Any` and downcasting](https://doc.rust-lang.org/std/any/trait.Any.html) · [`?` on `Option`](https://doc.rust-lang.org/std/option/enum.Option.html#the-question-mark-operator) · PostgreSQL [join planning](https://www.postgresql.org/docs/current/planner-optimizer.html)

## Performance

Recognising keys is plan-time work, linear in the size of the predicate: nothing next to execution. What it buys is turning `|L| × |R|` predicate evaluations into `|L| + |R|` hash operations in the next stage.

**Measure it.** Nothing to measure here; stage 2 shows the difference.

## Hints

### Check each conjunct, then collect

Do not return the first pair you find: a later conjunct that is not a key must make the answer `None`. Loop over all, pushing pairs, returning early on a bad one.

### The tuple indexes decide which side

`(0, 1)`: the first child is the left key. `(1, 0)`: swap. `(0, 0)` and `(1, 1)` are not join keys.

### An empty list is not a key list

`conjuncts` of a non-empty predicate is never empty, but be careful to return `None` rather than `Some((vec![], vec![]))` if no keys were found.
