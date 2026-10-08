A cast converts a value to another type: `'42'` to an integer, an integer to a smaller integer, a number to text. In SQL it is written `CAST(x AS ...)` and it also happens silently: comparing `'32'` with `32`, adding a string to a number, inserting an integer into a decimal column. Every such conversion in the engine goes through one function, so this stage is where the rules live: what converts, what is checked, and what is an error.

## The task

In `src/types/value.rs` implement `cast_as(&self, to: TypeId) -> Result<Value>` (and the helpers `cast_integer`, `cast_decimal`, `cast_text` and the given `leading_number`):
- **Allowed conversions**: numbers (integers and decimal) to numbers and to `Varchar`; a `Varchar` to a boolean, a number or itself; a boolean to itself and `Varchar`; a timestamp to itself and `Varchar`. Everything else is an error ("INTEGER is not coercable to BOOLEAN"), even for a NULL.
- A **NULL** converts to the NULL of the target type.
- A number to `Varchar` is its `Display` text.
- **Integer to a narrower integer type**: `OutOfRange` unless it fits `[MIN + 1, MAX]` of the target (the reserved number is not a value). Integer to decimal is exact.
- **Decimal to an integer type**: `OutOfRange` unless it is within the target's range (compare as `f64`; for `BigInt`, `>= i64::MAX as f64` is out), then **truncate toward zero**.
- **Varchar to a number**: the number at the start of the text after white space (`"32"`, `"  -7"`, `"12abc"` is 12, `"2.5e1"` as a decimal is 25), `Conversion` error if there are no digits, `OutOfRange` if it does not fit. **To a boolean**: `true`/`1`/`t` or `false`/`0`/`f`, any case; else an error.

## Tests

- Integer widening and narrowing with the exact boundaries (127, 128, -127, -128, 40,000 into SMALLINT), decimals truncating toward zero with range errors.
- Text to numbers (white space, a sign, trailing junk, an exponent, no digits, too big) and to booleans; numbers and booleans to text.
- NULLs and the impossible casts.

## Syntax and methods

```rust
let in_range = |min: i64, max: i64| if (min..=max).contains(&v) { Ok(()) } else { Err(out_of_range()) };
d.trunc() as i64                                  // f64 -> i64 truncating toward zero
s.trim_start()                                    // skip leading white space
text.parse::<i64>().map_err(|_| out_of_range())   // a number too big for i64 parses as an error
```

## Notes

**One function, one table.** `cast_as` first decides whether the conversion is *allowed at all* (from the type pair), then converts. Keeping those two steps separate is what makes the NULL case simple (a NULL passes the first step and skips the second) and keeps the error message the same for every impossible pair.

**`"12abc"` is 12.** C++'s `std::stoi` parses a prefix and ignores the rest, and BusTub's casts use it. Rust's `str::parse` is strict ("12abc" is an error). The given `leading_number(s, decimal)` finds the prefix text so you can hand just that to `parse`. Whether silently accepting trailing garbage is a good rule is arguable (PostgreSQL rejects it); the course keeps BusTub's behaviour because the `.slt` tests depend on it.

**Narrowing must check.** `x as i8` in Rust silently wraps (300 becomes 44). Always check the range first and return `OutOfRange`. (BusTub's own `VARCHAR` to `TINYINT` cast truncates before checking; this port checks properly.)

## In BusTub

`CastAs` in `integer_type.cpp` ("if (val.GetAs<int32_t>() > BUSTUB_INT8_MAX || val.GetAs<int32_t>() < BUSTUB_INT8_MIN) { throw Exception(ExceptionType::OUT_OF_RANGE, "Numeric value out of range."); }"), `decimal_type.cpp` and `varlen_type.cpp` (the `stoi`/`stoll`/`stod` casts, and "if (str == "true" || str == "1" || str == "t") { return {type_id, 1}; }").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `static_cast<int8_t>(x)`, `(int8_t)x` (wraps silently) | `i8::try_from(x)` or an explicit range check; `x as i8` only when wrapping is what you want |
| `std::stoi(str)` (prefix parse; throws `invalid_argument`/`out_of_range`) | `leading_number(..)` then `parse::<i64>()` with `?`/`map_err` |
| `(int64_t)3.99` (truncation toward zero) | `3.99_f64.trunc() as i64` (a Rust `as` cast from float saturates; check the range first) |
| `std::to_string(double)` | `format!("{d:.6}")` |

**Port rule:** every narrowing conversion gets a range check; every text-to-number conversion decides what to do with trailing text.

## Learn more
- [`TryFrom`/`TryInto`](https://doc.rust-lang.org/std/convert/trait.TryFrom.html) · [`str::parse`](https://doc.rust-lang.org/std/primitive.str.html#method.parse) · [`f64::trunc`](https://doc.rust-lang.org/std/primitive.f64.html#method.trunc) · [Numeric casts in the Reference](https://doc.rust-lang.org/reference/expressions/operator-expr.html#numeric-cast)

## Performance

A cast of a number is a few comparisons; a cast of text parses the digits (linear in the text) and, for `Varchar` targets, allocates a `String`. Comparing `'32'` with `32` therefore costs a parse each time, and a query that compares a string column with a number constant would do it for every row, which is why the planner (module 3) converts constants *once* and why a column's type should match what you compare it with.

**Measure it.** Time 10 million `cast_as(Integer)` of `"12345"` and compare with `str::parse::<i32>`; then 10 million `Value::integer` to `Varchar` casts and see the allocation cost.

## Hints

### Decide "is it allowed" before you look at the value

Write the allowed-pairs `match` first and test it alone (every source type against every target type). The value-dependent work (ranges, parsing) only happens for allowed pairs, and a NULL never reaches it.

### Compare in the widest type that cannot lose information

An `i64` holds every integer value of every integer type, so integer-to-integer is one range check on an `i64`. A decimal compared with an integer range is compared as `f64`. Do not convert the bounds to the narrow type (`i8::MAX as i64` is fine; `v as i8` first is not).

### Let `leading_number` do the scanning

You get the text of the number (or `None`); `parse` turns it into a value; a parse failure on text that *is* all digits means it was too big (`OutOfRange`), not a bad format (`Conversion`).
