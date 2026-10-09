//! Tests for module 3h: optimizer rules.

use std::sync::Arc;

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

// ---- 3h-02 · nested loop join to hash join ----------------------------------------------------------------------------------------

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
fn s3h_02_an_equality_join_becomes_a_hash_join() {
    let db = join_db();
    let p = plan(&db, "select * from a inner join b on a.x = b.p");
    assert!(p.contains("HashJoin { type=Inner, left_key=[#0.0], right_key=[#0.0] }"), "{p}");
    assert!(!p.contains("NestedLoopJoin"), "{p}");
}

#[test]
fn s3h_02_a_cross_join_with_a_where_becomes_a_hash_join() {
    let db = join_db();
    let p = plan(&db, "select * from a, b where a.x = b.p");
    assert!(p.contains("HashJoin"), "{p}");
    assert!(!p.contains("Filter"), "the filter was merged into the join and used as keys: {p}");
}

#[test]
fn s3h_02_several_conditions_make_several_keys() {
    let db = join_db();
    let p = plan(&db, "select * from a join b on a.x = b.p and b.q = a.y");
    assert!(p.contains("left_key=[#0.0, #0.1], right_key=[#0.0, #0.1]"), "{p}");
}

#[test]
fn s3h_02_a_condition_that_is_not_an_equality_keeps_the_nested_loop() {
    let db = join_db();
    assert!(plan(&db, "select * from a join b on a.x < b.p").contains("NestedLoopJoin"), "a condition that is not an equality keeps the nested loop: expected `plan(&db, \"select * from a join b on a.x < b.p\").contains(\"NestedLoopJoin\")`");
    assert!(plan(&db, "select * from a join b on a.x = b.p and a.y > 5").contains("NestedLoopJoin"), "a condition that is not an equality keeps the nested loop: expected `plan(&db, \"select * from a join b on a.x = b.p and a.y > 5\").contains(\"NestedLoopJoin\")`");
    assert!(plan(&db, "select * from a join b on a.x = b.p or a.y = b.q").contains("NestedLoopJoin"), "a condition that is not an equality keeps the nested loop: expected `plan(&db, \"select * from a join b on a.x = b.p or a.y = b.q\").contains(\"NestedLoopJoin\")`");
    assert!(plan(&db, "select * from a join b on a.x + 1 = b.p").contains("NestedLoopJoin"), "an expression is not a column key");
}

#[test]
fn s3h_02_left_joins_become_hash_joins_too() {
    let db = join_db();
    let p = plan(&db, "select * from a left join b on a.x = b.p");
    assert!(p.contains("HashJoin { type=Left"), "{p}");
}

#[test]
fn s3h_02_the_results_are_the_same_as_with_nested_loops() {
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
        assert!(!h.is_empty() || q.contains("a.y = b.q"), "left joins become hash joins too: expected `!h.is_empty() || q.contains(\"a.y = b.q\")`");
    }
}

#[test]
fn s3h_02_a_three_way_join_becomes_two_hash_joins() {
    let db = join_db();
    let q = "select * from a join b on a.x = b.p join c on c.r = a.x";
    let p = plan(&db, q);
    assert_eq!(p.matches("HashJoin").count(), 2, "{p}");
    let (h, n) = both_ways(&db, q);
    assert_eq!(h, n, "left joins become hash joins too");
    let nested = "select * from c join (a join b on a.x = b.p) on c.r = b.p";
    assert_eq!(plan(&db, nested).matches("HashJoin").count(), 2, "left joins become hash joins too");
    let (h, n) = both_ways(&db, nested);
    assert_eq!(h, n, "left joins become hash joins too");
}

// ---- 3h-03 · sort + limit to top-N ------------------------------------------------------------------------------------------------

fn topn_db() -> BusTubInstance {
    let db = new_db();
    sql(&db, "create table t(a int, b int)");
    let rows: Vec<String> = (0..60).map(|i| format!("({}, {})", (i * 37) % 11, i)).collect();
    sql(&db, &format!("insert into t values {}", rows.join(", ")));
    db
}

