//! Tests for module 3d: expressions.

use std::sync::Arc;

use bustub::catalog::column::Column;
use bustub::catalog::schema::Schema;
use bustub::common::bustub_instance::BusTubInstance;
use bustub::common::exception::ExceptionType;
use bustub::common::result_writer::SimpleStreamWriter;
use bustub::execution::expressions::abstract_expression::{ExprRef, Expression};
use bustub::execution::expressions::arithmetic_expression::{ArithmeticExpression, ArithmeticType};
use bustub::execution::expressions::column_value_expression::ColumnValueExpression;
use bustub::execution::expressions::comparison_expression::{ComparisonExpression, ComparisonType};
use bustub::execution::expressions::constant_value_expression::ConstantValueExpression;
use bustub::execution::expressions::logic_expression::{LogicExpression, LogicType};
use bustub::execution::expressions::string_expression::{StringExpression, StringExpressionType};
use bustub::planner::planner::Planner;
use bustub::storage::table::tuple::Tuple;
use bustub::types::type_id::TypeId;
use bustub::types::value::Value;

fn int(v: i32) -> Value {
    Value::integer(v)
}

fn constant(v: Value) -> ExprRef {
    Arc::new(ConstantValueExpression::new(v))
}

fn col(tuple_idx: u32, col_idx: u32, type_id: TypeId) -> ExprRef {
    let c = if type_id == TypeId::Varchar { Column::new_varchar("c", 64) } else { Column::new("c", type_id) };
    Arc::new(ColumnValueExpression::new(tuple_idx, col_idx, c))
}

/// (a INTEGER, b VARCHAR(64), c INTEGER)
fn schema_abc() -> Schema {
    Schema::new(vec![Column::new("a", TypeId::Integer), Column::new_varchar("b", 64), Column::new("c", TypeId::Integer)])
}

fn tuple_abc(a: Value, b: &str, c: Value) -> Tuple {
    Tuple::new(&[a, Value::varchar(b), c], &schema_abc())
}

fn empty() -> (Tuple, Schema) {
    (Tuple::empty(), Schema::new(vec![]))
}

fn eval(e: &ExprRef) -> Value {
    let (t, s) = empty();
    e.evaluate(&t, &s).unwrap()
}

fn cmp(l: Value, r: Value, t: ComparisonType) -> Value {
    eval(&(Arc::new(ComparisonExpression::new(constant(l), constant(r), t)) as ExprRef))
}

fn boolean_null() -> Value {
    Value::null(TypeId::Boolean)
}

// ---- 3d-01 · constants and columns ----------------------------------------------------------------------------------------------

#[test]
fn s3d_01_a_constant_is_its_value_for_any_tuple() {
    let c = constant(int(42));
    assert_eq!(eval(&c), int(42), "a constant is its value for any tuple");
    let schema = schema_abc();
    let t = tuple_abc(int(1), "x", int(2));
    assert_eq!(c.evaluate(&t, &schema).unwrap(), int(42), "the tuple does not matter");
    assert_eq!(constant(Value::varchar("hi")).evaluate(&t, &schema).unwrap(), Value::varchar("hi"), "a constant is its value for any tuple");
    assert_eq!(constant(Value::null(TypeId::Integer)).evaluate(&t, &schema).unwrap(), Value::null(TypeId::Integer), "a constant is its value for any tuple");
}

#[test]
fn s3d_01_a_constant_evaluated_in_a_join_is_still_its_value() {
    let (schema, t) = (schema_abc(), tuple_abc(int(1), "x", int(2)));
    let c = constant(Value::boolean(true));
    assert_eq!(c.evaluate_join(&t, &schema, &t, &schema).unwrap(), Value::boolean(true), "a constant evaluated in a join is still its value");
}

#[test]
fn s3d_01_a_column_value_reads_the_column_of_the_tuple() {
    let (schema, t) = (schema_abc(), tuple_abc(int(7), "seven", int(70)));
    assert_eq!(col(0, 0, TypeId::Integer).evaluate(&t, &schema).unwrap(), int(7), "a column value reads the column of the tuple");
    assert_eq!(col(0, 1, TypeId::Varchar).evaluate(&t, &schema).unwrap(), Value::varchar("seven"), "a column value reads the column of the tuple");
    assert_eq!(col(0, 2, TypeId::Integer).evaluate(&t, &schema).unwrap(), int(70), "a column value reads the column of the tuple");
}

