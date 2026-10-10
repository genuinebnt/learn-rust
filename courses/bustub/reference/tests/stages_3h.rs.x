//! Tests for module 3h: optimizer rules.

use std::sync::Arc;

mod common;

use bustub::catalog::column::Column;
use bustub::common::bustub_instance::BusTubInstance;
use bustub::common::result_writer::SimpleStreamWriter;
use bustub::execution::expressions::abstract_expression::{ExprRef, Expression};
use bustub::execution::expressions::column_value_expression::ColumnValueExpression;
use bustub::execution::expressions::comparison_expression::{ComparisonExpression, ComparisonType};
use bustub::execution::expressions::constant_value_expression::ConstantValueExpression;
use bustub::execution::expressions::logic_expression::{LogicExpression, LogicType};
use bustub::optimizer::optimizer::Optimizer;
use bustub::types::type_id::TypeId;
use bustub::types::value::Value;
use common::sql_model as model;
use proptest::prelude::*;

fn new_db() -> BusTubInstance {
    BusTubInstance::new(128)
}

fn sql(db: &BusTubInstance, sql: &str) -> Vec<String> {
    let mut out = String::new();
    db.execute_sql(sql, &mut SimpleStreamWriter::new(&mut out, true, " "), None).unwrap_or_else(|e| panic!("{sql}: {e}"));
    out.lines().map(|l| l.trim_end().to_string()).collect()
}

fn sorted(mut v: Vec<String>) -> Vec<String> {
    v.sort();
    v
}

/// The optimized plan of a query as text.
fn plan(db: &BusTubInstance, query: &str) -> String {
    sql(db, &format!("explain (o) {query}")).join("\n")
}

fn col(tuple_idx: u32, idx: u32) -> ExprRef {
    Arc::new(ColumnValueExpression::new(tuple_idx, idx, Column::new("c", TypeId::Integer)))
}

fn constant(v: i32) -> ExprRef {
    Arc::new(ConstantValueExpression::new(Value::integer(v)))
}

fn cmp(l: ExprRef, r: ExprRef, t: ComparisonType) -> ExprRef {
    Arc::new(ComparisonExpression::new(l, r, t))
}

fn eq(l: ExprRef, r: ExprRef) -> ExprRef {
    cmp(l, r, ComparisonType::Equal)
}

fn and(l: ExprRef, r: ExprRef) -> ExprRef {
    Arc::new(LogicExpression::new(l, r, LogicType::And).unwrap())
}

fn or(l: ExprRef, r: ExprRef) -> ExprRef {
    Arc::new(LogicExpression::new(l, r, LogicType::Or).unwrap())
}

fn texts(exprs: &[ExprRef]) -> Vec<String> {
    exprs.iter().map(|e| Expression::to_string(e.as_ref())).collect()
}

// ---- 3h-01 · equi-join keys --------------------------------------------------------------------------------------------------------

#[test]
fn s3h_01_one_equality_between_the_sides_gives_a_key_pair() {
    let (l, r) = Optimizer::extract_equi_join_keys(&eq(col(0, 1), col(1, 2))).unwrap();
    assert_eq!((texts(&l), texts(&r)), (vec!["#0.1".to_string()], vec!["#0.2".to_string()]), "each side's key refers to its own input as tuple 0");
}

#[test]
fn s3h_01_the_equality_may_be_written_either_way_round() {
    let (l, r) = Optimizer::extract_equi_join_keys(&eq(col(1, 2), col(0, 1))).unwrap();
    assert_eq!((texts(&l), texts(&r)), (vec!["#0.1".to_string()], vec!["#0.2".to_string()]), "left is the column that reads tuple 0");
}

#[test]
fn s3h_01_several_equalities_in_any_nesting_give_keys_in_order() {
    let p = and(and(eq(col(0, 0), col(1, 3)), eq(col(1, 1), col(0, 2))), eq(col(0, 4), col(1, 5)));
    let (l, r) = Optimizer::extract_equi_join_keys(&p).unwrap();
    assert_eq!(texts(&l), vec!["#0.0", "#0.2", "#0.4"], "several equalities in any nesting give keys in order");
    assert_eq!(texts(&r), vec!["#0.3", "#0.1", "#0.5"], "several equalities in any nesting give keys in order");
}

#[test]
fn s3h_01_one_conjunct_that_is_not_such_an_equality_rules_it_out() {
    let key = eq(col(0, 0), col(1, 0));
    assert!(Optimizer::extract_equi_join_keys(&and(key.clone(), cmp(col(1, 1), constant(10), ComparisonType::GreaterThan))).is_none(), "a residual condition");
    assert!(Optimizer::extract_equi_join_keys(&and(key.clone(), eq(col(1, 1), constant(10)))).is_none(), "a constant is not a join key");
    assert!(Optimizer::extract_equi_join_keys(&cmp(col(0, 0), col(1, 0), ComparisonType::LessThan)).is_none(), "one conjunct that is not such an equality rules it out: expected `Optimizer::extract_equi_join_keys(&cmp(col(0, 0), col(1, 0), ComparisonType::LessThan)).is_none()`");
    assert!(Optimizer::extract_equi_join_keys(&cmp(col(0, 0), col(1, 0), ComparisonType::NotEqual)).is_none(), "one conjunct that is not such an equality rules it out: expected `Optimizer::extract_equi_join_keys(&cmp(col(0, 0), col(1, 0), ComparisonType::NotEqual)).is_none()`");
}

