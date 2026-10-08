//! Port of `src/include/type/value.h` and the per-type files of `src/type/` (`integer_type.cpp`, `varlen_type.cpp`, ...). BusTub has
//! one `Type` subclass per SQL type and a `Value` holding a tagged union; the Rust spelling is one `enum Value` and `match`.
//!
//! A `Value` is a SQL value: a number, a boolean, a string or **NULL** (which still has a type). Like BusTub:
//! * the smallest number of each integer type is reserved as the stored encoding of NULL, so constructing a `Value` with it
//!   gives a NULL (`Value::integer(i32::MIN)` is `NULL`), and the smallest usable value is one above it;
//! * comparisons answer with a three-valued [`CmpBool`] (`NULL = 1` is neither true nor false);
//! * arithmetic with a NULL is NULL; overflow, a bad cast and a division by zero are [`Exception`]s.

use std::fmt;

use super::limits::*;
use super::type_id::TypeId;
use crate::common::exception::{Exception, ExceptionType, Result};

/// A comparison's answer in SQL's three-valued logic. BusTub's `CmpBool`.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CmpBool {
    False,
    True,
    Null,
}

impl CmpBool {
    pub fn from_bool(b: bool) -> CmpBool {
        if b {
            CmpBool::True
        } else {
            CmpBool::False
        }
    }
}

#[derive(Clone, Debug, PartialEq)]
pub enum Value {
    /// NULL of a type (`Null(TypeId::Integer)` is the integer NULL; every type has one).
    Null(TypeId),
    Boolean(bool),
    TinyInt(i8),
    SmallInt(i16),
    Integer(i32),
    BigInt(i64),
    Decimal(f64),
    /// A timestamp is carried and compared as a number; this course does not parse or format dates.
    Timestamp(u64),
    Varchar(String),
}

fn err(kind: ExceptionType, message: impl Into<String>) -> Exception {
    Exception::new(kind, message)
}

fn out_of_range() -> Exception {
    err(ExceptionType::OutOfRange, "Numeric value out of range.")
}

impl Value {
    // ---- 3a-02 · constructing values ----------------------------------------------------------------------------------------

    /// NULL of `type_id`. BusTub: `Value(type_id)`.
    pub fn null(type_id: TypeId) -> Value {
        todo!("3a-02: the NULL of that type")
    }

    pub fn boolean(b: bool) -> Value {
        todo!("3a-02: a BOOLEAN")
    }

    /// A TINYINT; `BUSTUB_INT8_NULL` (`i8::MIN`) is the stored encoding of NULL, so that number gives a NULL.
    pub fn tinyint(v: i8) -> Value {
        todo!("3a-02: a TINYINT, or the TINYINT NULL for the reserved number i8::MIN")
    }

    pub fn smallint(v: i16) -> Value {
        todo!("3a-02: like tinyint, for i16")
    }

    pub fn integer(v: i32) -> Value {
        todo!("3a-02: like tinyint, for i32")
    }

    pub fn bigint(v: i64) -> Value {
        todo!("3a-02: like tinyint, for i64")
    }

    /// A DECIMAL; `BUSTUB_DECIMAL_NULL` (the lowest `f64`) is the NULL encoding.
    pub fn decimal(v: f64) -> Value {
        todo!("3a-02: a DECIMAL, or the DECIMAL NULL for the reserved number f64::MIN")
    }

    pub fn timestamp(v: u64) -> Value {
        todo!("3a-02: a TIMESTAMP, or the TIMESTAMP NULL for u64::MAX")
    }

    pub fn varchar(s: &str) -> Value {
        todo!("3a-02: a VARCHAR holding the string")
    }

    pub fn type_id(&self) -> TypeId {
        todo!("3a-02: the type of the value (a NULL has the type it was made with)")
    }

    pub fn is_null(&self) -> bool {
        todo!("3a-02: is this a NULL")
    }

    /// Any integer type's value as an `i64` (`None` for NULL and the other types).
    pub fn as_i64(&self) -> Option<i64> {
        todo!("3a-02: Some for TINYINT, SMALLINT, INTEGER and BIGINT values, widened; None otherwise")
    }

