---
title: CASE expressions: choosing without evaluating the rest
summary: CASE is the one expression that must not evaluate all its operands. First true branch wins, NULL is not true, only the chosen branch runs; its type is fixed at planning time; COALESCE and NULLIF are CASE in disguise.
minutes: 8
---
`select a / b from t` fails the moment one row has `b = 0`, and the whole query fails with it. The fix everybody reaches for is `case when b = 0 then 0 else a / b end`, and it works for a reason that is easy to miss: the division is **never evaluated** for the rows where the condition picks the first branch. A function call evaluates all its arguments before it runs; a `CASE` does not. That one difference is the whole reason it is a different kind of expression and not another function in the factory.

## What a CASE says

There are two spellings. The **searched** form lists conditions: `case when a >= 4 then 'big' when a >= 2 then 'mid' else 'small' end`. The **operand** form compares one value with several: `case a when 1 then 'one' when 2 then 'two' end`, which is exactly `case when a = 1 then 'one' when a = 2 then 'two' end`. A parser can rewrite the second into the first and the rest of the system only ever sees the searched form.

The rules are short and each one has a trap behind it:

- Conditions are tried **in order**, and the first one that is **TRUE** decides. Order matters: `when a >= 2` before `when a >= 4` makes the second branch unreachable.
- A condition that is **NULL is not TRUE**. A row with `a = NULL` falls through every `when a > 2` to the `else`, which is also what `where` does with a NULL condition.
- With no `else`, an unmatched CASE is **NULL**, not an error and not zero.
- `case a when null then ...` never matches: it is `a = NULL`, which is never TRUE. Testing for NULL needs `when a is null`.

## Evaluating only what was chosen

The evaluation order is the contract. An executor walks the branches, evaluates a condition, and only when it is TRUE evaluates that branch's result and stops. Results of the other branches, and conditions after the winner, are not touched. Three things depend on it:

- **Errors.** Division by zero, an overflow, a cast that fails: all of them stay inside the branch that is not taken. This is the guard idiom.
- **Cost.** A `case when cheap then x else <expensive subquery> end` should be cheap for the rows that take the first branch.
- **Side effects.** SQL has `nextval()` and `random()`; a branch that is not taken must not advance the sequence.

A planner or optimizer that "simplifies" a CASE by hoisting a sub-expression out of it (to compute it once) can destroy this guarantee, which is why constant folding is careful around CASE.

## The type is decided before any row is read