#[test]
fn s3h_01_both_columns_on_one_side_or_an_or_is_not_a_join_key() {
    assert!(Optimizer::extract_equi_join_keys(&eq(col(0, 0), col(0, 1))).is_none(), "both columns on one side or an or is not a join key: expected `Optimizer::extract_equi_join_keys(&eq(col(0, 0), col(0, 1))).is_none()`");
    assert!(Optimizer::extract_equi_join_keys(&eq(col(1, 0), col(1, 1))).is_none(), "both columns on one side or an or is not a join key: expected `Optimizer::extract_equi_join_keys(&eq(col(1, 0), col(1, 1))).is_none()`");
    assert!(Optimizer::extract_equi_join_keys(&or(eq(col(0, 0), col(1, 0)), eq(col(0, 1), col(1, 1)))).is_none(), "both columns on one side or an or is not a join key: expected `Optimizer::extract_equi_join_keys(&or(eq(col(0, 0), col(1, 0)), eq(col(0, 1), col(1, 1)))).is_none()`");
    assert!(Optimizer::extract_equi_join_keys(&constant(1)).is_none(), "both columns on one side or an or is not a join key: expected `Optimizer::extract_equi_join_keys(&constant(1)).is_none()`");
}

#[test]
fn s3h_01_conjuncts_flatten_ands_and_keep_ors_whole() {
    let p = and(and(eq(col(0, 0), col(1, 0)), or(eq(col(0, 1), constant(1)), eq(col(0, 1), constant(2)))), cmp(col(1, 0), constant(5), ComparisonType::GreaterThan));
    let mut out = vec![];
    Optimizer::conjuncts(&p, &mut out);
    assert_eq!(out.len(), 3, "conjuncts flatten ands and keep ors whole");
    assert!(out[1].as_any().downcast_ref::<LogicExpression>().is_some_and(|l| l.logic_type == LogicType::Or), "conjuncts flatten ands and keep ors whole: expected `out[1].as_any().downcast_ref::<LogicExpression>().is_some_and(|l| l.logic_type == LogicType::Or)`");
}

// ---- 3h-01 · nested loop join to hash join ----------------------------------------------------------------------------------------

fn join_db() -> BusTubInstance {
    let db = new_db();
    sql(&db, "create table a(x int, y int)");
    sql(&db, "create table b(p int, q int)");
    sql(&db, "create table c(r int)");
    sql(&db, "insert into a values (1, 10), (2, 20), (3, 30), (null, 40), (3, 31)");
    sql(&db, "insert into b values (1, 10), (3, 30), (3, 99), (4, 40), (null, 50)");
    sql(&db, "insert into c values (1), (3), (7)");
    db
}

/// The rows of a query with the optimizer's default rules and with BusTub's starter rules (which have no hash join).
fn both_ways(db: &BusTubInstance, query: &str) -> (Vec<String>, Vec<String>) {
    let with_hash = sorted(sql(db, query));
    sql(db, "set force_optimizer_starter_rule=yes");
    let nested_loop = sorted(sql(db, query));
    sql(db, "set force_optimizer_starter_rule=no");
    (with_hash, nested_loop)
}

#[test]
fn s3h_01_an_equality_join_becomes_a_hash_join() {
    let db = join_db();
    let p = plan(&db, "select * from a inner join b on a.x = b.p");
    assert!(p.contains("HashJoin { type=Inner, left_key=[#0.0], right_key=[#0.0] }"), "{p}");
    assert!(!p.contains("NestedLoopJoin"), "{p}");
}

#[test]
fn s3h_01_a_cross_join_with_a_where_becomes_a_hash_join() {
    let db = join_db();
    let p = plan(&db, "select * from a, b where a.x = b.p");
    assert!(p.contains("HashJoin"), "{p}");
    assert!(!p.contains("Filter"), "the filter was merged into the join and used as keys: {p}");
}

#[test]
fn s3h_01_several_conditions_make_several_keys() {
    let db = join_db();
    let p = plan(&db, "select * from a join b on a.x = b.p and b.q = a.y");
    assert!(p.contains("left_key=[#0.0, #0.1], right_key=[#0.0, #0.1]"), "{p}");
}

#[test]
fn s3h_01_a_condition_that_is_not_an_equality_keeps_the_nested_loop() {
    let db = join_db();
    assert!(plan(&db, "select * from a join b on a.x < b.p").contains("NestedLoopJoin"), "a condition that is not an equality keeps the nested loop: expected `plan(&db, \"select * from a join b on a.x < b.p\").contains(\"NestedLoopJoin\")`");
    assert!(plan(&db, "select * from a join b on a.x = b.p and a.y > 5").contains("NestedLoopJoin"), "a condition that is not an equality keeps the nested loop: expected `plan(&db, \"select * from a join b on a.x = b.p and a.y > 5\").contains(\"NestedLoopJoin\")`");
    assert!(plan(&db, "select * from a join b on a.x = b.p or a.y = b.q").contains("NestedLoopJoin"), "a condition that is not an equality keeps the nested loop: expected `plan(&db, \"select * from a join b on a.x = b.p or a.y = b.q\").contains(\"NestedLoopJoin\")`");
    assert!(plan(&db, "select * from a join b on a.x + 1 = b.p").contains("NestedLoopJoin"), "an expression is not a column key");
}

