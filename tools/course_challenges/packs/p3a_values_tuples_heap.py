from _c import C
M3A, M3B, M3C = "12-values-and-types", "13-schemas-tuples-and-table-pages", "14-table-heap-and-catalog"
CH = []

CH.append(C("3a-c1", M3A, "90-challenge-decimal-arithmetic", "build", "Challenge: decimal arithmetic", "medium", "stages_3a::s3a_c1",
  ["fixed-point arithmetic on integers with explicit rounding","parsing and printing exact decimals"],
  ["overflow-and-checked-arithmetic","integers-and-casts","parsing-numbers-from-text"],
  "`Decimal` in `src/types/decimal.rs`: an exact decimal number with **two** fractional digits (money), stored as a count of hundredths. `parse`, `Display`, checked `add`/`sub`, and `mul`/`div` that round **half away from zero** to two places.",
  "Floating point cannot hold 0.10 exactly, which is why databases have `DECIMAL`. The type is small, and every detail is a decision a database must make once and apply everywhere: how many digits are accepted, what rounds which way, what happens on overflow and on division by zero.",
  ["`Decimal::parse(s)`: optional `+`/`-`, digits, optionally `.` and **one or two** digits; no exponent, no spaces. Anything else is `None`. `-0.00` is zero.","`Display` prints `[-]int.dd` with exactly two digits.","`add`, `sub` return `None` on `i128` overflow; `mul` is `a * b / 100` and `div` is `a * 100 / b`, both rounded half away from zero; `div` by zero is `None`."],
  ["`from_cents(c).cents() == c`.","`parse(&d.to_string()) == Some(d)` for every value.","Zero has a single representation."],
  ["`add` and `mul` are commutative; `a + b - b == a` when nothing overflows.","`mul` by 1.00 and `div` by 1.00 are the identity.","Negating the inputs of `mul` or `div` negates (never changes the magnitude of) the rounded result."],
  ["\"12.5\" -> 12.50","\"0.1\" + \"0.2\" -> 0.30","1.25 * 1.25 -> 1.56 (1.5625 rounds up)","-1.25 * 1.25 -> -1.56","1.00 / 3.00 -> 0.33; 2.00 / 3.00 -> 0.67","\"1.234\" -> None"],
  ["Parsing and printing.","Add, sub and overflow.","Rounding of mul and div, including negatives and exact halves.","A property against `i128` arithmetic."],
  src=("src/types/decimal.rs", '''
//! An exact decimal with two fractional digits, stored as hundredths.

use std::fmt;

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub struct Decimal {
    cents: i128,
}

/// `n / d` rounded half away from zero (`d != 0`).
fn div_round(n: i128, d: i128) -> i128 {
    let (q, r) = (n / d, n % d);
    if r.abs() * 2 >= d.abs() {
        q + if (n < 0) != (d < 0) { -1 } else { 1 }
    } else {
        q
    }
}

impl Decimal {
    pub fn from_cents(cents: i128) -> Decimal {
        Decimal { cents }
    }

    pub fn cents(&self) -> i128 {
        self.cents
    }

    /// `[+-]digits[.d[d]]`, nothing else.
    pub fn parse(s: &str) -> Option<Decimal> {
        // @begin 3a-c1
        let (neg, body) = match s.as_bytes().first()? {
            b'-' => (true, &s[1..]),
            b'+' => (false, &s[1..]),
            _ => (false, s),
        };
        let (int, frac) = match body.split_once('.') {
            Some((i, f)) => (i, f),
            None => (body, ""),
        };
        if int.is_empty() || !int.bytes().all(|b| b.is_ascii_digit()) || frac.len() > 2 || !frac.bytes().all(|b| b.is_ascii_digit()) {
            return None;
        }
        if body.contains('.') && frac.is_empty() {
            return None;
        }
        let mut cents = int.parse::<i128>().ok()?.checked_mul(100)?;
        let f: i128 = if frac.is_empty() { 0 } else { frac.parse::<i128>().ok()? * if frac.len() == 1 { 10 } else { 1 } };
        cents = cents.checked_add(f)?;
        Some(Decimal { cents: if neg { -cents } else { cents } })
        //~ todo!("3a-c1: sign, digits, at most two fractional digits")
        // @end
    }

    pub fn add(self, other: Decimal) -> Option<Decimal> {
        // @begin 3a-c1
        self.cents.checked_add(other.cents).map(Decimal::from_cents)
        //~ todo!("3a-c1: checked addition of hundredths")
        // @end
    }

    pub fn sub(self, other: Decimal) -> Option<Decimal> {
        // @begin 3a-c1
        self.cents.checked_sub(other.cents).map(Decimal::from_cents)
        //~ todo!("3a-c1: checked subtraction")
        // @end
    }

    pub fn mul(self, other: Decimal) -> Option<Decimal> {
        // @begin 3a-c1
        let p = self.cents.checked_mul(other.cents)?;
        Some(Decimal::from_cents(div_round(p, 100)))
        //~ todo!("3a-c1: multiply, then scale back by 100 rounding half away from zero")
        // @end
    }

    pub fn div(self, other: Decimal) -> Option<Decimal> {
        // @begin 3a-c1
        if other.cents == 0 {
            return None;
        }
        let n = self.cents.checked_mul(100)?;
        Some(Decimal::from_cents(div_round(n, other.cents)))
        //~ todo!("3a-c1: scale up by 100, divide, rounding half away from zero; zero is None")
        // @end
    }
}

impl fmt::Display for Decimal {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        // @begin 3a-c1
        let a = self.cents.unsigned_abs();
        write!(f, "{}{}.{:02}", if self.cents < 0 { "-" } else { "" }, a / 100, a % 100)
        //~ todo!("3a-c1: [-]int.dd")
        // @end
    }
}
'''),
  test=("tests/stages_3a.rs", '''
use bustub::types::decimal::Decimal;

fn d(s: &str) -> Decimal {
    Decimal::parse(s).unwrap_or_else(|| panic!("{s:?} should parse"))
}

#[test]
fn s3a_c1_parsing_and_printing() {
    assert_eq!(d("12.5").to_string(), "12.50");
    assert_eq!(d("-0.07").to_string(), "-0.07");
    assert_eq!(d("+3").to_string(), "3.00");
    assert_eq!(d("-0.00").to_string(), "0.00");
    assert_eq!(d("-0.00"), d("0"));
}

#[test]
fn s3a_c1_what_is_not_a_decimal() {
    for s in ["", "-", "1.234", "1.", ".5", "1e3", " 1", "1 ", "1.2.3", "--1", "0x10"] {
        assert_eq!(Decimal::parse(s), None, "{s:?}");
    }
}

#[test]
fn s3a_c1_addition_is_exact_where_floats_are_not() {
    assert_eq!(d("0.1").add(d("0.2")).unwrap(), d("0.30"));
    assert_eq!(d("10").sub(d("0.01")).unwrap().to_string(), "9.99");
    assert_eq!(Decimal::from_cents(i128::MAX).add(d("0.01")), None);
    assert_eq!(Decimal::from_cents(i128::MIN).sub(d("0.01")), None);
}

#[test]
fn s3a_c1_multiplication_rounds_half_away_from_zero() {
    assert_eq!(d("1.25").mul(d("1.25")).unwrap().to_string(), "1.56");
    assert_eq!(d("-1.25").mul(d("1.25")).unwrap().to_string(), "-1.56");
    assert_eq!(d("0.05").mul(d("0.10")).unwrap().to_string(), "0.01", "0.005 rounds to 0.01");
    assert_eq!(d("0.04").mul(d("0.10")).unwrap().to_string(), "0.00");
}

#[test]
fn s3a_c1_division_rounds_and_refuses_zero() {
    assert_eq!(d("1").div(d("3")).unwrap().to_string(), "0.33");
    assert_eq!(d("2").div(d("3")).unwrap().to_string(), "0.67");
    assert_eq!(d("-2").div(d("3")).unwrap().to_string(), "-0.67");
    assert_eq!(d("1").div(d("0")), None);
    assert_eq!(d("5").div(d("2")).unwrap().to_string(), "2.50");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against `i128` arithmetic on hundredths, and printing then parsing is the identity.
    #[test]
    fn s3a_c1_property_decimals_match_integer_arithmetic(a in -100_000i128..100_000, b in -100_000i128..100_000) {
        let (x, y) = (Decimal::from_cents(a), Decimal::from_cents(b));
        prop_assert_eq!(Decimal::parse(&x.to_string()), Some(x));
        prop_assert_eq!(x.add(y).unwrap().cents(), a + b);
        prop_assert_eq!(x.sub(y).unwrap().cents(), a - b);
        let rnd = |n: i128, dd: i128| { let q = n / dd; let r = n % dd; if r.abs() * 2 >= dd.abs() { q + if (n < 0) != (dd < 0) { -1 } else { 1 } } else { q } };
        prop_assert_eq!(x.mul(y).unwrap().cents(), rnd(a * b, 100));
        if b != 0 { prop_assert_eq!(x.div(y).unwrap().cents(), rnd(a * 100, b)); } else { prop_assert_eq!(x.div(y), None); }
        prop_assert_eq!(x.add(y), y.add(x));
        prop_assert_eq!(x.mul(y), y.mul(x));
        prop_assert_eq!(x.mul(Decimal::from_cents(100)), Some(x));
    }
}
''')))

CH.append(C("3a-c2", M3A, "91-challenge-nulls-first-or-last", "build", "Challenge: NULLS FIRST or LAST", "easy", "stages_3a::s3a_c2",
  ["ordering values that may be NULL in either direction with NULLs placed independently","a comparator that is a total preorder"],
  ["sort-keys-and-null-ordering","sql-types-and-three-valued-logic"],
  "`cmp_nullable` in `src/types/null_order.rs`: compare two values that may be NULL, for one sort key, with a direction (`Asc`/`Desc`) and a NULL placement (`First`/`Last`). The NULL placement is **independent of the direction**: `ORDER BY x DESC NULLS FIRST` puts NULLs first and the non-NULL values in descending order after them.",
  "`ORDER BY` is in every report and every pagination query, and NULL handling is where databases differ (and where bugs in ports come from). The two options are orthogonal, and the comparator must be a consistent total preorder or a sort will misbehave or panic.",
  ["`cmp_nullable(a, b, dir, nulls)` returns an `Ordering` meaning \"`a` sorts before / equal / after `b`\".","Two NULLs are equal. NULL against a value is decided by `nulls` alone.","Two values compare by `dir`."],
  ["It is a total preorder: reflexive, transitive, and `cmp(a, b) == cmp(b, a).reverse()`.","Sorting with it never panics and is stable for equal keys."],
  ["Flipping `dir` reverses the order of the non-NULL values and leaves the NULLs where they were.","Flipping `nulls` moves all NULLs to the other end and leaves the non-NULL order alone.","`Asc/Last` equals `Option`'s natural order with `None` last."],
  ["[3, NULL, 1] ASC NULLS LAST -> 1, 3, NULL","[3, NULL, 1] DESC NULLS FIRST -> NULL, 3, 1","[3, NULL, 1] ASC NULLS FIRST -> NULL, 1, 3"],
  ["The four combinations on a small list.","Equal NULLs; stability.","Properties: antisymmetry, transitivity, and the effect of flipping each option."],
  src=("src/types/null_order.rs", '''
//! Ordering values that may be NULL.

use std::cmp::Ordering;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Dir {
    Asc,
    Desc,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Nulls {
    First,
    Last,
}

/// Compares two nullable integers for one sort key.
pub fn cmp_nullable(a: Option<i64>, b: Option<i64>, dir: Dir, nulls: Nulls) -> Ordering {
    // @begin 3a-c2
    match (a, b) {
        (None, None) => Ordering::Equal,
        (None, Some(_)) => if nulls == Nulls::First { Ordering::Less } else { Ordering::Greater },
        (Some(_), None) => if nulls == Nulls::First { Ordering::Greater } else { Ordering::Less },
        (Some(x), Some(y)) => if dir == Dir::Asc { x.cmp(&y) } else { y.cmp(&x) },
    }
    //~ todo!("3a-c2: NULLs by placement, values by direction")
    // @end
}
'''),
  test=("tests/stages_3a.rs", '''
use bustub::types::null_order::{cmp_nullable, Dir, Nulls};

fn sorted(v: &[Option<i64>], dir: Dir, nulls: Nulls) -> Vec<Option<i64>> {
    let mut v = v.to_vec();
    v.sort_by(|a, b| cmp_nullable(*a, *b, dir, nulls));
    v
}

const ROWS: [Option<i64>; 3] = [Some(3), None, Some(1)];

#[test]
fn s3a_c2_ascending_nulls_last() {
    assert_eq!(sorted(&ROWS, Dir::Asc, Nulls::Last), vec![Some(1), Some(3), None]);
}

#[test]
fn s3a_c2_descending_nulls_first_puts_nulls_first_and_values_downwards() {
    assert_eq!(sorted(&ROWS, Dir::Desc, Nulls::First), vec![None, Some(3), Some(1)]);
}

#[test]
fn s3a_c2_the_placement_is_independent_of_the_direction() {
    assert_eq!(sorted(&ROWS, Dir::Asc, Nulls::First), vec![None, Some(1), Some(3)]);
    assert_eq!(sorted(&ROWS, Dir::Desc, Nulls::Last), vec![Some(3), Some(1), None]);
}

#[test]
fn s3a_c2_two_nulls_are_equal_and_sorting_is_stable() {
    use std::cmp::Ordering::Equal;
    assert_eq!(cmp_nullable(None, None, Dir::Desc, Nulls::First), Equal);
    let mut tagged = vec![(None, 'a'), (Some(1), 'b'), (None, 'c'), (Some(1), 'd')];
    tagged.sort_by(|x, y| cmp_nullable(x.0, y.0, Dir::Asc, Nulls::Last));
    assert_eq!(tagged.iter().map(|t| t.1).collect::<String>(), "bdac");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: a total preorder whose NULL placement ignores the direction and whose value order flips with it.
    #[test]
    fn s3a_c2_property_a_total_preorder_with_independent_options(a in proptest::option::of(-3i64..3), b in proptest::option::of(-3i64..3), c in proptest::option::of(-3i64..3)) {
        for dir in [Dir::Asc, Dir::Desc] {
            for nulls in [Nulls::First, Nulls::Last] {
                let f = |x, y| cmp_nullable(x, y, dir, nulls);
                prop_assert_eq!(f(a, b), f(b, a).reverse());
                prop_assert_eq!(f(a, a), std::cmp::Ordering::Equal);
                if f(a, b).is_le() && f(b, c).is_le() { prop_assert!(f(a, c).is_le()); }
            }
        }
        for nulls in [Nulls::First, Nulls::Last] {
            let asc = cmp_nullable(a, b, Dir::Asc, nulls);
            let desc = cmp_nullable(a, b, Dir::Desc, nulls);
            if a.is_some() && b.is_some() { prop_assert_eq!(desc, asc.reverse()); } else { prop_assert_eq!(desc, asc); }
        }
    }
}
''')))