#[test]
fn s3d_01_a_column_value_can_be_null() {
    let (schema, t) = (schema_abc(), tuple_abc(Value::null(TypeId::Integer), "x", int(1)));
    assert_eq!(col(0, 0, TypeId::Integer).evaluate(&t, &schema).unwrap(), Value::null(TypeId::Integer), "a column value can be null");
}

#[test]
fn s3d_01_in_a_join_tuple_idx_picks_the_side_and_each_side_has_its_own_schema() {
    let left_schema = schema_abc();
    let right_schema = Schema::new(vec![Column::new("x", TypeId::Integer), Column::new("y", TypeId::Integer)]);
    let left = tuple_abc(int(1), "left", int(3));
    let right = Tuple::new(&[int(100), int(200)], &right_schema);
    let left_c2 = col(0, 2, TypeId::Integer);
    let right_c1 = col(1, 1, TypeId::Integer);
    assert_eq!(left_c2.evaluate_join(&left, &left_schema, &right, &right_schema).unwrap(), int(3), "in a join tuple idx picks the side and each side has its own schema");
    assert_eq!(right_c1.evaluate_join(&left, &left_schema, &right, &right_schema).unwrap(), int(200), "in a join tuple idx picks the side and each side has its own schema");
    assert_eq!(col(1, 0, TypeId::Integer).evaluate_join(&left, &left_schema, &right, &right_schema).unwrap(), int(100), "in a join tuple idx picks the side and each side has its own schema");
}

#[test]
fn s3d_01_expressions_describe_themselves() {
    assert_eq!(col(0, 3, TypeId::Integer).to_string(), "#0.3", "expressions describe themselves");
    assert_eq!(col(1, 0, TypeId::Integer).to_string(), "#1.0", "expressions describe themselves");
    assert_eq!(constant(int(5)).to_string(), "5", "expressions describe themselves");
    assert_eq!(constant(Value::varchar("a")).to_string(), "a", "expressions describe themselves");
    assert_eq!(col(0, 0, TypeId::Integer).return_type().type_id(), TypeId::Integer, "expressions describe themselves");
    assert_eq!(constant(Value::boolean(true)).return_type().type_id(), TypeId::Boolean, "expressions describe themselves");
    assert!(constant(int(1)).children().is_empty(), "expressions describe themselves: expected `constant(int(1)).children().is_empty()`");
}

// ---- 3d-02 · comparisons --------------------------------------------------------------------------------------------------------

#[test]
fn s3d_02_the_six_comparisons_on_integers() {
    use ComparisonType::*;
    let t = Value::boolean(true);
    let f = Value::boolean(false);
    assert_eq!(cmp(int(1), int(1), Equal), t, "the six comparisons on integers");
    assert_eq!(cmp(int(1), int(2), Equal), f, "the six comparisons on integers");
    assert_eq!(cmp(int(1), int(2), NotEqual), t, "the six comparisons on integers");
    assert_eq!(cmp(int(1), int(2), LessThan), t, "the six comparisons on integers");
    assert_eq!(cmp(int(2), int(2), LessThan), f, "the six comparisons on integers");
    assert_eq!(cmp(int(2), int(2), LessThanOrEqual), t, "the six comparisons on integers");
    assert_eq!(cmp(int(3), int(2), GreaterThan), t, "the six comparisons on integers");
    assert_eq!(cmp(int(2), int(2), GreaterThan), f, "the six comparisons on integers");
    assert_eq!(cmp(int(2), int(2), GreaterThanOrEqual), t, "the six comparisons on integers");
    assert_eq!(cmp(int(1), int(2), GreaterThanOrEqual), f, "the six comparisons on integers");
}

#[test]
fn s3d_02_comparing_with_null_is_null_not_false() {
    use ComparisonType::*;
    let null = Value::null(TypeId::Integer);
    for t in [Equal, NotEqual, LessThan, LessThanOrEqual, GreaterThan, GreaterThanOrEqual] {
        assert_eq!(cmp(null.clone(), int(1), t), boolean_null(), "NULL {t:?} 1");
        assert_eq!(cmp(int(1), null.clone(), t), boolean_null(), "1 {t:?} NULL");
        assert_eq!(cmp(null.clone(), null.clone(), t), boolean_null(), "NULL {t:?} NULL");
    }
}