#[test]
fn s3h_01_left_joins_become_hash_joins_too() {
    let db = join_db();
    let p = plan(&db, "select * from a left join b on a.x = b.p");
    assert!(p.contains("HashJoin { type=Left"), "{p}");
}

#[test]
fn s3h_01_the_results_are_the_same_as_with_nested_loops() {
    let db = join_db();
    for q in [
        "select * from a join b on a.x = b.p",
        "select * from a left join b on a.x = b.p",
        "select * from a, b where a.x = b.p",
        "select * from a join b on a.x = b.p and a.y = b.q",
        "select * from a join b on b.p = a.x",
    ] {
        let (h, n) = both_ways(&db, q);
        assert_eq!(h, n, "{q}");
        assert!(!h.is_empty() || q.contains("a.y = b.q"), "he results are the same as with nested loops: expected `!h.is_empty() || q.contains(\"a.y = b.q\")`");
    }
}

#[test]
fn s3h_01_a_three_way_join_becomes_two_hash_joins() {
    let db = join_db();
    let q = "select * from a join b on a.x = b.p join c on c.r = a.x";
    let p = plan(&db, q);
    assert_eq!(p.matches("HashJoin").count(), 2, "{p}");
    let (h, n) = both_ways(&db, q);
    assert_eq!(h, n, " three way join becomes two hash joins");
    let nested = "select * from c join (a join b on a.x = b.p) on c.r = b.p";
    assert_eq!(plan(&db, nested).matches("HashJoin").count(), 2, " three way join becomes two hash joins");
    let (h, n) = both_ways(&db, nested);
    assert_eq!(h, n, " three way join becomes two hash joins");
}

// ---- 3h-02 · sort + limit to top-N ------------------------------------------------------------------------------------------------

fn topn_db() -> BusTubInstance {
    let db = new_db();
    sql(&db, "create table t(a int, b int)");
    let rows: Vec<String> = (0..60).map(|i| format!("({}, {})", (i * 37) % 11, i)).collect();
    sql(&db, &format!("insert into t values {}", rows.join(", ")));
    db
}

#[test]
fn s3h_02_order_by_with_a_limit_becomes_top_n() {
    let db = topn_db();
    let p = plan(&db, "select * from t order by a desc limit 5");
    assert!(p.contains("TopN { n=5"), "{p}");
    assert!(!p.contains("ExternalMergeSort") && !p.contains("Limit"), "{p}");
}

#[test]
fn s3h_02_order_by_alone_and_limit_alone_are_left_alone() {
    let db = topn_db();
    let sort_only = plan(&db, "select * from t order by a");
    assert!(sort_only.contains("ExternalMergeSort") && !sort_only.contains("TopN"), "{sort_only}");
    let limit_only = plan(&db, "select * from t limit 5");
    assert!(limit_only.contains("Limit") && !limit_only.contains("TopN"), "{limit_only}");
}

#[test]
fn s3h_02_the_rows_are_the_same_as_sorting_everything() {
    let db = topn_db();
    let top = sql(&db, "select * from t order by a desc, b limit 7");
    let all = sql(&db, "select * from t order by a desc, b");
    assert_eq!(top, all[..7].to_vec(), "he rows are the same as sorting everything");
    let top = sql(&db, "select b, a from t order by a, b desc limit 4");
    let all = sql(&db, "select b, a from t order by a, b desc");
    assert_eq!(top, all[..4].to_vec(), "he rows are the same as sorting everything");
}

#[test]
fn s3h_02_ties_come_out_as_a_stable_sort_followed_by_a_limit_would_give() {
    let db = topn_db();
    let top = sql(&db, "select * from t order by a limit 12");
    let all = sql(&db, "select * from t order by a");
    assert_eq!(top, all[..12].to_vec(), "rows with equal a keep their table order");
}

#[test]
fn s3h_02_limit_zero_and_a_limit_larger_than_the_table() {
    let db = topn_db();
    assert!(sql(&db, "select * from t order by a limit 0").is_empty(), "imit zero and a limit larger than the table: expected `sql(&db, \"select * from t order by a limit 0\").is_empty()`");
    assert_eq!(sql(&db, "select * from t order by a limit 1000").len(), 60, "imit zero and a limit larger than the table");
}

