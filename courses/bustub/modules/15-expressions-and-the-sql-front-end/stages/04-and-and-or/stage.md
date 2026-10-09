`WHERE price > 10 AND stock > 0`: `AND` and `OR` combine two answers that can each be true, false or **NULL**. SQL's truth tables treat NULL as *unknown*, and some combinations are known anyway: `FALSE AND anything` is FALSE, because no value of "anything" can make it true; `TRUE OR anything` is TRUE. Getting the NULL rows right is what separates a database from a boolean calculator.

> [!CHECK] What do `NULL AND FALSE`, `NULL OR TRUE` and `NULL AND TRUE` evaluate to, and why can the first two be answered without knowing the NULL?
> ||FALSE, TRUE and NULL. `AND` is false when either side is false, and `OR` is true when either side is true, whatever the unknown value turns out to be; `NULL AND TRUE` depends on the unknown, so it stays NULL.||
>
> - Replace NULL by true, then by false: does the answer change?
> - Which results are the same for both replacements?
> - Does your `evaluate` have to evaluate the right side when the left decides the answer?

## The task

In `src/execution/expressions/logic_expression.rs` (`LogicType`, the constructor with its BOOLEAN check, `to_string` and the conversion to a BOOLEAN `Value` are given):
- `perform_computation(lhs, rhs) -> CmpBool`: the truth tables below, with a NULL input represented by `CmpBool::Null` (`as_cmp_bool`, given, converts a `Value`);
- `evaluate` and `evaluate_join`: evaluate both children, compute, convert with `cmp_to_value`.

| AND | TRUE | FALSE | NULL | | OR | TRUE | FALSE | NULL |
|---|---|---|---|---|---|---|---|---|
| **TRUE** | TRUE | FALSE | NULL | | **TRUE** | TRUE | TRUE | TRUE |
| **FALSE** | FALSE | FALSE | FALSE | | **FALSE** | TRUE | FALSE | NULL |
| **NULL** | NULL | FALSE | NULL | | **NULL** | TRUE | NULL | NULL |

## Tests

- All nine combinations of `AND` and of `OR`.
- Both sides must be BOOLEAN when the node is built (`NotImplemented` otherwise).
- Logic over comparisons: `a > 1 AND c = 2` with a NULL column, in a row and in a join.
- The text `(trueorfalse)` and the BOOLEAN return type.

## Syntax and methods

```rust
match (l, r) {                                   // match on a pair of CmpBool: the table, nearly verbatim
    (CmpBool::False, _) | (_, CmpBool::False) => CmpBool::False,
    (CmpBool::True, CmpBool::True) => CmpBool::True,
    _ => CmpBool::Null,
}
val.as_bool()                                    // Option<bool>: None for a NULL
```

## Notes

**Both sides are evaluated.** Many languages short-circuit `&&`. SQL does not promise to (the optimizer may reorder a `WHERE`), and BusTub evaluates both children and then looks at the table. That also means an error in the second child surfaces even when the first already decides the result; it is the simple semantics, and it is deterministic.

**The tables, as rules.** AND: *any FALSE gives FALSE*, otherwise *any NULL gives NULL*, otherwise TRUE. OR: *any TRUE gives TRUE*, otherwise *any NULL gives NULL*, otherwise FALSE. Writing those two rules in order is shorter and less error-prone than nine arms.

**De Morgan survives.** `NOT (a AND b)` equals `(NOT a) OR (NOT b)` in three-valued logic as well; the planner relies on it when it pushes filters around. (BusTub's shell has no `NOT` yet: the binder accepts it, the planner refuses.)

## In BusTub

`logic_expression.h`: `PerformComputation` with `GetBoolAsCmpBool` and the `And`/`Or` branches: `if (l == CmpBool::CmpFalse || r == CmpBool::CmpFalse) { return CmpBool::CmpFalse; } if (l == CmpBool::CmpTrue && r == CmpBool::CmpTrue) { return CmpBool::CmpTrue; } return CmpBool::CmpNull;`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `enum class CmpBool { CmpFalse, CmpTrue, CmpNull }` and chains of `if` | `enum CmpBool { False, True, Null }` and `match` on a pair |
| `throw NotImplementedException("expect boolean from either side")` in the constructor | `Err(..)` from a fallible constructor |
| `val.GetAs<bool>()` after an `IsNull()` check | `val.as_bool()` returns an `Option` |
| `&&` on `bool` short-circuits | evaluate both children first, then combine |

**Port rule:** a three-valued boolean is its own enum, not `bool` plus a flag; combine two of them with a `match` on the pair.

## Learn more
- [PostgreSQL: logical operators](https://www.postgresql.org/docs/current/functions-logical.html) · [Three-valued logic](https://en.wikipedia.org/wiki/Three-valued_logic) · [`Option<bool>` as a three-valued boolean](https://doc.rust-lang.org/std/option/enum.Option.html)

## Performance

A logic node adds two child evaluations and a match: cheap, but each child is itself a comparison with its own cost. The optimizer's `merge filter` rules (module 3h) matter because a predicate evaluated *inside* the scan avoids building and passing a tuple only to drop it.

**Measure it.** Evaluate `a > 1 AND b < 5 AND c = 3` over a million rows, then reorder the three terms. The time does not change, because both sides of every `AND` are always evaluated; a short-circuiting engine would gain from putting the most selective, cheapest term first.

## Hints

### Write the rules, not the table

Check "is either side FALSE" first for AND (and "is either side TRUE" for OR); then "is either side NULL"; the last case is the other value. A first-match-wins `if` chain is the rule order.

### NULL is not an error

`Value::null(TypeId::Boolean)` arriving from a child (a comparison with NULL) is an ordinary input. `as_cmp_bool` maps it to `CmpBool::Null`; do not unwrap `as_bool()` yourself.

### The join variant is the same code

`evaluate_join` evaluates its children with `evaluate_join` and then calls the same `perform_computation`. Keep the truth table in one place.