#[test]
fn s3d_02_strings_and_mixed_numbers_compare_by_value() {
    use ComparisonType::*;
    assert_eq!(cmp(Value::varchar("abc"), Value::varchar("abd"), LessThan), Value::boolean(true), "strings and mixed numbers compare by value");
    assert_eq!(cmp(Value::varchar("b"), Value::varchar("b"), Equal), Value::boolean(true), "strings and mixed numbers compare by value");
    assert_eq!(cmp(int(1), Value::decimal(1.5), LessThan), Value::boolean(true), "strings and mixed numbers compare by value");
    assert_eq!(cmp(Value::bigint(5), int(5), Equal), Value::boolean(true), "strings and mixed numbers compare by value");
}

#[test]
fn s3d_02_a_comparison_of_columns_in_a_join_and_in_a_row() {
    let schema = schema_abc();
    let t = tuple_abc(int(5), "x", int(5));
    let same_row: ExprRef = Arc::new(ComparisonExpression::new(col(0, 0, TypeId::Integer), col(0, 2, TypeId::Integer), ComparisonType::Equal));
    assert_eq!(same_row.evaluate(&t, &schema).unwrap(), Value::boolean(true), "a comparison of columns in a join and in a row");

    let right_schema = Schema::new(vec![Column::new("y", TypeId::Integer)]);
    let right = Tuple::new(&[int(9)], &right_schema);
    let join_pred: ExprRef = Arc::new(ComparisonExpression::new(col(0, 0, TypeId::Integer), col(1, 0, TypeId::Integer), ComparisonType::LessThan));
    assert_eq!(join_pred.evaluate_join(&t, &schema, &right, &right_schema).unwrap(), Value::boolean(true), "a comparison of columns in a join and in a row");
}

#[test]
fn s3d_02_a_comparison_describes_itself_and_returns_a_boolean() {
    let e = ComparisonExpression::new(col(0, 0, TypeId::Integer), constant(int(5)), ComparisonType::GreaterThanOrEqual);
    assert_eq!(Expression::to_string(&e), "(#0.0>=5)", "a comparison describes itself and returns a boolean");
    assert_eq!(e.return_type().type_id(), TypeId::Boolean, "a comparison describes itself and returns a boolean");
    assert_eq!(e.children().len(), 2, "a comparison describes itself and returns a boolean");
    let ne = ComparisonExpression::new(constant(int(1)), constant(int(2)), ComparisonType::NotEqual);
    assert_eq!(Expression::to_string(&ne), "(1!=2)", "a comparison describes itself and returns a boolean");
}

// ---- 3d-03 · arithmetic ---------------------------------------------------------------------------------------------------------

fn arith(l: Value, r: Value, t: ArithmeticType) -> bustub::common::exception::Result<Value> {
    let e: ExprRef = Arc::new(ArithmeticExpression::new(constant(l), constant(r), t)?);
    let (tup, schema) = empty();
    e.evaluate(&tup, &schema)
}

#[test]
fn s3d_03_plus_and_minus() {
    assert_eq!(arith(int(1), int(2), ArithmeticType::Plus).unwrap(), int(3), "plus and minus");
    assert_eq!(arith(int(1), int(2), ArithmeticType::Minus).unwrap(), int(-1), "plus and minus");
    assert_eq!(arith(int(-5), int(-7), ArithmeticType::Minus).unwrap(), int(2), "plus and minus");
    assert_eq!(arith(int(0), int(0), ArithmeticType::Plus).unwrap(), int(0), "plus and minus");
}

#[test]
fn s3d_03_a_null_operand_makes_a_null_result_of_type_integer() {
    let null = Value::null(TypeId::Integer);
    assert_eq!(arith(int(1), null.clone(), ArithmeticType::Plus).unwrap(), null, "a null operand makes a null result of type integer");
    assert_eq!(arith(null.clone(), int(1), ArithmeticType::Minus).unwrap(), null, "a null operand makes a null result of type integer");
    assert_eq!(arith(null.clone(), null.clone(), ArithmeticType::Plus).unwrap(), null, "a null operand makes a null result of type integer");
}