#[test]
fn s3h_02_two_top_ns_in_one_query_and_top_n_inside_a_join() {
    let db = topn_db();
    let p = plan(&db, "select * from (select * from t order by a desc limit 5) order by a asc limit 3");
    assert_eq!(p.matches("TopN").count(), 2, "{p}");
    let rows = sql(&db, "select * from (select * from t order by a desc limit 5) order by a asc limit 3");
    assert_eq!(rows.len(), 3, "wo top ns in one query and top n inside a join");
    let joined = plan(&db, "select * from t x, (select * from t order by b desc limit 4) y where x.b = y.b");
    assert!(joined.contains("TopN"), "{joined}");
    assert_eq!(sql(&db, "select * from t x, (select * from t order by b desc limit 4) y where x.b = y.b").len(), 4, "wo top ns in one query and top n inside a join");
}

// ---- 3h-03 · point lookups ---------------------------------------------------------------------------------------------------------

#[test]
fn s3h_03_column_equals_constant_either_way_round() {
    let (c, keys) = Optimizer::extract_point_lookup(&eq(col(0, 3), constant(7))).unwrap();
    assert_eq!((c, texts(&keys)), (3, vec!["7".to_string()]), "olumn equals constant either way round");
    let (c, keys) = Optimizer::extract_point_lookup(&eq(constant(9), col(0, 1))).unwrap();
    assert_eq!((c, texts(&keys)), (1, vec!["9".to_string()]), "olumn equals constant either way round");
}

#[test]
fn s3h_03_an_or_of_equalities_on_one_column_gives_all_the_keys_in_order() {
    let p = or(eq(constant(4), col(0, 0)), eq(col(0, 0), constant(7)));
    let (c, keys) = Optimizer::extract_point_lookup(&p).unwrap();
    assert_eq!((c, texts(&keys)), (0, vec!["4".to_string(), "7".to_string()]), "n or of equalities on one column gives all the keys in order");
    let three = or(or(eq(col(0, 2), constant(1)), eq(col(0, 2), constant(2))), eq(col(0, 2), constant(3)));
    assert_eq!(texts(&Optimizer::extract_point_lookup(&three).unwrap().1), vec!["1", "2", "3"], "n or of equalities on one column gives all the keys in order");
}

#[test]
fn s3h_03_other_predicates_are_not_point_lookups() {
    assert!(Optimizer::extract_point_lookup(&cmp(col(0, 0), constant(1), ComparisonType::GreaterThan)).is_none(), "ther predicates are not point lookups: expected `Optimizer::extract_point_lookup(&cmp(col(0, 0), constant(1), ComparisonType::GreaterThan)).is_none()`");
    assert!(Optimizer::extract_point_lookup(&cmp(col(0, 0), constant(1), ComparisonType::NotEqual)).is_none(), "ther predicates are not point lookups: expected `Optimizer::extract_point_lookup(&cmp(col(0, 0), constant(1), ComparisonType::NotEqual)).is_none()`");
    assert!(Optimizer::extract_point_lookup(&eq(col(0, 0), col(0, 1))).is_none(), "column = column");
    assert!(Optimizer::extract_point_lookup(&eq(constant(1), constant(1))).is_none(), "constant = constant");
}

#[test]
fn s3h_03_an_or_over_different_columns_or_with_another_condition_is_not_one() {
    assert!(Optimizer::extract_point_lookup(&or(eq(col(0, 0), constant(1)), eq(col(0, 1), constant(2)))).is_none(), "n or over different columns or with another condition is not one: expected `Optimizer::extract_point_lookup(&or(eq(col(0, 0), constant(1)), eq(col(0, 1), constant(2)))).is_none...`");
    assert!(Optimizer::extract_point_lookup(&or(eq(col(0, 0), constant(1)), cmp(col(0, 0), constant(2), ComparisonType::LessThan))).is_none(), "n or over different columns or with another condition is not one: expected `Optimizer::extract_point_lookup(&or(eq(col(0, 0), constant(1)), cmp(col(0, 0), constant(2), Comparis...`");
    assert!(Optimizer::extract_point_lookup(&and(eq(col(0, 0), constant(1)), eq(col(0, 0), constant(1)))).is_none(), "an AND is handled by the rule, conjunct by conjunct");
}

#[test]
fn s3h_03_the_constant_may_be_negative_or_a_string_expression_is_refused() {
    assert_eq!(texts(&Optimizer::extract_point_lookup(&eq(col(0, 0), constant(-5))).unwrap().1), vec!["-5"], "he constant may be negative or a string expression is refused");
    let arithmetic = eq(col(0, 0), cmp(constant(1), constant(2), ComparisonType::Equal));
    assert!(Optimizer::extract_point_lookup(&arithmetic).is_none(), "the key must be a constant expression node, not a computation");
}

// ---- 3h-03 · sequential scan to index scan ------------------------------------------------------------------------------------------

fn index_db() -> BusTubInstance {
    let db = new_db();
    sql(&db, "create table t(v1 int, v2 int, v3 int)");
    sql(&db, "insert into t values (1, 50, 645), (2, 40, 721), (4, 20, 445), (5, 10, 445), (3, 30, 645), (null, 0, 0)");
    sql(&db, "create index t_v1 on t(v1)");
    db
}