#[test]
fn s3h_03_order_by_with_a_limit_becomes_top_n() {
    let db = topn_db();
    let p = plan(&db, "select * from t order by a desc limit 5");
    assert!(p.contains("TopN { n=5"), "{p}");
    assert!(!p.contains("ExternalMergeSort") && !p.contains("Limit"), "{p}");
}

#[test]
fn s3h_03_order_by_alone_and_limit_alone_are_left_alone() {
    let db = topn_db();
    let sort_only = plan(&db, "select * from t order by a");
    assert!(sort_only.contains("ExternalMergeSort") && !sort_only.contains("TopN"), "{sort_only}");
    let limit_only = plan(&db, "select * from t limit 5");
    assert!(limit_only.contains("Limit") && !limit_only.contains("TopN"), "{limit_only}");
}

#[test]
fn s3h_03_the_rows_are_the_same_as_sorting_everything() {
    let db = topn_db();
    let top = sql(&db, "select * from t order by a desc, b limit 7");
    let all = sql(&db, "select * from t order by a desc, b");
    assert_eq!(top, all[..7].to_vec(), "left joins become hash joins too");
    let top = sql(&db, "select b, a from t order by a, b desc limit 4");
    let all = sql(&db, "select b, a from t order by a, b desc");
    assert_eq!(top, all[..4].to_vec(), "left joins become hash joins too");
}

#[test]
fn s3h_03_ties_come_out_as_a_stable_sort_followed_by_a_limit_would_give() {
    let db = topn_db();
    let top = sql(&db, "select * from t order by a limit 12");
    let all = sql(&db, "select * from t order by a");
    assert_eq!(top, all[..12].to_vec(), "rows with equal a keep their table order");
}

#[test]
fn s3h_03_limit_zero_and_a_limit_larger_than_the_table() {
    let db = topn_db();
    assert!(sql(&db, "select * from t order by a limit 0").is_empty(), "left joins become hash joins too: expected `sql(&db, \"select * from t order by a limit 0\").is_empty()`");
    assert_eq!(sql(&db, "select * from t order by a limit 1000").len(), 60, "left joins become hash joins too");
}

#[test]
fn s3h_03_two_top_ns_in_one_query_and_top_n_inside_a_join() {
    let db = topn_db();
    let p = plan(&db, "select * from (select * from t order by a desc limit 5) order by a asc limit 3");
    assert_eq!(p.matches("TopN").count(), 2, "{p}");
    let rows = sql(&db, "select * from (select * from t order by a desc limit 5) order by a asc limit 3");
    assert_eq!(rows.len(), 3, "left joins become hash joins too");
    let joined = plan(&db, "select * from t x, (select * from t order by b desc limit 4) y where x.b = y.b");
    assert!(joined.contains("TopN"), "{joined}");
    assert_eq!(sql(&db, "select * from t x, (select * from t order by b desc limit 4) y where x.b = y.b").len(), 4, "left joins become hash joins too");
}

// ---- 3h-04 · point lookups ---------------------------------------------------------------------------------------------------------

#[test]
fn s3h_04_column_equals_constant_either_way_round() {
    let (c, keys) = Optimizer::extract_point_lookup(&eq(col(0, 3), constant(7))).unwrap();
    assert_eq!((c, texts(&keys)), (3, vec!["7".to_string()]), "left joins become hash joins too");
    let (c, keys) = Optimizer::extract_point_lookup(&eq(constant(9), col(0, 1))).unwrap();
    assert_eq!((c, texts(&keys)), (1, vec!["9".to_string()]), "left joins become hash joins too");
}

