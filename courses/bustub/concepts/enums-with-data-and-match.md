---
title: Enums that carry data, and match
summary: Rust's enum is a tagged union the compiler checks: each variant can hold different data, a match must cover every variant, and Option and Result are just enums. How a SQL value, a page type or an expression becomes one type.
minutes: 9
---
A SQL value is *one of* several things: an integer, a string, a boolean or a NULL, and which one decides everything you can do with it. In C++ you write a class with a `union`, a type tag and a destructor that must look at the tag. In Rust you write an **enum**, and the language keeps the tag and the data together for you.

```rust
enum Value {
    Null(TypeId),       // carries a type
    Boolean(bool),
    Integer(i32),
    Varchar(String),    // owns its text
}
```

Each variant has its own payload (or none). A `Value` is exactly one variant at a time, it takes the size of the largest payload plus a tag, and you cannot read the integer out of a `Varchar` by mistake: the only way to reach the payload is to **match**.

## `match` must cover everything

```rust
fn describe(v: &Value) -> String {
    match v {
        Value::Null(t) => format!("NULL of {t:?}"),
        Value::Boolean(b) => b.to_string(),
        Value::Integer(i) if *i < 0 => format!("negative {i}"),   // a guard
        Value::Integer(i) => i.to_string(),
        Value::Varchar(s) => s.clone(),
    }
}
```

The compiler checks that every variant is handled. Add `Value::Decimal(f64)` and every `match` without a catch-all stops compiling until you decide what it does: that is the feature. (A wildcard `_ =>` arm turns it off: use it only when "everything else" is truly one case.)

| tool | use |
|---|---|
| `match v { ... }` | handle every variant |
| `if let Value::Integer(i) = v { ... }` | one variant matters |
| `let Value::Integer(i) = v else { return Err(..) };` | one variant matters, otherwise leave |
| `matches!(v, Value::Null(_) \| Value::Boolean(_))` | a boolean question about the shape |
| `v.as_i64()` (your own accessor returning `Option`) | repeated "get the payload or None" |
| `or`-patterns: `A \| B => ...` | variants that share a body |

## `Option` and `Result` are enums

`Option<T>` is `enum Option<T> { None, Some(T) }`; `Result<T, E>` is `enum Result<T, E> { Ok(T), Err(E) }`. Everything above works on them, and their methods (`map`, `ok_or`, `unwrap_or`, `?`) are ordinary functions on those enums.

## C++ comparison

| C / C++ | Rust |
|---|---|
| a class with `union { int32_t i; char *s; }`, a `TypeId` tag and manual copy/destroy | `enum Value { Integer(i32), Varchar(String) }`: tag, data and destructor generated and correct |
| `switch (v.type) { case INTEGER: ...; default: throw ...; }` (a forgotten case compiles) | `match v { ... }` (a forgotten variant does not compile) |
| `std::variant<int, std::string>` and `std::visit` | an enum and `match`, with better ergonomics |
| `std::optional<T>` | `Option<T>` |

## In real code

### Using it: a small value type, matched exhaustively

```rust test
#[derive(Clone, Debug, PartialEq)]
enum Value { Null, Boolean(bool), Integer(i32), Varchar(String) }

impl Value {
    fn type_name(&self) -> &'static str {
        match self {                                   // no wildcard: a new variant must be handled here
            Value::Null => "null",
            Value::Boolean(_) => "boolean",
            Value::Integer(_) => "integer",
            Value::Varchar(_) => "varchar",
        }
    }
    fn as_i64(&self) -> Option<i64> {
        if let Value::Integer(i) = self { Some(*i as i64) } else { None }
    }
    fn is_scalar(&self) -> bool { matches!(self, Value::Boolean(_) | Value::Integer(_)) }
}

#[test]
fn each_variant_carries_its_own_data() {
    let values = [Value::Null, Value::Boolean(true), Value::Integer(-4), Value::Varchar("hi".into())];
    let names: Vec<_> = values.iter().map(Value::type_name).collect();
    assert_eq!(names, vec!["null", "boolean", "integer", "varchar"]);
    assert_eq!(values[2].as_i64(), Some(-4));
    assert_eq!(values[3].as_i64(), None, "the text is not reachable as a number");
    assert_eq!(values.iter().filter(|v| v.is_scalar()).count(), 2);
}

#[test]
fn patterns_bind_guard_and_nest() {
    fn classify(v: &Value) -> &'static str {
        match v {
            Value::Integer(i) if *i < 0 => "negative",
            Value::Integer(0) => "zero",
            Value::Integer(_) => "positive",
            Value::Varchar(s) if s.is_empty() => "empty text",
            Value::Varchar(_) => "text",
            Value::Null | Value::Boolean(_) => "other",
        }
    }
    assert_eq!(classify(&Value::Integer(-1)), "negative");
    assert_eq!(classify(&Value::Integer(0)), "zero");
    assert_eq!(classify(&Value::Integer(9)), "positive");
    assert_eq!(classify(&Value::Varchar(String::new())), "empty text");
    assert_eq!(classify(&Value::Null), "other");
    // pairs of enums match together: how a binary operator picks its implementation
    let pair = (Value::Integer(2), Value::Integer(3));
    let sum = match &pair { (Value::Integer(a), Value::Integer(b)) => Some(a + b), _ => None };
    assert_eq!(sum, Some(5));
}
```

```rust test
#[test]
fn option_and_result_are_enums_with_the_same_tools() {
    let parsed: Vec<Result<i32, _>> = ["7", "x", "-3"].iter().map(|s| s.parse::<i32>()).collect();
    assert!(matches!(parsed[0], Ok(7)));
    assert!(matches!(parsed[1], Err(_)));
    let present: Vec<i32> = parsed.into_iter().filter_map(Result::ok).collect();
    assert_eq!(present, vec![7, -3]);

    let first: Option<&i32> = present.first();
    let Some(&n) = first else { panic!("empty") };       // let-else
    assert_eq!(n, 7);
    assert_eq!(present.get(5).copied().unwrap_or(-1), -1);
    assert_eq!(Some(4).map(|x| x * 2).filter(|x| *x > 5), Some(8));
    assert_eq!(std::mem::size_of::<Option<Box<i32>>>(), std::mem::size_of::<Box<i32>>(), "Option<Box<T>> costs nothing: None is the null pointer (a niche)");
}
```

### In the exercises

- **3a-01 to 3a-05:** `TypeId` is a plain enum and `Value` the enum with data; every operation is a `match` on the variant (or on a pair of variants).
- **Module 3b onward:** plan nodes (`PlanNode`) and expressions (`Expression`) are enums too: each executor is a `match` on the kind of node.

### Where it is used

- **Compilers and interpreters**: an AST is an enum (`rustc`'s `ExprKind`, the `sqlparser` crate's `Statement` and `Expr`); evaluating it is a `match`.
- **State machines**: a connection is `enum State { Connecting, Open(Socket), Closed(Reason) }` and illegal states are unrepresentable.
- **Error handling**: every library error type is an enum of causes (`std::io::ErrorKind`).
- **Messages**: wire protocols and actor messages (`enum Command { Get(Key), Put(Key, Value) }`).