#[test]
fn s3h_03_equality_on_an_indexed_column_uses_the_index() {
    let db = index_db();
    let p = plan(&db, "select * from t where v1 = 2");
    assert!(p.contains("IndexScan"), "{p}");
    assert!(!p.contains("SeqScan"), "{p}");
    assert_eq!(sql(&db, "select * from t where v1 = 2"), vec!["2 40 721"], "quality on an indexed column uses the index");
    assert_eq!(sql(&db, "select * from t where 3 = v1"), vec!["3 30 645"], "quality on an indexed column uses the index");
}

#[test]
fn s3h_03_an_or_of_equalities_looks_up_each_key() {
    let db = index_db();
    assert!(plan(&db, "select * from t where 4 = v1 or v1 = 5").contains("IndexScan"), "n or of equalities looks up each key: expected `plan(&db, \"select * from t where 4 = v1 or v1 = 5\").contains(\"IndexScan\")`");
    assert_eq!(sorted(sql(&db, "select * from t where 4 = v1 or v1 = 5")), vec!["4 20 445", "5 10 445"], "n or of equalities looks up each key");
    assert_eq!(sql(&db, "select * from t where v1 = 99 or v1 = 98").len(), 0, "n or of equalities looks up each key");
}

#[test]
fn s3h_03_other_predicates_and_other_columns_stay_sequential_scans() {
    let db = index_db();
    assert!(plan(&db, "select * from t where v1 > 2").contains("SeqScan"), "ther predicates and other columns stay sequential scans: expected `plan(&db, \"select * from t where v1 > 2\").contains(\"SeqScan\")`");
    assert!(plan(&db, "select * from t where v2 = 20").contains("SeqScan"), "no index on v2");
    assert!(plan(&db, "select * from t where v1 = 2 or v2 = 20").contains("SeqScan"), "an OR over two columns");
    assert!(plan(&db, "select * from t").contains("SeqScan"), "ther predicates and other columns stay sequential scans: expected `plan(&db, \"select * from t\").contains(\"SeqScan\")`");
}

#[test]
fn s3h_03_another_condition_is_checked_on_what_the_index_finds() {
    let db = index_db();
    let p = plan(&db, "select * from t where v1 = 5 and v3 = 445");
    assert!(p.contains("IndexScan"), "{p}");
    assert_eq!(sql(&db, "select * from t where v1 = 5 and v3 = 445"), vec!["5 10 445"], "nother condition is checked on what the index finds");
    assert_eq!(sql(&db, "select * from t where v1 = 5 and v3 = 1").len(), 0, "the whole predicate still applies");
    assert_eq!(sql(&db, "select * from t where v3 = 645 and v1 = 3"), vec!["3 30 645"], "the indexed conjunct may be second");
}

#[test]
fn s3h_03_comparing_with_null_finds_nothing() {
    let db = index_db();
    assert_eq!(sql(&db, "select * from t where v1 = null").len(), 0, "NULL = NULL is unknown, not true");
}

#[test]
fn s3h_03_updates_and_deletes_see_the_same_rows_as_a_scan() {
    let db = index_db();
    assert_eq!(sql(&db, "update t set v3 = 1 where v1 = 4"), vec!["1"], "pdates and deletes see the same rows as a scan");
    assert_eq!(sql(&db, "select * from t where v1 = 4"), vec!["4 20 1"], "pdates and deletes see the same rows as a scan");
    assert_eq!(sql(&db, "delete from t where v1 = 4 or v1 = 5"), vec!["2"], "pdates and deletes see the same rows as a scan");
    assert_eq!(sql(&db, "select * from t where v1 = 5").len(), 0, "pdates and deletes see the same rows as a scan");
    assert_eq!(sql(&db, "select * from t").len(), 4, "pdates and deletes see the same rows as a scan");
    sql(&db, "insert into t values (4, 1, 1)");
    assert_eq!(sql(&db, "select * from t where v1 = 4"), vec!["4 1 1"], "the deleted key can be used again");
}

#[test]
fn s3h_03_an_empty_table_with_an_index() {
    let db = new_db();
    sql(&db, "create table e(v1 int)");
    sql(&db, "create index e_v1 on e(v1)");
    assert!(plan(&db, "select * from e where v1 = 1").contains("IndexScan"), "n empty table with an index: expected `plan(&db, \"select * from e where v1 = 1\").contains(\"IndexScan\")`");
    assert!(sql(&db, "select * from e where v1 = 1").is_empty(), "n empty table with an index: expected `sql(&db, \"select * from e where v1 = 1\").is_empty()`");
    sql(&db, "insert into e values (1)");
    assert_eq!(sql(&db, "select * from e where v1 = 1"), vec!["1"], "n empty table with an index");
}

// ---- properties: rules against their specification and against plain Rust --------------------------------------------------------

fn pconfig() -> ProptestConfig {
    ProptestConfig { cases: 48, max_shrink_iters: 1000, ..ProptestConfig::default() }
}