CH.append(C("3a-c3", M3A, "92-challenge-strict-integer-parsing", "build", "Challenge: strict integer parsing", "easy", "stages_3a::s3a_c3",
  ["parsing text into an integer with every failure named","detecting overflow without parsing into a wider type"],
  ["parsing-numbers-from-text","overflow-and-checked-arithmetic","errors-as-values-with-result"],
  "`parse_sql_int` in `src/types/int_parse.rs`: turn text into an `i64` the way a `CAST('...' AS BIGINT)` should: surrounding ASCII whitespace is ignored, an optional `+` or `-`, then one or more decimal digits and nothing else. Every other input is an error that says which kind.",
  "`str::parse::<i64>` is close, but a database must decide the edges on purpose: is `\" 7 \"` a number, is `\"+5\"`, is `\"1_000\"`, is `\"9223372036854775808\"`? Casts run on user data, so every one of these happens, and the error kind decides whether the query fails or the row is skipped.",
  ["`Ok(value)` for `[ws][+-]digits[ws]` that fits in `i64` (including `-9223372036854775808`).","`Err(Empty)` for an empty or all-whitespace string, `Err(Invalid)` for anything with another character (a sign alone, `1_0`, `0x1`, `1.0`, internal spaces), `Err(OutOfRange)` for valid digits that do not fit."],
  ["Every `i64` printed with `to_string()` parses back to itself.","The function never panics."],
  ["Adding surrounding whitespace never changes the result.","`parse(\"+\" + digits) == parse(digits)` for non-negative values.","A value that does not fit is `OutOfRange`, never a wrapped number."],
  ["\"  42 \" -> 42","\"-9223372036854775808\" -> MIN","\"9223372036854775808\" -> OutOfRange","\"4 2\" -> Invalid","\"+\" -> Invalid","\"\" -> Empty"],
  ["Each kind of input.","The edges of `i64`.","A property against `str::parse` on well-formed input and against 128-bit arithmetic."],
  src=("src/types/int_parse.rs", '''
//! Strict text to integer conversion.

#[derive(Debug, PartialEq, Eq)]
pub enum IntError {
    Empty,
    Invalid,
    OutOfRange,
}

pub fn parse_sql_int(s: &str) -> Result<i64, IntError> {
    // @begin 3a-c3
    let t = s.trim_matches(|c: char| c.is_ascii_whitespace());
    if t.is_empty() {
        return Err(IntError::Empty);
    }
    let (neg, digits) = match t.as_bytes()[0] {
        b'-' => (true, &t[1..]),
        b'+' => (false, &t[1..]),
        _ => (false, t),
    };
    if digits.is_empty() || !digits.bytes().all(|b| b.is_ascii_digit()) {
        return Err(IntError::Invalid);
    }
    let mut acc: i64 = 0;
    for b in digits.bytes() {
        let d = (b - b'0') as i64;
        acc = acc.checked_mul(10).and_then(|a| if neg { a.checked_sub(d) } else { a.checked_add(d) }).ok_or(IntError::OutOfRange)?;
    }
    Ok(acc)
    //~ todo!("3a-c3: trim, sign, digits, checked accumulation")
    // @end
}
'''),
  test=("tests/stages_3a.rs", '''
use bustub::types::int_parse::{parse_sql_int, IntError};

#[test]
fn s3a_c3_numbers_with_surrounding_whitespace_and_signs() {
    assert_eq!(parse_sql_int("  42 "), Ok(42));
    assert_eq!(parse_sql_int("+5"), Ok(5));
    assert_eq!(parse_sql_int("-0"), Ok(0));
    assert_eq!(parse_sql_int("\\t-17\\n"), Ok(-17));
    assert_eq!(parse_sql_int("007"), Ok(7));
}

#[test]
fn s3a_c3_the_edges_of_i64() {
    assert_eq!(parse_sql_int("9223372036854775807"), Ok(i64::MAX));
    assert_eq!(parse_sql_int("-9223372036854775808"), Ok(i64::MIN));
    assert_eq!(parse_sql_int("9223372036854775808"), Err(IntError::OutOfRange));
    assert_eq!(parse_sql_int("-9223372036854775809"), Err(IntError::OutOfRange));
    assert_eq!(parse_sql_int("99999999999999999999999999"), Err(IntError::OutOfRange));
}

#[test]
fn s3a_c3_empty_and_invalid_are_different_errors() {
    assert_eq!(parse_sql_int(""), Err(IntError::Empty));
    assert_eq!(parse_sql_int("   "), Err(IntError::Empty));
    for s in ["+", "-", "4 2", "1_0", "0x1", "1.0", "1e3", "--1", "+-1", "12a", "\\u{0663}"] {
        assert_eq!(parse_sql_int(s), Err(IntError::Invalid), "{s:?}");
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: every printed `i64` parses back, whitespace changes nothing, and everything else agrees with 128-bit parsing.
    #[test]
    fn s3a_c3_property_round_trip_and_range(v in any::<i64>(), w in 0usize..3, digits in "[0-9]{1,24}", neg in any::<bool>()) {
        prop_assert_eq!(parse_sql_int(&v.to_string()), Ok(v));
        let padded = format!("{}{}{}", " ".repeat(w), v, "\\t".repeat(w));
        prop_assert_eq!(parse_sql_int(&padded), Ok(v));
        let text = format!("{}{}", if neg { "-" } else { "" }, digits);
        let wide: i128 = text.parse().unwrap_or(i128::MAX);
        let want = if wide >= i64::MIN as i128 && wide <= i64::MAX as i128 && digits.len() < 38 { Ok(wide as i64) } else { Err(IntError::OutOfRange) };
        prop_assert_eq!(parse_sql_int(&text), want);
    }

    /// Property: never panics on any string.
    #[test]
    fn s3a_c3_property_never_panics(s in ".{0,12}") {
        let _ = parse_sql_int(&s);
    }
}
''')))

CH.append(C("3a-c4", M3A, "93-challenge-the-division-that-panics", "debug", "Challenge: the division that panics", "easy", "stages_3a::s3a_c4",
  ["finding the one integer division that overflows","turning a panic on user data into an error"],
  ["overflow-and-checked-arithmetic","integers-and-casts","property-testing-and-fuzzing"],
  "`src/types/int_ops.rs` has the checked integer operations of a SQL engine: they return an error instead of wrapping or panicking. One of them still panics on a value a user can send. Find it with the tests and fix it.",
  "A query engine must never crash on data: `SELECT -2147483648 / -1` is a legal statement, and the only integer division that overflows is exactly that one. Rust panics in debug builds and wraps in release, both wrong for a database. The fix is a single method, and finding which one is the exercise.",
  ["`checked_add_i32`, `checked_neg_i32`, `checked_abs_i32`, `checked_div_i32` return `Ok(result)` or `Err(IntOpError::Overflow)`, and `Err(IntOpError::DivisionByZero)` for a zero divisor.","No operation ever panics, whatever the arguments."],
  ["A result that is `Ok` is the mathematical result.","Overflow is reported exactly when the mathematical result does not fit in `i32`."],
  ["`neg(neg(x)) == x` whenever the first negation succeeds.","`abs(x) >= 0` whenever it succeeds.","`div(a, b) * b + (a % b) == a` whenever `b != 0` and the division succeeds."],
  ["div(MIN, -1) -> Overflow","div(5, 0) -> DivisionByZero","abs(MIN) -> Overflow","div(-7, 2) -> -3"],
  ["Ordinary values.","Every extreme: `i32::MIN` and `i32::MAX` with `0`, `1` and `-1`.","A property against 64-bit arithmetic."],
  src=("src/types/int_ops.rs", '''
//! Integer operations that report overflow and division by zero as errors.

#[derive(Debug, PartialEq, Eq)]
pub enum IntOpError {
    Overflow,
    DivisionByZero,
}

pub fn checked_add_i32(a: i32, b: i32) -> Result<i32, IntOpError> {
    a.checked_add(b).ok_or(IntOpError::Overflow)
}

pub fn checked_neg_i32(a: i32) -> Result<i32, IntOpError> {
    a.checked_neg().ok_or(IntOpError::Overflow)
}

pub fn checked_abs_i32(a: i32) -> Result<i32, IntOpError> {
    a.checked_abs().ok_or(IntOpError::Overflow)
}

pub fn checked_div_i32(a: i32, b: i32) -> Result<i32, IntOpError> {
    if b == 0 {
        return Err(IntOpError::DivisionByZero);
    }
    // @begin 3a-c4
    a.checked_div(b).ok_or(IntOpError::Overflow)
    //~ Ok(a / b)
    // @end
}
'''),
  test=("tests/stages_3a.rs", '''
use bustub::types::int_ops::{checked_abs_i32, checked_add_i32, checked_div_i32, checked_neg_i32, IntOpError};

#[test]
fn s3a_c4_ordinary_values() {
    assert_eq!(checked_add_i32(2, 3), Ok(5));
    assert_eq!(checked_neg_i32(7), Ok(-7));
    assert_eq!(checked_abs_i32(-7), Ok(7));
    assert_eq!(checked_div_i32(-7, 2), Ok(-3), "truncation towards zero, as SQL does");
}

#[test]
fn s3a_c4_division_by_zero_is_an_error() {
    assert_eq!(checked_div_i32(5, 0), Err(IntOpError::DivisionByZero));
    assert_eq!(checked_div_i32(i32::MIN, 0), Err(IntOpError::DivisionByZero));
}

#[test]
fn s3a_c4_the_one_division_that_overflows_is_an_error_not_a_panic() {
    assert_eq!(checked_div_i32(i32::MIN, -1), Err(IntOpError::Overflow));
    assert_eq!(checked_div_i32(i32::MIN, 1), Ok(i32::MIN));
    assert_eq!(checked_div_i32(i32::MAX, -1), Ok(-i32::MAX));
}

#[test]
fn s3a_c4_the_other_extremes() {
    assert_eq!(checked_abs_i32(i32::MIN), Err(IntOpError::Overflow));
    assert_eq!(checked_neg_i32(i32::MIN), Err(IntOpError::Overflow));
    assert_eq!(checked_add_i32(i32::MAX, 1), Err(IntOpError::Overflow));
    assert_eq!(checked_add_i32(i32::MIN, -1), Err(IntOpError::Overflow));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: never panics, and agrees with 64-bit arithmetic, over values that include the extremes.
    #[test]
    fn s3a_c4_property_agrees_with_64_bit_arithmetic(a in prop_oneof![any::<i32>(), Just(i32::MIN), Just(i32::MAX), Just(0), Just(-1), Just(1)], b in prop_oneof![any::<i32>(), Just(i32::MIN), Just(i32::MAX), Just(0), Just(-1), Just(1)]) {
        let fit = |x: i64| i32::try_from(x).map_err(|_| IntOpError::Overflow);
        prop_assert_eq!(checked_add_i32(a, b), fit(a as i64 + b as i64));
        prop_assert_eq!(checked_neg_i32(a), fit(-(a as i64)));
        prop_assert_eq!(checked_abs_i32(a), fit((a as i64).abs()));
        let want = if b == 0 { Err(IntOpError::DivisionByZero) } else { fit(a as i64 / b as i64) };
        prop_assert_eq!(checked_div_i32(a, b), want);
    }
}
''')))

