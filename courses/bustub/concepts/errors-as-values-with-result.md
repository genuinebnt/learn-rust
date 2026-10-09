---
title: Errors as values: Result, ?, and your own error type
summary: How Rust reports failure without exceptions, the ? operator, a small error type with a kind and a message, conversions between error types, and when to panic instead.
minutes: 9
---
BusTub throws C++ exceptions: `throw Exception(ExceptionType::OUT_OF_RANGE, "Numeric value out of range.")`. Whoever catches it, somewhere up the stack, decides what happens, and nothing in a function's signature says it can throw. Rust has no exceptions for ordinary failure. A function that can fail **returns** its failure:

```rust
fn parse_port(s: &str) -> Result<u16, std::num::ParseIntError> { s.trim().parse() }
```

`Result<T, E>` is an enum: `Ok(T)` or `Err(E)`. The type tells every caller the function can fail and how; the compiler warns if you ignore a `Result`.

## The `?` operator

```rust
fn add_ports(a: &str, b: &str) -> Result<u16, ParseIntError> {
    let (x, y) = (parse_port(a)?, parse_port(b)?);   // on Err, return it from this function now
    Ok(x + y)
}
```

`expr?` means: if `expr` is `Ok(v)` give `v`; if it is `Err(e)` return `Err(e.into())` immediately. It is a `throw` that is visible in the code and costs nothing when there is no error.

## An error type for a project

BusTub's `Exception` has a kind and a message. The same in Rust:

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum ExceptionType { OutOfRange, DivideByZero, Conversion }
#[derive(Debug, Clone, PartialEq)]
struct Exception { kind: ExceptionType, message: String }
impl std::fmt::Display for Exception { /* "Exception: [OutOfRange] message" */ }
impl std::error::Error for Exception {}
type Result<T> = std::result::Result<T, Exception>;
```

Tests match on `err.kind`, not on the message text; messages can change without breaking anything.

| tool | use |
|---|---|
| `?` | propagate |
| `.map_err(\|e\| Exception::new(..))` | change the error type |
| `.ok_or(err)` / `.ok_or_else(\|\| err)` | `Option` to `Result` |
| `.unwrap_or_default()`, `.unwrap_or(v)` | recover with a default |
| `match r { Ok(v) => .., Err(e) => .. }` | handle both |
| `impl From<ParseIntError> for Exception` | make `?` convert automatically |
| `.expect("msg")` / `.unwrap()` | "this cannot fail": panic with a message if it does |

> [!NOTE] Error or panic?
> An **error** is something that can happen on correct input (a number out of range, a cast that cannot be done): return `Err`. A **panic** is a bug (an index past the end of a page the code just checked, a violated invariant): `assert!`/`expect`. SQL `1/0` is an error; a leaf page with `size > max_size` is a panic.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `throw Exception(ExceptionType::X, "msg")` | `return Err(Exception::new(ExceptionType::X, "msg"))` |
| `try { f(); } catch (Exception &e) { ... }` | `match f() { Ok(v) => .., Err(e) => .. }` |
| an exception passing silently through frames | `?` at each frame, visible |
| `EXPECT_THROW(f(), Exception)` | `assert!(f().is_err())`, or `assert_eq!(f().unwrap_err().kind, ExceptionType::X)` |
| `noexcept`, or nothing | the return type says it |

## In real code

### Using it: a project error type, `?` and conversions

```rust test
use std::fmt;

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
enum ExceptionType { OutOfRange, DivideByZero, Conversion }

#[derive(Debug, Clone, PartialEq)]
struct Exception { kind: ExceptionType, message: String }

impl Exception {
    fn new(kind: ExceptionType, message: impl Into<String>) -> Exception { Exception { kind, message: message.into() } }
}
impl fmt::Display for Exception {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { write!(f, "Exception: [{:?}] {}", self.kind, self.message) }
}
impl std::error::Error for Exception {}
type Result<T> = std::result::Result<T, Exception>;

// `?` converts a ParseIntError into an Exception through From
impl From<std::num::ParseIntError> for Exception {
    fn from(e: std::num::ParseIntError) -> Exception { Exception::new(ExceptionType::Conversion, e.to_string()) }
}