/// A conjunct of a join predicate between the left input (tuple 0) and the right input (tuple 1), described so that the model can
/// say whether it is a key of a hash join.
#[derive(Clone, Debug)]
enum Conjunct {
    /// `left.c = right.d`, written in either order.
    CrossEq { left: u32, right: u32, swapped: bool },
    /// Both columns from one side.
    SameSide { side: u32, a: u32, b: u32 },
    /// `left.c < right.d` (or `<>`).
    CrossLess { left: u32, right: u32 },
    /// `left.c = 7`.
    EqConst { left: u32 },
    /// `left.c = right.d or left.e = right.f`.
    OrOfCross { a: (u32, u32), b: (u32, u32) },
}

fn conjunct_strategy() -> impl Strategy<Value = Conjunct> {
    prop_oneof![
        5 => (0u32..3, 0u32..3, any::<bool>()).prop_map(|(left, right, swapped)| Conjunct::CrossEq { left, right, swapped }),
        1 => (0u32..2, 0u32..3, 0u32..3).prop_map(|(side, a, b)| Conjunct::SameSide { side, a, b }),
        1 => (0u32..3, 0u32..3).prop_map(|(left, right)| Conjunct::CrossLess { left, right }),
        1 => (0u32..3).prop_map(|left| Conjunct::EqConst { left }),
        1 => ((0u32..3, 0u32..3), (0u32..3, 0u32..3)).prop_map(|(a, b)| Conjunct::OrOfCross { a, b }),
    ]
}

impl Conjunct {
    fn expr(&self) -> ExprRef {
        match self {
            Conjunct::CrossEq { left, right, swapped: false } => eq(col(0, *left), col(1, *right)),
            Conjunct::CrossEq { left, right, swapped: true } => eq(col(1, *right), col(0, *left)),
            Conjunct::SameSide { side, a, b } => eq(col(*side, *a), col(*side, *b)),
            Conjunct::CrossLess { left, right } => cmp(col(0, *left), col(1, *right), ComparisonType::LessThan),
            Conjunct::EqConst { left } => eq(col(0, *left), constant(7)),
            Conjunct::OrOfCross { a, b } => or(eq(col(0, a.0), col(1, a.1)), eq(col(0, b.0), col(1, b.1))),
        }
    }

    fn is_key(&self) -> bool {
        matches!(self, Conjunct::CrossEq { .. })
    }
}

/// Folds the conjuncts into an AND tree of the given shape: right-leaning, left-leaning or balanced.
fn and_tree(conjuncts: &[ExprRef], shape: u8) -> ExprRef {
    match conjuncts {
        [one] => one.clone(),
        _ => {
            let mid = match shape % 3 {
                0 => 1,
                1 => conjuncts.len() - 1,
                _ => conjuncts.len() / 2,
            };
            and(and_tree(&conjuncts[..mid], shape / 3), and_tree(&conjuncts[mid..], shape / 3))
        }
    }
}