CH.append(C("3a-c5", M3A, "94-challenge-like", "build", "Challenge: LIKE", "medium", "stages_3a::s3a_c5",
  ["matching a pattern with wildcards without exponential backtracking","an escape character and its error case"],
  ["parsing-numbers-from-text","property-testing-and-fuzzing"],
  "`like` in `src/types/like_match.rs`: SQL's `text LIKE pattern`. `%` matches any run of characters (including none), `_` matches exactly one character, and an optional **escape** character makes the next pattern character literal. A pattern that ends with the escape is an error.",
  "`LIKE` is in nearly every report query, and a naive recursive matcher takes exponential time on `%a%a%a%a%b` against a long string of `a`s: a denial of service sent as a search term. A two-pointer matcher with one backtrack point is linear in the common case and polynomial always.",
  ["Characters are Unicode scalar values (`_` matches one `char`, not one byte).","`like(text, pattern, escape)` is `Ok(true/false)`, or `Err(TrailingEscape)` when the pattern ends with an unescaped escape character.","Matching is over the whole text, case-sensitive."],
  ["The result does not depend on how the pattern is written when the meaning is the same (`%%` is `%`).","A pattern with no wildcards matches only itself."],
  ["`text LIKE '%'` is true for every text.","`text LIKE text` (with wildcards in `text` escaped) is true.","Replacing a `%` by any substring of the text keeps a match a match.","Linear time on `%a%a%a...%b` against a long run of `a`."],
  ["'hello' LIKE 'h%o' -> true","'hello' LIKE 'h_llo' -> true","'100%' LIKE '100\\\\%' ESCAPE '\\\\' -> true","'ab' LIKE 'a\\\\' ESCAPE '\\\\' -> error"],
  ["Wildcards, literals, escapes and the error.","Unicode text.","A 20 000-character adversarial case finishes quickly.","A property against a brute-force recursive matcher."],
  src=("src/types/like_match.rs", '''
//! SQL `LIKE`.

#[derive(Debug, PartialEq, Eq)]
pub enum LikeError {
    TrailingEscape,
}

/// Does `text` match `pattern`? `escape`, when given, makes the following pattern character literal.
pub fn like(text: &str, pattern: &str, escape: Option<char>) -> Result<bool, LikeError> {
    // @begin 3a-c5
    #[derive(Clone, Copy)]
    enum Tok {
        Any,
        One,
        Lit(char),
    }
    let mut toks = Vec::new();
    let mut it = pattern.chars();
    while let Some(c) = it.next() {
        if Some(c) == escape {
            toks.push(Tok::Lit(it.next().ok_or(LikeError::TrailingEscape)?));
        } else if c == '%' {
            if !matches!(toks.last(), Some(Tok::Any)) {
                toks.push(Tok::Any);
            }
        } else if c == '_' {
            toks.push(Tok::One);
        } else {
            toks.push(Tok::Lit(c));
        }
    }
    let t: Vec<char> = text.chars().collect();
    let (mut ti, mut pi) = (0, 0);
    let mut star: Option<(usize, usize)> = None; // (pattern index after the %, text index it has absorbed up to)
    while ti < t.len() {
        match toks.get(pi) {
            Some(Tok::Any) => {
                star = Some((pi + 1, ti));
                pi += 1;
            }
            Some(Tok::One) => {
                ti += 1;
                pi += 1;
            }
            Some(Tok::Lit(c)) if *c == t[ti] => {
                ti += 1;
                pi += 1;
            }
            _ => match star {
                Some((p, s)) => {
                    star = Some((p, s + 1));
                    pi = p;
                    ti = s + 1;
                }
                None => return Ok(false),
            },
        }
    }
    while matches!(toks.get(pi), Some(Tok::Any)) {
        pi += 1;
    }
    Ok(pi == toks.len())
    //~ todo!("3a-c5: tokenise the pattern, then match with one backtrack point for the latest %")
    // @end
}
'''),
  test=("tests/stages_3a.rs", '''
use bustub::types::like_match::{like, LikeError};

#[test]
fn s3a_c5_wildcards_and_literals() {
    assert_eq!(like("hello", "h%o", None), Ok(true));
    assert_eq!(like("hello", "h_llo", None), Ok(true));
    assert_eq!(like("hello", "h_lo", None), Ok(false));
    assert_eq!(like("hello", "%", None), Ok(true));
    assert_eq!(like("", "%", None), Ok(true));
    assert_eq!(like("", "_", None), Ok(false));
    assert_eq!(like("hello", "HELLO", None), Ok(false), "case-sensitive");
    assert_eq!(like("hello", "hell", None), Ok(false), "the whole text must match");
}

#[test]
fn s3a_c5_the_escape_character_makes_the_next_character_literal() {
    assert_eq!(like("100%", "100\\\\%", Some('\\\\')), Ok(true));
    assert_eq!(like("1000", "100\\\\%", Some('\\\\')), Ok(false));
    assert_eq!(like("a_b", "a\\\\_b", Some('\\\\')), Ok(true));
    assert_eq!(like("axb", "a\\\\_b", Some('\\\\')), Ok(false));
    assert_eq!(like("a\\\\b", "a\\\\\\\\b", Some('\\\\')), Ok(true), "an escaped escape is a literal escape");
}

#[test]
fn s3a_c5_a_trailing_escape_is_an_error() {
    assert_eq!(like("ab", "a\\\\", Some('\\\\')), Err(LikeError::TrailingEscape));
    assert_eq!(like("a\\\\", "a\\\\", None), Ok(true), "without an escape character it is just a character");
}

#[test]
fn s3a_c5_unicode_characters_count_as_one() {
    assert_eq!(like("héllo", "h_llo", None), Ok(true));
    assert_eq!(like("日本語", "___", None), Ok(true));
    assert_eq!(like("日本語", "__", None), Ok(false));
}

#[test]
fn s3a_c5_an_adversarial_pattern_finishes_quickly() {
    let text = "a".repeat(20_000);
    let pat = format!("{}b", "%a".repeat(12));
    let t = std::time::Instant::now();
    assert_eq!(like(&text, &pat, None), Ok(false));
    assert!(t.elapsed() < std::time::Duration::from_secs(3), "took {:?}: a recursive matcher is exponential here", t.elapsed());
}

fn brute(t: &[char], p: &[char]) -> bool {
    match p.split_first() {
        None => t.is_empty(),
        Some((&'%', rest)) => (0..=t.len()).any(|i| brute(&t[i..], rest)),
        Some((&'_', rest)) => !t.is_empty() && brute(&t[1..], rest),
        Some((c, rest)) => t.first() == Some(c) && brute(&t[1..], rest),
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 512, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against a brute-force recursive matcher on short strings over a small alphabet.
    #[test]
    fn s3a_c5_property_matches_a_brute_force_matcher(text in "[ab]{0,8}", pattern in "[ab%_]{0,7}") {
        let t: Vec<char> = text.chars().collect();
        let p: Vec<char> = pattern.chars().collect();
        prop_assert_eq!(like(&text, &pattern, None), Ok(brute(&t, &p)), "{:?} LIKE {:?}", text, pattern);
    }
}
''')))

