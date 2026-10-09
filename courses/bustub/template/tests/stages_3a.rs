//! Tests for the values and types stages (3a-01 … 3a-06). A test named `s3a_03_…` belongs to stage 3a-03.

use bustub::common::exception::ExceptionType;
use bustub::types::limits::*;
use bustub::types::type_id::TypeId;
use bustub::types::value::{CmpBool, Value};

use TypeId::*;

const ALL: [TypeId; 9] = [Invalid, Boolean, TinyInt, SmallInt, Integer, BigInt, Decimal, Varchar, Timestamp];

fn kind<T: std::fmt::Debug>(r: Result<T, bustub::common::exception::Exception>) -> ExceptionType {
    r.expect_err("expected an exception").kind
}

// ---- 3a-01 · Types and what is true of each ---------------------------------------------------------------------------------------

#[test]
fn s3a_01_every_type_has_a_size_in_bytes() {
    let sizes: Vec<u64> = [Boolean, TinyInt, SmallInt, Integer, BigInt, Decimal, Timestamp, Varchar].iter().map(|t| t.type_size().unwrap()).collect();
    assert_eq!(sizes, vec![1, 1, 2, 4, 8, 8, 8, 0], "a VARCHAR's bytes are not in the fixed part: size 0");
}

#[test]
fn s3a_01_the_invalid_type_has_no_size() {
    assert_eq!(kind(Invalid.type_size()), ExceptionType::UnknownType, "the invalid type has no size");
}

#[test]
fn s3a_01_types_print_their_sql_names() {
    let names: Vec<&str> = ALL.iter().map(|t| t.type_id_to_string()).collect();
    assert_eq!(names, vec!["INVALID", "BOOLEAN", "TINYINT", "SMALLINT", "INTEGER", "BIGINT", "DECIMAL", "VARCHAR", "TIMESTAMP"], "types print their sql names");
}

#[test]
fn s3a_01_the_coercion_table_is_exactly_bustubs() {
    // for every target and every source: BusTub's `Type::IsCoercableFrom`
    let numeric = [TinyInt, SmallInt, Integer, BigInt, Decimal];
    for target in ALL {
        for from in ALL {
            let expected = match target {
                Invalid => false,
                Boolean => true,
                t if numeric.contains(&t) => numeric.contains(&from) || from == Varchar,
                Timestamp => matches!(from, Varchar | Timestamp),
                Varchar => from != Invalid,
                _ => unreachable!(),
            };
            assert_eq!(target.is_coercable_from(from), expected, "{target:?} from {from:?}");
        }
    }
}

#[test]
fn s3a_01_a_type_is_always_coercable_from_itself_except_invalid() {
    for t in ALL.into_iter().filter(|&t| t != Invalid) {
        assert!(t.is_coercable_from(t), "{t:?}");
    }
    assert!(!Invalid.is_coercable_from(Invalid), "a type is always coercable from itself except invalid: expected `!Invalid.is_coercable_from(Invalid)`");
    assert!(!Integer.is_coercable_from(Boolean), "a number cannot be made from a boolean");
}

// ---- 3a-02 · Constructing values -------------------------------------------------------------------------------------------------

#[test]
fn s3a_02_values_know_their_type_and_their_number() {
    assert_eq!(Value::boolean(true).type_id(), Boolean, "values know their type and their number");
    assert_eq!(Value::tinyint(7).type_id(), TinyInt, "values know their type and their number");
    assert_eq!(Value::integer(-42).as_i64(), Some(-42), "values know their type and their number");
    assert_eq!(Value::bigint(1 << 40).as_i64(), Some(1 << 40), "values know their type and their number");
    assert_eq!(Value::decimal(2.5).as_f64(), Some(2.5), "values know their type and their number");
    assert_eq!(Value::integer(3).as_f64(), Some(3.0), "an integer is also a number for as_f64");
    assert_eq!(Value::varchar("héllo").as_str(), Some("héllo"), "values know their type and their number");
    assert_eq!(Value::varchar("x").as_i64(), None, "values know their type and their number");
    assert!(!Value::integer(0).is_null(), "values know their type and their number: expected `!Value::integer(0).is_null()`");
}