    /// Any numeric type's value as an `f64` (`None` for NULL and the non-numeric types).
    pub fn as_f64(&self) -> Option<f64> {
        todo!("3a-02: Some for the numeric types (integers widened to f64); None otherwise")
    }

    pub fn as_bool(&self) -> Option<bool> {
        match self {
            Value::Boolean(b) => Some(*b),
            _ => None,
        }
    }

    pub fn as_str(&self) -> Option<&str> {
        match self {
            Value::Varchar(s) => Some(s),
            _ => None,
        }
    }

    /// Can `self` be compared with `other`? BusTub's `Value::CheckComparable`: a boolean with a boolean or a string, a number with a
    /// number or a string, a string with anything, a timestamp with a timestamp.
    pub fn check_comparable(&self, other: &Value) -> bool {
        todo!("3a-02: the comparability table in the doc comment")
    }

    // ---- 3a-03 · casting ----------------------------------------------------------------------------------------------------

    /// Converts the value to another type (BusTub's `CastAs`).
    /// * Numbers (integers and decimal) convert to each other and to `Varchar` (the number as text). A narrower integer type must be
    ///   able to hold the number (else `OutOfRange`); a decimal truncates toward zero.
    /// * A `Varchar` converts to a boolean (`true`/`1`/`t`, `false`/`0`/`f`, any case), a number (the leading number in the text: `"32"`,
    ///   `" -7"`, `"12abc"` is 12) or itself. No digits is a `Conversion` error.
    /// * A boolean converts to itself and to `Varchar`; a timestamp to itself and to `Varchar`. Anything else is an error ("X is not
    ///   coercable to Y").
    /// * A NULL converts to the NULL of the target type (if the conversion is allowed at all).
    pub fn cast_as(&self, to: TypeId) -> Result<Value> {
        todo!("3a-03: check the conversion is allowed (the table in the doc comment); a NULL becomes the NULL of the target; a number to VARCHAR is its text; otherwise convert, checking the range of the target")
    }

    // ---- 3a-04 · comparing --------------------------------------------------------------------------------------------------

    /// Compares `self` with `other`: `None` if either is NULL, otherwise the ordering. A number and a string compare after the string
    /// is converted to the number's type; a boolean and a string after the string is converted to a boolean; a string and a number (or
    /// anything else) after the other value is converted to text. Incomparable types are an error.
    fn compare(&self, other: &Value) -> Result<Option<std::cmp::Ordering>> {
        todo!("3a-04: NULL on either side: None; otherwise convert the second value as the doc comment says and compare (two integers exactly; anything with a decimal as f64)")
    }

    fn cmp_with(&self, other: &Value, f: impl Fn(std::cmp::Ordering) -> bool) -> Result<CmpBool> {
        Ok(match self.compare(other)? {
            None => CmpBool::Null,
            Some(ord) => CmpBool::from_bool(f(ord)),
        })
    }

    pub fn compare_equals(&self, other: &Value) -> Result<CmpBool> {
        todo!("3a-04: Null if either is NULL, else whether they are equal")
    }

    pub fn compare_not_equals(&self, other: &Value) -> Result<CmpBool> {
        todo!("3a-04: Null if either is NULL, else whether they differ")
    }

    pub fn compare_less_than(&self, other: &Value) -> Result<CmpBool> {
        todo!("3a-04: Null if either is NULL, else self < other")
    }

    pub fn compare_less_than_equals(&self, other: &Value) -> Result<CmpBool> {
        todo!("3a-04: Null if either is NULL, else self <= other")
    }

    pub fn compare_greater_than(&self, other: &Value) -> Result<CmpBool> {
        todo!("3a-04: Null if either is NULL, else self > other")
    }

    pub fn compare_greater_than_equals(&self, other: &Value) -> Result<CmpBool> {
        todo!("3a-04: Null if either is NULL, else self >= other")
    }