CH.append(C("3b-c1", M3B, "90-challenge-a-row-with-a-null-bitmap", "build", "Challenge: a row with a null bitmap", "medium", "stages_3b::s3b_c1",
  ["a row format whose size depends on which columns are NULL","decoding bytes against a schema without trusting them"],
  ["structs-and-accessors","bytes-endianness-and-views","errors-as-values-with-result"],
  "`encode_row` and `decode_row` in `src/storage/table/null_row.rs`: a row of `Option<Cell>` (each cell an `Int(i64)` or a `Text(String)`) as bytes. A **null bitmap** (one bit per column, rounded up to whole bytes) comes first; then, for each column that is **not** NULL, its value: 8 little-endian bytes for an `Int`, a 4-byte little-endian length and the UTF-8 bytes for a `Text`.",
  "A row with many NULLs should cost almost nothing, and that is how every serious row format works (PostgreSQL's heap tuples, SQLite records, InnoDB's compact format). The decoder is the delicate half: it reads a length from disk and must not trust it.",
  ["`encode_row(row)` writes the bitmap (bit `i` set = column `i` is NULL, least significant bit first) then the non-NULL values in column order.","`decode_row(bytes, types)` takes the schema (`Ty::Int` or `Ty::Text` per column) and returns the row, or `None` if the bytes are not exactly one row of that schema (truncated, a text that is not UTF-8, trailing bytes, a NULL in a column the schema says is present... any inconsistency)."],
  ["`encoded_len == ceil(columns / 8) + sum(8 for each non-NULL Int, 4 + len for each non-NULL Text)`.","`decode_row(encode_row(r), types_of(r)) == Some(r)`.","`decode_row` never panics on any bytes."],
  ["Setting a column to NULL never makes the row longer.","Two rows that differ only in a NULL column's former value encode alike.","Any strict prefix of an encoded row is rejected."],
  ["[Int(1), NULL, Text(\"ab\")] -> [0b010, 1,0,0,0,0,0,0,0, 2,0,0,0, a, b]","[NULL, NULL] -> [0b11]"],
  ["Exact bytes for a mixed row.","Round trips; the size formula; many columns (bitmaps over 8 columns).","Malformed input: truncated, bad UTF-8, trailing bytes.","A property over random bytes."],
  src=("src/storage/table/null_row.rs", '''
//! A row of nullable cells with a null bitmap in front.

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum Cell {
    Int(i64),
    Text(String),
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Ty {
    Int,
    Text,
}

pub fn encode_row(row: &[Option<Cell>]) -> Vec<u8> {
    // @begin 3b-c1
    let mut out = vec![0u8; row.len().div_ceil(8)];
    for (i, c) in row.iter().enumerate() {
        if c.is_none() {
            out[i / 8] |= 1 << (i % 8);
        }
    }
    for c in row.iter().flatten() {
        match c {
            Cell::Int(v) => out.extend_from_slice(&v.to_le_bytes()),
            Cell::Text(s) => {
                out.extend_from_slice(&(s.len() as u32).to_le_bytes());
                out.extend_from_slice(s.as_bytes());
            }
        }
    }
    out
    //~ todo!("3b-c1: the bitmap, then each non-NULL value")
    // @end
}

pub fn decode_row(bytes: &[u8], types: &[Ty]) -> Option<Vec<Option<Cell>>> {
    // @begin 3b-c1
    let bm = types.len().div_ceil(8);
    if bytes.len() < bm {
        return None;
    }
    let (bitmap, mut rest) = bytes.split_at(bm);
    let mut row = Vec::with_capacity(types.len());
    for (i, ty) in types.iter().enumerate() {
        if bitmap[i / 8] >> (i % 8) & 1 == 1 {
            row.push(None);
            continue;
        }
        match ty {
            Ty::Int => {
                let (v, r) = rest.split_first_chunk::<8>()?;
                row.push(Some(Cell::Int(i64::from_le_bytes(*v))));
                rest = r;
            }
            Ty::Text => {
                let (len, r) = rest.split_first_chunk::<4>()?;
                let len = u32::from_le_bytes(*len) as usize;
                if r.len() < len {
                    return None;
                }
                let s = std::str::from_utf8(&r[..len]).ok()?;
                row.push(Some(Cell::Text(s.to_owned())));
                rest = &r[len..];
            }
        }
    }
    // bits past the last column must be clear, and nothing may follow
    if rest.is_empty() && (types.len() % 8 == 0 || bitmap[bm - 1] >> (types.len() % 8) == 0) {
        Some(row)
    } else {
        None
    }
    //~ todo!("3b-c1: read the bitmap, then the value of each column that is not NULL; refuse anything inconsistent")
    // @end
}
'''),
  test=("tests/stages_3b.rs", '''
use bustub::storage::table::null_row::{decode_row, encode_row, Cell, Ty};

fn i(v: i64) -> Option<Cell> {
    Some(Cell::Int(v))
}
fn t(s: &str) -> Option<Cell> {
    Some(Cell::Text(s.to_owned()))
}

#[test]
fn s3b_c1_the_exact_bytes_of_a_mixed_row() {
    let bytes = encode_row(&[i(1), None, t("ab")]);
    let mut want = vec![0b010];
    want.extend_from_slice(&1i64.to_le_bytes());
    want.extend_from_slice(&2u32.to_le_bytes());
    want.extend_from_slice(b"ab");
    assert_eq!(bytes, want);
    assert_eq!(encode_row(&[None, None]), vec![0b11]);
}

#[test]
fn s3b_c1_rows_round_trip_including_more_than_eight_columns() {
    let row: Vec<Option<Cell>> = (0..11).map(|n| if n % 3 == 0 { None } else if n % 2 == 0 { t("x") } else { i(n) }).collect();
    let types: Vec<Ty> = row.iter().enumerate().map(|(n, _)| if n % 2 == 0 { Ty::Text } else { Ty::Int }).collect();
    assert_eq!(decode_row(&encode_row(&row), &types), Some(row));
}

#[test]
fn s3b_c1_a_null_costs_one_bit_not_a_value() {
    let full = encode_row(&[i(1), i(2), i(3)]);
    let nulls = encode_row(&[None, None, None]);
    assert_eq!((full.len(), nulls.len()), (1 + 24, 1));
}

#[test]
fn s3b_c1_malformed_bytes_are_rejected() {
    let types = [Ty::Int, Ty::Text];
    let good = encode_row(&[i(7), t("hi")]);
    for cut in 0..good.len() {
        assert_eq!(decode_row(&good[..cut], &types), None, "cut at {cut}");
    }
    let mut trailing = good.clone();
    trailing.push(0);
    assert_eq!(decode_row(&trailing, &types), None);
    let mut bad_utf8 = vec![0u8, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0xFF];
    bad_utf8[9] = 1;
    assert_eq!(decode_row(&bad_utf8, &types), None);
    assert_eq!(decode_row(&[0b100], &types), None, "a bit set past the last column");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: round trip, the size formula, and no panic on arbitrary bytes.
    #[test]
    fn s3b_c1_property_rows_round_trip(cols in proptest::collection::vec(proptest::option::of(prop_oneof![any::<i64>().prop_map(Cell::Int), "[a-z]{0,6}".prop_map(Cell::Text)]), 0..14)) {
        let types: Vec<Ty> = cols.iter().map(|c| match c { Some(Cell::Text(_)) => Ty::Text, _ => Ty::Int }).collect();
        // a NULL column may be either type: use Int for it
        let bytes = encode_row(&cols);
        let want_len = cols.len().div_ceil(8) + cols.iter().flatten().map(|c| match c { Cell::Int(_) => 8, Cell::Text(s) => 4 + s.len() }).sum::<usize>();
        prop_assert_eq!(bytes.len(), want_len);
        prop_assert_eq!(decode_row(&bytes, &types), Some(cols));
    }

    #[test]
    fn s3b_c1_property_arbitrary_bytes_never_panic(bytes in proptest::collection::vec(any::<u8>(), 0..40), types in proptest::collection::vec(prop_oneof![Just(Ty::Int), Just(Ty::Text)], 0..6)) {
        if let Some(row) = decode_row(&bytes, &types) {
            prop_assert_eq!(encode_row(&row), bytes, "accepted bytes must be exactly what encoding the row gives");
        }
    }
}
''')))

CH.append(C("3b-c2", M3B, "91-challenge-struct-layout", "build", "Challenge: struct layout", "medium", "stages_3b::s3b_c2",
  ["computing padding and alignment like a C compiler","finding the field order with the least padding"],
  ["repr-c-layouts-and-const-asserts","shifts-masks-and-bit-tricks"],
  "`layout` and `packed_order` in `src/storage/table/struct_layout.rs`: given fields as `(size, align)` pairs (alignment a power of two, size a multiple of it), `layout` places them **in the given order** as C does (each at the next multiple of its alignment) and reports the offsets, the total size (rounded up to the largest alignment) and that alignment. `packed_order` returns the field order that gives the **smallest** total size.",
  "A header laid out carelessly wastes bytes in every one of millions of records, and a `#[repr(C)]` struct's size is exactly this computation. Rust's own `repr(Rust)` reorders for you; on-disk formats must not, so you do it deliberately and write the rule down.",
  ["`layout(fields)` returns `Layout { offsets, size, align }`: `offsets[i]` is the lowest multiple of `align_i` at or after the end of the previous field; `align` is the maximum field alignment (1 for no fields); `size` is the end of the last field rounded up to `align`.","`packed_order(fields)` returns a permutation of the indexes whose `layout` has the smallest `size` (ties: the lowest indexes first, stable)."],
  ["Every offset is a multiple of its field's alignment.","Fields do not overlap and stay in the given order.","`size` is a multiple of `align`."],
  ["Sorting by descending alignment never gives a larger size than any other order (when each size is a multiple of its alignment).","`size >= sum of field sizes`.","Reordering fields never changes `align` or the sum of field sizes."],
  ["(1,1),(8,8),(2,2) -> offsets [0,8,16], size 24","packed order of the same -> [1,2,0], size 16"],
  ["Padding, trailing padding and an empty struct.","The best order against all permutations for up to six fields.","Properties."],
  src=("src/storage/table/struct_layout.rs", '''
//! The layout of fields in a C-like struct, and the field order that wastes the least.

#[derive(Debug, PartialEq, Eq)]
pub struct Layout {
    pub offsets: Vec<usize>,
    pub size: usize,
    pub align: usize,
}

/// Rounds `n` up to a multiple of `align` (a power of two).
fn round_up(n: usize, align: usize) -> usize {
    n.div_ceil(align) * align
}

/// `fields[i] = (size, align)`.
pub fn layout(fields: &[(usize, usize)]) -> Layout {
    // @begin 3b-c2
    let mut offsets = Vec::with_capacity(fields.len());
    let mut end = 0;
    let mut align = 1;
    for &(size, a) in fields {
        let at = round_up(end, a);
        offsets.push(at);
        end = at + size;
        align = align.max(a);
    }
    Layout { offsets, size: round_up(end, align), align }
    //~ todo!("3b-c2: place each field at the next multiple of its alignment; round the total up")
    // @end
}

/// The order of field indexes that gives the smallest total size.
pub fn packed_order(fields: &[(usize, usize)]) -> Vec<usize> {
    // @begin 3b-c2
    let mut idx: Vec<usize> = (0..fields.len()).collect();
    idx.sort_by(|&a, &b| fields[b].1.cmp(&fields[a].1).then(a.cmp(&b)));
    idx
    //~ todo!("3b-c2: largest alignment first")
    // @end
}
'''),
  test=("tests/stages_3b.rs", '''
use bustub::storage::table::struct_layout::{layout, packed_order, Layout};

#[test]
fn s3b_c2_padding_between_and_after_fields() {
    let l = layout(&[(1, 1), (8, 8), (2, 2)]);
    assert_eq!(l, Layout { offsets: vec![0, 8, 16], size: 24, align: 8 });
}

#[test]
fn s3b_c2_no_fields_and_one_field() {
    assert_eq!(layout(&[]), Layout { offsets: vec![], size: 0, align: 1 });
    assert_eq!(layout(&[(4, 4)]), Layout { offsets: vec![0], size: 4, align: 4 });
}

#[test]
fn s3b_c2_the_packed_order_removes_the_padding() {
    let fields = [(1, 1), (8, 8), (2, 2)];
    let order = packed_order(&fields);
    assert_eq!(order, vec![1, 2, 0]);
    let packed: Vec<_> = order.iter().map(|&i| fields[i]).collect();
    assert_eq!(layout(&packed).size, 16);
}

#[test]
fn s3b_c2_equal_alignments_keep_their_order() {
    assert_eq!(packed_order(&[(4, 4), (4, 4), (4, 4)]), vec![0, 1, 2]);
}

fn permutations(n: usize) -> Vec<Vec<usize>> {
    if n == 0 {
        return vec![vec![]];
    }
    let mut out = Vec::new();
    for p in permutations(n - 1) {
        for at in 0..=p.len() {
            let mut q = p.clone();
            q.insert(at, n - 1);
            out.push(q);
        }
    }
    out
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: layouts are valid, and the packed order is as small as the best of all permutations.
    #[test]
    fn s3b_c2_property_layouts_are_valid_and_the_packed_order_is_minimal(fields in proptest::collection::vec((0u32..4, 1usize..4), 0..6)) {
        let fields: Vec<(usize, usize)> = fields.into_iter().map(|(mult, e)| { let align = 1usize << (e - 1); (align * (mult as usize), align) }).collect();
        let l = layout(&fields);
        for (i, &(size, a)) in fields.iter().enumerate() {
            prop_assert_eq!(l.offsets[i] % a, 0);
            if i > 0 { prop_assert!(l.offsets[i] >= l.offsets[i - 1] + fields[i - 1].0); }
            let _ = size;
        }
        prop_assert_eq!(l.size % l.align, 0);
        prop_assert!(l.size >= fields.iter().map(|f| f.0).sum::<usize>());
        let best = permutations(fields.len()).into_iter().map(|p| layout(&p.iter().map(|&i| fields[i]).collect::<Vec<_>>()).size).min().unwrap();
        let order = packed_order(&fields);
        let mut sorted = order.clone();
        sorted.sort();
        prop_assert_eq!(sorted, (0..fields.len()).collect::<Vec<_>>());
        prop_assert_eq!(layout(&order.iter().map(|&i| fields[i]).collect::<Vec<_>>()).size, best);
    }
}
''')))