#[test]
fn s3a_02_the_reserved_number_makes_a_null() {
    assert!(Value::tinyint(i8::MIN).is_null(), "the reserved number makes a null: expected `Value::tinyint(i8::MIN).is_null()`");
    assert!(Value::smallint(i16::MIN).is_null(), "the reserved number makes a null: expected `Value::smallint(i16::MIN).is_null()`");
    assert!(Value::integer(i32::MIN).is_null(), "the reserved number makes a null: expected `Value::integer(i32::MIN).is_null()`");
    assert!(Value::bigint(i64::MIN).is_null(), "the reserved number makes a null: expected `Value::bigint(i64::MIN).is_null()`");
    assert!(Value::decimal(f64::MIN).is_null(), "the reserved number makes a null: expected `Value::decimal(f64::MIN).is_null()`");
    assert!(Value::timestamp(u64::MAX).is_null(), "the reserved number makes a null: expected `Value::timestamp(u64::MAX).is_null()`");
    assert_eq!(Value::integer(i32::MIN).type_id(), Integer, "a NULL keeps its type");
    assert!(!Value::integer(i32::MIN + 1).is_null(), "the reserved number makes a null: expected `!Value::integer(i32::MIN + 1).is_null()`");
    assert_eq!(Value::null(Varchar).type_id(), Varchar, "the reserved number makes a null");
    assert!(Value::null(Boolean).is_null(), "the reserved number makes a null: expected `Value::null(Boolean).is_null()`");
    assert_eq!(Value::null(Integer).as_i64(), None, "the reserved number makes a null");
}

#[test]
fn s3a_02_minimum_and_maximum_values() {
    assert_eq!(Integer.min_value().unwrap(), Value::Integer(BUSTUB_INT32_MIN), "minimum and maximum values");
    assert_eq!(Integer.max_value().unwrap(), Value::Integer(i32::MAX), "minimum and maximum values");
    assert_eq!(TinyInt.min_value().unwrap().as_i64(), Some(-127), "-128 is the NULL encoding");
    assert_eq!(BigInt.max_value().unwrap().as_i64(), Some(i64::MAX), "minimum and maximum values");
    assert_eq!(Boolean.min_value().unwrap(), Value::Boolean(false), "minimum and maximum values");
    assert_eq!(Boolean.max_value().unwrap(), Value::Boolean(true), "minimum and maximum values");
    assert_eq!(Varchar.min_value().unwrap(), Value::varchar(""), "minimum and maximum values");
    assert!(Varchar.max_value().unwrap().is_null(), "there is no largest string");
    for t in [Boolean, TinyInt, SmallInt, Integer, BigInt, Decimal, Timestamp] {
        assert!(!t.min_value().unwrap().is_null() && !t.max_value().unwrap().is_null(), "{t:?}");
    }
    assert_eq!(kind(Invalid.min_value()), ExceptionType::MismatchType, "minimum and maximum values");
    assert_eq!(kind(Invalid.max_value()), ExceptionType::MismatchType, "minimum and maximum values");
}

#[test]
fn s3a_02_values_print_like_bustub() {
    assert_eq!(Value::boolean(true).to_string(), "true", "values print like bustub");
    assert_eq!(Value::boolean(false).to_string(), "false", "values print like bustub");
    assert_eq!(Value::integer(-5).to_string(), "-5", "values print like bustub");
    assert_eq!(Value::decimal(3.14).to_string(), "3.140000", "six digits after the point, like std::to_string");
    assert_eq!(Value::varchar("hi there").to_string(), "hi there", "values print like bustub");
    assert_eq!(Value::null(Integer).to_string(), "integer_null", "values print like bustub");
    assert_eq!(Value::null(Varchar).to_string(), "varlen_null", "values print like bustub");
    assert_eq!(Value::null(Decimal).to_string(), "decimal_null", "values print like bustub");
    assert_eq!(Value::null(Boolean).to_string(), "boolean_null", "values print like bustub");
}

#[test]
fn s3a_02_which_types_can_be_compared() {
    let (i, d, s, b, t) = (Value::integer(1), Value::decimal(1.0), Value::varchar("1"), Value::boolean(true), Value::timestamp(5));
    assert!(i.check_comparable(&d) && d.check_comparable(&i) && i.check_comparable(&s), "which types can be compared: expected `i.check_comparable(&d) && d.check_comparable(&i) && i.check_comparable(&s)`");
    assert!(s.check_comparable(&b) && s.check_comparable(&t) && s.check_comparable(&i), "anything can be compared with a string");
    assert!(b.check_comparable(&b) && b.check_comparable(&s), "which types can be compared: expected `b.check_comparable(&b) && b.check_comparable(&s)`");
    assert!(!b.check_comparable(&i) && !i.check_comparable(&b), "a boolean is not a number");
    assert!(t.check_comparable(&t) && !t.check_comparable(&i), "which types can be compared: expected `t.check_comparable(&t) && !t.check_comparable(&i)`");
}

