`SELECT price * qty`, `UPDATE t SET v3 = v3 + v1`, `sum(x)`: the executors of module 3b add, subtract, multiply and divide `Value`s all day. This stage is the arithmetic, with the three rules that make it SQL's and not just a calculator's: operands of different widths produce the **wider** type, **overflow is an error** (not a wrap-around), and **NULL poisons the result**.

## The task

In `src/types/value.rs` implement `arithmetic(&self, other, op)` and its public wrappers `add`, `subtract`, `multiply`, `divide`, `modulo` (all `Result<Value>`), plus `operate_null`, `is_zero`, `min`, `max` and `sqrt`:
- The left operand must be a **number** (integer type or decimal): otherwise a `NotImplemented` error. The right operand must be `check_comparable` with it: a **string** on the right is converted to the *left's* type first (`2 + '40'` is 42); a boolean on the right is an error.
- A **NULL** on either side gives `operate_null`: the NULL of the result type, even if the other operand would have divided by zero.
- **Division or modulo by zero** is `DivideByZero` (an integer zero, a decimal `0.0`, or a string that converts to zero).
- The **result type** is the wider of the two: `Decimal` if either is, else the wider integer type (`TinyInt` < `SmallInt` < `Integer` < `BigInt`).
- **Integer arithmetic is exact**: the result must fit the result type (not the left's!), else `OutOfRange` (`100 + 100` in tinyints overflows; a tinyint plus an integer is an integer and fits). Division truncates toward zero; modulo takes the dividend's sign.
- **Decimal arithmetic** is `f64` arithmetic; its modulo is `x - trunc(x / y) * y`.
- `min`/`max` of two comparable values (a NULL on either side gives a NULL); `sqrt` gives a `Decimal` (negative: a `Decimal` error; NULL: the decimal NULL); `is_zero` for numbers (anything else `NotImplemented`).

## Tests

- The five operations on integers, including negative division and modulo; the result type of every mix of widths, with decimals.
- Overflow (add, multiply, subtract past the minimum, tinyints) and the three divisions by zero; NULL in every position, and NULL winning over zero.
- Strings converting on the right, non-numbers refused on both sides; min/max/sqrt/is_zero.

## Syntax and methods

```rust
let exact: i128 = x as i128 * y as i128;                       // widen first: i64 * i64 cannot overflow an i128
i64::try_from(exact).map_err(|_| out_of_range())?              // does it fit an i64? then check the result TYPE's range
a.max(b)                                                       // TypeId derives Ord: BigInt > Integer > SmallInt > TinyInt
x.checked_add(y)  x.checked_mul(y)                             // the std way: None on overflow
```

## Notes

**Widen, compute, narrow.** Doing the arithmetic in `i128` makes overflow impossible during the computation, so the only question is whether the *result* fits the result type: one range check instead of a case analysis per operator. (BusTub's C++ detects overflow after the fact with sign tests; `checked_add` and friends are the std way when you stay in one width.)

**Why the reserved number matters again.** An integer result equal to the NULL encoding (`i32::MIN`) must not silently become NULL; `cast_integer` (stage 3) already refuses it, so `i32::MIN + 1 - 1` is an `OutOfRange`, not a surprise NULL.

**NULL beats errors.** `NULL / 0` is NULL in SQL, not a division-by-zero error: check NULL before zero. That is how `SELECT 1/0` errors but `SELECT NULL/0` does not.

## In BusTub

`integer_parent_type.h` (`AddValue<T1, T2>`: "if ((x + y) != sum1 && (x + y) != sum2) { throw Exception(ExceptionType::OUT_OF_RANGE, "Numeric value out of range."); }" and the "sizeof(x) >= sizeof(y)" result-type rule), `IntegerType::Divide` ("if (right.IsZero()) { throw Exception(ExceptionType::DIVIDE_BY_ZERO, "Division by zero on right-hand side"); }"), `IntegerType::OperateNull`, `IntegerType::Sqrt` ("Cannot take square root of a negative number.").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `if (x > 0 && y > 0 && sum < 0) throw ...` (UB-adjacent: signed overflow is undefined behaviour in C++) | `checked_add`, or widen to `i128` and range-check |
| `template <class T1, class T2> AddValue(...)`, one instantiation per pair of widths | one function over `i128`, then a range check against the result type |
| `std::sqrt`, `std::fmod` | `f64::sqrt`, `x - (x / y).trunc() * y` (or `%`, which is the truncated remainder for floats too) |

**Port rule:** signed overflow in C++ is undefined behaviour and in Rust a panic (debug) or a wrap (release) unless you use `checked_*`: always say which you mean.

## Learn more
- [`i64::checked_add`](https://doc.rust-lang.org/std/primitive.i64.html#method.checked_add) · [`wrapping_`, `saturating_`, `overflowing_`](https://doc.rust-lang.org/std/primitive.i64.html#method.overflowing_add) · [`i128`](https://doc.rust-lang.org/std/primitive.i128.html) · [`f64::sqrt`](https://doc.rust-lang.org/std/primitive.f64.html#method.sqrt)

## Performance

An `i128` multiply is a handful of instructions (a 64x64 to 128 multiplication is one machine instruction on x86-64), so the widen-and-check approach costs little more than the raw operation plus a range comparison; `checked_mul` on `i64` is similar. The expensive part of `Value` arithmetic is the dispatch: a `match` on two tags per operation. Real engines avoid it with vectorised execution: they resolve the types once and run a tight loop over a column of `i32`s.

**Measure it.** Sum a million `Value::integer`s with `add` and compare with summing a `Vec<i32>`: the ratio is the cost of a dynamically typed value.

## Hints

### Check the order: type, NULL, zero, convert, compute

(1) The left operand is not a number: error. (2) A NULL on either side: return `operate_null`. (3) Division by zero, after converting a string on the right to the left's type. (4) The result type. (5) Compute exactly and range-check. The test `NULL / 0` pins the second and third in that order.

### The result type is not the left's type

`tinyint(100) + integer(100)` is an `integer(200)`. Compute the result type first, then check the exact result against *its* range.

### Integer division and modulo have no overflow, but have signs

`-17 / 5` is `-3` and `-17 % 5` is `-2` (toward zero; the remainder has the dividend's sign). Rust's `/` and `%` on integers do exactly that, so no special code: just do not use `rem_euclid` or `div_euclid` (those round toward negative infinity).