fn to_u8(v: i64) -> Result<u8> {
    u8::try_from(v).map_err(|_| Exception::new(ExceptionType::OutOfRange, "Numeric value out of range."))
}

fn divide(a: i64, b: i64) -> Result<i64> {
    if b == 0 { return Err(Exception::new(ExceptionType::DivideByZero, "Division by zero.")); }
    Ok(a / b)
}

fn average_of_text(a: &str, b: &str, count: i64) -> Result<u8> {
    let sum: i64 = a.trim().parse::<i64>()? + b.trim().parse::<i64>()?;     // two `?` conversions
    to_u8(divide(sum, count)?)                                              // two more, all visible
}

#[test]
fn question_mark_returns_the_first_error_and_converts_it() {
    assert_eq!(average_of_text(" 10", "20 ", 2), Ok(15));
    assert_eq!(average_of_text("10", "x", 2).unwrap_err().kind, ExceptionType::Conversion);
    assert_eq!(average_of_text("10", "20", 0).unwrap_err().kind, ExceptionType::DivideByZero);
    assert_eq!(average_of_text("1000", "1000", 2).unwrap_err().kind, ExceptionType::OutOfRange);
    assert_eq!(average_of_text("1000", "x", 0).unwrap_err().kind, ExceptionType::Conversion, "the first failure wins: the parse comes before the division");
}

#[test]
fn display_and_the_error_trait_make_it_a_normal_error() {
    let e = divide(1, 0).unwrap_err();
    assert_eq!(e.to_string(), "Exception: [DivideByZero] Division by zero.");
    let boxed: Box<dyn std::error::Error> = Box::new(e);            // usable wherever a dyn Error is wanted
    assert!(boxed.to_string().contains("DivideByZero"));
}
```

```rust test
#[test]
fn option_to_result_collect_and_defaults() {
    let numbers = ["1", "2", "3"];
    let all: Result<Vec<i32>, _> = numbers.iter().map(|s| s.parse::<i32>()).collect();   // the first Err stops the collection
    assert_eq!(all.unwrap(), vec![1, 2, 3]);
    let bad: Result<Vec<i32>, _> = ["1", "oops", "3"].iter().map(|s| s.parse::<i32>()).collect();
    assert!(bad.is_err());

    let found: Option<&str> = numbers.iter().copied().find(|s| *s == "2");
    let as_result: Result<&str, String> = found.ok_or_else(|| "no 2".to_string());
    assert_eq!(as_result, Ok("2"));
    let missing = numbers.iter().copied().find(|s| *s == "9").ok_or("no 9");
    assert_eq!(missing, Err("no 9"));

    assert_eq!("x".parse::<i32>().unwrap_or(-1), -1);
    assert_eq!("5".parse::<i32>().map(|n| n * 2), Ok(10));
    // expect is for "cannot fail": it panics with the message if it does
    let n: i32 = "42".parse().expect("a literal is a number");
    assert_eq!(n, 42);
}

#[test]
#[should_panic(expected = "invariant")]
fn a_violated_invariant_is_a_panic_not_an_error() {
    let size = 5;
    let max = 4;
    assert!(size <= max, "invariant: a page never holds more than max_size entries");
}
```

### In the exercises

- **3a-01 to 3a-04:** `type_size`, `cast_as`, the comparisons and the arithmetic return `Result`; `?` chains the checks, and the `Err` carries an `Exception` with a kind (`OutOfRange`, `Conversion`, `DivideByZero`, ...).
- **Everything later**: executors return `Result<Option<Tuple>>` and an error aborts the query with its message printed by the shell (module 3b).

### Where it is used

- **Every Rust program**: `std::io::Result`, `std::fmt::Result`, `Result<(), Box<dyn Error>>` in `main`.
- **`thiserror` and `anyhow`**: the first derives `Display` and `From` for error enums like the one above; the second is a catch-all error type for applications (`anyhow::Result`, `.context("reading the file")`).
- **Databases written in Rust** (`sqlparser-rs`' `ParserError`, `redb`'s `StorageError`, `datafusion`'s `DataFusionError`) are enums of error kinds with messages, just like BusTub's `Exception`.