// ---- 3a-03 · Casting -------------------------------------------------------------------------------------------------------------

#[test]
fn s3a_03_numbers_convert_to_wider_and_to_narrower_types_when_they_fit() {
    assert_eq!(Value::integer(5).cast_as(BigInt).unwrap(), Value::bigint(5), "numbers convert to wider and to narrower types when they fit");
    assert_eq!(Value::tinyint(-3).cast_as(Integer).unwrap(), Value::integer(-3), "numbers convert to wider and to narrower types when they fit");
    assert_eq!(Value::integer(100).cast_as(TinyInt).unwrap(), Value::tinyint(100), "numbers convert to wider and to narrower types when they fit");
    assert_eq!(Value::bigint(70_000).cast_as(Integer).unwrap(), Value::integer(70_000), "numbers convert to wider and to narrower types when they fit");
    assert_eq!(Value::integer(5).cast_as(Decimal).unwrap(), Value::decimal(5.0), "numbers convert to wider and to narrower types when they fit");
    assert_eq!(kind(Value::integer(128).cast_as(TinyInt)), ExceptionType::OutOfRange, "numbers convert to wider and to narrower types when they fit");
    assert_eq!(kind(Value::integer(-128).cast_as(TinyInt)), ExceptionType::OutOfRange, "-128 is the NULL encoding of TINYINT: not a value");
    assert_eq!(kind(Value::bigint(1 << 40).cast_as(Integer)), ExceptionType::OutOfRange, "numbers convert to wider and to narrower types when they fit");
    assert_eq!(kind(Value::integer(40_000).cast_as(SmallInt)), ExceptionType::OutOfRange, "numbers convert to wider and to narrower types when they fit");
}

#[test]
fn s3a_03_a_decimal_truncates_toward_zero_and_checks_the_range() {
    assert_eq!(Value::decimal(3.99).cast_as(Integer).unwrap(), Value::integer(3), "a decimal truncates toward zero and checks the range");
    assert_eq!(Value::decimal(-3.99).cast_as(Integer).unwrap(), Value::integer(-3), "a decimal truncates toward zero and checks the range");
    assert_eq!(Value::decimal(2.5).cast_as(Decimal).unwrap(), Value::decimal(2.5), "a decimal truncates toward zero and checks the range");
    assert_eq!(Value::decimal(127.0).cast_as(TinyInt).unwrap(), Value::tinyint(127), "a decimal truncates toward zero and checks the range");
    assert_eq!(kind(Value::decimal(128.0).cast_as(TinyInt)), ExceptionType::OutOfRange, "a decimal truncates toward zero and checks the range");
    assert_eq!(kind(Value::decimal(1e30).cast_as(BigInt)), ExceptionType::OutOfRange, "a decimal truncates toward zero and checks the range");
    assert_eq!(kind(Value::decimal(-3e9).cast_as(Integer)), ExceptionType::OutOfRange, "a decimal truncates toward zero and checks the range");
}

#[test]
fn s3a_03_anything_can_become_text_and_text_can_become_a_number() {
    assert_eq!(Value::integer(-7).cast_as(Varchar).unwrap(), Value::varchar("-7"), "anything can become text and text can become a number");
    assert_eq!(Value::decimal(1.5).cast_as(Varchar).unwrap(), Value::varchar("1.500000"), "anything can become text and text can become a number");
    assert_eq!(Value::boolean(true).cast_as(Varchar).unwrap(), Value::varchar("true"), "anything can become text and text can become a number");
    assert_eq!(Value::varchar("32").cast_as(Integer).unwrap(), Value::integer(32), "anything can become text and text can become a number");
    assert_eq!(Value::varchar("  -7").cast_as(BigInt).unwrap(), Value::bigint(-7), "anything can become text and text can become a number");
    assert_eq!(Value::varchar("12abc").cast_as(SmallInt).unwrap(), Value::smallint(12), "like std::stoi: the leading number");
    assert_eq!(Value::varchar("2.5e1").cast_as(Decimal).unwrap(), Value::decimal(25.0), "anything can become text and text can become a number");
    assert_eq!(Value::varchar("abc").cast_as(Varchar).unwrap(), Value::varchar("abc"), "anything can become text and text can become a number");
    assert_eq!(kind(Value::varchar("abc").cast_as(Integer)), ExceptionType::Conversion, "anything can become text and text can become a number");
    assert_eq!(kind(Value::varchar("").cast_as(Integer)), ExceptionType::Conversion, "anything can become text and text can become a number");
    assert_eq!(kind(Value::varchar("300").cast_as(TinyInt)), ExceptionType::OutOfRange, "anything can become text and text can become a number");
    assert_eq!(kind(Value::varchar("99999999999").cast_as(Integer)), ExceptionType::OutOfRange, "anything can become text and text can become a number");
}