#[test]
fn s3h_04_an_or_of_equalities_on_one_column_gives_all_the_keys_in_order() {
    let p = or(eq(constant(4), col(0, 0)), eq(col(0, 0), constant(7)));
    let (c, keys) = Optimizer::extract_point_lookup(&p).unwrap();
    assert_eq!((c, texts(&keys)), (0, vec!["4".to_string(), "7".to_string()]), "left joins become hash joins too");
    let three = or(or(eq(col(0, 2), constant(1)), eq(col(0, 2), constant(2))), eq(col(0, 2), constant(3)));
    assert_eq!(texts(&Optimizer::extract_point_lookup(&three).unwrap().1), vec!["1", "2", "3"], "left joins become hash joins too");
}

#[test]
fn s3h_04_other_predicates_are_not_point_lookups() {
    assert!(Optimizer::extract_point_lookup(&cmp(col(0, 0), constant(1), ComparisonType::GreaterThan)).is_none(), "left joins become hash joins too: expected `Optimizer::extract_point_lookup(&cmp(col(0, 0), constant(1), ComparisonType::GreaterThan)).is_none()`");
    assert!(Optimizer::extract_point_lookup(&cmp(col(0, 0), constant(1), ComparisonType::NotEqual)).is_none(), "left joins become hash joins too: expected `Optimizer::extract_point_lookup(&cmp(col(0, 0), constant(1), ComparisonType::NotEqual)).is_none()`");
    assert!(Optimizer::extract_point_lookup(&eq(col(0, 0), col(0, 1))).is_none(), "column = column");
    assert!(Optimizer::extract_point_lookup(&eq(constant(1), constant(1))).is_none(), "constant = constant");
}

#[test]
fn s3h_04_an_or_over_different_columns_or_with_another_condition_is_not_one() {
    assert!(Optimizer::extract_point_lookup(&or(eq(col(0, 0), constant(1)), eq(col(0, 1), constant(2)))).is_none(), "left joins become hash joins too: expected `Optimizer::extract_point_lookup(&or(eq(col(0, 0), constant(1)), eq(col(0, 1), constant(2)))).is_none...`");
    assert!(Optimizer::extract_point_lookup(&or(eq(col(0, 0), constant(1)), cmp(col(0, 0), constant(2), ComparisonType::LessThan))).is_none(), "left joins become hash joins too: expected `Optimizer::extract_point_lookup(&or(eq(col(0, 0), constant(1)), cmp(col(0, 0), constant(2), Comparis...`");
    assert!(Optimizer::extract_point_lookup(&and(eq(col(0, 0), constant(1)), eq(col(0, 0), constant(1)))).is_none(), "an AND is handled by the rule, conjunct by conjunct");
}

#[test]
fn s3h_04_the_constant_may_be_negative_or_a_string_expression_is_refused() {
    assert_eq!(texts(&Optimizer::extract_point_lookup(&eq(col(0, 0), constant(-5))).unwrap().1), vec!["-5"], "left joins become hash joins too");
    let arithmetic = eq(col(0, 0), cmp(constant(1), constant(2), ComparisonType::Equal));
    assert!(Optimizer::extract_point_lookup(&arithmetic).is_none(), "the key must be a constant expression node, not a computation");
}

// ---- 3h-05 · sequential scan to index scan ------------------------------------------------------------------------------------------

fn index_db() -> BusTubInstance {
    let db = new_db();
    sql(&db, "create table t(v1 int, v2 int, v3 int)");
    sql(&db, "insert into t values (1, 50, 645), (2, 40, 721), (4, 20, 445), (5, 10, 445), (3, 30, 645), (null, 0, 0)");
    sql(&db, "create index t_v1 on t(v1)");
    db
}

#[test]
fn s3h_05_equality_on_an_indexed_column_uses_the_index() {
    let db = index_db();
    let p = plan(&db, "select * from t where v1 = 2");
    assert!(p.contains("IndexScan"), "{p}");
    assert!(!p.contains("SeqScan"), "{p}");
    assert_eq!(sql(&db, "select * from t where v1 = 2"), vec!["2 40 721"], "left joins become hash joins too");
    assert_eq!(sql(&db, "select * from t where 3 = v1"), vec!["3 30 645"], "left joins become hash joins too");
}

