`id = 3`, `price > 10`, `name != 'x'`: a comparison is a node with two children and an operator, and an answer that is **true, false or NULL** (module 3a's three-valued `CmpBool`). A `WHERE` clause keeps the rows for which the answer is *true*; `NULL` rows are dropped like `false` ones, which is the part newcomers to SQL get wrong.

## The task

In `src/execution/expressions/comparison_expression.rs` (`ComparisonType`, the constructor, `to_string` and `cmp_to_value` are given):
- `perform_comparison(lhs, rhs)`: dispatch on `self.comp_type` to the `Value` methods of module 3a: `compare_equals`, `compare_not_equals`, `compare_less_than`, `compare_less_than_equals`, `compare_greater_than`, `compare_greater_than_equals`;
- `evaluate`: evaluate both children on the tuple, compare, and convert the `CmpBool` into a BOOLEAN value with `cmp_to_value` (`Null` becomes the BOOLEAN NULL);
- `evaluate_join`: the same, evaluating the children with `evaluate_join`.

## Tests

- The six operators on integers, true and false cases.
- A NULL on either side, or on both, gives the BOOLEAN NULL for every operator.
- Strings compare by value and numbers of different types compare as numbers.
- Comparing two columns, in a row and across a join; the text `(#0.0>=5)` and the BOOLEAN return type.

## Syntax and methods

```rust
match self.comp_type {
    ComparisonType::Equal => lhs.compare_equals(rhs),     // Result<CmpBool>
    /* ... */
}
let lhs = self.children[0].evaluate(tuple, schema)?;      // ? passes an error up
Ok(cmp_to_value(self.perform_comparison(&lhs, &rhs)?))
```

## Notes

**Children first.** An expression node never touches the tuple itself; it asks its children for values and combines them. That is why `(a + 1) > b` works: the comparison does not care that its left child is an arithmetic node. The recursion is the whole interpreter.

**`?` and errors.** Comparing a string to a number the wrong way can fail (module 3a's `check_comparable`), so `compare_*` returns `Result<CmpBool>`. The expression passes the error up; the executor reports it as a failed query.

**Unknown is not false.** `NULL = NULL` is NULL, not true. The planner (given) turns `WHERE x = NULL` into exactly that, which is why it returns no rows, and why SQL has `IS NULL`. A comparison that answered `false` for NULL would make `NOT (x = 5)` true for NULL rows, which SQL specifically avoids.

## In BusTub

`comparison_expression.h`: `Value lhs = GetChildAt(0)->Evaluate(tuple, schema); Value rhs = GetChildAt(1)->Evaluate(tuple, schema); return ValueFactory::GetBooleanValue(PerformComparison(lhs, rhs));` and the switch in `PerformComparison` over `ComparisonType::{Equal, NotEqual, LessThan, LessThanOrEqual, GreaterThan, GreaterThanOrEqual}`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `switch (comp_type_) { case ...: return lhs.CompareEquals(rhs); default: BUSTUB_ASSERT(false, ...) }` | an exhaustive `match`: no `default`, and a new variant is a compile error here |
| `ValueFactory::GetBooleanValue(CmpBool)` | `cmp_to_value(CmpBool)` |
| `Value lhs = ...->Evaluate(...)` (throws on error) | `let lhs = ...evaluate(...)?;` (returns the error) |
| `fmt::format("({}{}{})", ...)` for `EXPLAIN` | `format!("({}{}{})", ...)` |

**Port rule:** replace `default: assert(false)` in a `switch` over an enum with an exhaustive `match`; the compiler checks what the assert only hoped.

## Learn more
- [`match`](https://doc.rust-lang.org/book/ch06-02-match.html) · [Three-valued logic (Wikipedia)](https://en.wikipedia.org/wiki/Null_(SQL)) · PostgreSQL [comparison functions and operators](https://www.postgresql.org/docs/current/functions-comparison.html)

## Performance

A comparison evaluates two children, then calls into module 3a's type-checking comparison: dozens of instructions per row, plus one `Value` allocation if either side is a string. A `WHERE id = 3` over a million rows therefore does a million of these; the index (module 3e) exists to evaluate it once.

**Measure it.** Evaluate `#0.0 = 5` over a million tuples with and without a NULL column; compare with a hand-written `x == 5` loop to see what the generality costs.

## Hints

### Three answers, one conversion

Do not turn `CmpBool` into `bool` on the way: `cmp_to_value` is the only place where `Null` becomes a NULL BOOLEAN. A shortcut like `matches!(r, CmpBool::True)` turns every NULL into `false`.

### Which side is left

`a < b` is `children[0] < children[1]`. `GreaterThan` is not `LessThan` with swapped arguments in your head: call `compare_greater_than(lhs, rhs)` and keep the order, which also keeps the error messages right.

### `evaluate_join` does not call `evaluate`

The children must be evaluated with `evaluate_join` so that column values pick the right input; calling `evaluate` on them would read the wrong tuple.
