A `Value` is a SQL value: a number, a boolean, a string, or **NULL**. NULL is not "no value": it is a value *of a type* (an integer NULL is not a string NULL), and it behaves differently from every ordinary value in comparisons and arithmetic (the next stages). This stage builds the enum, its constructors and the limits of each type.

BusTub has one design decision here that is worth understanding and that surprises everyone: it stores NULL **inside** the number. The smallest number of each integer type (`INT_MIN` for a 32-bit integer) is *reserved* to mean NULL. That is why a `TINYINT` is `-127..=127`, not `-128..=127`, and why a value constructed with the reserved number *is* a NULL.

## The task

In `src/types/value.rs` (the `Value` enum is given: `Null(TypeId)`, `Boolean`, `TinyInt`, `SmallInt`, `Integer`, `BigInt`, `Decimal`, `Timestamp`, `Varchar(String)`) implement:
- constructors `Value::null(type_id)`, `boolean`, `tinyint`, `smallint`, `integer`, `bigint`, `decimal`, `timestamp`, `varchar(&str)`: the number-taking ones return the NULL of their type when given the reserved number (`i8::MIN`, `i16::MIN`, `i32::MIN`, `i64::MIN`, `f64::MIN`, `u64::MAX`);
- `type_id()`, `is_null()`, `as_i64()` (any integer type, widened; `None` for NULL or non-integers) and `as_f64()` (any numeric type);
- `check_comparable(other)`: a boolean with a boolean or a string; a number with a number or a string; a string with anything; a timestamp with a timestamp;
- `Display`: `true`/`false`, integers in decimal, decimals with **six** digits after the point (`3.140000`), strings as they are, timestamps as the number, NULLs as `integer_null`, `varlen_null`, `decimal_null`, `boolean_null`...;
- in `type_id.rs`: `min_value()` and `max_value()` for each type (`Invalid` is a `MismatchType` error): the integers' minimum is **one above** the reserved number; a `Varchar`'s minimum is `""` and its maximum is NULL (there is no largest string).

## Tests

- The type and number of each value; the reserved number makes a NULL of the right type (and one above it does not); `Value::null(t)` has no number.
- Minimum and maximum of every type, including `-127` as the TINYINT minimum and `Invalid` as an error; the printed forms of numbers, decimals and every kind of NULL.
- Which pairs of types `check_comparable` allows.

## Syntax and methods

```rust
pub fn integer(v: i32) -> Value {
    if v == BUSTUB_INT32_NULL { Value::Null(TypeId::Integer) } else { Value::Integer(v) }
}
match self { Value::TinyInt(v) => Some(*v as i64), Value::BigInt(v) => Some(*v), _ => None }
impl fmt::Display for Value { fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result { write!(f, "{v:.6}") } }   // {:.6}: six decimals
```

## Notes

**Two ways to say NULL.** Rust would say `Option<i32>`; SQL says "an integer that might be NULL" for every column. BusTub avoids a flag by spending one number per type: the stored value is just the number, and `NULL` is the number that cannot be a value. Cost: you lose one value of the range (`-128` for a `TINYINT`) and every place that makes a value from a raw number must check it. Benefit: a tuple's integer column is exactly 4 bytes with no null bitmap. Real systems more often keep a separate null bitmap (PostgreSQL, SQLite's record format uses a type code): the next module's tuples will not need one because of this choice.

**The trap.** `Value::integer(i32::MIN)` is not an error and not a minimum value: it is a NULL. Code that computes `x - 1` on the smallest legal integer and wraps lands on the reserved number and silently turns into NULL. (Stage 5 checks for it.)

**Decimals print like C.** `std::to_string(3.14)` is `"3.140000"`; `format!("{v:.6}")` is the same, and the `.slt` tests of module 3's boss compare these strings exactly.

## In BusTub

`value.h`/`value.cpp` (constructors such as `Value::Value(TypeId type, int32_t i)`: "case TypeId::INTEGER: value_.integer_ = i; size_.len_ = (value_.integer_ == BUSTUB_INT32_NULL ? BUSTUB_VALUE_NULL : 0);"), `limits.h` ("static constexpr int32_t BUSTUB_INT32_MIN = (INT_MIN + 1); ... static constexpr int32_t BUSTUB_INT32_NULL = INT_MIN;") and `Type::GetMinValue/GetMaxValue`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| a class with a `union { int8_t boolean_; ...; char *varlen_; }`, a type id and a length that doubles as the NULL flag | `enum Value { Null(TypeId), Boolean(bool), ..., Varchar(String) }`: the compiler tracks which variant is live |
| `Value(TypeId type, int32_t i)`: one overloaded constructor per C++ integer type | a named constructor per SQL type: `Value::integer(i)` |
| `new char[len]` and a `manage_data_` flag for a string | an owned `String`; the flag and the destructor disappear |

**Port rule:** a C++ tagged union (`union` plus a discriminant) is a Rust `enum`; the manual ownership flag is the type system's job.

## Learn more
- [`fmt::Display`](https://doc.rust-lang.org/std/fmt/trait.Display.html) · [Formatting: precision](https://doc.rust-lang.org/std/fmt/index.html#precision) · [`i32::MIN`](https://doc.rust-lang.org/std/primitive.i32.html#associatedconstant.MIN)

## Performance

A `Value` is an enum of at most one machine word of payload plus a tag, except `Varchar`, which owns a heap string: cloning a number is a copy, cloning a string allocates. That is the reason later stages pass `&Value` and clone only at the edges (when a value must outlive its tuple). `size_of::<Value>()` is a few words (a `String` alone is three), which is what a vector of values costs per slot.

**Measure it.** Print `size_of::<Value>()` and `size_of::<Option<i32>>()`; build a million-element `Vec<Value>` of integers and one of `Vec<i32>` and compare the memory and the time to sum them.

## Hints

### Make the constructors the only way in

If code builds `Value::Integer(i32::MIN)` directly it bypasses the check and creates a value that serialises as NULL. Use the constructors everywhere (the enum's variants are public so you can `match` on them, but you should rarely *build* one by hand).

### Order the checks in `check_comparable` by the left type

The rule is about the left value's type: a number is comparable with numbers and strings; a boolean with booleans and strings; a string with everything; a timestamp only with a timestamp. `matches!(other.type_id(), ...)` per arm.

### Minimum is not the reserved number

`TypeId::Integer.min_value()` must be `i32::MIN + 1`, because `i32::MIN` would construct a NULL. The test `min_value().is_null()` is false for every type; that is what the constants in `limits.rs` are for.