#[test]
fn s3a_03_text_becomes_a_boolean_only_in_the_known_spellings() {
    for yes in ["true", "TRUE", "1", "t", "T"] {
        assert_eq!(Value::varchar(yes).cast_as(Boolean).unwrap(), Value::boolean(true), "{yes}");
    }
    for no in ["false", "False", "0", "f"] {
        assert_eq!(Value::varchar(no).cast_as(Boolean).unwrap(), Value::boolean(false), "{no}");
    }
    assert!(Value::varchar("yes").cast_as(Boolean).is_err(), "text becomes a boolean only in the known spellings: expected `Value::varchar(\"yes\").cast_as(Boolean).is_err()`");
    assert!(Value::varchar("2").cast_as(Boolean).is_err(), "text becomes a boolean only in the known spellings: expected `Value::varchar(\"2\").cast_as(Boolean).is_err()`");
}

#[test]
fn s3a_03_a_null_becomes_the_null_of_the_target_and_impossible_casts_are_errors() {
    assert_eq!(Value::null(Integer).cast_as(BigInt).unwrap(), Value::null(BigInt), "a null becomes the null of the target and impossible casts are errors");
    assert_eq!(Value::null(Integer).cast_as(Varchar).unwrap(), Value::null(Varchar), "a null becomes the null of the target and impossible casts are errors");
    assert_eq!(Value::null(Varchar).cast_as(Integer).unwrap(), Value::null(Integer), "a null becomes the null of the target and impossible casts are errors");
    assert!(Value::null(Integer).cast_as(Boolean).is_err(), "even a NULL cannot go where its type cannot");
    assert!(Value::integer(1).cast_as(Boolean).is_err(), "a null becomes the null of the target and impossible casts are errors: expected `Value::integer(1).cast_as(Boolean).is_err()`");
    assert!(Value::boolean(true).cast_as(Integer).is_err(), "a null becomes the null of the target and impossible casts are errors: expected `Value::boolean(true).cast_as(Integer).is_err()`");
    assert!(Value::decimal(1.0).cast_as(Timestamp).is_err(), "a null becomes the null of the target and impossible casts are errors: expected `Value::decimal(1.0).cast_as(Timestamp).is_err()`");
    assert_eq!(Value::timestamp(9).cast_as(Varchar).unwrap(), Value::varchar("9"), "a null becomes the null of the target and impossible casts are errors");
    assert_eq!(Value::timestamp(9).cast_as(Timestamp).unwrap(), Value::timestamp(9), "a null becomes the null of the target and impossible casts are errors");
}

// ---- 3a-04 · Comparing -----------------------------------------------------------------------------------------------------------

#[test]
fn s3a_04_numbers_compare_across_types() {
    let (i, big, dec) = (Value::integer(5), Value::bigint(5), Value::decimal(5.0));
    assert_eq!(i.compare_equals(&big).unwrap(), CmpBool::True, "numbers compare across types");
    assert_eq!(big.compare_equals(&dec).unwrap(), CmpBool::True, "numbers compare across types");
    assert_eq!(dec.compare_equals(&i).unwrap(), CmpBool::True, "numbers compare across types");
    assert_eq!(Value::tinyint(3).compare_less_than(&Value::bigint(1 << 40)).unwrap(), CmpBool::True, "numbers compare across types");
    assert_eq!(Value::integer(3).compare_greater_than(&Value::decimal(3.5)).unwrap(), CmpBool::False, "numbers compare across types");
    assert_eq!(Value::smallint(-1).compare_less_than_equals(&Value::integer(-1)).unwrap(), CmpBool::True, "numbers compare across types");
    assert_eq!(Value::integer(2).compare_greater_than_equals(&Value::integer(3)).unwrap(), CmpBool::False, "numbers compare across types");
    assert_eq!(Value::integer(2).compare_not_equals(&Value::integer(3)).unwrap(), CmpBool::True, "numbers compare across types");
}