#[test]
fn s3d_03_overflow_is_an_error_not_a_wrapped_number() {
    let e = arith(int(i32::MAX), int(1), ArithmeticType::Plus).unwrap_err();
    assert_eq!(e.kind, ExceptionType::OutOfRange, "overflow is an error not a wrapped number");
    assert_eq!(arith(int(-i32::MAX), int(2), ArithmeticType::Minus).unwrap_err().kind, ExceptionType::OutOfRange, "overflow is an error not a wrapped number");
    // the largest results that do fit
    assert_eq!(arith(int(i32::MAX - 1), int(1), ArithmeticType::Plus).unwrap(), int(i32::MAX), "overflow is an error not a wrapped number");
    assert_eq!(arith(int(-i32::MAX + 1), int(-1), ArithmeticType::Plus).unwrap(), int(-i32::MAX), "overflow is an error not a wrapped number");
}

#[test]
fn s3d_03_i32_min_is_the_null_encoding_so_it_is_not_a_result() {
    // -2147483647 - 1 = i32::MIN would be stored as a NULL: an error is better than a quietly wrong NULL
    assert_eq!(arith(int(-i32::MAX), int(1), ArithmeticType::Minus).unwrap_err().kind, ExceptionType::OutOfRange, "i32 min is the null encoding so it is not a result");
}

#[test]
fn s3d_03_only_integers_are_accepted_when_the_expression_is_built() {
    let e = ArithmeticExpression::new(constant(Value::varchar("a")), constant(int(1)), ArithmeticType::Plus).unwrap_err();
    assert_eq!(e.kind, ExceptionType::NotImplemented, "only integers are accepted when the expression is built");
    assert!(e.message.contains("integer"), "only integers are accepted when the expression is built: expected `e.message.contains(\"integer\")`");
    assert!(ArithmeticExpression::new(constant(int(1)), constant(Value::decimal(1.5)), ArithmeticType::Minus).is_err(), "only integers are accepted when the expression is built: expected `ArithmeticExpression::new(constant(int(1)), constant(Value::decimal(1.5)), ArithmeticType::Minus).is...`");
    assert!(ArithmeticExpression::new(constant(Value::boolean(true)), constant(int(1)), ArithmeticType::Plus).is_err(), "only integers are accepted when the expression is built: expected `ArithmeticExpression::new(constant(Value::boolean(true)), constant(int(1)), ArithmeticType::Plus).is...`");
}

#[test]
fn s3d_03_arithmetic_on_columns_in_a_row_and_in_a_join_and_nested() {
    let schema = schema_abc();
    let t = tuple_abc(int(10), "x", int(3));
    let a_minus_c: ExprRef = Arc::new(ArithmeticExpression::new(col(0, 0, TypeId::Integer), col(0, 2, TypeId::Integer), ArithmeticType::Minus).unwrap());
    assert_eq!(a_minus_c.evaluate(&t, &schema).unwrap(), int(7), "arithmetic on columns in a row and in a join and nested");
    // (a - c) + 100
    let nested: ExprRef = Arc::new(ArithmeticExpression::new(a_minus_c.clone(), constant(int(100)), ArithmeticType::Plus).unwrap());
    assert_eq!(nested.evaluate(&t, &schema).unwrap(), int(107), "arithmetic on columns in a row and in a join and nested");
    assert_eq!(Expression::to_string(nested.as_ref()), "((#0.0-#0.2)+100)", "arithmetic on columns in a row and in a join and nested");

    let right_schema = Schema::new(vec![Column::new("y", TypeId::Integer)]);
    let right = Tuple::new(&[int(1000)], &right_schema);
    let join: ExprRef = Arc::new(ArithmeticExpression::new(col(0, 0, TypeId::Integer), col(1, 0, TypeId::Integer), ArithmeticType::Plus).unwrap());
    assert_eq!(join.evaluate_join(&t, &schema, &right, &right_schema).unwrap(), int(1010), "arithmetic on columns in a row and in a join and nested");
    assert_eq!(join.return_type().type_id(), TypeId::Integer, "arithmetic on columns in a row and in a join and nested");
}

// ---- 3d-04 · logic --------------------------------------------------------------------------------------------------------------

fn logic(l: Value, r: Value, t: LogicType) -> Value {
    let e: ExprRef = Arc::new(LogicExpression::new(constant(l), constant(r), t).unwrap());
    eval(&e)
}