proptest! {
    #![proptest_config(pconfig())]

    /// A predicate is a list of hash-join keys exactly when every one of its AND-ed parts is an equality between a column of each
    /// side, whatever the nesting; the keys come out in the order the parts are written, left column first.
    #[test]
    fn s3h_01_equi_join_keys_exist_exactly_when_every_conjunct_is_a_cross_equality(conjuncts in prop::collection::vec(conjunct_strategy(), 1..6), shape in 0u8..27) {
        let exprs: Vec<ExprRef> = conjuncts.iter().map(Conjunct::expr).collect();
        let found = Optimizer::extract_equi_join_keys(&and_tree(&exprs, shape));
        if conjuncts.iter().all(Conjunct::is_key) {
            let (l, r) = found.expect("every part is a cross equality");
            let want_l: Vec<String> = conjuncts.iter().map(|c| match c { Conjunct::CrossEq { left, .. } => format!("#0.{left}"), _ => unreachable!() }).collect();
            let want_r: Vec<String> = conjuncts.iter().map(|c| match c { Conjunct::CrossEq { right, .. } => format!("#0.{right}"), _ => unreachable!() }).collect();
            prop_assert_eq!((texts(&l), texts(&r)), (want_l, want_r));
        } else {
            prop_assert!(found.is_none(), "a part that is not a cross equality rules the predicate out");
        }
        let mut flat = vec![];
        Optimizer::conjuncts(&and_tree(&exprs, shape), &mut flat);
        prop_assert_eq!(flat.len(), conjuncts.len(), "conjuncts flatten AND at any depth and keep everything else whole");
    }

    /// For random tables and random join conditions (any mix of equalities, comparisons, constants and ORs), the plan has a hash
    /// join exactly when every part is a cross equality, and the rows are those of the naive join, with the rule and without it.
    #[test]
    fn s3h_01_the_hash_join_rule_fires_exactly_for_equalities_and_changes_no_rows(
        a in prop::collection::vec(prop::collection::vec(model::cell(), 3), 0..12),
        b in prop::collection::vec(prop::collection::vec(model::cell(), 3), 0..12),
        conjuncts in prop::collection::vec(conjunct_strategy(), 1..4),
        left in any::<bool>(),
        where_form in any::<bool>(),
    ) {
        let db = new_db();
        sql(&db, "create table a(c0 int, c1 int, c2 int)");
        sql(&db, "create table b(c0 int, c1 int, c2 int)");
        for (name, rows) in [("a", &a), ("b", &b)] {
            if !rows.is_empty() { sql(&db, &format!("insert into {name} values {}", rows.iter().map(model::values).collect::<Vec<_>>().join(", "))); }
        }
        let text = |c: &Conjunct| match c {
            Conjunct::CrossEq { left, right, swapped: false } => format!("a.c{left} = b.c{right}"),
            Conjunct::CrossEq { left, right, swapped: true } => format!("b.c{right} = a.c{left}"),
            Conjunct::SameSide { side, a, b } => { let t = ["a", "b"][*side as usize]; format!("{t}.c{a} = {t}.c{b}") }
            Conjunct::CrossLess { left, right } => format!("a.c{left} < b.c{right}"),
            Conjunct::EqConst { left } => format!("a.c{left} = 7"),
            Conjunct::OrOfCross { a, b } => format!("(a.c{} = b.c{} or a.c{} = b.c{})", a.0, a.1, b.0, b.1),
        };
        let predicate = conjuncts.iter().map(text).collect::<Vec<_>>().join(" and ");
        let columns = ["a.c0", "a.c1", "a.c2", "b.c0", "b.c1", "b.c2"];
        let holds = |row: &model::Row| conjuncts.iter().all(|c| {
            let v = |i: usize| row[i];
            let eqv = |x: Option<i64>, y: Option<i64>| x.is_some() && x == y;
            match c {
                Conjunct::CrossEq { left, right, .. } => eqv(v(*left as usize), v(3 + *right as usize)),
                Conjunct::SameSide { side, a, b } => eqv(v((*side * 3 + *a) as usize), v((*side * 3 + *b) as usize)),
                Conjunct::CrossLess { left, right } => matches!((v(*left as usize), v(3 + *right as usize)), (Some(x), Some(y)) if x < y),
                Conjunct::EqConst { left } => v(*left as usize) == Some(7),
                Conjunct::OrOfCross { a, b } => eqv(v(a.0 as usize), v(3 + a.1 as usize)) || eqv(v(b.0 as usize), v(3 + b.1 as usize)),
            }
        });
        let query = if left { format!("select * from a left join b on {predicate}") } else if where_form { format!("select * from a, b where {predicate}") } else { format!("select * from a join b on {predicate}") };
        let _ = columns;
        let p = plan(&db, &query);
        let all_keys = conjuncts.iter().all(Conjunct::is_key);
        prop_assert_eq!(p.contains("HashJoin"), all_keys, "{}\n{}", query, p);
        prop_assert_eq!(!p.contains("NestedLoopJoin"), all_keys, "{}\n{}", query, p);
        let want = model::naive_join(&a, &b, 3, left, holds);
        let (optimized, plain) = both_ways(&db, &query);
        prop_assert_eq!(optimized, want.clone(), "with the rule: {}", query);
        prop_assert_eq!(plain, want, "without it: {}", query);
    }

    /// `order by .. limit n` becomes a top-N exactly when both are present, never changes the rows, and nothing else becomes a top-N.
    #[test]
    fn s3h_02_top_n_replaces_exactly_a_sort_followed_by_a_limit(rows in prop::collection::vec((0i32..6, 0i32..50), 0..60), order in 0u8..4, limit in prop::option::of(0usize..70)) {
        let db = new_db();
        sql(&db, "create table t(a int, b int)");
        if !rows.is_empty() { sql(&db, &format!("insert into t values {}", rows.iter().map(|(a, b)| format!("({a}, {b})")).collect::<Vec<_>>().join(", "))); }
        let clause = ["", " order by a", " order by a desc, b", " order by b desc"][order as usize];
        let query = format!("select * from t{}{}", clause, limit.map_or(String::new(), |n| format!(" limit {n}")));
        let p = plan(&db, &query);
        prop_assert_eq!(p.contains("TopN"), order > 0 && limit.is_some(), "{}\n{}", query, p);
        let mut want: Vec<(i32, i32)> = rows.clone();
        match order {
            1 => want.sort_by_key(|r| r.0),
            2 => want.sort_by(|x, y| y.0.cmp(&x.0).then(x.1.cmp(&y.1))),
            3 => want.sort_by_key(|r| std::cmp::Reverse(r.1)),
            _ => {}
        }
        if let Some(n) = limit { want.truncate(n); }
        let got: Vec<(i32, i32)> = sql(&db, &query).iter().map(|l| { let mut it = l.split(' ').map(|x| x.parse::<i32>().unwrap()); (it.next().unwrap(), it.next().unwrap()) }).collect();
        prop_assert_eq!(got, want, "{}", query);
    }

    /// A point lookup on an indexed column becomes an index scan, with the whole predicate kept as a filter; every other predicate
    /// stays a sequential scan; and the rows are those of the plain filter on a vector.
    #[test]
    fn s3h_03_point_lookups_use_the_index_and_change_no_rows(
        n in 0i64..25,
        rows in prop::collection::vec((model::cell(), model::cell()), 0..25),
        parts in prop::collection::vec((0u8..7, -2i64..27, -2i64..27), 1..4),
    ) {
        let db = new_db();
        sql(&db, "create table t(v1 int, v2 int, v3 int)");
        let data: Vec<model::Row> = rows.iter().take(n as usize).enumerate().map(|(i, (b, c))| vec![Some(i as i64), *b, *c]).collect();
        if !data.is_empty() { sql(&db, &format!("insert into t values {}", data.iter().map(model::values).collect::<Vec<_>>().join(", "))); }
        sql(&db, "create index t_v1 on t(v1)");
        // kinds: 0 v1 = k, 1 k = v1, 2 v1 = k or v1 = k2, 3 v2 = k, 4 v1 > k, 5 v1 = v2, 6 v3 = k
        let text = |(kind, k, k2): &(u8, i64, i64)| match kind {
            0 => format!("v1 = {k}"),
            1 => format!("{k} = v1"),
            2 => format!("(v1 = {k} or v1 = {k2})"),
            3 => format!("v2 = {k}"),
            4 => format!("v1 > {k}"),
            5 => "v1 = v2".to_string(),
            _ => format!("v3 = {k}"),
        };
        let holds = |row: &model::Row| parts.iter().all(|(kind, k, k2)| {
            let (v1, v2, v3) = (row[0], row[1], row[2]);
            match kind {
                0 | 1 => v1 == Some(*k),
                2 => v1 == Some(*k) || v1 == Some(*k2),
                3 => v2 == Some(*k),
                4 => matches!(v1, Some(x) if x > *k),
                5 => v1.is_some() && v1 == v2,
                _ => v3 == Some(*k),
            }
        });
        let predicate = parts.iter().map(text).collect::<Vec<_>>().join(" and ");
        let query = format!("select * from t where {predicate}");
        let p = plan(&db, &query);
        let indexable = parts.iter().any(|(kind, ..)| *kind <= 2);
        prop_assert_eq!(p.contains("IndexScan"), indexable, "{}\n{}", query, p);
        let want: Vec<String> = { let mut v: Vec<String> = data.iter().filter(|r| holds(r)).map(model::line).collect(); v.sort(); v };
        prop_assert_eq!(sorted(sql(&db, &query)), want, "{}", query);
    }
}