#[test]
fn s3a_04_a_comparison_with_null_is_null_not_false() {
    let n = Value::null(Integer);
    for other in [Value::integer(1), Value::null(Integer), Value::decimal(1.0)] {
        assert_eq!(n.compare_equals(&other).unwrap(), CmpBool::Null, "a comparison with null is null not false");
        assert_eq!(n.compare_not_equals(&other).unwrap(), CmpBool::Null, "a comparison with null is null not false");
        assert_eq!(n.compare_less_than(&other).unwrap(), CmpBool::Null, "a comparison with null is null not false");
        assert_eq!(other.compare_greater_than_equals(&n).unwrap(), CmpBool::Null, "a comparison with null is null not false");
    }
    assert_eq!(Value::varchar("a").compare_equals(&Value::null(Varchar)).unwrap(), CmpBool::Null, "a comparison with null is null not false");
    assert_eq!(Value::boolean(true).compare_equals(&Value::null(Boolean)).unwrap(), CmpBool::Null, "a comparison with null is null not false");
}

#[test]
fn s3a_04_strings_compare_bytewise_and_mixed_types_go_through_text() {
    assert_eq!(Value::varchar("abc").compare_less_than(&Value::varchar("abd")).unwrap(), CmpBool::True, "strings compare bytewise and mixed types go through text");
    assert_eq!(Value::varchar("ab").compare_less_than(&Value::varchar("abc")).unwrap(), CmpBool::True, "a prefix is smaller");
    assert_eq!(Value::varchar("B").compare_less_than(&Value::varchar("a")).unwrap(), CmpBool::True, "bytewise: upper case first");
    assert_eq!(Value::varchar("").compare_equals(&Value::varchar("")).unwrap(), CmpBool::True, "strings compare bytewise and mixed types go through text");
    // the test from BusTub's type_test: the string "32" equals the integer 32 (in both directions)
    assert_eq!(Value::varchar("32").compare_equals(&Value::integer(32)).unwrap(), CmpBool::True, "strings compare bytewise and mixed types go through text");
    assert_eq!(Value::integer(32).compare_equals(&Value::varchar("32")).unwrap(), CmpBool::True, "strings compare bytewise and mixed types go through text");
    assert_eq!(Value::integer(5).compare_less_than(&Value::varchar("12")).unwrap(), CmpBool::True, "the string is converted to the number's type, not the reverse");
    assert_eq!(Value::varchar("5").compare_less_than(&Value::integer(12)).unwrap(), CmpBool::False, "as text, '5' is greater than '12'");
}

#[test]
fn s3a_04_booleans_compare_and_incomparable_types_are_errors() {
    assert_eq!(Value::boolean(false).compare_less_than(&Value::boolean(true)).unwrap(), CmpBool::True, "booleans compare and incomparable types are errors");
    assert_eq!(Value::boolean(true).compare_equals(&Value::varchar("T")).unwrap(), CmpBool::True, "booleans compare and incomparable types are errors");
    assert!(Value::boolean(true).compare_equals(&Value::integer(1)).is_err(), "booleans compare and incomparable types are errors: expected `Value::boolean(true).compare_equals(&Value::integer(1)).is_err()`");
    assert!(Value::integer(1).compare_equals(&Value::boolean(true)).is_err(), "booleans compare and incomparable types are errors: expected `Value::integer(1).compare_equals(&Value::boolean(true)).is_err()`");
    assert!(Value::timestamp(1).compare_equals(&Value::integer(1)).is_err(), "booleans compare and incomparable types are errors: expected `Value::timestamp(1).compare_equals(&Value::integer(1)).is_err()`");
    assert_eq!(Value::timestamp(1).compare_less_than(&Value::timestamp(2)).unwrap(), CmpBool::True, "booleans compare and incomparable types are errors");
}