    /// Equal in the sense of grouping and hashing, not of SQL: two NULLs are equal here (BusTub's `CompareExactlyEquals`).
    pub fn compare_exactly_equals(&self, other: &Value) -> bool {
        todo!("3a-04: true for two NULLs; otherwise whether compare_equals says True (an error counts as false)")
    }

    // ---- 3a-05 · arithmetic -------------------------------------------------------------------------------------------------

    /// What an arithmetic operation with a NULL gives: the NULL of the result type (the wider integer type, or DECIMAL if either side is a
    /// decimal). BusTub's `OperateNull`.
    pub fn operate_null(&self, other: &Value) -> Result<Value> {
        todo!("3a-05: the NULL of the result type: DECIMAL if either is DECIMAL, else the wider integer type (a string on the right counts as the left's type); non-numeric operands are an error")
    }

    pub fn is_zero(&self) -> Result<bool> {
        todo!("3a-05: is a numeric value zero; other types are a NotImplemented error")
    }

    fn arithmetic(&self, other: &Value, op: Op) -> Result<Value> {
        todo!("3a-05: NULL on either side: operate_null; a string on the right is converted to the left's type; dividing (or taking a modulo) by zero is a DivideByZero error; the result type is the wider of the two; DECIMAL arithmetic in f64 (modulo is x - trunc(x / y) * y); integers exactly, OutOfRange if the result does not fit the result type")
    }

    fn is_zero_after_cast(&self, left: TypeId) -> Result<bool> {
        if self.type_id() == TypeId::Varchar {
            return self.cast_as(left)?.is_zero();
        }
        self.is_zero()
    }

    pub fn add(&self, other: &Value) -> Result<Value> {
        todo!("3a-05: self + other")
    }

    pub fn subtract(&self, other: &Value) -> Result<Value> {
        todo!("3a-05: self - other")
    }

    pub fn multiply(&self, other: &Value) -> Result<Value> {
        todo!("3a-05: self * other")
    }

    pub fn divide(&self, other: &Value) -> Result<Value> {
        todo!("3a-05: self / other (integers divide toward zero)")
    }

    pub fn modulo(&self, other: &Value) -> Result<Value> {
        todo!("3a-05: self % other")
    }

    /// The smaller of the two (a NULL on either side gives a NULL). Works on numbers and strings.
    pub fn min(&self, other: &Value) -> Result<Value> {
        todo!("3a-05: NULL if either is NULL; otherwise the smaller of the two by compare_less_than_equals")
    }

    /// The larger of the two (a NULL on either side gives a NULL).
    pub fn max(&self, other: &Value) -> Result<Value> {
        todo!("3a-05: NULL if either is NULL; otherwise the larger of the two by compare_greater_than_equals")
    }

    fn operate_null_or_varchar(&self, other: &Value) -> Result<Value> {
        if self.type_id() == TypeId::Varchar {
            Ok(Value::Null(TypeId::Varchar))
        } else {
            self.operate_null(other)
        }
    }

    /// The square root as a DECIMAL (NULL for NULL). A negative number is a `Decimal` error.
    pub fn sqrt(&self) -> Result<Value> {
        todo!("3a-05: NULL for NULL; a negative number is a Decimal error; otherwise the square root as a DECIMAL")
    }

    // ---- 3a-06 · storage ----------------------------------------------------------------------------------------------------

    /// How many bytes `serialize_to` writes. Fixed-size types: their size. A `Varchar`: a 4-byte length, then the text and a terminating
    /// zero byte (the length counts that zero byte, like BusTub's `GetStorageSize`); a NULL string is just the 4-byte marker.
    pub fn storage_size(&self) -> usize {
        todo!("3a-06: the number of bytes serialize_to writes: the type's size, or for VARCHAR 4 + the text + 1 (a NULL VARCHAR: 4)")
    }

    /// Writes the value into `storage` (at least `storage_size()` bytes), little-endian. A NULL is written as its reserved encoding
    /// (`i32::MIN` for an INTEGER, ...; a VARCHAR as the length `u32::MAX`), a boolean as one byte 0 or 1.
    pub fn serialize_to(&self, storage: &mut [u8]) {
        todo!("3a-06: write the value little-endian at the start of storage; a NULL as its reserved encoding; a VARCHAR as a 4-byte length (text + 1) then the text and a zero byte")
    }