#[test]
fn s3d_04_and_truth_table() {
    let (t, f, n) = (Value::boolean(true), Value::boolean(false), boolean_null());
    let cases = [
        (&t, &t, &t),
        (&t, &f, &f),
        (&f, &t, &f),
        (&f, &f, &f),
        (&t, &n, &n),
        (&n, &t, &n),
        (&f, &n, &f),
        (&n, &f, &f),
        (&n, &n, &n),
    ];
    for (l, r, want) in cases {
        assert_eq!(&logic(l.clone(), r.clone(), LogicType::And), want, "{l:?} AND {r:?}");
    }
}

#[test]
fn s3d_04_or_truth_table() {
    let (t, f, n) = (Value::boolean(true), Value::boolean(false), boolean_null());
    let cases = [
        (&t, &t, &t),
        (&t, &f, &t),
        (&f, &t, &t),
        (&f, &f, &f),
        (&t, &n, &t),
        (&n, &t, &t),
        (&f, &n, &n),
        (&n, &f, &n),
        (&n, &n, &n),
    ];
    for (l, r, want) in cases {
        assert_eq!(&logic(l.clone(), r.clone(), LogicType::Or), want, "{l:?} OR {r:?}");
    }
}

#[test]
fn s3d_04_both_sides_must_be_boolean() {
    let e = LogicExpression::new(constant(int(1)), constant(Value::boolean(true)), LogicType::And).unwrap_err();
    assert_eq!(e.kind, ExceptionType::NotImplemented, "both sides must be boolean");
    assert!(LogicExpression::new(constant(Value::boolean(true)), constant(Value::varchar("x")), LogicType::Or).is_err(), "both sides must be boolean: expected `LogicExpression::new(constant(Value::boolean(true)), constant(Value::varchar(\"x\")), LogicType::Or).i...`");
}

#[test]
fn s3d_04_logic_of_comparisons_in_a_row_and_a_join() {
    let schema = schema_abc();
    let t = tuple_abc(int(5), "x", Value::null(TypeId::Integer));
    let a_gt_1: ExprRef = Arc::new(ComparisonExpression::new(col(0, 0, TypeId::Integer), constant(int(1)), ComparisonType::GreaterThan));
    let c_eq_2: ExprRef = Arc::new(ComparisonExpression::new(col(0, 2, TypeId::Integer), constant(int(2)), ComparisonType::Equal));
    let and: ExprRef = Arc::new(LogicExpression::new(a_gt_1.clone(), c_eq_2.clone(), LogicType::And).unwrap());
    let or: ExprRef = Arc::new(LogicExpression::new(a_gt_1, c_eq_2, LogicType::Or).unwrap());
    assert_eq!(and.evaluate(&t, &schema).unwrap(), boolean_null(), "TRUE AND NULL");
    assert_eq!(or.evaluate(&t, &schema).unwrap(), Value::boolean(true), "TRUE OR NULL");

    let right_schema = Schema::new(vec![Column::new("y", TypeId::Integer)]);
    let right = Tuple::new(&[int(5)], &right_schema);
    let l_eq_r: ExprRef = Arc::new(ComparisonExpression::new(col(0, 0, TypeId::Integer), col(1, 0, TypeId::Integer), ComparisonType::Equal));
    let both: ExprRef = Arc::new(LogicExpression::new(l_eq_r.clone(), l_eq_r, LogicType::And).unwrap());
    assert_eq!(both.evaluate_join(&t, &schema, &right, &right_schema).unwrap(), Value::boolean(true), "logic of comparisons in a row and a join");
}

#[test]
fn s3d_04_logic_describes_itself() {
    let e = LogicExpression::new(constant(Value::boolean(true)), constant(Value::boolean(false)), LogicType::Or).unwrap();
    assert_eq!(Expression::to_string(&e), "(trueorfalse)", "logic describes itself");
    assert_eq!(e.return_type().type_id(), TypeId::Boolean, "logic describes itself");
}

// ---- 3d-05 · strings ------------------------------------------------------------------------------------------------------------

fn string_fn(arg: Value, t: StringExpressionType) -> Value {
    let e: ExprRef = Arc::new(StringExpression::new(constant(arg), t).unwrap());
    eval(&e)
}

