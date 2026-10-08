---
title: Overflow: checked, wrapping and saturating arithmetic
summary: What happens when an integer does not fit, the four std families (checked, wrapping, saturating, overflowing), widening to i128, as-casts versus try_from, and how a database decides.
minutes: 8
---
A 32-bit integer holds numbers up to 2,147,483,647. Add 1 and the answer does not fit. What should happen? Languages disagree, and a database must pick *one* answer and apply it everywhere:

| choice | result of `i32::MAX + 1` | who does this |
|---|---|---|
| **wrap around** | -2,147,483,648 | C/C++ unsigned; Rust release builds with `+` (not guaranteed); `wrapping_add` |
| **undefined behaviour** | anything | C/C++ **signed** overflow |
| **panic** | the program stops | Rust debug builds with `+` |
| **saturate** | 2,147,483,647 | `saturating_add`, DSP code |
| **report an error** | `None` / `Err` | `checked_add`; **SQL** (`ERROR: integer out of range`) |

SQL's answer is always the last one: an arithmetic result that does not fit is an **error**, never a wrong number.

## The four std families

For every integer type, `i32::checked_add`, `wrapping_add`, `saturating_add` and `overflowing_add` (and the same for `sub`, `mul`, `neg`, `pow`, `abs`, `shl`...):

- `checked_*` returns `Option<T>`: `None` on overflow. Use for **"it must not overflow"**.
- `wrapping_*` wraps modulo 2^N. Use for hashes and checksums.
- `saturating_*` clamps to MIN/MAX. Use for counters that must not wrap.
- `overflowing_*` returns `(wrapped, did_overflow)`.

A plain `+` panics on overflow in debug builds and wraps in release builds (unless `overflow-checks` is on): never rely on either.

## Widening: the easy way to be exact

To add or multiply two `i64`s without overflow, do it in `i128`: the product of two 64-bit numbers always fits in 128 bits. Then ask **once** whether the result fits the target type. One range check replaces a case analysis per operation, and the result is correct for every operator.

```rust
let exact = x as i128 * y as i128;
i64::try_from(exact)            // Err(TryFromIntError) if it does not fit
```

## `as` versus `try_from`

`300_i32 as i8` silently truncates to 44; `i8::try_from(300_i32)` is an `Err`. `as` is for when you *want* truncation (taking the low byte, converting an index); anywhere a wrong value would be a bug, use `try_from` or a range check. (`as` from a float to an integer saturates, and NaN becomes 0.)

## The reserved-NULL wrinkle

BusTub reserves `INT_MIN` as NULL, so a *result* equal to `INT_MIN` is not a valid value: the range of an `i32` column is `[INT_MIN + 1, INT_MAX]`. The check after the computation is therefore against that range, not the type's.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `if (x > 0 && y > 0 && x + y < 0)` (the test itself is signed overflow: UB) | `x.checked_add(y)` |
| `__builtin_add_overflow(x, y, &out)` | `x.overflowing_add(y)` or `checked_add` |
| `static_cast<int8_t>(300)` | `300 as i8` (truncates) or `i8::try_from(300)` (errors) |
| `std::numeric_limits<int>::max()` | `i32::MAX` |

## In real code

### Using it: the four families, widening and a range-checked result

```rust test
#[test]
fn the_four_families_on_the_edge() {
    let max = i32::MAX;
    assert_eq!(max.checked_add(1), None);
    assert_eq!(max.wrapping_add(1), i32::MIN);
    assert_eq!(max.saturating_add(1), i32::MAX);
    assert_eq!(max.overflowing_add(1), (i32::MIN, true));
    assert_eq!(5i32.checked_add(1), Some(6));
    assert_eq!(i32::MIN.checked_neg(), None, "even negation overflows: -MIN does not exist");
    assert_eq!(i32::MIN.checked_abs(), None);
    assert_eq!(2i32.checked_pow(31), None);
    assert_eq!(2i32.checked_pow(30), Some(1 << 30));
    assert_eq!(7i32.checked_div(0), None);
    assert_eq!(i32::MIN.checked_div(-1), None, "the one integer division that overflows");
}

#[test]
fn as_truncates_and_try_from_checks() {
    assert_eq!(300_i32 as i8, 44);
    assert_eq!(-1_i32 as u8, 255);
    assert_eq!(3.99_f64 as i32, 3);
    assert_eq!(1e20_f64 as i32, i32::MAX, "a float cast saturates");
    assert_eq!(f64::NAN as i32, 0);
    assert!(i8::try_from(300_i32).is_err());
    assert_eq!(i8::try_from(100_i32), Ok(100));
    assert!(u32::try_from(-1_i64).is_err());
}
```

```rust test
/// Exact arithmetic on SQL integers: compute in i128, then check the RESULT TYPE's range (MIN + 1 ..= MAX: MIN is NULL).
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
enum Int { Tiny, Small, Int, Big }

impl Int {
    fn range(self) -> (i128, i128) {
        match self {
            Int::Tiny => (i8::MIN as i128 + 1, i8::MAX as i128),
            Int::Small => (i16::MIN as i128 + 1, i16::MAX as i128),
            Int::Int => (i32::MIN as i128 + 1, i32::MAX as i128),
            Int::Big => (i64::MIN as i128 + 1, i64::MAX as i128),
        }
    }
}

fn add(a: (i64, Int), b: (i64, Int)) -> Result<(i64, Int), &'static str> {
    let result_type = a.1.max(b.1);                          // the wider type
    let exact = a.0 as i128 + b.0 as i128;
    let (lo, hi) = result_type.range();
    if exact < lo || exact > hi { return Err("Numeric value out of range."); }
    Ok((exact as i64, result_type))
}

#[test]
fn the_result_type_decides_whether_it_fits() {
    assert_eq!(add((100, Int::Tiny), (100, Int::Tiny)), Err("Numeric value out of range."));
    assert_eq!(add((100, Int::Tiny), (100, Int::Int)), Ok((200, Int::Int)), "the same numbers fit in the wider result type");
    assert_eq!(add((i32::MAX as i64, Int::Int), (1, Int::Int)), Err("Numeric value out of range."));
    assert_eq!(add((i32::MAX as i64, Int::Int), (1, Int::Big)), Ok((i32::MAX as i64 + 1, Int::Big)));
    assert_eq!(add((i32::MIN as i64 + 1, Int::Int), (-1, Int::Int)), Err("Numeric value out of range."), "MIN is the NULL encoding: not a value");
    assert_eq!(add((i64::MAX, Int::Big), (1, Int::Big)), Err("Numeric value out of range."), "i128 makes even bigint + bigint exact");
}
```

### In the exercises

- **3a-03:** `cast_integer` is the range check against `[MIN + 1, MAX]`; `cast_decimal` bounds in `f64`.
- **3a-05:** `arithmetic` computes in `i128` and calls `cast_integer` with the *result* type; `checked_*` is the std alternative when you stay in one width.
- **Module 3b:** aggregation `SUM` overflows the same way and is the same error.

### Where it is used

- **Databases**: PostgreSQL's `int4pl` uses `pg_add_s32_overflow` and raises "integer out of range"; SQLite promotes to a float on overflow instead; MySQL errors or wraps depending on SQL mode.
- **Rust itself**: slice indexing and `Vec::with_capacity` use `checked_mul` for sizes (a request for `usize::MAX` elements is an error, not a tiny allocation); `Duration` and `Instant` arithmetic have checked versions.
- **Security**: integer overflow in a length computation is the root cause of countless buffer overflows; `checked_*` and `try_from` are how Rust code avoids them.