Every result branch, and the else, must have **one type**, and that type is the type of the CASE. `case when a > 1 then 'x' else 1 end` is an error, and it is found when the query is planned, not when the first row reaches the else. The one allowance is a bare `NULL` literal: `case when a > 1 then 'x' else null end` is a string expression, because a NULL has no type of its own and borrows the type of its neighbours. An engine that types its NULL literal as INTEGER (BusTub's does) has to remember this exception, or the most common CASE in SQL stops working.

## COALESCE and NULLIF are CASE with other names

`coalesce(a, b, c)` is `case when a is not null then a when b is not null then b else c end`. `nullif(a, b)` is `case when a = b then null else a end`. They look like functions, and they are not: `coalesce(x, expensive())` must not call `expensive()` when `x` is set, and a function factory that evaluates arguments first would get that wrong. So they are **rewritten in the binder** into a CASE, and nothing downstream knows they existed. The price of the rewrite is that `a` appears twice in the tree; for expressions without side effects that costs a second evaluation and nothing else.

`a / nullif(b, 0)` is the guard idiom in its shortest form: when `b` is zero the divisor becomes NULL, and a division by NULL is NULL, not an error.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `cond ? a : b` evaluates only the chosen side | `if cond { a } else { b }`: the same, and an expression |
| a function call `f(a, b)` evaluates `a` and `b` first | the same; a `CASE` needs closures or a tree walk to stay lazy |
| `std::variant` or a base class with a virtual `Evaluate` | an `enum` with `Box`ed children and a `match`, or a trait object |
| `nullptr` for "no else" | `Option<ExprRef>` |

## In real code

### Using it: a lazy CASE, and COALESCE and NULLIF as rewrites

```rust test
#[derive(Debug, Clone, PartialEq)]
enum E {
    Int(Option<i64>),
    Col(&'static str),
    IsNotNull(Box<E>),
    Eq(Box<E>, Box<E>),
    Gt(Box<E>, Box<E>),
    Div(Box<E>, Box<E>),
    Case(Vec<(E, E)>, Option<Box<E>>),
}
use E::*;

fn b(e: E) -> Box<E> {
    Box::new(e)
}

#[derive(Debug, PartialEq)]
enum V {
    Int(Option<i64>),
    Bool(Option<bool>),
}

/// Evaluates on a row `(a, b)`. Division by zero is an `Err`.
fn eval(e: &E, row: (Option<i64>, Option<i64>)) -> Result<V, &'static str> {
    let int = |v: V| match v {
        V::Int(x) => x,
        V::Bool(_) => panic!("type error"),
    };
    Ok(match e {
        Int(v) => V::Int(*v),
        Col("a") => V::Int(row.0),
        Col(_) => V::Int(row.1),
        IsNotNull(x) => V::Bool(Some(int(eval(x, row)?).is_some())),
        Eq(x, y) => V::Bool(match (int(eval(x, row)?), int(eval(y, row)?)) {
            (Some(x), Some(y)) => Some(x == y),
            _ => None,
        }),
        Gt(x, y) => V::Bool(match (int(eval(x, row)?), int(eval(y, row)?)) {
            (Some(x), Some(y)) => Some(x > y),
            _ => None,
        }),
        Div(x, y) => {
            let (x, y) = (int(eval(x, row)?), int(eval(y, row)?));
            match (x, y) {
                (_, Some(0)) => return Err("division by zero"),
                (Some(x), Some(y)) => V::Int(Some(x / y)),
                _ => V::Int(None),
            }
        }
        Case(branches, otherwise) => {
            for (cond, result) in branches {
                // a NULL condition is not TRUE; the result is evaluated only now
                if eval(cond, row)? == V::Bool(Some(true)) {
                    return eval(result, row);
                }
            }
            match otherwise {
                Some(e) => eval(e, row)?,
                None => V::Int(None),
            }
        }
    })
}

/// `coalesce(a, b, c)` is a CASE.
fn coalesce(args: Vec<E>) -> E {
    let mut args = args;
    let last = args.pop().unwrap();
    Case(args.into_iter().map(|a| (IsNotNull(b(a.clone())), a)).collect(), Some(b(last)))
}

/// `nullif(a, b)` is a CASE.
fn nullif(x: E, y: E) -> E {
    Case(vec![(Eq(b(x.clone()), b(y)), Int(None))], Some(b(x)))
}

#[test]
fn only_the_chosen_branch_is_evaluated() {
    // case when b = 0 then 0 else a / b end
    let guarded = Case(vec![(Eq(b(Col("b")), b(Int(Some(0)))), Int(Some(0)))], Some(b(Div(b(Col("a")), b(Col("b"))))));
    assert_eq!(eval(&guarded, (Some(7), Some(0))), Ok(V::Int(Some(0))), "the division is never reached");
    assert_eq!(eval(&guarded, (Some(7), Some(2))), Ok(V::Int(Some(3))));
    // without the guard the same row is an error
    assert_eq!(eval(&Div(b(Col("a")), b(Col("b"))), (Some(7), Some(0))), Err("division by zero"));
}

#[test]
fn a_null_condition_is_not_true_and_no_else_is_null() {
    // case when a > 1 then 10 end
    let e = Case(vec![(Gt(b(Col("a")), b(Int(Some(1)))), Int(Some(10)))], None);
    assert_eq!(eval(&e, (Some(5), None)), Ok(V::Int(Some(10))));
    assert_eq!(eval(&e, (Some(0), None)), Ok(V::Int(None)), "no branch matched and no else");
    assert_eq!(eval(&e, (None, None)), Ok(V::Int(None)), "a NULL condition does not match");
}

#[test]
fn coalesce_and_nullif_are_cases_and_keep_the_laziness() {
    let c = coalesce(vec![Col("a"), Div(b(Int(Some(1))), b(Int(Some(0))))]);
    assert_eq!(eval(&c, (Some(3), None)), Ok(V::Int(Some(3))), "the second argument is never evaluated when the first is set");
    assert_eq!(eval(&c, (None, None)), Err("division by zero"), "but it is when it is needed");
    let n = nullif(Col("a"), Col("b"));
    assert_eq!(eval(&n, (Some(2), Some(2))), Ok(V::Int(None)));
    assert_eq!(eval(&n, (Some(2), Some(3))), Ok(V::Int(Some(2))));
    // a / nullif(b, 0): the guard idiom
    let safe = Div(b(Col("a")), b(nullif(Col("b"), Int(Some(0)))));
    assert_eq!(eval(&safe, (Some(8), Some(0))), Ok(V::Int(None)));
}
```

### In the exercises

- **3i-03:** `CaseExpression::new` (typing the branches, a NULL literal adopting the type) and `evaluate` (stop at the first TRUE condition and evaluate only that result), and the binder's rewrite of `coalesce` and `nullif`.
- **3i-08:** the boss generates random CASE, COALESCE and NULLIF expressions and compares them with a model like `eval` above.

### Where it is used

- **PostgreSQL**: `CaseExpr` and `CoalesceExpr` are separate node types, and `NULLIF` is its own `NullIfExpr`; the planner's expression simplifier is careful not to evaluate a CASE branch early ("case_test_expr", `eval_const_expressions`).
- **SQL standard**: defines `COALESCE` and `NULLIF` as abbreviations of `CASE` (ISO/IEC 9075-2, section "case expression").
- **DataFusion / Velox**: a conditional expression evaluates its branches only for the rows that select them (selection vectors), which is the vectorised form of the same rule.