CH.append(C("3b-c3", M3B, "92-challenge-the-shifted-column", "debug", "Challenge: the shifted column", "easy", "stages_3b::s3b_c3",
  ["finding an off-by-one in an offsets array","reading the boundaries of variable-length columns"],
  ["slices-copy-within-and-binary-search","property-testing-and-fuzzing"],
  "`src/storage/table/var_row.rs` stores a row of variable-length byte columns as an array of end offsets followed by the data, and `column(bytes, i)` slices out column `i`. It returns the wrong bytes for some columns. Find the bug and fix it.",
  "Offset arrays are how every variable-length format finds a field in constant time, and the slip is always the same: a column's start is the *previous* column's end (and 0 for the first), not its own entry. The error shows as one column holding the tail of another.",
  ["`encode(columns)`: a count byte, then `n` little-endian `u16` end offsets (cumulative, relative to the start of the data), then the concatenated data.","`column(bytes, i)` is the bytes of column `i`, or `None` if `i` is out of range or the bytes are malformed."],
  ["Column `i` starts at the end of column `i - 1` (0 for the first) and ends at its own end offset.","The columns are contiguous and cover the data exactly."],
  ["Concatenating `column(bytes, 0..n)` gives the data section.","`column(encode(cols), i) == cols[i]` for every `i`.","The lengths of the columns add up to the data length."],
  ["[\"ab\", \"\", \"cde\"] -> ends [2, 2, 5]; column 0 = \"ab\", 1 = \"\", 2 = \"cde\""],
  ["Each column of a small row, including empty columns.","Out-of-range index.","A property over random rows."],
  src=("src/storage/table/var_row.rs", '''
//! A row of variable-length columns: end offsets, then the data.

pub fn encode(columns: &[Vec<u8>]) -> Vec<u8> {
    let mut out = vec![columns.len() as u8];
    let mut end = 0u16;
    for c in columns {
        end += c.len() as u16;
        out.extend_from_slice(&end.to_le_bytes());
    }
    for c in columns {
        out.extend_from_slice(c);
    }
    out
}

/// The bytes of column `i`.
pub fn column(bytes: &[u8], i: usize) -> Option<&[u8]> {
    let n = *bytes.first()? as usize;
    if i >= n {
        return None;
    }
    let offsets = bytes.get(1..1 + 2 * n)?;
    let data = bytes.get(1 + 2 * n..)?;
    let end_of = |k: usize| u16::from_le_bytes([offsets[2 * k], offsets[2 * k + 1]]) as usize;
    // @begin 3b-c3
    let start = if i == 0 { 0 } else { end_of(i - 1) };
    //~ let start = end_of(i);
    // @end
    data.get(start..end_of(i))
}
'''),
  test=("tests/stages_3b.rs", '''
use bustub::storage::table::var_row::{column, encode};

fn cols(v: &[&str]) -> Vec<Vec<u8>> {
    v.iter().map(|s| s.as_bytes().to_vec()).collect()
}

#[test]
fn s3b_c3_each_column_comes_back() {
    let b = encode(&cols(&["ab", "", "cde"]));
    assert_eq!(column(&b, 0), Some(&b"ab"[..]));
    assert_eq!(column(&b, 1), Some(&b""[..]));
    assert_eq!(column(&b, 2), Some(&b"cde"[..]));
}

#[test]
fn s3b_c3_an_index_past_the_end_is_none() {
    let b = encode(&cols(&["x"]));
    assert_eq!(column(&b, 1), None);
    assert_eq!(column(&[], 0), None);
}

#[test]
fn s3b_c3_the_first_column_starts_at_zero_and_a_single_column_row_works() {
    let b = encode(&cols(&["hello"]));
    assert_eq!(column(&b, 0), Some(&b"hello"[..]));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: every column reads back, and together they are exactly the data section.
    #[test]
    fn s3b_c3_property_columns_read_back(rows in proptest::collection::vec(proptest::collection::vec(any::<u8>(), 0..6), 0..8)) {
        let b = encode(&rows);
        let mut all = Vec::new();
        for (i, c) in rows.iter().enumerate() {
            prop_assert_eq!(column(&b, i), Some(c.as_slice()), "column {}", i);
            all.extend_from_slice(column(&b, i).unwrap());
        }
        prop_assert_eq!(all.len(), rows.iter().map(|c| c.len()).sum::<usize>());
        prop_assert_eq!(column(&b, rows.len()), None);
    }
}
''')))

CH.append(C("3b-c4", M3B, "93-challenge-checksummed-pages", "build", "Challenge: checksummed pages", "medium", "stages_3b::s3b_c4",
  ["a table-driven CRC-32","sealing a payload and refusing damaged ones"],
  ["durability-and-fsync","bytes-endianness-and-views","errors-as-values-with-result"],
  "`crc32`, `seal` and `unseal` in `src/storage/table/checksum.rs`: the standard CRC-32 (IEEE 802.3, reflected, polynomial `0xEDB88320`, initial value and final xor `0xFFFFFFFF`) of a byte slice; `seal(payload)` returns the payload followed by its CRC as 4 little-endian bytes; `unseal(bytes)` returns the payload if the CRC matches and an error naming the problem otherwise.",
  "A disk lies in small ways: a bit flips, a write is torn. A checksum on every page turns silent corruption into an error you can act on (use the replica, run recovery). CRC-32 detects every single-bit error and every burst up to 32 bits, and a table makes it fast enough to run on every page read.",
  ["`crc32(b\"123456789\") == 0xCBF43926`; `crc32(b\"\") == 0`.","`seal(p)` is `p` plus 4 bytes. `unseal` fails with `TooShort` for fewer than 4 bytes and `Mismatch` when the stored CRC is not the CRC of the rest."],
  ["`unseal(seal(p)) == Ok(p)`.","The CRC of the data is a function of the bytes only (no state between calls)."],
  ["Flipping any single bit of a sealed buffer makes `unseal` fail.","Appending or removing a byte makes `unseal` fail (with overwhelming likelihood: for these tests, always).","Two different payloads of equal length seal to different CRCs in the cases tested."],
  ["crc32(\"123456789\") = 0xCBF43926","seal(\"abc\") = \"abc\" + crc32(\"abc\") little-endian"],
  ["The standard check values.","Round trips.","Every single-bit flip of a sealed buffer is caught.","A property over random payloads."],
  src=("src/storage/table/checksum.rs", '''
//! CRC-32 (IEEE) and sealed payloads.

#[derive(Debug, PartialEq, Eq)]
pub enum SealError {
    TooShort,
    Mismatch,
}

pub fn crc32(data: &[u8]) -> u32 {
    // @begin 3b-c4
    let mut table = [0u32; 256];
    for (i, slot) in table.iter_mut().enumerate() {
        let mut c = i as u32;
        for _ in 0..8 {
            c = if c & 1 == 1 { 0xEDB8_8320 ^ (c >> 1) } else { c >> 1 };
        }
        *slot = c;
    }
    let mut crc = 0xFFFF_FFFFu32;
    for &b in data {
        crc = table[((crc ^ b as u32) & 0xFF) as usize] ^ (crc >> 8);
    }
    !crc
    //~ todo!("3b-c4: the table of 256 entries, then one table lookup per byte")
    // @end
}

pub fn seal(payload: &[u8]) -> Vec<u8> {
    // @begin 3b-c4
    let mut out = payload.to_vec();
    out.extend_from_slice(&crc32(payload).to_le_bytes());
    out
    //~ todo!("3b-c4: the payload, then its CRC in 4 little-endian bytes")
    // @end
}

pub fn unseal(bytes: &[u8]) -> Result<&[u8], SealError> {
    // @begin 3b-c4
    if bytes.len() < 4 {
        return Err(SealError::TooShort);
    }
    let (payload, crc) = bytes.split_at(bytes.len() - 4);
    if u32::from_le_bytes([crc[0], crc[1], crc[2], crc[3]]) == crc32(payload) {
        Ok(payload)
    } else {
        Err(SealError::Mismatch)
    }
    //~ todo!("3b-c4: check the stored CRC against the payload")
    // @end
}
'''),
  test=("tests/stages_3b.rs", '''
use bustub::storage::table::checksum::{crc32, seal, unseal, SealError};

#[test]
fn s3b_c4_the_standard_check_values() {
    assert_eq!(crc32(b"123456789"), 0xCBF4_3926);
    assert_eq!(crc32(b""), 0);
    assert_eq!(crc32(b"a"), 0xE8B7_BE43);
    assert_eq!(crc32(b"The quick brown fox jumps over the lazy dog"), 0x414F_A339);
}

#[test]
fn s3b_c4_sealing_appends_the_crc_in_little_endian() {
    let s = seal(b"abc");
    assert_eq!(&s[..3], b"abc");
    assert_eq!(&s[3..], &crc32(b"abc").to_le_bytes());
    assert_eq!(unseal(&s), Ok(&b"abc"[..]));
    assert_eq!(unseal(&seal(b"")), Ok(&b""[..]));
}

#[test]
fn s3b_c4_short_and_damaged_buffers_are_refused() {
    assert_eq!(unseal(b"abc"), Err(SealError::TooShort));
    assert_eq!(unseal(b""), Err(SealError::TooShort));
    let mut s = seal(b"hello world");
    s[2] ^= 1;
    assert_eq!(unseal(&s), Err(SealError::Mismatch));
}

#[test]
fn s3b_c4_every_single_bit_flip_of_a_sealed_page_is_detected() {
    let page: Vec<u8> = (0..200u32).map(|i| (i * 31 % 251) as u8).collect();
    let s = seal(&page);
    for byte in 0..s.len() {
        for bit in 0..8 {
            let mut t = s.clone();
            t[byte] ^= 1 << bit;
            assert!(unseal(&t).is_err(), "flipping bit {bit} of byte {byte} went unnoticed");
        }
    }
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: seal then unseal is the identity, and dropping or adding a byte is caught.
    #[test]
    fn s3b_c4_property_sealed_payloads_round_trip_and_changes_are_caught(p in proptest::collection::vec(any::<u8>(), 0..64), extra in any::<u8>()) {
        let s = seal(&p);
        prop_assert_eq!(unseal(&s), Ok(p.as_slice()));
        let mut more = s.clone();
        more.push(extra);
        prop_assert!(unseal(&more).is_err());
        if !p.is_empty() {
            let mut less = s.clone();
            less.remove(0);
            prop_assert!(unseal(&less).is_err());
        }
    }
}
''')))

CH.append(C("3b-c5", M3B, "94-challenge-distinct-rows", "build", "Challenge: distinct rows", "easy", "stages_3b::s3b_c5",
  ["the one place SQL treats NULL as equal to NULL","removing duplicates while keeping first-seen order"],
  ["sql-types-and-three-valued-logic","hashing-values-and-keys","eq-hash-ord-contracts"],
  "`distinct_rows` in `src/storage/table/distinct.rs`: remove duplicate rows from a list, keeping the **first** occurrence of each and the original order. Rows are vectors of nullable integers, and for `DISTINCT` (and `GROUP BY`) two NULLs count as **equal**, even though `NULL = NULL` is unknown in a `WHERE` clause.",
  "SQL has two notions of sameness: *equal* (three-valued, NULL is unknown) and *not distinct* (two-valued, NULL is the same as NULL). `DISTINCT`, `GROUP BY`, `UNION`, hash joins on `IS NOT DISTINCT FROM` and unique indexes (in most systems) use the second. A port that uses `==` on `Option<i64>` gets it right by luck; one that uses SQL `=` gets it wrong.",
  ["`distinct_rows(rows)` returns the rows with later duplicates removed, order preserved.","`(None, 1)` and `(None, 1)` are duplicates; `(None, 1)` and `(Some(0), 1)` are not.","`distinct_count(rows)` is the number of distinct rows."],
  ["The output has no two equal rows.","Every output row appears in the input, and every input row equals some output row.","The output is a subsequence of the input."],
  ["`distinct(distinct(x)) == distinct(x)`.","Permuting the input permutes which duplicates survive but never changes `distinct_count`.","Appending a row already present changes nothing."],
  ["[(1,NULL),(1,NULL),(2,3),(1,NULL)] -> [(1,NULL),(2,3)]"],
  ["Duplicates with NULLs.","Order of first occurrences.","A property against a first-seen filter."],
  src=("src/storage/table/distinct.rs", '''
//! DISTINCT over rows of nullable integers.

use std::collections::HashSet;

pub type Row = Vec<Option<i64>>;

pub fn distinct_rows(rows: &[Row]) -> Vec<Row> {
    // @begin 3b-c5
    let mut seen: HashSet<&Row> = HashSet::new();
    rows.iter().filter(|r| seen.insert(r)).cloned().collect()
    //~ todo!("3b-c5: keep the first of each distinct row, treating NULL as equal to NULL")
    // @end
}

pub fn distinct_count(rows: &[Row]) -> usize {
    // @begin 3b-c5
    rows.iter().collect::<HashSet<_>>().len()
    //~ todo!("3b-c5: how many distinct rows")
    // @end
}
'''),
  test=("tests/stages_3b.rs", '''
use bustub::storage::table::distinct::{distinct_count, distinct_rows, Row};

fn r(v: &[Option<i64>]) -> Row {
    v.to_vec()
}

#[test]
fn s3b_c5_nulls_are_the_same_for_distinct() {
    let rows = vec![r(&[Some(1), None]), r(&[Some(1), None]), r(&[Some(2), Some(3)]), r(&[Some(1), None])];
    assert_eq!(distinct_rows(&rows), vec![r(&[Some(1), None]), r(&[Some(2), Some(3)])]);
    assert_eq!(distinct_count(&rows), 2);
}

#[test]
fn s3b_c5_null_and_zero_are_different() {
    let rows = vec![r(&[None]), r(&[Some(0)]), r(&[None])];
    assert_eq!(distinct_rows(&rows), vec![r(&[None]), r(&[Some(0)])]);
}

#[test]
fn s3b_c5_first_occurrences_keep_their_order() {
    let rows = vec![r(&[Some(3)]), r(&[Some(1)]), r(&[Some(3)]), r(&[Some(2)]), r(&[Some(1)])];
    assert_eq!(distinct_rows(&rows), vec![r(&[Some(3)]), r(&[Some(1)]), r(&[Some(2)])]);
}

#[test]
fn s3b_c5_empty_input_and_rows_of_different_lengths() {
    assert_eq!(distinct_rows(&[]), Vec::<Row>::new());
    assert_eq!(distinct_rows(&[r(&[]), r(&[]), r(&[None])]), vec![r(&[]), r(&[None])]);
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: a first-seen filter, idempotent, with a count that does not depend on order.
    #[test]
    fn s3b_c5_property_distinct_keeps_first_occurrences(rows in proptest::collection::vec(proptest::collection::vec(proptest::option::of(0i64..3), 0..3), 0..20)) {
        let out = distinct_rows(&rows);
        let mut want: Vec<Row> = Vec::new();
        for row in &rows { if !want.contains(row) { want.push(row.clone()); } }
        prop_assert_eq!(&out, &want);
        prop_assert_eq!(distinct_rows(&out), out.clone());
        prop_assert_eq!(distinct_count(&rows), out.len());
        let mut rev = rows.clone();
        rev.reverse();
        prop_assert_eq!(distinct_count(&rev), out.len());
    }
}
''')))