#[test]
fn s3a_04_exact_equality_is_for_grouping_two_nulls_are_the_same_group() {
    assert!(Value::null(Integer).compare_exactly_equals(&Value::null(Integer)), "exact equality is for grouping two nulls are the same group: expected `Value::null(Integer).compare_exactly_equals(&Value::null(Integer))`");
    assert!(!Value::null(Integer).compare_exactly_equals(&Value::integer(1)), "exact equality is for grouping two nulls are the same group: expected `!Value::null(Integer).compare_exactly_equals(&Value::integer(1))`");
    assert!(Value::integer(1).compare_exactly_equals(&Value::bigint(1)), "exact equality is for grouping two nulls are the same group: expected `Value::integer(1).compare_exactly_equals(&Value::bigint(1))`");
    assert!(!Value::integer(1).compare_exactly_equals(&Value::integer(2)), "exact equality is for grouping two nulls are the same group: expected `!Value::integer(1).compare_exactly_equals(&Value::integer(2))`");
    assert!(!Value::boolean(true).compare_exactly_equals(&Value::integer(1)), "an error counts as not equal");
}

// ---- 3a-05 · Arithmetic ----------------------------------------------------------------------------------------------------------

#[test]
fn s3a_05_integers_add_subtract_multiply_divide_and_take_a_modulo() {
    let (a, b) = (Value::integer(17), Value::integer(5));
    assert_eq!(a.add(&b).unwrap(), Value::integer(22), "integers add subtract multiply divide and take a modulo");
    assert_eq!(a.subtract(&b).unwrap(), Value::integer(12), "integers add subtract multiply divide and take a modulo");
    assert_eq!(a.multiply(&b).unwrap(), Value::integer(85), "integers add subtract multiply divide and take a modulo");
    assert_eq!(a.divide(&b).unwrap(), Value::integer(3), "integer division");
    assert_eq!(a.modulo(&b).unwrap(), Value::integer(2), "integers add subtract multiply divide and take a modulo");
    assert_eq!(Value::integer(-17).divide(&b).unwrap(), Value::integer(-3), "toward zero");
    assert_eq!(Value::integer(-17).modulo(&b).unwrap(), Value::integer(-2), "the sign of the dividend");
}

#[test]
fn s3a_05_the_result_has_the_wider_type() {
    assert_eq!(Value::tinyint(1).add(&Value::integer(1)).unwrap().type_id(), Integer, "the result has the wider type");
    assert_eq!(Value::integer(1).add(&Value::tinyint(1)).unwrap().type_id(), Integer, "the result has the wider type");
    assert_eq!(Value::integer(1).add(&Value::bigint(1)).unwrap().type_id(), BigInt, "the result has the wider type");
    assert_eq!(Value::smallint(1).multiply(&Value::bigint(2)).unwrap(), Value::bigint(2), "the result has the wider type");
    assert_eq!(Value::integer(1).add(&Value::decimal(0.5)).unwrap(), Value::decimal(1.5), "the result has the wider type");
    assert_eq!(Value::decimal(0.5).add(&Value::bigint(1)).unwrap(), Value::decimal(1.5), "the result has the wider type");
    assert_eq!(Value::integer(7).divide(&Value::decimal(2.0)).unwrap(), Value::decimal(3.5), "the result has the wider type");
    assert_eq!(Value::decimal(7.5).modulo(&Value::integer(2)).unwrap(), Value::decimal(1.5), "the result has the wider type");
}

#[test]
fn s3a_05_overflow_and_division_by_zero_are_errors() {
    assert_eq!(kind(Value::integer(i32::MAX).add(&Value::integer(1))), ExceptionType::OutOfRange, "overflow and division by zero are errors");
    assert_eq!(kind(Value::tinyint(100).add(&Value::tinyint(100))), ExceptionType::OutOfRange, "overflow and division by zero are errors");
    assert_eq!(kind(Value::bigint(i64::MAX).multiply(&Value::bigint(2))), ExceptionType::OutOfRange, "overflow and division by zero are errors");
    assert_eq!(kind(Value::integer(i32::MIN + 1).subtract(&Value::integer(1))), ExceptionType::OutOfRange, "overflow and division by zero are errors");
    assert_eq!(Value::tinyint(100).add(&Value::integer(100)).unwrap(), Value::integer(200), "fits in the wider result type");
    assert_eq!(kind(Value::integer(1).divide(&Value::integer(0))), ExceptionType::DivideByZero, "overflow and division by zero are errors");
    assert_eq!(kind(Value::integer(1).modulo(&Value::integer(0))), ExceptionType::DivideByZero, "overflow and division by zero are errors");
    assert_eq!(kind(Value::decimal(1.0).divide(&Value::decimal(0.0))), ExceptionType::DivideByZero, "overflow and division by zero are errors");
    assert_eq!(kind(Value::integer(1).divide(&Value::varchar("0"))), ExceptionType::DivideByZero, "overflow and division by zero are errors");
}