    /// Reads a value of `type_id` from the start of `storage`. The inverse of `serialize_to`: a reserved encoding is a NULL.
    pub fn deserialize_from(storage: &[u8], type_id: TypeId) -> Result<Value> {
        todo!("3a-06: read the type's bytes little-endian; the reserved encodings are NULLs (the typed constructors already do that for the numbers); a VARCHAR: a 4-byte length (u32::MAX is NULL), then length - 1 bytes of text")
    }
}

#[derive(Clone, Copy, Debug)]
enum Op {
    Add,
    Subtract,
    Multiply,
    Divide,
    Modulo,
}

impl Op {
    fn divides(self) -> bool {
        matches!(self, Op::Divide | Op::Modulo)
    }
}

/// The type an operation on two numbers produces: DECIMAL if either is, else the wider integer type.
fn wider(a: TypeId, b: TypeId) -> TypeId {
    if a == TypeId::Decimal || b == TypeId::Decimal {
        TypeId::Decimal
    } else {
        a.max(b)
    }
}

/// Converts an integer to `to` (an integer type, DECIMAL), checking that the target can hold it (the reserved NULL number cannot be a value).
fn cast_integer(v: i64, to: TypeId) -> Result<Value> {
    todo!("3a-03: the value as the target type; OutOfRange if it is outside [MIN + 1, MAX] of the target (the NULL encoding is not a value); DECIMAL: the number as f64")
}

fn cast_decimal(d: f64, to: TypeId) -> Result<Value> {
    todo!("3a-03: DECIMAL stays; to an integer type: OutOfRange if the number is outside the target's range, else truncate toward zero")
}

/// Converts a string to `to`: the number or boolean written at its start.
fn cast_text(s: &str, to: TypeId) -> Result<Value> {
    todo!("3a-03: VARCHAR stays; BOOLEAN: true/1/t or false/0/f in any case (else an error); a number type: parse the leading number (leading_number gives its text; no digits is a Conversion error), OutOfRange if it does not fit")
}

/// The text of the number at the start of `s` after optional white space: an optional sign and digits (and, for decimals, a fraction and an
/// exponent). `None` if there are no digits. Like C++'s `std::stoi` / `std::stod`, anything after the number is ignored.
fn leading_number(s: &str, decimal: bool) -> Option<&str> {
    let s = s.trim_start();
    let bytes = s.as_bytes();
    let mut i = 0;
    if i < bytes.len() && (bytes[i] == b'+' || bytes[i] == b'-') {
        i += 1;
    }
    let digits_start = i;
    while i < bytes.len() && bytes[i].is_ascii_digit() {
        i += 1;
    }
    if decimal && i < bytes.len() && bytes[i] == b'.' {
        i += 1;
        while i < bytes.len() && bytes[i].is_ascii_digit() {
            i += 1;
        }
    }
    if i == digits_start || (decimal && i == digits_start + 1 && bytes[digits_start] == b'.') {
        return None;
    }
    if decimal && i < bytes.len() && (bytes[i] == b'e' || bytes[i] == b'E') {
        let mut j = i + 1;
        if j < bytes.len() && (bytes[j] == b'+' || bytes[j] == b'-') {
            j += 1;
        }
        let exp_start = j;
        while j < bytes.len() && bytes[j].is_ascii_digit() {
            j += 1;
        }
        if j > exp_start {
            i = j;
        }
    }
    Some(&s[..i])
}

impl fmt::Display for Value {
    /// BusTub's `ToString`: booleans `true`/`false`, integers in decimal, decimals with six digits after the point (`3.140000`, C++'s
    /// `std::to_string`), strings as they are, timestamps as the number; a NULL as `<type>_null` (`integer_null`, `varlen_null`, ...).
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        todo!("3a-02: the text of the value as the doc comment says")
    }
}