CH.append(C("3c-c1", M3C, "90-challenge-a-free-space-map", "build", "Challenge: a free space map", "medium", "stages_3c::s3c_c1",
  ["finding the first page with enough room without scanning","a segment tree of maxima"],
  ["heap-files","slot-allocation-and-invariants","model-based-testing"],
  "`FreeSpaceMap` in `src/storage/table/free_space_map.rs`: for each page of a heap file, how many bytes are free. `set(page, free)` records it; `find(need)` returns the **lowest-numbered** page with at least `need` free bytes, in `O(log n)`.",
  "An insert into a heap must find a page with room. Scanning every page's header is how a table with a million pages makes every insert slow; PostgreSQL keeps a *free space map* for exactly this. A tree of maxima answers \"leftmost page with at least `need`\" with one descent, and updating a page is one path up.",
  ["`new(pages)` starts with every page at 0 free bytes.","`set(page, free)` updates one page; `get(page)` reads it back.","`find(need)` is the smallest page index whose free space is at least `need`, or `None`; `need == 0` is page 0 (if there is any page)."],
  ["`get` returns what `set` last stored.","`find` returns a page that really has enough room, and no lower page does."],
  ["Raising a page's free space can only move `find` results to a lower or equal page.","`find(n)` is never lower than `find(m)` for `n >= m`... in the other direction: a larger need never finds an earlier page.","With all pages at 0, `find(1)` is `None`."],
  ["free [0, 50, 20, 80]: find(10) = 1, find(60) = 3, find(100) = None","set(0, 70) -> find(60) = 0"],
  ["Finding after updates.","Edge cases: no pages, need 0, need larger than any page.","A property against a linear scan, and a large map finishing quickly."],
  src=("src/storage/table/free_space_map.rs", '''
//! Which page of a heap file has room for a row.

pub struct FreeSpaceMap {
    // @begin 3c-c1
    n: usize,
    /// A binary tree of maxima over the pages; leaves start at `size`.
    tree: Vec<u32>,
    size: usize,
    //~ _fsm: (),
    // @end
}

impl FreeSpaceMap {
    pub fn new(pages: usize) -> FreeSpaceMap {
        // @begin 3c-c1
        let size = pages.next_power_of_two().max(1);
        FreeSpaceMap { n: pages, tree: vec![0; 2 * size], size }
        //~ todo!("3c-c1: every page has no free space")
        // @end
    }

    pub fn pages(&self) -> usize {
        // @begin 3c-c1
        self.n
        //~ todo!("3c-c1: how many pages")
        // @end
    }

    pub fn set(&mut self, page: usize, free: u32) {
        // @begin 3c-c1
        let mut i = self.size + page;
        self.tree[i] = free;
        while i > 1 {
            i /= 2;
            self.tree[i] = self.tree[2 * i].max(self.tree[2 * i + 1]);
        }
        //~ todo!("3c-c1: store the value and fix the maxima on the way up")
        // @end
    }

    pub fn get(&self, page: usize) -> u32 {
        // @begin 3c-c1
        self.tree[self.size + page]
        //~ todo!("3c-c1: the stored value")
        // @end
    }

    /// The lowest page with at least `need` free bytes.
    pub fn find(&self, need: u32) -> Option<usize> {
        // @begin 3c-c1
        if self.n == 0 || self.tree[1] < need {
            return None;
        }
        let mut i = 1;
        while i < self.size {
            i = if self.tree[2 * i] >= need { 2 * i } else { 2 * i + 1 };
        }
        let page = i - self.size;
        if page < self.n {
            Some(page)
        } else {
            None
        }
        //~ todo!("3c-c1: descend, going left whenever the left half has enough room")
        // @end
    }
}
'''),
  test=("tests/stages_3c.rs", '''
use bustub::storage::table::free_space_map::FreeSpaceMap;

#[test]
fn s3c_c1_the_lowest_page_with_enough_room() {
    let mut m = FreeSpaceMap::new(4);
    for (p, f) in [(1, 50), (2, 20), (3, 80)] {
        m.set(p, f);
    }
    assert_eq!((m.find(10), m.find(60), m.find(100)), (Some(1), Some(3), None));
    m.set(0, 70);
    assert_eq!(m.find(60), Some(0));
    assert_eq!(m.get(0), 70);
}

#[test]
fn s3c_c1_nothing_has_room_in_a_new_map() {
    let m = FreeSpaceMap::new(5);
    assert_eq!(m.find(1), None);
    assert_eq!(m.find(0), Some(0), "every page has at least 0 bytes");
}

#[test]
fn s3c_c1_no_pages_and_one_page() {
    let m = FreeSpaceMap::new(0);
    assert_eq!((m.find(0), m.pages()), (None, 0));
    let mut one = FreeSpaceMap::new(1);
    one.set(0, 5);
    assert_eq!((one.find(5), one.find(6)), (Some(0), None));
}

#[test]
fn s3c_c1_pages_that_do_not_fill_the_tree_are_never_returned() {
    let mut m = FreeSpaceMap::new(5);
    m.set(4, 9);
    assert_eq!(m.find(9), Some(4));
    assert_eq!(m.find(10), None, "the padding leaves of the tree are not pages");
}

#[test]
fn s3c_c1_a_large_map_answers_quickly() {
    let n = 200_000;
    let mut m = FreeSpaceMap::new(n);
    m.set(n - 1, 100);
    let t = std::time::Instant::now();
    for _ in 0..200_000 {
        assert_eq!(m.find(100), Some(n - 1));
    }
    assert!(t.elapsed() < std::time::Duration::from_secs(5), "200 000 finds took {:?}: find must not scan", t.elapsed());
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against a linear scan, after any updates.
    #[test]
    fn s3c_c1_property_find_equals_a_scan(pages in 0usize..20, ops in proptest::collection::vec((0usize..20, 0u32..100), 0..60), probes in proptest::collection::vec(0u32..120, 1..10)) {
        let mut m = FreeSpaceMap::new(pages);
        let mut model = vec![0u32; pages];
        for (p, f) in ops {
            if pages == 0 { break; }
            let p = p % pages;
            m.set(p, f);
            model[p] = f;
            for &need in &probes {
                prop_assert_eq!(m.find(need), model.iter().position(|&x| x >= need));
            }
            prop_assert_eq!(m.get(p), f);
        }
    }
}
''')))

CH.append(C("3c-c2", M3C, "91-challenge-table-names", "build", "Challenge: table names", "easy", "stages_3c::s3c_c2",
  ["identifier rules in a catalog: case, uniqueness and never reusing an id","rename and drop without breaking what points at the id"],
  ["structs-and-accessors","slot-allocation-and-invariants"],
  "`NameCatalog` in `src/catalog/name_catalog.rs`: the names half of a catalog. `create(name)` returns a new table id (`u32`), `lookup`, `rename` and `drop` work by name, and names are **case-insensitive** (ASCII). Ids are handed out in increasing order and are **never reused**, even after a drop.",
  "Everything else in the engine refers to a table by id, so an id must mean one table for ever: reusing one would make an old plan or a cached handle silently point at a different table. Names are what users type, and `Users`, `USERS` and `users` must be the same table.",
  ["`create(name)` is `Err(Exists)` if a table with that name (any case) exists, `Err(Invalid)` for an empty name; otherwise the next id, starting at 1.","`lookup(name)` is the id; `drop(name)` removes it (false if absent); `rename(old, new)` moves the name, keeping the id (`Err` if `old` is missing or `new` exists).","`names()` lists the names in lowercase, sorted."],
  ["Every id is handed out at most once, ever.","Two live tables never share a name (case-insensitively)."],
  ["`lookup(drop-and-create(n))` has a larger id than before.","`rename(a, b)` then `lookup(b)` equals the id `lookup(a)` had.","`create(n)` then `drop(n)` leaves `names()` as it was."],
  ["create Users -> 1; create USERS -> Exists; lookup users -> 1; drop; create users -> 2"],
  ["Case-insensitivity, uniqueness, and ids that stay unique.","Rename and drop.","A property against a model."],
  src=("src/catalog/name_catalog.rs", '''
//! Table names and ids.

use std::collections::BTreeMap;

#[derive(Debug, PartialEq, Eq)]
pub enum NameError {
    Exists,
    Missing,
    Invalid,
}

pub struct NameCatalog {
    // @begin 3c-c2
    by_name: BTreeMap<String, u32>,
    next_id: u32,
    //~ _names: (),
    // @end
}

impl NameCatalog {
    pub fn new() -> NameCatalog {
        // @begin 3c-c2
        NameCatalog { by_name: BTreeMap::new(), next_id: 1 }
        //~ todo!("3c-c2: no tables; ids start at 1")
        // @end
    }

    pub fn create(&mut self, name: &str) -> Result<u32, NameError> {
        // @begin 3c-c2
        if name.is_empty() {
            return Err(NameError::Invalid);
        }
        let key = name.to_ascii_lowercase();
        if self.by_name.contains_key(&key) {
            return Err(NameError::Exists);
        }
        let id = self.next_id;
        self.next_id += 1;
        self.by_name.insert(key, id);
        Ok(id)
        //~ todo!("3c-c2: a new id for a new name")
        // @end
    }

    pub fn lookup(&self, name: &str) -> Option<u32> {
        // @begin 3c-c2
        self.by_name.get(&name.to_ascii_lowercase()).copied()
        //~ todo!("3c-c2: the id of the table")
        // @end
    }

    pub fn drop(&mut self, name: &str) -> bool {
        // @begin 3c-c2
        self.by_name.remove(&name.to_ascii_lowercase()).is_some()
        //~ todo!("3c-c2: forget the name (the id is not reused)")
        // @end
    }

    pub fn rename(&mut self, old: &str, new: &str) -> Result<(), NameError> {
        // @begin 3c-c2
        if new.is_empty() {
            return Err(NameError::Invalid);
        }
        let (old, new) = (old.to_ascii_lowercase(), new.to_ascii_lowercase());
        if !self.by_name.contains_key(&old) {
            return Err(NameError::Missing);
        }
        if old != new && self.by_name.contains_key(&new) {
            return Err(NameError::Exists);
        }
        let id = self.by_name.remove(&old).unwrap();
        self.by_name.insert(new, id);
        Ok(())
        //~ todo!("3c-c2: move the name, keep the id")
        // @end
    }

    pub fn names(&self) -> Vec<String> {
        // @begin 3c-c2
        self.by_name.keys().cloned().collect()
        //~ todo!("3c-c2: lowercase names, sorted")
        // @end
    }
}

impl Default for NameCatalog {
    fn default() -> Self {
        NameCatalog::new()
    }
}
'''),
  test=("tests/stages_3c.rs", '''
use bustub::catalog::name_catalog::{NameCatalog, NameError};
use std::collections::BTreeMap;

#[test]
fn s3c_c2_names_are_case_insensitive_and_unique() {
    let mut c = NameCatalog::new();
    assert_eq!(c.create("Users"), Ok(1));
    assert_eq!(c.create("USERS"), Err(NameError::Exists));
    assert_eq!(c.lookup("users"), Some(1));
    assert_eq!(c.create(""), Err(NameError::Invalid));
    assert_eq!(c.names(), vec!["users".to_string()]);
}

#[test]
fn s3c_c2_an_id_is_never_reused() {
    let mut c = NameCatalog::new();
    assert_eq!(c.create("a"), Ok(1));
    assert!(c.drop("A"));
    assert!(!c.drop("a"));
    assert_eq!(c.create("a"), Ok(2), "the dropped table's id must not come back");
    assert_eq!(c.create("b"), Ok(3));
}

#[test]
fn s3c_c2_rename_keeps_the_id() {
    let mut c = NameCatalog::new();
    c.create("old").unwrap();
    c.create("other").unwrap();
    assert_eq!(c.rename("OLD", "New"), Ok(()));
    assert_eq!((c.lookup("old"), c.lookup("new")), (None, Some(1)));
    assert_eq!(c.rename("missing", "x"), Err(NameError::Missing));
    assert_eq!(c.rename("new", "OTHER"), Err(NameError::Exists));
    assert_eq!(c.rename("new", "NEW"), Ok(()), "renaming to the same name in another case is fine");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against a map from lowercase name to id with a counter that only grows.
    #[test]
    fn s3c_c2_property_a_catalog_matches_a_model(ops in proptest::collection::vec((0u8..3, 0u8..4, any::<bool>()), 0..60)) {
        let mut c = NameCatalog::new();
        let mut m: BTreeMap<String, u32> = BTreeMap::new();
        let mut next = 1u32;
        for (op, n, upper) in ops {
            let name = if upper { format!("T{n}") } else { format!("t{n}") };
            let low = name.to_ascii_lowercase();
            match op {
                0 => {
                    let want = if m.contains_key(&low) { Err(NameError::Exists) } else { m.insert(low, next); next += 1; Ok(next - 1) };
                    prop_assert_eq!(c.create(&name), want);
                }
                1 => prop_assert_eq!(c.drop(&name), m.remove(&low).is_some()),
                _ => {
                    let new = format!("t{}", (n + 1) % 4);
                    let want = if !m.contains_key(&low) { Err(NameError::Missing) } else if low != new && m.contains_key(&new) { Err(NameError::Exists) } else { let id = m.remove(&low).unwrap(); m.insert(new.clone(), id); Ok(()) };
                    prop_assert_eq!(c.rename(&name, &new), want);
                }
            }
            prop_assert_eq!(c.names(), m.keys().cloned().collect::<Vec<_>>());
            for (k, &id) in &m { prop_assert_eq!(c.lookup(k), Some(id)); }
        }
    }
}
''')))