#[test]
fn s3a_05_arithmetic_with_a_null_is_a_null_of_the_result_type() {
    assert_eq!(Value::null(Integer).add(&Value::integer(1)).unwrap(), Value::null(Integer), "arithmetic with a null is a null of the result type");
    assert_eq!(Value::integer(1).add(&Value::null(BigInt)).unwrap(), Value::null(BigInt), "arithmetic with a null is a null of the result type");
    assert_eq!(Value::null(Integer).multiply(&Value::decimal(2.0)).unwrap(), Value::null(Decimal), "arithmetic with a null is a null of the result type");
    assert_eq!(Value::null(TinyInt).add(&Value::null(Integer)).unwrap(), Value::null(Integer), "arithmetic with a null is a null of the result type");
    assert_eq!(Value::null(Integer).divide(&Value::integer(0)).unwrap(), Value::null(Integer), "NULL wins over division by zero");
}

#[test]
fn s3a_05_strings_on_the_right_are_converted_and_non_numbers_are_refused() {
    assert_eq!(Value::integer(2).add(&Value::varchar("40")).unwrap(), Value::integer(42), "strings on the right are converted and non numbers are refused");
    assert_eq!(Value::decimal(1.0).add(&Value::varchar("0.5")).unwrap(), Value::decimal(1.5), "strings on the right are converted and non numbers are refused");
    assert!(Value::varchar("1").add(&Value::integer(1)).is_err(), "a string is not a number on the left");
    assert!(Value::boolean(true).add(&Value::integer(1)).is_err(), "strings on the right are converted and non numbers are refused: expected `Value::boolean(true).add(&Value::integer(1)).is_err()`");
    assert!(Value::integer(1).add(&Value::boolean(true)).is_err(), "strings on the right are converted and non numbers are refused: expected `Value::integer(1).add(&Value::boolean(true)).is_err()`");
    assert!(Value::integer(1).add(&Value::varchar("x")).is_err(), "strings on the right are converted and non numbers are refused: expected `Value::integer(1).add(&Value::varchar(\"x\")).is_err()`");
}

#[test]
fn s3a_05_min_max_sqrt_and_is_zero() {
    assert_eq!(Value::integer(3).min(&Value::integer(5)).unwrap(), Value::integer(3), "min max sqrt and is zero");
    assert_eq!(Value::integer(3).max(&Value::bigint(5)).unwrap(), Value::bigint(5), "min max sqrt and is zero");
    assert_eq!(Value::varchar("b").min(&Value::varchar("a")).unwrap(), Value::varchar("a"), "min max sqrt and is zero");
    assert_eq!(Value::varchar("b").max(&Value::varchar("a")).unwrap(), Value::varchar("b"), "min max sqrt and is zero");
    assert!(Value::integer(3).min(&Value::null(Integer)).unwrap().is_null(), "min max sqrt and is zero: expected `Value::integer(3).min(&Value::null(Integer)).unwrap().is_null()`");
    assert!(Value::varchar("a").max(&Value::null(Varchar)).unwrap().is_null(), "min max sqrt and is zero: expected `Value::varchar(\"a\").max(&Value::null(Varchar)).unwrap().is_null()`");
    assert_eq!(Value::integer(16).sqrt().unwrap(), Value::decimal(4.0), "min max sqrt and is zero");
    assert_eq!(Value::decimal(2.25).sqrt().unwrap(), Value::decimal(1.5), "min max sqrt and is zero");
    assert_eq!(kind(Value::integer(-1).sqrt()), ExceptionType::Decimal, "min max sqrt and is zero");
    assert_eq!(Value::null(Integer).sqrt().unwrap(), Value::null(Decimal), "min max sqrt and is zero");
    assert!(Value::integer(0).is_zero().unwrap() && Value::decimal(0.0).is_zero().unwrap(), "min max sqrt and is zero: expected `Value::integer(0).is_zero().unwrap() && Value::decimal(0.0).is_zero().unwrap()`");
    assert!(!Value::bigint(3).is_zero().unwrap(), "min max sqrt and is zero: expected `!Value::bigint(3).is_zero().unwrap()`");
    assert!(Value::varchar("0").is_zero().is_err(), "min max sqrt and is zero: expected `Value::varchar(\"0\").is_zero().is_err()`");
}