#[test]
fn s3h_05_an_or_of_equalities_looks_up_each_key() {
    let db = index_db();
    assert!(plan(&db, "select * from t where 4 = v1 or v1 = 5").contains("IndexScan"), "left joins become hash joins too: expected `plan(&db, \"select * from t where 4 = v1 or v1 = 5\").contains(\"IndexScan\")`");
    assert_eq!(sorted(sql(&db, "select * from t where 4 = v1 or v1 = 5")), vec!["4 20 445", "5 10 445"], "left joins become hash joins too");
    assert_eq!(sql(&db, "select * from t where v1 = 99 or v1 = 98").len(), 0, "left joins become hash joins too");
}

#[test]
fn s3h_05_other_predicates_and_other_columns_stay_sequential_scans() {
    let db = index_db();
    assert!(plan(&db, "select * from t where v1 > 2").contains("SeqScan"), "left joins become hash joins too: expected `plan(&db, \"select * from t where v1 > 2\").contains(\"SeqScan\")`");
    assert!(plan(&db, "select * from t where v2 = 20").contains("SeqScan"), "no index on v2");
    assert!(plan(&db, "select * from t where v1 = 2 or v2 = 20").contains("SeqScan"), "an OR over two columns");
    assert!(plan(&db, "select * from t").contains("SeqScan"), "left joins become hash joins too: expected `plan(&db, \"select * from t\").contains(\"SeqScan\")`");
}

#[test]
fn s3h_05_another_condition_is_checked_on_what_the_index_finds() {
    let db = index_db();
    let p = plan(&db, "select * from t where v1 = 5 and v3 = 445");
    assert!(p.contains("IndexScan"), "{p}");
    assert_eq!(sql(&db, "select * from t where v1 = 5 and v3 = 445"), vec!["5 10 445"], "left joins become hash joins too");
    assert_eq!(sql(&db, "select * from t where v1 = 5 and v3 = 1").len(), 0, "the whole predicate still applies");
    assert_eq!(sql(&db, "select * from t where v3 = 645 and v1 = 3"), vec!["3 30 645"], "the indexed conjunct may be second");
}

#[test]
fn s3h_05_comparing_with_null_finds_nothing() {
    let db = index_db();
    assert_eq!(sql(&db, "select * from t where v1 = null").len(), 0, "NULL = NULL is unknown, not true");
}

#[test]
fn s3h_05_updates_and_deletes_see_the_same_rows_as_a_scan() {
    let db = index_db();
    assert_eq!(sql(&db, "update t set v3 = 1 where v1 = 4"), vec!["1"], "left joins become hash joins too");
    assert_eq!(sql(&db, "select * from t where v1 = 4"), vec!["4 20 1"], "left joins become hash joins too");
    assert_eq!(sql(&db, "delete from t where v1 = 4 or v1 = 5"), vec!["2"], "left joins become hash joins too");
    assert_eq!(sql(&db, "select * from t where v1 = 5").len(), 0, "left joins become hash joins too");
    assert_eq!(sql(&db, "select * from t").len(), 4, "left joins become hash joins too");
    sql(&db, "insert into t values (4, 1, 1)");
    assert_eq!(sql(&db, "select * from t where v1 = 4"), vec!["4 1 1"], "the deleted key can be used again");
}

#[test]
fn s3h_05_an_empty_table_with_an_index() {
    let db = new_db();
    sql(&db, "create table e(v1 int)");
    sql(&db, "create index e_v1 on e(v1)");
    assert!(plan(&db, "select * from e where v1 = 1").contains("IndexScan"), "left joins become hash joins too: expected `plan(&db, \"select * from e where v1 = 1\").contains(\"IndexScan\")`");
    assert!(sql(&db, "select * from e where v1 = 1").is_empty(), "left joins become hash joins too: expected `sql(&db, \"select * from e where v1 = 1\").is_empty()`");
    sql(&db, "insert into e values (1)");
    assert_eq!(sql(&db, "select * from e where v1 = 1"), vec!["1"], "left joins become hash joins too");
}