// ---- 3h-04 · boss: optimised and plain plans return the same rows ------------------------------------------------------------------

proptest! {
    #![proptest_config(ProptestConfig { cases: 40, max_shrink_iters: 500, ..ProptestConfig::default() })]

    /// A query that joins, filters, sorts and limits returns the same rows with every optimizer rule on, with only BusTub's starter
    /// rules, and in a plain Rust computation: the definition of a correct rewrite.
    #[test]
    fn s3h_04_the_optimised_plan_and_the_plain_plan_return_the_same_rows(
        a in prop::collection::vec((model::cell(), model::cell()), 0..12),
        b in prop::collection::vec((model::cell(), model::cell()), 0..12),
        threshold in -3i64..4,
        n in 0usize..20,
        indexed in any::<bool>(),
    ) {
        let db = new_db();
        sql(&db, "create table a(x int, y int)");
        sql(&db, "create table b(p int, q int)");
        // the index holds one row per key (it is a primary-key style index), so an indexed table has distinct keys
        let b: Vec<(Option<i64>, Option<i64>)> = if indexed {
            let mut seen = std::collections::HashSet::new();
            b.iter().copied().filter(|(p, _)| p.is_none() || seen.insert(*p)).collect()
        } else { b.clone() };
        for (name, rows) in [("a", &a), ("b", &b)] {
            if !rows.is_empty() { sql(&db, &format!("insert into {name} values {}", rows.iter().map(|(x, y)| format!("({}, {})", x.map_or("null".to_string(), |v| v.to_string()), y.map_or("null".to_string(), |v| v.to_string()))).collect::<Vec<_>>().join(", "))); }
        }

        if indexed { sql(&db, "create index b_p on b(p)"); }
        let query = format!("select * from a join b on a.x = b.p where a.y > {threshold} order by a.x, a.y, b.p, b.q limit {n}");
        let la: Vec<model::Row> = a.iter().map(|(x, y)| vec![*x, *y]).collect();
        let lb: Vec<model::Row> = b.iter().map(|(x, y)| vec![*x, *y]).collect();
        let mut want: Vec<model::Row> = vec![];
        for l in &la { for r in &lb { if l[0].is_some() && l[0] == r[0] && matches!(l[1], Some(y) if y > threshold) { want.push(l.iter().chain(r.iter()).copied().collect()); } } }
        want.sort_by(|p, q| p.iter().zip(q.iter()).map(|(x, y)| x.cmp(y)).find(|o| *o != std::cmp::Ordering::Equal).unwrap_or(std::cmp::Ordering::Equal));
        want.truncate(n);
        let want: Vec<String> = want.iter().map(model::line).collect();
        prop_assert_eq!(sql(&db, &query), want.clone(), "all rules");
        sql(&db, "set force_optimizer_starter_rule=yes");
        prop_assert_eq!(sql(&db, &query), want, "starter rules only");
        sql(&db, "set force_optimizer_starter_rule=no");
    }
}
