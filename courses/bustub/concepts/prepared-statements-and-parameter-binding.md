---
title: Prepared statements: parse once, bind values, never re-parse text
summary: A prepared statement is SQL with `?` placeholders that is parsed once and executed many times with values. Binding values into the syntax tree, not into the text, is what makes SQL injection impossible and what lets a plan be reused.
minutes: 8
---
Two programs build the same query. The first writes `format!("select * from users where name = '{name}'")` and runs it. The second writes `select * from users where name = ?` once, and hands the database the name separately. They return the same rows for ordinary names and behave completely differently for `x' or '1'='1`: the first one returns every user, because the quote ended the literal and the rest became SQL; the second one looks for a user whose name is that odd string, because the value was never *parsed*.

## The three things a prepared statement is

1. **A statement with holes.** `?` marks a place where a value goes. Placeholders are numbered in the order they appear: `where a between ? and ? limit ?` has three.
2. **A parse that happens once.** `prepare` runs the lexer and parser and keeps the syntax tree. Executing it again does not re-tokenise, re-parse or re-resolve names.
3. **Values bound into the tree.** `execute` takes a list of values, replaces each placeholder with a *literal node* holding that value, and runs the result. A string value becomes a string literal node: it is data in the tree, not characters for the lexer to look at.

The third point is the security argument and also the correctness argument. A value cannot change the *shape* of the statement, whatever it contains, because the shape was fixed before the value existed.

## Where the values go, and where they cannot

A placeholder stands for a **value**, so it works wherever a literal works: comparisons, `IN` lists, `BETWEEN`, `LIKE` patterns, `LIMIT`, `OFFSET`, `VALUES` rows, `SET` assignments. It cannot stand for an identifier or a keyword: `select * from ?` and `order by ? desc` (the sort direction) are not prepared-statement features, because a table name decides what the statement *is*. Code that needs a dynamic table name must build the text itself and check the name against the catalog.

## Checking the call

Binding is a function from `(statement, values)` to a statement, and it can go wrong in three ways that a real driver reports as errors: **too few** values (a placeholder would remain unbound: a runtime failure in the middle of execution is the worst way to find out), **too many** (a bug in the caller), and a value of a type the engine cannot write as a literal. The count is known at prepare time, so the check is one comparison before any work.

A statement that reaches the binder with a placeholder still in it (somebody called plain `execute_sql` on SQL with a `?`) must fail with a message that says what happened, not be bound to NULL or be guessed.

## Reuse: what a prepared statement can and cannot save

Preparing saves lexing and parsing, which is cheap. The expensive parts are planning and optimizing. A system can cache the **plan** too, and then values are bound at execution time rather than into the tree; but now the plan was chosen without seeing the values, and the best plan for `where a = 1` (a rare value: use the index) may be wrong for `where a = 2` (half the table: scan). PostgreSQL's answer is to plan with the actual values for the first few executions and switch to a "generic" plan only when it is not worse. Substituting into the tree and planning every time, as this course does, is the simple end of that spectrum and has no such problem.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `PQprepare` / `PQexecPrepared`, `sqlite3_prepare_v2` / `sqlite3_bind_int` | `prepare` returning a handle, `execute(&handle, &[Value])` |
| bind by position (`?`) or by name (`:name`, `$1`) | by position here |
| the driver may re-prepare silently when the schema changed | a prepared statement that names a dropped table fails at execution |
| a visitor class over the AST | a function taking `&mut dyn FnMut(&mut Expr)` and walking every node |

## In real code

### Using it: counting and binding placeholders in a tree

```rust test
#[derive(Debug, Clone, PartialEq)]
enum Literal {
    Int(i64),
    Str(String),
    Null,
}

#[derive(Debug, Clone, PartialEq)]
enum E {
    Lit(Literal),
    Param(usize),
    Col(&'static str),
    Eq(Box<E>, Box<E>),
    And(Box<E>, Box<E>),
}
use E::*;

fn b(e: E) -> Box<E> {
    Box::new(e)
}

/// Calls `f` on every node, children after the node itself.
fn visit(e: &mut E, f: &mut dyn FnMut(&mut E)) {
    f(e);
    match e {
        Eq(l, r) | And(l, r) => {
            visit(l, f);
            visit(r, f);
        }
        _ => {}
    }
}

fn param_count(e: &E) -> usize {
    let mut n = 0;
    visit(&mut e.clone(), &mut |x| {
        if matches!(x, Param(_)) {
            n += 1;
        }
    });
    n
}

/// A copy of `e` with each `?` replaced by its value; the number of values must match.
fn bind(e: &E, values: &[Literal]) -> Result<E, String> {
    if values.len() != param_count(e) {
        return Err(format!("{} placeholder(s), {} value(s)", param_count(e), values.len()));
    }
    let mut out = e.clone();
    visit(&mut out, &mut |x| {
        if let Param(i) = x {
            *x = Lit(values[*i].clone());
        }
    });
    Ok(out)
}

#[test]
fn placeholders_are_numbered_by_position_and_counted() {
    // name = ? and age = ?
    let q = And(b(Eq(b(Col("name")), b(Param(0)))), b(Eq(b(Col("age")), b(Param(1)))));
    assert_eq!(param_count(&q), 2);
    assert_eq!(param_count(&Eq(b(Col("a")), b(Lit(Literal::Int(1))))), 0);
}

#[test]
fn a_value_that_looks_like_sql_is_only_a_literal() {
    let q = Eq(b(Col("name")), b(Param(0)));
    let evil = Literal::Str("x' or '1'='1".to_string());
    let bound = bind(&q, &[evil.clone()]).unwrap();
    assert_eq!(bound, Eq(b(Col("name")), b(E::Lit(evil))), "the tree has the same shape as before: one comparison");
}

#[test]
fn the_number_of_values_is_checked_and_the_original_is_untouched() {
    let q = And(b(Eq(b(Col("a")), b(Param(0)))), b(Eq(b(Col("b")), b(Param(1)))));
    assert!(bind(&q, &[Literal::Int(1)]).is_err());
    assert!(bind(&q, &[Literal::Int(1), Literal::Int(2), Literal::Int(3)]).is_err());
    let first = bind(&q, &[Literal::Int(1), Literal::Null]).unwrap();
    let second = bind(&q, &[Literal::Int(7), Literal::Int(8)]).unwrap();
    assert_ne!(first, second, "the same statement, executed with other values");
    assert_eq!(param_count(&q), 2, "the prepared statement still has its holes");
}
```

### In the exercises

- **3i-07:** `prepare` is `param_count` over the parsed statements; `execute_prepared` is `bind` followed by the normal execution; `literal` turns a `Value` into the literal node. The syntax tree's `visit_exprs_mut` is given.

### Where it is used

- **PostgreSQL**: `PREPARE` / `EXECUTE` and the extended query protocol's Parse / Bind / Execute messages; `plan_cache_mode` chooses custom or generic plans.
- **SQLite**: `sqlite3_prepare_v2`, `sqlite3_bind_*`; a statement is compiled to bytecode once and run many times.
- **Every database driver**: JDBC `PreparedStatement`, Python's DB-API `cursor.execute(sql, params)`, Rust's `sqlx::query(...).bind(...)`.