#[test]
fn s3d_05_lower_and_upper() {
    assert_eq!(string_fn(Value::varchar("CMU 15-445 Database Systems"), StringExpressionType::Lower), Value::varchar("cmu 15-445 database systems"), "lower and upper");
    assert_eq!(string_fn(Value::varchar("CMU 15-445 Database Systems"), StringExpressionType::Upper), Value::varchar("CMU 15-445 DATABASE SYSTEMS"), "lower and upper");
    assert_eq!(string_fn(Value::varchar(""), StringExpressionType::Upper), Value::varchar(""), "lower and upper");
    assert_eq!(string_fn(Value::varchar("1 + 1 = 2"), StringExpressionType::Lower), Value::varchar("1 + 1 = 2"), "lower and upper");
}

#[test]
fn s3d_05_unicode_letters_change_case_too() {
    assert_eq!(string_fn(Value::varchar("ÉCOLE"), StringExpressionType::Lower), Value::varchar("école"), "unicode letters change case too");
    assert_eq!(string_fn(Value::varchar("école straße"), StringExpressionType::Upper), Value::varchar("ÉCOLE STRASSE"), "unicode letters change case too");
    assert_eq!(string_fn(Value::varchar("🥰 Abc"), StringExpressionType::Upper), Value::varchar("🥰 ABC"), "unicode letters change case too");
}

#[test]
fn s3d_05_null_in_null_out() {
    assert_eq!(string_fn(Value::null(TypeId::Varchar), StringExpressionType::Lower), Value::null(TypeId::Varchar), "null in null out");
    assert_eq!(string_fn(Value::null(TypeId::Varchar), StringExpressionType::Upper), Value::null(TypeId::Varchar), "null in null out");
}

#[test]
fn s3d_05_the_argument_must_be_a_varchar() {
    let e = StringExpression::new(constant(int(1)), StringExpressionType::Lower).unwrap_err();
    assert_eq!(e.kind, ExceptionType::Execution, "the argument must be a varchar");
    assert!(StringExpression::new(constant(Value::boolean(true)), StringExpressionType::Upper).is_err(), "the argument must be a varchar: expected `StringExpression::new(constant(Value::boolean(true)), StringExpressionType::Upper).is_err()`");
}

#[test]
fn s3d_05_strings_from_columns_in_a_row_and_a_join_and_nested() {
    let schema = schema_abc();
    let t = tuple_abc(int(1), "Hello World", int(2));
    let upper: ExprRef = Arc::new(StringExpression::new(col(0, 1, TypeId::Varchar), StringExpressionType::Upper).unwrap());
    assert_eq!(upper.evaluate(&t, &schema).unwrap(), Value::varchar("HELLO WORLD"), "strings from columns in a row and a join and nested");
    let lower_upper: ExprRef = Arc::new(StringExpression::new(upper.clone(), StringExpressionType::Lower).unwrap());
    assert_eq!(lower_upper.evaluate(&t, &schema).unwrap(), Value::varchar("hello world"), "strings from columns in a row and a join and nested");
    assert_eq!(Expression::to_string(lower_upper.as_ref()), "lower(upper(#0.1))", "strings from columns in a row and a join and nested");

    let right_schema = Schema::new(vec![Column::new_varchar("s", 20)]);
    let right = Tuple::new(&[Value::varchar("MiXeD")], &right_schema);
    let join: ExprRef = Arc::new(StringExpression::new(col(1, 0, TypeId::Varchar), StringExpressionType::Lower).unwrap());
    assert_eq!(join.evaluate_join(&t, &schema, &right, &right_schema).unwrap(), Value::varchar("mixed"), "strings from columns in a row and a join and nested");
    assert_eq!(join.return_type().type_id(), TypeId::Varchar, "strings from columns in a row and a join and nested");
}

#[test]
fn s3d_05_compute_is_a_plain_string_function() {
    let lower = StringExpression::new(constant(Value::varchar("x")), StringExpressionType::Lower).unwrap();
    let upper = StringExpression::new(constant(Value::varchar("x")), StringExpressionType::Upper).unwrap();
    assert_eq!(lower.compute("AbC"), "abc", "compute is a plain string function");
    assert_eq!(upper.compute("AbC"), "ABC", "compute is a plain string function");
}

// ---- 3d-06 · the function factory in the planner -------------------------------------------------------------------------------

fn run(db: &BusTubInstance, sql: &str) -> bustub::common::exception::Result<String> {
    let mut out = String::new();
    db.execute_sql(sql, &mut SimpleStreamWriter::new(&mut out, true, " "), None)?;
    Ok(out)
}