CH.append(C("3c-c3", M3C, "92-challenge-the-endless-raise", "debug", "Challenge: the endless raise", "easy", "stages_3c::s3c_c3",
  ["finding the Halloween problem in an update that appends","scanning a snapshot of the table's extent"],
  ["halloween-problem","heap-files","property-testing-and-fuzzing"],
  "`give_raise` in `src/storage/table/raise.rs` implements `UPDATE emp SET salary = salary * factor WHERE salary < limit` on a heap that only appends: it marks the old row version dead and appends the new version at the end. It looks right, and some employees get the raise twice (or the loop does not end). Find the bug and fix it.",
  "This is the Halloween problem, named for the night in 1976 that IBM engineers saw it: an update that moves a row ahead of the scan finds it again and updates it again. The cure is one of two things: scan only what existed when the scan started, or collect the updates first and apply them afterwards.",
  ["`give_raise(rows, limit, factor)`: every live row whose salary is below `limit` gets its salary multiplied by `factor` **exactly once**; the old version is marked dead (its slot becomes `None`) and the new one appended.","Returns the number of rows updated."],
  ["Every employee appears once among the live rows afterwards.","Rows that did not match are untouched.","The scan ends."],
  ["The set of live salaries equals applying the raise once to every row below the limit.","The result does not depend on the order the rows are scanned.","Running with `factor = 1` leaves the live salaries unchanged."],
  ["[(1, 100), (2, 5000)], limit 1000, factor 2 -> live: (2, 5000), (1, 200); updated 1"],
  ["One matching row; none; many.","A factor that keeps salaries below the limit (the loop would not end).","A property against a map."],
  src=("src/storage/table/raise.rs", '''
//! The Halloween problem in an append-only heap.

/// A heap slot: `Some((employee id, salary))` while live, `None` once the version is dead.
pub type Slot = Option<(u32, i64)>;

/// Multiplies the salary of every live row below `limit` by `factor`, once. Returns how many rows changed.
pub fn give_raise(rows: &mut Vec<Slot>, limit: i64, factor: i64) -> usize {
    // @begin 3c-c3
    let scan_to = rows.len();
    let mut updated = 0;
    for i in 0..scan_to {
        if let Some((id, salary)) = rows[i] {
            if salary < limit {
                rows[i] = None;
                rows.push(Some((id, salary * factor)));
                updated += 1;
            }
        }
    }
    updated
    //~ let mut updated = 0;
    //~ let mut i = 0;
    //~ while i < rows.len() {
    //~     if let Some((id, salary)) = rows[i] {
    //~         if salary < limit {
    //~             rows[i] = None;
    //~             rows.push(Some((id, salary * factor)));
    //~             updated += 1;
    //~         }
    //~     }
    //~     i += 1;
    //~ }
    //~ updated
    // @end
}
'''),
  test=("tests/stages_3c.rs", '''
use bustub::storage::table::raise::{give_raise, Slot};
use std::collections::BTreeMap;

fn live(rows: &[Slot]) -> BTreeMap<u32, i64> {
    let mut m = BTreeMap::new();
    for (id, s) in rows.iter().flatten() {
        assert!(m.insert(*id, *s).is_none(), "employee {id} is live twice");
    }
    m
}

#[test]
fn s3c_c3_each_matching_row_is_raised_once() {
    let mut rows = vec![Some((1, 100)), Some((2, 5000))];
    assert_eq!(give_raise(&mut rows, 1000, 2), 1);
    assert_eq!(live(&rows), BTreeMap::from([(1, 200), (2, 5000)]));
}

#[test]
fn s3c_c3_the_update_ends_even_when_the_new_salary_is_still_below_the_limit() {
    let mut rows = vec![Some((1, 1)), Some((2, 2))];
    assert_eq!(give_raise(&mut rows, 1_000_000, 3), 2, "each row once, not until it passes the limit");
    assert_eq!(live(&rows), BTreeMap::from([(1, 3), (2, 6)]));
}

#[test]
fn s3c_c3_nothing_matches_and_dead_slots_are_skipped() {
    let mut rows = vec![None, Some((1, 5000)), None];
    assert_eq!(give_raise(&mut rows, 1000, 2), 0);
    assert_eq!(rows.len(), 3, "nothing was appended");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 256, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: the live salaries equal applying the raise once to the rows below the limit.
    #[test]
    fn s3c_c3_property_the_raise_is_applied_once(sal in proptest::collection::vec(proptest::option::of(1i64..2000), 0..12), limit in 1i64..2500, factor in 1i64..4) {
        let mut rows: Vec<Slot> = sal.iter().enumerate().map(|(i, s)| s.map(|x| (i as u32, x))).collect();
        let before = live(&rows);
        let n = give_raise(&mut rows, limit, factor);
        let want: BTreeMap<u32, i64> = before.iter().map(|(&id, &s)| (id, if s < limit { s * factor } else { s })).collect();
        prop_assert_eq!(live(&rows), want);
        prop_assert_eq!(n, before.values().filter(|&&s| s < limit).count());
    }
}
''')))