// ---- 3a-06 · Storage -------------------------------------------------------------------------------------------------------------

fn round_trip(v: &Value) -> Value {
    let mut buf = vec![0xAAu8; v.storage_size() + 3];
    v.serialize_to(&mut buf);
    Value::deserialize_from(&buf, v.type_id()).unwrap()
}

#[test]
fn s3a_06_every_type_round_trips_through_its_bytes() {
    for v in [
        Value::boolean(true),
        Value::boolean(false),
        Value::tinyint(-100),
        Value::smallint(30_000),
        Value::integer(i32::MAX),
        Value::integer(i32::MIN + 1),
        Value::bigint(i64::MIN + 1),
        Value::decimal(-0.125),
        Value::timestamp(123_456_789),
        Value::varchar(""),
        Value::varchar("hello"),
        Value::varchar("héllo wörld 🥰"),
    ] {
        assert_eq!(round_trip(&v), v, "{v}");
    }
}

#[test]
fn s3a_06_a_null_is_its_reserved_encoding_and_comes_back_as_a_null() {
    for t in [Boolean, TinyInt, SmallInt, Integer, BigInt, Decimal, Timestamp, Varchar] {
        assert_eq!(round_trip(&Value::null(t)), Value::null(t), "{t:?}");
    }
    let mut buf = [0u8; 4];
    Value::null(Integer).serialize_to(&mut buf);
    assert_eq!(buf, i32::MIN.to_le_bytes(), "a null is its reserved encoding and comes back as a null");
    let mut buf = [0u8; 4];
    Value::null(Varchar).serialize_to(&mut buf);
    assert_eq!(buf, u32::MAX.to_le_bytes(), "a NULL string is a length of u32::MAX and nothing else");
}

#[test]
fn s3a_06_fixed_size_values_take_their_type_size_little_endian() {
    let mut buf = [0u8; 8];
    Value::integer(0x0102_0304).serialize_to(&mut buf);
    assert_eq!(&buf[..4], &[4, 3, 2, 1], "fixed size values take their type size little endian");
    assert_eq!(Value::integer(1).storage_size(), 4, "fixed size values take their type size little endian");
    assert_eq!(Value::bigint(1).storage_size(), 8, "fixed size values take their type size little endian");
    assert_eq!(Value::tinyint(1).storage_size(), 1, "fixed size values take their type size little endian");
    assert_eq!(Value::boolean(true).storage_size(), 1, "fixed size values take their type size little endian");
    assert_eq!(Value::decimal(1.0).storage_size(), 8, "fixed size values take their type size little endian");
    let mut buf = [0u8; 1];
    Value::boolean(true).serialize_to(&mut buf);
    assert_eq!(buf, [1], "fixed size values take their type size little endian");
    Value::boolean(false).serialize_to(&mut buf);
    assert_eq!(buf, [0], "fixed size values take their type size little endian");
}

#[test]
fn s3a_06_a_string_is_a_length_the_text_and_a_zero_byte() {
    let v = Value::varchar("abc");
    assert_eq!(v.storage_size(), 4 + 3 + 1, "a string is a length the text and a zero byte");
    let mut buf = vec![0xFFu8; v.storage_size()];
    v.serialize_to(&mut buf);
    assert_eq!(&buf[..4], &4u32.to_le_bytes(), "the length counts the zero byte, like BusTub's GetStorageSize");
    assert_eq!(&buf[4..], b"abc\0", "a string is a length the text and a zero byte");
    assert_eq!(Value::varchar("").storage_size(), 5, "a string is a length the text and a zero byte");
    assert_eq!(Value::null(Varchar).storage_size(), 4, "a string is a length the text and a zero byte");
}

#[test]
fn s3a_06_deserializing_reads_only_what_the_type_needs_and_the_invalid_type_is_an_error() {
    let mut buf = vec![0u8; 16];
    Value::integer(77).serialize_to(&mut buf);
    buf[4..].fill(0xEE);
    assert_eq!(Value::deserialize_from(&buf, Integer).unwrap(), Value::integer(77), "the bytes after the value are not part of it");
    assert_eq!(Value::deserialize_from(&buf, SmallInt).unwrap(), Value::smallint(77), "a shorter type reads a prefix of the bytes");
    assert_eq!(kind(Value::deserialize_from(&buf, Invalid)), ExceptionType::UnknownType, "deserializing reads only what the type needs and the invalid type is an error");
}