#[test]
fn s3d_06_the_factory_builds_lower_and_upper() {
    let lower = Planner::get_func_call_from_factory("lower", vec![constant(Value::varchar("ABC"))]).unwrap();
    assert_eq!(eval(&lower), Value::varchar("abc"), "the factory builds lower and upper");
    let upper = Planner::get_func_call_from_factory("upper", vec![constant(Value::varchar("abc"))]).unwrap();
    assert_eq!(eval(&upper), Value::varchar("ABC"), "the factory builds lower and upper");
    assert_eq!(Expression::to_string(lower.as_ref()), "lower(ABC)", "the factory builds lower and upper");
}

#[test]
fn s3d_06_the_factory_refuses_other_names_and_other_argument_counts() {
    assert!(Planner::get_func_call_from_factory("reverse", vec![constant(Value::varchar("a"))]).is_err(), "the factory refuses other names and other argument counts: expected `Planner::get_func_call_from_factory(\"reverse\", vec![constant(Value::varchar(\"a\"))]).is_err()`");
    assert!(Planner::get_func_call_from_factory("lower", vec![]).is_err(), "the factory refuses other names and other argument counts: expected `Planner::get_func_call_from_factory(\"lower\", vec![]).is_err()`");
    assert!(Planner::get_func_call_from_factory("upper", vec![constant(Value::varchar("a")), constant(Value::varchar("b"))]).is_err(), "the factory refuses other names and other argument counts: expected `Planner::get_func_call_from_factory(\"upper\", vec![constant(Value::varchar(\"a\")), constant(Value::var...`");
}

#[test]
fn s3d_06_the_factory_refuses_arguments_that_are_not_strings() {
    assert!(Planner::get_func_call_from_factory("lower", vec![constant(int(1))]).is_err(), "the factory refuses arguments that are not strings: expected `Planner::get_func_call_from_factory(\"lower\", vec![constant(int(1))]).is_err()`");
    assert!(Planner::get_func_call_from_factory("upper", vec![constant(Value::boolean(true))]).is_err(), "the factory refuses arguments that are not strings: expected `Planner::get_func_call_from_factory(\"upper\", vec![constant(Value::boolean(true))]).is_err()`");
}

#[test]
fn s3d_06_sql_lower_and_upper_end_to_end() {
    let db = BusTubInstance::new(32);
    assert_eq!(run(&db, "select lower('MiXeD')").unwrap().trim(), "mixed", "sql lower and upper end to end");
    assert_eq!(run(&db, "select upper('MiXeD'), lower('MiXeD')").unwrap().trim(), "MIXED mixed", "sql lower and upper end to end");
    assert_eq!(run(&db, "select UPPER(lower('aBc'))").unwrap().trim(), "ABC", "function names are not case sensitive");
}

#[test]
fn s3d_06_sql_with_a_wrong_call_is_an_error() {
    let db = BusTubInstance::new(32);
    assert!(run(&db, "select upper(1)").is_err(), "sql with a wrong call is an error: expected `run(&db, \"select upper(1)\").is_err()`");
    assert!(run(&db, "select lower('a', 'b')").is_err(), "sql with a wrong call is an error: expected `run(&db, \"select lower('a', 'b')\").is_err()`");
    assert!(run(&db, "select nosuchfunction('a')").is_err(), "sql with a wrong call is an error: expected `run(&db, \"select nosuchfunction('a')\").is_err()`");
    assert!(run(&db, "select lower()").is_err(), "sql with a wrong call is an error: expected `run(&db, \"select lower()\").is_err()`");
}

#[test]
fn s3d_06_the_function_is_planned_over_a_columns_and_shows_in_explain() {
    let db = BusTubInstance::new(32);
    db.generate_mock_table();
    let out = run(&db, "select upper(day_of_week) from __mock_table_schedule where has_lecture = 1").unwrap();
    let mut days: Vec<&str> = out.split_whitespace().collect();
    days.sort();
    assert_eq!(days, ["MONDAY", "WEDNESDAY"], "the function is planned over a columns and shows in explain");
    let plan = run(&db, "explain (o) select upper(day_of_week) from __mock_table_schedule").unwrap();
    assert!(plan.contains("upper(#0.0)"), "{plan}");
    assert!(plan.contains("MockScan { table=__mock_table_schedule }"), "{plan}");
}
