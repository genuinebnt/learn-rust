`price - discount`, `age + 1`, `a + b + c`: arithmetic is a node with two children, like a comparison, but it produces a *number*, and numbers can **overflow**. BusTub supports `+` and `-` on INTEGERs only ("ONLY SUPPORT INTEGER FOR NOW"); `*`, `/` and `%` parse but the planner refuses them.

## The task

In `src/execution/expressions/arithmetic_expression.rs` (`ArithmeticType`, the constructor with its type check, `to_string` and the `result` helper are given):
- `perform_computation(lhs, rhs) -> Result<Option<i32>>`: `None` (a NULL result) if either side is NULL; otherwise the sum or difference as a **checked** `i32` operation. An overflow is an `OutOfRange` error. The result `i32::MIN` is also an error: module 3a reserves it as the stored encoding of the INTEGER NULL, so it cannot be a value;
- `evaluate` and `evaluate_join`: evaluate both children (with `evaluate` or `evaluate_join`), combine them with `perform_computation`, and answer with `Value::integer` (or `Value::null(TypeId::Integer)` for `None`).

## Tests

- Plus and minus, including negatives and zero.
- A NULL operand gives the INTEGER NULL.
- Overflow is an `OutOfRange` error, including the result `i32::MIN`; the largest results that do fit work.
- Only INTEGER children are accepted when the node is built (given): a VARCHAR, DECIMAL or BOOLEAN is `NotImplemented`.
- Columns in a row and in a join, nested expressions, and the text `((#0.0-#0.2)+100)`.

## Syntax and methods

```rust
let (Value::Integer(l), Value::Integer(r)) = (lhs, rhs) else { return Ok(None) };   // let-else: leave early for NULLs
l.checked_add(*r)            // Option<i32>: None on overflow
l.checked_sub(*r)
option.filter(|v| *v != i32::MIN)             // keep the value only if the test holds
option.ok_or_else(|| Exception::new(ExceptionType::OutOfRange, "..."))   // Option -> Result
```

## Notes

**NULL propagates.** `1 + NULL` is NULL. There is no `CmpBool` here: the NULL result has a *type* (the INTEGER NULL), because every column has one. That is why `perform_computation` returns `Option<i32>` and `evaluate` builds the typed NULL.

**Overflow is a query error.** C++'s `lhs + rhs` on `int32_t` is undefined behaviour when it overflows; BusTub's code doesn't check. Rust has four spellings: `+` (panics in debug builds, wraps in release), `wrapping_add`, `saturating_add` and `checked_add`. A database must not return a wrong number silently, so use `checked_*` and report the error: `select 2147483647 + 1;` fails.

**Check types where the node is built.** `ArithmeticExpression::new` refuses non-INTEGER children, so `evaluate` can assume integers (it still does not use `unwrap`: a NULL arrives as a different `Value` variant). This is "parse, don't validate": the planner finds `select 'a' + 1` while *building* the plan, before any row is read.

## In BusTub

`arithmetic_expression.h`: the constructor (`if (GetChildAt(0)->GetReturnType().GetType() != TypeId::INTEGER || ...) { throw bustub::NotImplementedException("only support integer for now"); }`) and `PerformComputation` (`if (lhs.IsNull() || rhs.IsNull()) { return std::nullopt; } ... return lhs.GetAs<int32_t>() + rhs.GetAs<int32_t>();`).

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `lhs.GetAs<int32_t>() + rhs.GetAs<int32_t>()` (overflow is UB) | `l.checked_add(*r)` and an `OutOfRange` error |
| `std::optional<int32_t>` and `std::nullopt` | `Option<i32>` and `None` |
| `throw bustub::NotImplementedException(...)` in the constructor | a constructor returning `Result<Self>` |
| `value.GetAs<int32_t>()` reads the union whatever the tag says | `let Value::Integer(l) = v else {..}` checks the tag |

**Port rule:** UB-on-overflow becomes `checked_*` plus an error; `std::optional` becomes `Option`; a throwing constructor becomes a fallible one.

## Learn more
- [Integer overflow](https://doc.rust-lang.org/book/ch03-02-data-types.html#integer-overflow) · [`checked_add`](https://doc.rust-lang.org/std/primitive.i32.html#method.checked_add) · [`let ... else`](https://doc.rust-lang.org/rust-by-example/flow_control/let_else.html)

## Performance

`checked_add` compiles to an add and a branch on the overflow flag: practically free. The cost of arithmetic in an engine is not the add but the interpretation around it (two child calls, two `Value` matches, a `Result`), tens of nanoseconds per node. Vectorised engines pay that once per thousand rows instead of once per row.

**Measure it.** Evaluate `(#0.0 + 1) - 1` a million times and compare with the same loop in plain `i32` arithmetic.

## Hints

### Two kinds of "nothing"

`None` from `perform_computation` means "the result is NULL", not "an error": errors travel in the `Result`. `Ok(None)` for a NULL operand, `Err(..)` for overflow, `Ok(Some(v))` otherwise.

### The NULL encoding bites

`Value::integer(i32::MIN)` is *a NULL* (module 3a). If a sum comes out as `i32::MIN` and you build the value anyway, the query silently returns NULL. The test `i32_min_is_the_null_encoding` checks that it is an error.

### Nested trees

`(a - c) + 100` is an `ArithmeticExpression` whose left child is another `ArithmeticExpression`. If your code only works for column and constant children, you are probably reading `Value`s from the tuple instead of calling `child.evaluate(...)`.