CH.append(C("3c-c4", M3C, "93-challenge-rows-that-move", "build", "Challenge: rows that move", "hard", "stages_3c::s3c_c4",
  ["keeping a row's id stable when an update no longer fits its page","an indirection layer between ids and locations"],
  ["heap-files","slotted-pages","slot-allocation-and-invariants","model-based-testing"],
  "`MovingHeap` in `src/storage/table/moving_heap.rs`: a heap of fixed-size pages (`page_size` bytes of row data each) that stores byte-string rows under **row ids that never change**. `update(rid, row)` may need more room than the row's page has: the row then moves to another page, and the id still works.",
  "Indexes store row ids, so an id must survive every update, however much the row grows. PostgreSQL leaves a forwarding pointer in the old slot (a HOT chain or a redirect), SQLite rewrites the b-tree cell, and most engines have an indirection. Doing it yourself shows what the invariants of a heap are: where bytes live, what points where, and when a page is full.",
  ["`insert(row)` returns a new `Rid` (a `u32`, increasing); it fails with `None` if the row is larger than a whole page.","`get(rid)`, `delete(rid)` (false if not live) and `update(rid, row)` (false if not live or the row is larger than a page).","`page_of(rid)` is the page currently holding the row; `used(page)` is the bytes of rows in that page, never more than `page_size`; `pages()` is the number of pages in use."],
  ["`used(page) <= page_size` for every page, always.","`get(rid)` returns the bytes last stored under `rid`, wherever the row lives now.","A deleted `rid` is never reused."],
  ["The heap behaves exactly like a map from `rid` to row, whatever the sizes.","An update that fits in place leaves `page_of(rid)` alone.","The sum of `used` over all pages is the total length of the live rows."],
  ["page size 10: insert 6 bytes -> rid 0 on page 0; insert 6 bytes -> rid 1 on page 1; update rid 0 to 8 bytes -> still rid 0, on page 0 if it fits, else another page"],
  ["Insert, get, delete.","Updates that fit and updates that need to move.","Oversized rows.","A property against a map, with the page invariant."],
  src=("src/storage/table/moving_heap.rs", '''
//! A heap whose row ids survive updates that make a row move.

use std::collections::BTreeMap;

pub type Rid = u32;

pub struct MovingHeap {
    // @begin 3c-c4
    page_size: usize,
    /// rid -> (page, row bytes)
    rows: BTreeMap<Rid, (usize, Vec<u8>)>,
    used: Vec<usize>,
    next_rid: Rid,
    //~ _heap: (),
    // @end
}

impl MovingHeap {
    pub fn new(page_size: usize) -> MovingHeap {
        // @begin 3c-c4
        MovingHeap { page_size, rows: BTreeMap::new(), used: Vec::new(), next_rid: 0 }
        //~ todo!("3c-c4: an empty heap of pages of `page_size` bytes")
        // @end
    }

    // @begin 3c-c4
    /// The lowest page with room for `len` bytes (a new page if there is none).
    fn page_with_room(&mut self, len: usize, except: Option<usize>) -> usize {
        match (0..self.used.len()).find(|&p| Some(p) != except && self.used[p] + len <= self.page_size) {
            Some(p) => p,
            None => {
                self.used.push(0);
                self.used.len() - 1
            }
        }
    }
    //~ // TODO(3c-c4): helpers of your own
    // @end

    pub fn insert(&mut self, row: &[u8]) -> Option<Rid> {
        // @begin 3c-c4
        if row.len() > self.page_size {
            return None;
        }
        let page = self.page_with_room(row.len(), None);
        self.used[page] += row.len();
        let rid = self.next_rid;
        self.next_rid += 1;
        self.rows.insert(rid, (page, row.to_vec()));
        Some(rid)
        //~ todo!("3c-c4: find a page with room, store the row there, hand out the next id")
        // @end
    }

    pub fn get(&self, rid: Rid) -> Option<&[u8]> {
        // @begin 3c-c4
        self.rows.get(&rid).map(|(_, r)| r.as_slice())
        //~ todo!("3c-c4: the row's bytes")
        // @end
    }

    pub fn delete(&mut self, rid: Rid) -> bool {
        // @begin 3c-c4
        match self.rows.remove(&rid) {
            Some((page, row)) => {
                self.used[page] -= row.len();
                true
            }
            None => false,
        }
        //~ todo!("3c-c4: free the row's bytes")
        // @end
    }

    pub fn update(&mut self, rid: Rid, row: &[u8]) -> bool {
        // @begin 3c-c4
        if row.len() > self.page_size {
            return false;
        }
        let Some((page, old)) = self.rows.get(&rid).map(|(p, r)| (*p, r.len())) else { return false };
        if self.used[page] - old + row.len() <= self.page_size {
            self.used[page] = self.used[page] - old + row.len();
            self.rows.get_mut(&rid).unwrap().1 = row.to_vec();
        } else {
            self.used[page] -= old;
            let to = self.page_with_room(row.len(), Some(page));
            self.used[to] += row.len();
            self.rows.insert(rid, (to, row.to_vec()));
        }
        true
        //~ todo!("3c-c4: rewrite in place if it fits, else move the row to another page and keep its id")
        // @end
    }

    pub fn page_of(&self, rid: Rid) -> Option<usize> {
        // @begin 3c-c4
        self.rows.get(&rid).map(|(p, _)| *p)
        //~ todo!("3c-c4: the page that holds the row now")
        // @end
    }

    pub fn used(&self, page: usize) -> usize {
        // @begin 3c-c4
        self.used.get(page).copied().unwrap_or(0)
        //~ todo!("3c-c4: bytes of rows in the page")
        // @end
    }

    pub fn pages(&self) -> usize {
        // @begin 3c-c4
        self.used.len()
        //~ todo!("3c-c4: pages in use")
        // @end
    }
}
'''),
  test=("tests/stages_3c.rs", '''
use bustub::storage::table::moving_heap::MovingHeap;
use std::collections::BTreeMap;

#[test]
fn s3c_c4_rows_keep_their_ids_and_land_on_pages_with_room() {
    let mut h = MovingHeap::new(10);
    let a = h.insert(&[1; 6]).unwrap();
    let b = h.insert(&[2; 6]).unwrap();
    assert_eq!((a, b), (0, 1));
    assert_ne!(h.page_of(a), h.page_of(b), "6 + 6 does not fit in a page of 10");
    assert_eq!((h.get(a), h.get(b)), (Some(&[1u8; 6][..]), Some(&[2u8; 6][..])));
}

#[test]
fn s3c_c4_an_update_that_fits_stays_where_it_is() {
    let mut h = MovingHeap::new(10);
    let a = h.insert(&[1; 4]).unwrap();
    let page = h.page_of(a);
    assert!(h.update(a, &[9; 9]));
    assert_eq!(h.page_of(a), page);
    assert_eq!(h.get(a), Some(&[9u8; 9][..]));
}

#[test]
fn s3c_c4_an_update_that_does_not_fit_moves_the_row_and_keeps_its_id() {
    let mut h = MovingHeap::new(10);
    let a = h.insert(&[1; 5]).unwrap();
    let b = h.insert(&[2; 5]).unwrap();
    assert_eq!(h.page_of(a), h.page_of(b));
    assert!(h.update(a, &[7; 8]), "8 does not fit beside b's 5, so a moves");
    assert_ne!(h.page_of(a), h.page_of(b));
    assert_eq!((h.get(a), h.get(b)), (Some(&[7u8; 8][..]), Some(&[2u8; 5][..])));
    for p in 0..h.pages() {
        assert!(h.used(p) <= 10);
    }
}

#[test]
fn s3c_c4_oversized_rows_and_unknown_ids_are_refused() {
    let mut h = MovingHeap::new(10);
    assert_eq!(h.insert(&[0; 11]), None);
    let a = h.insert(&[1; 3]).unwrap();
    assert!(!h.update(a, &[0; 11]));
    assert!(!h.update(99, &[1]));
    assert!(h.delete(a));
    assert!(!h.delete(a));
    assert_eq!(h.get(a), None);
    assert_eq!(h.insert(&[1]).unwrap(), 1, "ids are not reused");
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: against a map from rid to row, with every page within its size and the used bytes adding up.
    #[test]
    fn s3c_c4_property_a_moving_heap_is_a_map_within_its_pages(ops in proptest::collection::vec((0u8..3, 0u32..8, 0usize..14, any::<u8>()), 0..80)) {
        let mut h = MovingHeap::new(12);
        let mut m: BTreeMap<u32, Vec<u8>> = BTreeMap::new();
        let mut next = 0u32;
        for (op, rid, len, byte) in ops {
            let row = vec![byte; len];
            match op {
                0 => {
                    let got = h.insert(&row);
                    if len > 12 { prop_assert_eq!(got, None); } else { prop_assert_eq!(got, Some(next)); m.insert(next, row); next += 1; }
                }
                1 => {
                    let want = m.contains_key(&rid) && len <= 12;
                    prop_assert_eq!(h.update(rid, &row), want);
                    if want { m.insert(rid, row); }
                }
                _ => prop_assert_eq!(h.delete(rid), m.remove(&rid).is_some()),
            }
            for (k, v) in &m { prop_assert_eq!(h.get(*k), Some(v.as_slice())); }
            let mut total = 0;
            for p in 0..h.pages() { prop_assert!(h.used(p) <= 12); total += h.used(p); }
            prop_assert_eq!(total, m.values().map(|v| v.len()).sum::<usize>());
        }
    }
}
''')))

CH.append(C("3c-c5", M3C, "94-challenge-adding-a-column", "build", "Challenge: adding a column", "medium", "stages_3c::s3c_c5",
  ["schema change without rewriting the table","reading old rows through the current schema"],
  ["structs-and-accessors","option-and-result-combinators","model-based-testing"],
  "`EvolvingTable` in `src/catalog/evolving_table.rs`: a table of integer rows whose schema can change. `add_column(default)` appends a column that existing rows read as `default`, **without touching them**; `drop_column(i)` removes a column from every row's view. `get(rid)` always returns rows in the current schema.",
  "`ALTER TABLE ADD COLUMN ... DEFAULT 0` on a table of a billion rows must not take hours. PostgreSQL and MySQL both made it a metadata-only change for exactly this reason: old rows are stored short and the reader fills in the default. The cost moves from the write to every read, which is cheap, and the bookkeeping is what you build.",
  ["`insert(row)` stores a row (its length must equal the current column count; else `None`) and returns a row id.","`add_column(default)` raises the column count by one; rows inserted before read `default` in the new column, rows inserted after store their own value.","`drop_column(i)` removes column `i` from every row (false if out of range). `get(rid)` returns the row in the current schema; `columns()` is the current count."],
  ["Every row read has exactly `columns()` values.","A value read from a column is the one written there, or the column's default if the row predates it."],
  ["Adding a column never changes the values of the columns that existed.","Adding then dropping the last column restores every row's view.","The result equals rewriting every row eagerly at each schema change."],
  ["insert [1,2]; add_column(7); insert [3,4,5]; get(0) = [1,2,7]; drop_column(0); get(0) = [2,7]"],
  ["Defaults for old rows; new rows with their own values.","Drops, in any position.","A property against an eager model."],
  src=("src/catalog/evolving_table.rs", '''
//! A table whose columns can be added and dropped without rewriting its rows.

pub struct EvolvingTable {
    // @begin 3c-c5
    /// rows as stored; a row may be shorter than the number of columns ever added to it.
    rows: Vec<Vec<i64>>,
    /// For each *current* column: which stored position it reads, and the default for rows too short to have it.
    columns: Vec<(usize, i64)>,
    /// How many stored positions exist in total (dropped ones stay as holes).
    stored_width: usize,
    //~ _evolving: (),
    // @end
}

impl EvolvingTable {
    pub fn new(columns: usize) -> EvolvingTable {
        // @begin 3c-c5
        EvolvingTable { rows: Vec::new(), columns: (0..columns).map(|i| (i, 0)).collect(), stored_width: columns }
        //~ todo!("3c-c5: an empty table with `columns` columns")
        // @end
    }

    pub fn columns(&self) -> usize {
        // @begin 3c-c5
        self.columns.len()
        //~ todo!("3c-c5: the number of columns now")
        // @end
    }

    pub fn insert(&mut self, row: &[i64]) -> Option<usize> {
        // @begin 3c-c5
        if row.len() != self.columns.len() {
            return None;
        }
        let mut stored = vec![0; self.stored_width];
        for (&(pos, _), &v) in self.columns.iter().zip(row) {
            stored[pos] = v;
        }
        self.rows.push(stored);
        Some(self.rows.len() - 1)
        //~ todo!("3c-c5: store the row in the stored layout")
        // @end
    }

    pub fn add_column(&mut self, default: i64) {
        // @begin 3c-c5
        self.columns.push((self.stored_width, default));
        self.stored_width += 1;
        //~ todo!("3c-c5: a new column that old rows read as the default")
        // @end
    }

    pub fn drop_column(&mut self, i: usize) -> bool {
        // @begin 3c-c5
        if i >= self.columns.len() {
            return false;
        }
        self.columns.remove(i);
        true
        //~ todo!("3c-c5: hide the column from every row")
        // @end
    }

    pub fn get(&self, rid: usize) -> Option<Vec<i64>> {
        // @begin 3c-c5
        let stored = self.rows.get(rid)?;
        Some(self.columns.iter().map(|&(pos, default)| stored.get(pos).copied().unwrap_or(default)).collect())
        //~ todo!("3c-c5: the row as the current schema sees it")
        // @end
    }
}
'''),
  test=("tests/stages_3c.rs", '''
use bustub::catalog::evolving_table::EvolvingTable;

#[test]
fn s3c_c5_old_rows_read_the_default_of_a_new_column() {
    let mut t = EvolvingTable::new(2);
    let a = t.insert(&[1, 2]).unwrap();
    t.add_column(7);
    let b = t.insert(&[3, 4, 5]).unwrap();
    assert_eq!(t.get(a), Some(vec![1, 2, 7]));
    assert_eq!(t.get(b), Some(vec![3, 4, 5]));
    assert_eq!(t.columns(), 3);
}

#[test]
fn s3c_c5_dropping_a_column_removes_it_from_every_row() {
    let mut t = EvolvingTable::new(2);
    let a = t.insert(&[1, 2]).unwrap();
    t.add_column(7);
    assert!(t.drop_column(0));
    assert_eq!(t.get(a), Some(vec![2, 7]));
    assert!(!t.drop_column(5));
}

#[test]
fn s3c_c5_a_row_of_the_wrong_width_is_refused() {
    let mut t = EvolvingTable::new(2);
    assert_eq!(t.insert(&[1]), None);
    assert_eq!(t.insert(&[1, 2, 3]), None);
    t.add_column(0);
    assert!(t.insert(&[1, 2, 3]).is_some());
}

#[test]
fn s3c_c5_columns_added_later_have_their_own_defaults() {
    let mut t = EvolvingTable::new(1);
    let a = t.insert(&[1]).unwrap();
    t.add_column(10);
    let b = t.insert(&[2, 20]).unwrap();
    t.add_column(30);
    assert_eq!((t.get(a), t.get(b)), (Some(vec![1, 10, 30]), Some(vec![2, 20, 30])));
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 128, failure_persistence: None, ..ProptestConfig::default() })]

    /// Property: equal to a table that rewrites every row eagerly at each schema change.
    #[test]
    fn s3c_c5_property_lazy_defaults_equal_eager_rewriting(ops in proptest::collection::vec((0u8..3, any::<i64>(), 0usize..6), 0..40)) {
        let mut t = EvolvingTable::new(1);
        let mut rows: Vec<Vec<i64>> = Vec::new();
        let mut width = 1usize;
        for (op, v, i) in ops {
            match op {
                0 => { let row: Vec<i64> = (0..width as i64).map(|k| v.wrapping_add(k)).collect(); prop_assert_eq!(t.insert(&row), Some(rows.len())); rows.push(row); }
                1 => { t.add_column(v); for r in &mut rows { r.push(v); } width += 1; }
                _ => { let ok = i < width; prop_assert_eq!(t.drop_column(i), ok); if ok { for r in &mut rows { r.remove(i); } width -= 1; } }
            }
            prop_assert_eq!(t.columns(), width);
            for (rid, r) in rows.iter().enumerate() { prop_assert_eq!(t.get(rid), Some(r.clone())); }
        }
    }
}
''')))
