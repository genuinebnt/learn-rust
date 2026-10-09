//! Tests for module 3e: the access-method executors.

use std::sync::Arc;

mod common;

use bustub::catalog::catalog::TableInfo;
use bustub::catalog::column::Column;
use bustub::catalog::schema::Schema;
use bustub::common::bustub_instance::BusTubInstance;
use bustub::common::result_writer::SimpleStreamWriter;
use bustub::common::rid::Rid;
use bustub::execution::execution_engine::ExecutionEngine;
use bustub::execution::executor_context::ExecutorContext;
use bustub::execution::executor_factory::create_executor;
use bustub::execution::expressions::abstract_expression::ExprRef;
use bustub::execution::expressions::column_value_expression::ColumnValueExpression;
use bustub::execution::expressions::comparison_expression::{ComparisonExpression, ComparisonType};
use bustub::execution::expressions::constant_value_expression::ConstantValueExpression;
use bustub::execution::plans::plan_node::{PlanKind, PlanNode, PlanRef};
use bustub::storage::table::tuple::{Tuple, TupleMeta};
use bustub::types::type_id::TypeId;
use bustub::types::value::Value;
use common::sql_model as model;
use model::Row;
use proptest::prelude::*;

fn int(v: i32) -> Value {
    Value::integer(v)
}

fn ints(names: &[&str]) -> Schema {
    Schema::new(names.iter().map(|n| Column::new(n, TypeId::Integer)).collect())
}

fn new_db() -> BusTubInstance {
    BusTubInstance::new(64)
}

/// Runs SQL and returns the rows as lines of space separated cells.
fn sql(db: &BusTubInstance, sql: &str) -> Vec<String> {
    let mut out = String::new();
    db.execute_sql(sql, &mut SimpleStreamWriter::new(&mut out, true, " "), None).unwrap_or_else(|e| panic!("{sql}: {e}"));
    out.lines().map(|l| l.trim_end().to_string()).collect()
}

fn sql_err(db: &BusTubInstance, sql: &str) -> bool {
    let mut out = String::new();
    db.execute_sql(sql, &mut SimpleStreamWriter::new(&mut out, true, " "), None).is_err()
}

/// Creates the table `name` with integer columns and stores `rows` straight into its heap (no executors involved).
fn table_with_rows(db: &BusTubInstance, name: &str, columns: &[&str], rows: &[Vec<i32>]) -> Arc<TableInfo<'static>> {
    let info = db.catalog.write().unwrap().create_table(name, &ints(columns)).unwrap();
    for r in rows {
        let values: Vec<Value> = r.iter().map(|v| int(*v)).collect();
        info.table.insert_tuple(&TupleMeta { ts: 0, is_deleted: false }, &Tuple::new(&values, &info.schema)).unwrap();
    }
    info
}

fn rows_1_to(n: i32) -> Vec<Vec<i32>> {
    (1..=n).map(|i| vec![i]).collect()
}

fn seq_scan_plan(info: &TableInfo<'_>, filter: Option<ExprRef>) -> PlanRef {
    let schema = Schema::new(info.schema.columns().iter().map(|c| c.with_column_name(&format!("{}.{}", info.name, c.name()))).collect());
    PlanNode::new(Arc::new(schema), vec![], PlanKind::SeqScan { table_oid: info.oid, table_name: info.name.clone(), filter_predicate: filter })
}

fn cmp(col: u32, op: ComparisonType, v: i32) -> ExprRef {
    Arc::new(ComparisonExpression::new(
        Arc::new(ColumnValueExpression::new(0, col, Column::new("c", TypeId::Integer))),
        Arc::new(ConstantValueExpression::new(int(v))),
        op,
    ))
}

/// Pulls every batch out of `plan`, returning (batch sizes, the first value of each tuple).
fn run_batches(db: &BusTubInstance, plan: &PlanRef, batch_size: usize) -> (Vec<usize>, Vec<Value>) {
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let mut exec = create_executor(&ctx, plan).unwrap();
    exec.init().unwrap();
    let (mut tuples, mut rids) = (vec![], vec![]);
    let (mut sizes, mut values) = (vec![], vec![]);
    while exec.next(&mut tuples, &mut rids, batch_size).unwrap() {
        assert_eq!(tuples.len(), rids.len(), "in helper `run_batches`");
        sizes.push(tuples.len());
        for t in &tuples {
            values.push(t.get_value(exec.output_schema(), 0));
        }
    }
    assert!(tuples.is_empty() && rids.is_empty(), "the last call leaves empty batches");
    (sizes, values)
}

fn execute(db: &BusTubInstance, plan: &PlanRef) -> Vec<Tuple> {
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let (ok, tuples) = ExecutionEngine::execute(plan, &ctx).unwrap();
    assert!(ok, "in helper `execute`: expected `ok`");
    tuples
}

// ---- 3e-01 · sequential scan ----------------------------------------------------------------------------------------------------

#[test]
fn s3e_01_an_empty_table_has_no_batches() {
    let db = new_db();
    let info = table_with_rows(&db, "t", &["a"], &[]);
    let (sizes, values) = run_batches(&db, &seq_scan_plan(&info, None), 20);
    assert!(sizes.is_empty() && values.is_empty(), "an empty table has no batches: expected `sizes.is_empty() && values.is_empty()`");
}

#[test]
fn s3e_01_every_row_comes_back_in_storage_order() {
    let db = new_db();
    let info = table_with_rows(&db, "t", &["a"], &rows_1_to(1000));
    let (_, values) = run_batches(&db, &seq_scan_plan(&info, None), 20);
    assert_eq!(values.len(), 1000, "every row comes back in storage order");
    assert!(values.iter().enumerate().all(|(i, v)| *v == int(i as i32 + 1)), "the order of insertion, across many pages");
}

#[test]
fn s3e_01_batches_have_at_most_batch_size_tuples_and_only_the_last_is_short() {
    let db = new_db();
    let info = table_with_rows(&db, "t", &["a"], &rows_1_to(50));
    let (sizes, _) = run_batches(&db, &seq_scan_plan(&info, None), 20);
    assert_eq!(sizes, vec![20, 20, 10], "batches have at most batch size tuples and only the last is short");
    let (sizes, _) = run_batches(&db, &seq_scan_plan(&info, None), 7);
    assert_eq!(sizes.iter().sum::<usize>(), 50, "batches have at most batch size tuples and only the last is short");
    assert!(sizes.iter().all(|s| *s <= 7) && sizes[..sizes.len() - 1].iter().all(|s| *s == 7), "batches have at most batch size tuples and only the last is short: expected `sizes.iter().all(|s| *s <= 7) && sizes[..sizes.len() - 1].iter().all(|s| *s == 7)`");
    let (sizes, _) = run_batches(&db, &seq_scan_plan(&info, None), 1000);
    assert_eq!(sizes, vec![50], "batches have at most batch size tuples and only the last is short");
}

#[test]
fn s3e_01_the_rids_are_the_rids_of_the_rows() {
    let db = new_db();
    let info = table_with_rows(&db, "t", &["a"], &rows_1_to(5));
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let mut exec = create_executor(&ctx, &seq_scan_plan(&info, None)).unwrap();
    exec.init().unwrap();
    let (mut tuples, mut rids) = (vec![], vec![]);
    assert!(exec.next(&mut tuples, &mut rids, 20).unwrap(), "the rids are the rids of the rows: expected `exec.next(&mut tuples, &mut rids, 20).unwrap()`");
    for (t, rid) in tuples.iter().zip(&rids) {
        assert_eq!(info.table.get_tuple(*rid).unwrap().1.get_value(&info.schema, 0), t.get_value(&info.schema, 0), "the rids are the rids of the rows");
    }
    assert_eq!(rids.iter().map(|r| r.slot_num()).collect::<Vec<_>>(), vec![0, 1, 2, 3, 4], "the rids are the rids of the rows");
}

#[test]
fn s3e_01_deleted_rows_are_skipped() {
    let db = new_db();
    let info = table_with_rows(&db, "t", &["a"], &rows_1_to(10));
    for (i, (_, tuple)) in info.table.make_iterator().collect::<Vec<_>>().iter().enumerate() {
        if i % 2 == 0 {
            info.table.update_tuple_meta(&TupleMeta { ts: 0, is_deleted: true }, tuple.get_rid()).unwrap();
        }
    }
    let (_, values) = run_batches(&db, &seq_scan_plan(&info, None), 20);
    assert_eq!(values, vec![int(2), int(4), int(6), int(8), int(10)], "deleted rows are skipped");
}

#[test]
fn s3e_01_init_starts_over_and_rows_added_after_init_are_not_seen() {
    let db = new_db();
    let info = table_with_rows(&db, "t", &["a"], &rows_1_to(3));
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let mut exec = create_executor(&ctx, &seq_scan_plan(&info, None)).unwrap();
    exec.init().unwrap();
    // a row stored after init is beyond the point where this scan stops (the Halloween problem)
    info.table.insert_tuple(&TupleMeta { ts: 0, is_deleted: false }, &Tuple::new(&[int(99)], &info.schema)).unwrap();
    let (mut tuples, mut rids) = (vec![], vec![]);
    assert!(exec.next(&mut tuples, &mut rids, 20).unwrap(), "init starts over and rows added after init are not seen: expected `exec.next(&mut tuples, &mut rids, 20).unwrap()`");
    assert_eq!(tuples.len(), 3, "init starts over and rows added after init are not seen");
    assert!(!exec.next(&mut tuples, &mut rids, 20).unwrap(), "init starts over and rows added after init are not seen: expected `!exec.next(&mut tuples, &mut rids, 20).unwrap()`");
    // a second init sees all four rows
    exec.init().unwrap();
    assert!(exec.next(&mut tuples, &mut rids, 20).unwrap(), "init starts over and rows added after init are not seen: expected `exec.next(&mut tuples, &mut rids, 20).unwrap()`");
    assert_eq!(tuples.len(), 4, "init starts over and rows added after init are not seen");
}

#[test]
fn s3e_01_sql_select_star() {
    let db = new_db();
    table_with_rows(&db, "t", &["a", "b"], &[vec![1, 10], vec![2, 20], vec![3, 30]]);
    assert_eq!(sql(&db, "select * from t"), vec!["1 10", "2 20", "3 30"], "sql select star");
    assert_eq!(sql(&db, "select b, a + b from t"), vec!["10 11", "20 22", "30 33"], "sql select star");
}

// ---- 3e-01 · sequential scan with a predicate ----------------------------------------------------------------------------------

#[test]
fn s3e_01_only_rows_for_which_the_predicate_is_true_are_returned() {
    let db = new_db();
    let info = table_with_rows(&db, "t", &["a"], &rows_1_to(10));
    let (_, values) = run_batches(&db, &seq_scan_plan(&info, Some(cmp(0, ComparisonType::GreaterThan, 7))), 20);
    assert_eq!(values, vec![int(8), int(9), int(10)], "only rows for which the predicate is true are returned");
    let (_, none) = run_batches(&db, &seq_scan_plan(&info, Some(cmp(0, ComparisonType::LessThan, 0))), 20);
    assert!(none.is_empty(), "only rows for which the predicate is true are returned: expected `none.is_empty()`");
}

#[test]
fn s3e_01_null_is_not_true() {
    let db = new_db();
    let info = db.catalog.write().unwrap().create_table("t", &ints(&["a"])).unwrap();
    for v in [int(1), Value::null(TypeId::Integer), int(3)] {
        info.table.insert_tuple(&TupleMeta { ts: 0, is_deleted: false }, &Tuple::new(&[v], &info.schema)).unwrap();
    }
    let (_, values) = run_batches(&db, &seq_scan_plan(&info, Some(cmp(0, ComparisonType::NotEqual, 1))), 20);
    assert_eq!(values, vec![int(3)], "NULL != 1 is NULL, which a filter drops");
}

#[test]
fn s3e_01_batches_are_filled_with_matching_rows_not_with_scanned_rows() {
    let db = new_db();
    let info = table_with_rows(&db, "t", &["a"], &rows_1_to(100));
    // every 10th row matches: 10 rows; with batch size 4: 4 + 4 + 2
    let plan = seq_scan_plan(&info, Some(cmp(0, ComparisonType::GreaterThanOrEqual, 91)));
    let (sizes, _) = run_batches(&db, &plan, 4);
    assert_eq!(sizes, vec![4, 4, 2], "batches are filled with matching rows not with scanned rows");
}

#[test]
fn s3e_01_deleted_rows_that_match_are_still_skipped() {
    let db = new_db();
    let info = table_with_rows(&db, "t", &["a"], &rows_1_to(6));
    let victim = info.table.make_iterator().nth(4).unwrap().1.get_rid();
    info.table.update_tuple_meta(&TupleMeta { ts: 0, is_deleted: true }, victim).unwrap();
    let (_, values) = run_batches(&db, &seq_scan_plan(&info, Some(cmp(0, ComparisonType::GreaterThan, 3))), 20);
    assert_eq!(values, vec![int(4), int(6)], "deleted rows that match are still skipped");
}

#[test]
fn s3e_01_the_optimizer_moves_a_where_into_the_scan() {
    let db = new_db();
    table_with_rows(&db, "t", &["a", "b"], &[vec![1, 10], vec![2, 20], vec![3, 30], vec![4, 40]]);
    assert_eq!(sql(&db, "select * from t where a > 2"), vec!["3 30", "4 40"], "the optimizer moves a where into the scan");
    assert_eq!(sql(&db, "select b from t where a >= 2 and b < 40"), vec!["20", "30"], "the optimizer moves a where into the scan");
    let plan = sql(&db, "explain (o) select * from t where a > 2").join("\n");
    assert!(plan.contains("SeqScan { table=t, filter=(#0.0>2) }"), "{plan}");
}

#[test]
fn s3e_01_a_scan_in_a_scan_each_with_its_own_predicate() {
    let db = new_db();
    table_with_rows(&db, "t", &["a"], &rows_1_to(5));
    assert_eq!(sql(&db, "select * from (select a from t where a > 1) where a < 5"), vec!["2", "3", "4"], "a scan in a scan each with its own predicate");
    assert!(sql_err(&db, "select * from (select a + 1 from t where a > 3) where a > 0"), "an unnamed column cannot be referred to");
}

// ---- 3e-02 · insert ---------------------------------------------------------------------------------------------------------------

#[test]
fn s3e_02_insert_values_returns_how_many() {
    let db = new_db();
    sql(&db, "create table t(a int, b varchar(20))");
    assert_eq!(sql(&db, "insert into t values (1, 'x'), (2, 'yy'), (3, 'zzz')"), vec!["3"], "insert values returns how many");
    assert_eq!(sql(&db, "select * from t"), vec!["1 x", "2 yy", "3 zzz"], "insert values returns how many");
    assert_eq!(sql(&db, "insert into t values (4, 'w')"), vec!["1"], "insert values returns how many");
    assert_eq!(sql(&db, "select a from t").len(), 4, "insert values returns how many");
}

#[test]
fn s3e_02_insert_select_copies_a_query() {
    let db = new_db();
    table_with_rows(&db, "src", &["a"], &rows_1_to(30));
    sql(&db, "create table dst(a int)");
    assert_eq!(sql(&db, "insert into dst select * from src where a > 10"), vec!["20"], "insert select copies a query");
    assert_eq!(sql(&db, "select * from dst").len(), 20, "insert select copies a query");
    assert_eq!(sql(&db, "insert into dst select * from src where a < 0"), vec!["0"], "inserting nothing still answers with a count");
}

#[test]
fn s3e_02_the_count_is_produced_once() {
    let db = new_db();
    let info = table_with_rows(&db, "t", &["a"], &[]);
    let values_plan = PlanNode::new(
        Arc::new(ints(&["v.0"])),
        vec![],
        PlanKind::Values { values: vec![vec![Arc::new(ConstantValueExpression::new(int(7))) as ExprRef], vec![Arc::new(ConstantValueExpression::new(int(8))) as ExprRef]] },
    );
    let insert = PlanNode::new(Arc::new(ints(&["rows"])), vec![values_plan], PlanKind::Insert { table_oid: info.oid });
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let mut exec = create_executor(&ctx, &insert).unwrap();
    exec.init().unwrap();
    let (mut tuples, mut rids) = (vec![], vec![]);
    assert!(exec.next(&mut tuples, &mut rids, 20).unwrap(), "the count is produced once: expected `exec.next(&mut tuples, &mut rids, 20).unwrap()`");
    assert_eq!(tuples.len(), 1, "the count is produced once");
    assert_eq!(tuples[0].get_value(exec.output_schema(), 0), int(2), "the count is produced once");
    assert!(!exec.next(&mut tuples, &mut rids, 20).unwrap(), "the second call has nothing more to say");
    assert!(tuples.is_empty(), "the count is produced once: expected `tuples.is_empty()`");
    assert_eq!(info.table.make_iterator().count(), 2, "and nothing was inserted twice");
}

#[test]
fn s3e_02_more_rows_than_fit_in_a_page_or_a_batch() {
    let db = new_db();
    sql(&db, "create table t(a int, b varchar(100))");
    let values: Vec<String> = (0..2500).map(|i| format!("({i}, '{}')", "x".repeat(40))).collect();
    assert_eq!(sql(&db, &format!("insert into t values {}", values.join(", "))), vec!["2500"], "more rows than fit in a page or a batch");
    let rows = sql(&db, "select a from t");
    assert_eq!(rows.len(), 2500, "more rows than fit in a page or a batch");
    assert_eq!(rows[0], "0", "more rows than fit in a page or a batch");
    assert_eq!(rows[2499], "2499", "more rows than fit in a page or a batch");
}

#[test]
fn s3e_02_a_second_init_inserts_again_and_the_tuples_are_stored_as_given() {
    let db = new_db();
    sql(&db, "create table t(a int, b varchar(20), c int)");
    sql(&db, "insert into t values (1, '🥰', 10), (2, '🥰🥰', 20)");
    assert_eq!(sql(&db, "select * from t"), vec!["1 🥰 10", "2 🥰🥰 20"], "a second init inserts again and the tuples are stored as given");
    sql(&db, "insert into t select * from t");
    assert_eq!(sql(&db, "select * from t").len(), 4, "a table can be inserted into from itself without looping");
}

#[test]
fn s3e_02_a_value_of_the_wrong_type_is_a_planning_error() {
    let db = new_db();
    sql(&db, "create table t(a int, b varchar(20))");
    assert!(sql_err(&db, "insert into t values ('x', 1)"), "a value of the wrong type is a planning error: expected `sql_err(&db, \"insert into t values ('x', 1)\")`");
    assert!(sql_err(&db, "insert into t values (1)"), "a value of the wrong type is a planning error: expected `sql_err(&db, \"insert into t values (1)\")`");
    assert!(sql_err(&db, "insert into nosuchtable values (1)"), "a value of the wrong type is a planning error: expected `sql_err(&db, \"insert into nosuchtable values (1)\")`");
}

// ---- 3e-02 · insert and indexes ------------------------------------------------------------------------------------------------

fn lookup(info: &bustub::catalog::catalog::IndexInfo<'_>, key: &[i32]) -> Vec<Rid> {
    let values: Vec<Value> = key.iter().map(|v| int(*v)).collect();
    info.index.scan_key(&Tuple::new(&values, &info.key_schema))
}

#[test]
fn s3e_02_an_insert_adds_the_rows_to_the_indexes_of_the_table() {
    let db = new_db();
    sql(&db, "create table t(a int, b int)");
    sql(&db, "create index t_a on t(a)");
    sql(&db, "insert into t values (5, 50), (3, 30), (9, 90)");
    let catalog = db.catalog.read().unwrap();
    let table = catalog.get_table("t").unwrap();
    let index = catalog.get_index("t_a", "t").unwrap();
    for (a, b) in [(5, 50), (3, 30), (9, 90)] {
        let rids = lookup(&index, &[a]);
        assert_eq!(rids.len(), 1, "key {a}");
        assert_eq!(table.table.get_tuple(rids[0]).unwrap().1.get_value(&table.schema, 1), int(b), "the index leads to the row");
    }
    assert!(lookup(&index, &[4]).is_empty(), "an insert adds the rows to the indexes of the table: expected `lookup(&index, &[4]).is_empty()`");
    assert_eq!(index.index.scan_all().len(), 3, "an insert adds the rows to the indexes of the table");
}

#[test]
fn s3e_02_every_index_of_the_table_is_updated() {
    let db = new_db();
    sql(&db, "create table t(a int, b int, c int)");
    sql(&db, "create index ia on t(a)");
    sql(&db, "create index ib on t(b)");
    sql(&db, "create index iab on t(a, b)");
    sql(&db, "insert into t values (1, 2, 3), (4, 5, 6)");
    let catalog = db.catalog.read().unwrap();
    assert_eq!(lookup(&catalog.get_index("ia", "t").unwrap(), &[4]).len(), 1, "every index of the table is updated");
    assert_eq!(lookup(&catalog.get_index("ib", "t").unwrap(), &[2]).len(), 1, "every index of the table is updated");
    assert_eq!(lookup(&catalog.get_index("iab", "t").unwrap(), &[1, 2]).len(), 1, "every index of the table is updated");
    assert!(lookup(&catalog.get_index("iab", "t").unwrap(), &[2, 1]).is_empty(), "every index of the table is updated: expected `lookup(&catalog.get_index(\"iab\", \"t\").unwrap(), &[2, 1]).is_empty()`");
}

#[test]
fn s3e_02_the_primary_key_index_is_an_index_too() {
    let db = new_db();
    sql(&db, "create table t(id int primary key, v int)");
    sql(&db, "insert into t values (10, 1), (20, 2)");
    let catalog = db.catalog.read().unwrap();
    let pk = catalog.get_index("t_pk", "t").unwrap();
    assert_eq!(lookup(&pk, &[20]).len(), 1, "the primary key index is an index too");
    assert_eq!(pk.index.scan_all().len(), 2, "the primary key index is an index too");
}

#[test]
fn s3e_02_a_key_that_is_already_in_the_index_keeps_the_first_row() {
    let db = new_db();
    sql(&db, "create table t(a int, b int)");
    sql(&db, "create index ia on t(a)");
    sql(&db, "insert into t values (1, 100)");
    sql(&db, "insert into t values (1, 200)");
    assert_eq!(sql(&db, "select * from t").len(), 2, "both rows are in the table");
    let catalog = db.catalog.read().unwrap();
    let table = catalog.get_table("t").unwrap();
    let rids = lookup(&catalog.get_index("ia", "t").unwrap(), &[1]);
    assert_eq!(rids.len(), 1, "a key that is already in the index keeps the first row");
    assert_eq!(table.table.get_tuple(rids[0]).unwrap().1.get_value(&table.schema, 1), int(100), "the index remembers the first");
}

#[test]
fn s3e_02_an_index_created_after_the_insert_has_the_rows_and_later_inserts_join_them() {
    let db = new_db();
    sql(&db, "create table t(a int)");
    sql(&db, "insert into t values (1), (2), (3)");
    sql(&db, "create index ia on t(a)");
    sql(&db, "insert into t values (4), (5)");
    let catalog = db.catalog.read().unwrap();
    assert_eq!(catalog.get_index("ia", "t").unwrap().index.scan_all().len(), 5, "an index created after the insert has the rows and later inserts join them");
}

#[test]
fn s3e_02_other_tables_indexes_are_left_alone() {
    let db = new_db();
    sql(&db, "create table t(a int)");
    sql(&db, "create table u(a int)");
    sql(&db, "create index iu on u(a)");
    sql(&db, "insert into t values (1), (2)");
    let catalog = db.catalog.read().unwrap();
    assert!(catalog.get_index("iu", "u").unwrap().index.scan_all().is_empty(), "other tables indexes are left alone: expected `catalog.get_index(\"iu\", \"u\").unwrap().index.scan_all().is_empty()`");
}

// ---- 3e-03 · delete ---------------------------------------------------------------------------------------------------------------

#[test]
fn s3e_03_delete_returns_how_many_rows_and_they_disappear() {
    let db = new_db();
    table_with_rows(&db, "t", &["a", "b"], &[vec![1, 10], vec![2, 20], vec![3, 30], vec![4, 40]]);
    assert_eq!(sql(&db, "delete from t where a >= 3"), vec!["2"], "delete returns how many rows and they disappear");
    assert_eq!(sql(&db, "select * from t"), vec!["1 10", "2 20"], "delete returns how many rows and they disappear");
    assert_eq!(sql(&db, "delete from t"), vec!["2"], "delete returns how many rows and they disappear");
    assert!(sql(&db, "select * from t").is_empty(), "delete returns how many rows and they disappear: expected `sql(&db, \"select * from t\").is_empty()`");
    assert_eq!(sql(&db, "delete from t"), vec!["0"], "delete returns how many rows and they disappear");
}

#[test]
fn s3e_03_deleting_nothing_returns_zero_and_changes_nothing() {
    let db = new_db();
    table_with_rows(&db, "t", &["a"], &rows_1_to(5));
    assert_eq!(sql(&db, "delete from t where a > 100"), vec!["0"], "deleting nothing returns zero and changes nothing");
    assert_eq!(sql(&db, "delete from t where a != a"), vec!["0"], "deleting nothing returns zero and changes nothing");
    assert_eq!(sql(&db, "select * from t").len(), 5, "deleting nothing returns zero and changes nothing");
}

#[test]
fn s3e_03_a_deleted_tuple_is_marked_not_erased() {
    let db = new_db();
    let info = table_with_rows(&db, "t", &["a"], &rows_1_to(3));
    sql(&db, "delete from t where a = 2");
    let all: Vec<_> = info.table.make_iterator().collect();
    assert_eq!(all.len(), 3, "the slot is still there");
    assert_eq!(all.iter().map(|(m, _)| m.is_deleted).collect::<Vec<_>>(), vec![false, true, false], "a deleted tuple is marked not erased");
}

#[test]
fn s3e_03_delete_removes_the_index_entries() {
    let db = new_db();
    sql(&db, "create table t(a int, b int)");
    sql(&db, "create index ia on t(a)");
    sql(&db, "create index ib on t(b)");
    sql(&db, "insert into t values (1, 10), (2, 20), (3, 30)");
    assert_eq!(sql(&db, "delete from t where a = 2"), vec!["1"], "delete removes the index entries");
    let catalog = db.catalog.read().unwrap();
    assert!(lookup(&catalog.get_index("ia", "t").unwrap(), &[2]).is_empty(), "delete removes the index entries: expected `lookup(&catalog.get_index(\"ia\", \"t\").unwrap(), &[2]).is_empty()`");
    assert!(lookup(&catalog.get_index("ib", "t").unwrap(), &[20]).is_empty(), "delete removes the index entries: expected `lookup(&catalog.get_index(\"ib\", \"t\").unwrap(), &[20]).is_empty()`");
    assert_eq!(lookup(&catalog.get_index("ia", "t").unwrap(), &[3]).len(), 1, "delete removes the index entries");
}

#[test]
fn s3e_03_delete_everything_in_a_big_table() {
    let db = new_db();
    table_with_rows(&db, "t", &["a"], &rows_1_to(3000));
    assert_eq!(sql(&db, "delete from t"), vec!["3000"], "delete everything in a big table");
    assert!(sql(&db, "select * from t").is_empty(), "delete everything in a big table: expected `sql(&db, \"select * from t\").is_empty()`");
}

#[test]
fn s3e_03_a_key_can_be_inserted_again_after_it_was_deleted() {
    let db = new_db();
    sql(&db, "create table t(a int, b int)");
    sql(&db, "create index ia on t(a)");
    sql(&db, "insert into t values (7, 1)");
    sql(&db, "delete from t");
    sql(&db, "insert into t values (7, 2)");
    assert_eq!(sql(&db, "select * from t"), vec!["7 2"], "a key can be inserted again after it was deleted");
    let catalog = db.catalog.read().unwrap();
    let table = catalog.get_table("t").unwrap();
    let rids = lookup(&catalog.get_index("ia", "t").unwrap(), &[7]);
    assert_eq!(rids.len(), 1, "a key can be inserted again after it was deleted");
    assert_eq!(table.table.get_tuple(rids[0]).unwrap().1.get_value(&table.schema, 1), int(2), "a key can be inserted again after it was deleted");
}

// ---- 3e-03 · update ---------------------------------------------------------------------------------------------------------------

#[test]
fn s3e_03_update_returns_how_many_rows_and_changes_them() {
    let db = new_db();
    sql(&db, "create table t(a int, b varchar(20), c int)");
    sql(&db, "insert into t values (0, 'a', 10), (1, 'b', 11), (2, 'c', 12), (3, 'd', 13), (4, 'e', 14)");
    assert_eq!(sql(&db, "update t set c = 445 where a >= 3"), vec!["2"], "update returns how many rows and changes them");
    assert_eq!(sql(&db, "select * from t where a >= 3"), vec!["3 d 445", "4 e 445"], "update returns how many rows and changes them");
    assert_eq!(sql(&db, "select * from t where a < 3").len(), 3, "update returns how many rows and changes them");
    assert_eq!(sql(&db, "update t set c = 1 where a >= 5"), vec!["0"], "update returns how many rows and changes them");
}

#[test]
fn s3e_03_the_new_values_can_use_the_old_ones() {
    let db = new_db();
    table_with_rows(&db, "t", &["a", "b"], &[vec![1, 10], vec![2, 20], vec![3, 30]]);
    assert_eq!(sql(&db, "update t set b = b + a"), vec!["3"], "the new values can use the old ones");
    let mut rows = sql(&db, "select * from t");
    rows.sort();
    assert_eq!(rows, vec!["1 11", "2 22", "3 33"], "the new values can use the old ones");
    assert_eq!(sql(&db, "update t set a = b, b = a"), vec!["3"], "every expression sees the OLD row");
    let mut rows = sql(&db, "select * from t");
    rows.sort();
    assert_eq!(rows, vec!["11 1", "22 2", "33 3"], "the new values can use the old ones");
}

#[test]
fn s3e_03_every_row_is_updated_exactly_once() {
    let db = new_db();
    table_with_rows(&db, "t", &["a"], &rows_1_to(3000));
    assert_eq!(sql(&db, "update t set a = a + 1"), vec!["3000"], "every row is updated exactly once");
    let mut rows: Vec<i32> = sql(&db, "select a from t").iter().map(|l| l.parse().unwrap()).collect();
    rows.sort();
    assert_eq!(rows, (2..=3001).collect::<Vec<_>>(), "no row was updated twice, though the new rows are stored at the end of the table");
}

#[test]
fn s3e_03_a_string_can_change_length() {
    let db = new_db();
    sql(&db, "create table t(id int, s varchar(50))");
    sql(&db, "insert into t values (1, 'short'), (2, 'also short')");
    assert_eq!(sql(&db, "update t set s = 'a much longer string than before' where id = 1"), vec!["1"], "a string can change length");
    let mut rows = sql(&db, "select * from t");
    rows.sort();
    assert_eq!(rows, vec!["1 a much longer string than before", "2 also short"], "a string can change length");
}

#[test]
fn s3e_03_the_indexes_follow_an_update() {
    let db = new_db();
    sql(&db, "create table t(a int, b int)");
    sql(&db, "create index ia on t(a)");
    sql(&db, "insert into t values (1, 10), (2, 20), (3, 30)");
    assert_eq!(sql(&db, "update t set a = 8, b = -20 where a = 2"), vec!["1"], "the indexes follow an update");
    let catalog = db.catalog.read().unwrap();
    let table = catalog.get_table("t").unwrap();
    let ia = catalog.get_index("ia", "t").unwrap();
    assert!(lookup(&ia, &[2]).is_empty(), "the old key is gone");
    let rids = lookup(&ia, &[8]);
    assert_eq!(rids.len(), 1, "the new key is there");
    assert_eq!(table.table.get_tuple(rids[0]).unwrap().1.get_value(&table.schema, 1), int(-20), "the indexes follow an update");
    assert_eq!(ia.index.scan_all().len(), 3, "the indexes follow an update");
}

#[test]
fn s3e_03_updating_a_column_that_is_not_in_the_key_keeps_the_key() {
    let db = new_db();
    sql(&db, "create table t(a int, b int)");
    sql(&db, "create index ia on t(a)");
    sql(&db, "insert into t values (1, 10)");
    sql(&db, "update t set b = 99");
    let catalog = db.catalog.read().unwrap();
    let table = catalog.get_table("t").unwrap();
    let rids = lookup(&catalog.get_index("ia", "t").unwrap(), &[1]);
    assert_eq!(rids.len(), 1, "updating a column that is not in the key keeps the key");
    assert_eq!(table.table.get_tuple(rids[0]).unwrap().1.get_value(&table.schema, 1), int(99), "the index entry leads to the NEW tuple");
}

// ---- 3e-04 · index scan: every row in key order ---------------------------------------------------------------------------

fn index_scan_plan(info: &TableInfo<'_>, index_oid: u32, filter: Option<ExprRef>, keys: Vec<ExprRef>) -> PlanRef {
    let schema = Schema::new(info.schema.columns().iter().map(|c| c.with_column_name(&format!("{}.{}", info.name, c.name()))).collect());
    PlanNode::new(Arc::new(schema), vec![], PlanKind::IndexScan { table_oid: info.oid, index_oid, filter_predicate: filter, pred_keys: keys })
}

fn db_with_index(rows: &[Vec<i32>]) -> (BusTubInstance, u32, u32) {
    let db = new_db();
    sql(&db, "create table t(a int, b int)");
    sql(&db, "create index ia on t(a)");
    if !rows.is_empty() {
        let values: Vec<String> = rows.iter().map(|r| format!("({}, {})", r[0], r[1])).collect();
        sql(&db, &format!("insert into t values {}", values.join(", ")));
    }
    let (table_oid, index_oid) = {
        let c = db.catalog.read().unwrap();
        (c.get_table("t").unwrap().oid, c.get_index("ia", "t").unwrap().index_oid)
    };
    (db, table_oid, index_oid)
}

fn first_column(tuples: &[Tuple], schema: &Schema) -> Vec<i32> {
    tuples.iter().map(|t| t.get_value(schema, 0).as_i64().unwrap() as i32).collect()
}

#[test]
fn s3e_04_rows_come_back_in_key_order_not_storage_order() {
    let (db, table_oid, index_oid) = db_with_index(&[vec![5, 50], vec![1, 10], vec![4, 40], vec![2, 20], vec![3, 30]]);
    let info = db.catalog.read().unwrap().get_table_by_oid(table_oid).unwrap();
    let plan = index_scan_plan(&info, index_oid, None, vec![]);
    let (_, values) = run_batches(&db, &plan, 20);
    assert_eq!(values, vec![int(1), int(2), int(3), int(4), int(5)], "rows come back in key order not storage order");
    assert_eq!(first_column(&execute(&db, &plan), &info.schema), vec![1, 2, 3, 4, 5], "rows come back in key order not storage order");
}

#[test]
fn s3e_04_negative_keys_sort_as_numbers() {
    let (db, table_oid, index_oid) = db_with_index(&[vec![3, 0], vec![-7, 0], vec![0, 0], vec![-1, 0], vec![256, 0], vec![1, 0]]);
    let info = db.catalog.read().unwrap().get_table_by_oid(table_oid).unwrap();
    let rows = execute(&db, &index_scan_plan(&info, index_oid, None, vec![]));
    assert_eq!(first_column(&rows, &info.schema), vec![-7, -1, 0, 1, 3, 256], "negative keys sort as numbers");
}

#[test]
fn s3e_04_batches_have_at_most_batch_size_tuples() {
    let rows: Vec<Vec<i32>> = (0..45).rev().map(|i| vec![i, i]).collect();
    let (db, table_oid, index_oid) = db_with_index(&rows);
    let info = db.catalog.read().unwrap().get_table_by_oid(table_oid).unwrap();
    let (sizes, values) = run_batches(&db, &index_scan_plan(&info, index_oid, None, vec![]), 20);
    assert_eq!(sizes, vec![20, 20, 5], "batches have at most batch size tuples");
    assert_eq!(values[0], int(0), "batches have at most batch size tuples");
    assert_eq!(values[44], int(44), "batches have at most batch size tuples");
}

#[test]
fn s3e_04_an_empty_table_gives_nothing() {
    let (db, table_oid, index_oid) = db_with_index(&[]);
    let info = db.catalog.read().unwrap().get_table_by_oid(table_oid).unwrap();
    assert!(execute(&db, &index_scan_plan(&info, index_oid, None, vec![])).is_empty(), "an empty table gives nothing: expected `execute(&db, &index_scan_plan(&info, index_oid, None, vec![])).is_empty()`");
}

#[test]
fn s3e_04_deleted_rows_do_not_come_back() {
    let (db, table_oid, index_oid) = db_with_index(&[vec![1, 1], vec![2, 2], vec![3, 3]]);
    let info = db.catalog.read().unwrap().get_table_by_oid(table_oid).unwrap();
    // mark a row deleted behind the index's back, as a row deleted by a concurrent transaction would look
    let victim = info.table.make_iterator().nth(1).unwrap().1.get_rid();
    info.table.update_tuple_meta(&TupleMeta { ts: 0, is_deleted: true }, victim).unwrap();
    let rows = execute(&db, &index_scan_plan(&info, index_oid, None, vec![]));
    assert_eq!(first_column(&rows, &info.schema), vec![1, 3], "deleted rows do not come back");
}

#[test]
fn s3e_04_order_by_on_an_indexed_column_becomes_an_index_scan() {
    let (db, _, _) = db_with_index(&[vec![3, 30], vec![1, 10], vec![2, 20]]);
    sql(&db, "set force_optimizer_starter_rule=yes");
    let plan = sql(&db, "explain (o) select * from t order by a").join("\n");
    assert!(plan.contains("IndexScan"), "{plan}");
    assert_eq!(sql(&db, "select * from t order by a"), vec!["1 10", "2 20", "3 30"], "order by on an indexed column becomes an index scan");
    let no_index = sql(&db, "explain (o) select * from t order by b").join("\n");
    assert!(!no_index.contains("IndexScan"), "no index on b: the sort stays a sort\n{no_index}");
    sql(&db, "insert into t values (0, 0)");
    assert_eq!(sql(&db, "select * from t order by a"), vec!["0 0", "1 10", "2 20", "3 30"], "an inserted row is in the index");
}

// ---- 3e-04 · index scan: point lookups and predicates -------------------------------------------------------------------------

fn key(v: i32) -> ExprRef {
    Arc::new(ConstantValueExpression::new(int(v)))
}

#[test]
fn s3e_04_a_key_finds_its_row() {
    let (db, table_oid, index_oid) = db_with_index(&[vec![1, 10], vec![2, 20], vec![3, 30]]);
    let info = db.catalog.read().unwrap().get_table_by_oid(table_oid).unwrap();
    let rows = execute(&db, &index_scan_plan(&info, index_oid, None, vec![key(2)]));
    assert_eq!(rows.len(), 1, "a key finds its row");
    assert_eq!(rows[0].get_value(&info.schema, 1), int(20), "a key finds its row");
    assert!(execute(&db, &index_scan_plan(&info, index_oid, None, vec![key(9)])).is_empty(), "a missing key finds nothing");
}

#[test]
fn s3e_04_several_keys_are_looked_up_in_the_order_given() {
    let (db, table_oid, index_oid) = db_with_index(&[vec![1, 10], vec![2, 20], vec![3, 30], vec![4, 40]]);
    let info = db.catalog.read().unwrap().get_table_by_oid(table_oid).unwrap();
    let rows = execute(&db, &index_scan_plan(&info, index_oid, None, vec![key(4), key(1), key(9), key(3)]));
    assert_eq!(first_column(&rows, &info.schema), vec![4, 1, 3], "key order is the order of the keys, not of the index");
}

#[test]
fn s3e_04_a_deleted_row_is_not_found() {
    let (db, table_oid, index_oid) = db_with_index(&[vec![1, 10], vec![2, 20]]);
    let info = db.catalog.read().unwrap().get_table_by_oid(table_oid).unwrap();
    sql(&db, "delete from t where a = 2");
    assert!(execute(&db, &index_scan_plan(&info, index_oid, None, vec![key(2)])).is_empty(), "a deleted row is not found: expected `execute(&db, &index_scan_plan(&info, index_oid, None, vec![key(2)])).is_empty()`");
    assert_eq!(execute(&db, &index_scan_plan(&info, index_oid, None, vec![key(1)])).len(), 1, "a deleted row is not found");
}

#[test]
fn s3e_04_the_filter_predicate_applies_to_what_the_index_finds() {
    let (db, table_oid, index_oid) = db_with_index(&[vec![1, 10], vec![2, 20], vec![3, 30], vec![4, 40]]);
    let info = db.catalog.read().unwrap().get_table_by_oid(table_oid).unwrap();
    let b_gt_25 = cmp(1, ComparisonType::GreaterThan, 25);
    let rows = execute(&db, &index_scan_plan(&info, index_oid, Some(b_gt_25.clone()), vec![key(2), key(3)]));
    assert_eq!(first_column(&rows, &info.schema), vec![3], "key 2 is found but its b is 20");
    let rows = execute(&db, &index_scan_plan(&info, index_oid, Some(b_gt_25), vec![]));
    assert_eq!(first_column(&rows, &info.schema), vec![3, 4], "a filter on a full ordered scan keeps the order");
}

#[test]
fn s3e_04_a_lookup_sees_an_update_made_in_the_same_session() {
    let (db, table_oid, index_oid) = db_with_index(&[vec![1, 10], vec![2, 20]]);
    let info = db.catalog.read().unwrap().get_table_by_oid(table_oid).unwrap();
    sql(&db, "update t set b = 21 where a = 2");
    let rows = execute(&db, &index_scan_plan(&info, index_oid, None, vec![key(2)]));
    assert_eq!(rows.len(), 1, "a lookup sees an update made in the same session");
    assert_eq!(rows[0].get_value(&info.schema, 1), int(21), "a lookup sees an update made in the same session");
}

#[test]
fn s3e_04_a_batch_of_lookups_larger_than_the_batch_size() {
    let rows: Vec<Vec<i32>> = (0..100).map(|i| vec![i, i * 2]).collect();
    let (db, table_oid, index_oid) = db_with_index(&rows);
    let info = db.catalog.read().unwrap().get_table_by_oid(table_oid).unwrap();
    let keys: Vec<ExprRef> = (0..50).map(|i| key(i * 2)).collect();
    let (sizes, values) = run_batches(&db, &index_scan_plan(&info, index_oid, None, keys), 20);
    assert_eq!(sizes, vec![20, 20, 10], "a batch of lookups larger than the batch size");
    assert_eq!(values[49], int(98), "a batch of lookups larger than the batch size");
}

// ---- properties: the executors against plain Rust vectors ------------------------------------------------------------------------

fn pconfig() -> ProptestConfig {
    ProptestConfig { cases: 40, max_shrink_iters: 1000, ..ProptestConfig::default() }
}

fn cell_value(c: Option<i64>) -> Value {
    c.map_or_else(|| Value::null(TypeId::Integer), |v| int(v as i32))
}

/// Stores `rows` of `t(a, b, c)` straight into the heap (no executors involved).
fn heap_with_cells(db: &BusTubInstance, rows: &[Row]) {
    let info = db.catalog.write().unwrap().create_table("t", &ints(&["a", "b", "c"])).unwrap();
    for r in rows {
        let values: Vec<Value> = r.iter().map(|c| cell_value(*c)).collect();
        info.table.insert_tuple(&TupleMeta { ts: 0, is_deleted: false }, &Tuple::new(&values, &info.schema)).unwrap();
    }
}

fn rows_of(db: &BusTubInstance) -> Vec<String> {
    let mut v = sql(db, "select * from t");
    v.sort();
    v
}

fn row_strategy() -> impl Strategy<Value = Row> {
    prop::collection::vec(model::cell(), 3)
}

/// The rows of a table with a distinct `a` (the indexed column), a random `b` and `c`.
fn keyed_rows(max: usize) -> impl Strategy<Value = Vec<Row>> {
    prop::collection::vec((model::cell(), model::cell()), 0..max).prop_map(|bc| bc.into_iter().enumerate().map(|(i, (b, c))| vec![Some(i as i64), b, c]).collect())
}

proptest! {
    #![proptest_config(pconfig())]

    /// `select * from t where p` returns, in storage order, exactly the rows for which `p` is TRUE: rows where it is FALSE or unknown
    /// (a NULL somewhere) are not returned.
    #[test]
    fn s3e_01_a_scan_with_a_predicate_returns_exactly_the_rows_it_keeps(rows in prop::collection::vec(row_strategy(), 0..60), pred in model::predicate(&model::COLUMNS)) {
        let db = new_db();
        heap_with_cells(&db, &rows);
        let want: Vec<String> = rows.iter().filter(|r| model::keeps(&pred, r)).map(model::line).collect();
        prop_assert_eq!(sql(&db, &format!("select * from t where {}", model::show(&pred))), want, "where {}", model::show(&pred));
        prop_assert_eq!(sql(&db, "select * from t"), rows.iter().map(model::line).collect::<Vec<_>>());
    }

    /// The batch size changes how many tuples come back per call, never which tuples: one big batch, one tuple at a time and anything
    /// between give the same rows in the same order.
    #[test]
    fn s3e_01_the_batch_size_does_not_change_the_rows(n in 0i32..300, batch in 1usize..40, limit in 0i32..300) {
        let db = new_db();
        let info = table_with_rows(&db, "t", &["a"], &rows_1_to(n));
        let plan = seq_scan_plan(&info, Some(cmp(0, ComparisonType::LessThanOrEqual, limit)));
        let (sizes, values) = run_batches(&db, &plan, batch);
        let want: Vec<Value> = (1..=n.min(limit)).map(int).collect();
        prop_assert_eq!(values, want);
        prop_assert!(sizes.iter().all(|s| *s >= 1 && *s <= batch), "batches have between 1 and {} tuples: {:?}", batch, sizes);
    }

    /// Inserts answer with how many rows they added, and the table (and, if there is one, the index) then holds exactly the rows
    /// inserted so far.
    #[test]
    fn s3e_02_inserts_add_exactly_their_rows_to_the_table_and_the_index(batches in prop::collection::vec(keyed_rows(6), 1..8), index_first in any::<bool>()) {
        let db = new_db();
        sql(&db, "create table t(a int, b int, c int)");
        if index_first { sql(&db, "create index ia on t(a)"); }
        let mut model_rows: Vec<Row> = vec![];
        for mut batch in batches {
            let base = model_rows.len() as i64;
            for r in batch.iter_mut() { r[0] = r[0].map(|a| a + base); }
            if batch.is_empty() { continue; }
            let statement = format!("insert into t values {}", batch.iter().map(model::values).collect::<Vec<_>>().join(", "));
            prop_assert_eq!(sql(&db, &statement), vec![batch.len().to_string()]);
            model_rows.extend(batch);
            prop_assert_eq!(rows_of(&db), model::sorted_lines(&model_rows));
        }
        if !index_first { sql(&db, "create index ia on t(a)"); }
        let catalog = db.catalog.read().unwrap();
        let table = catalog.get_table("t").unwrap();
        let index = catalog.get_index("ia", "t").unwrap();
        let mut keys: Vec<i32> = index.index.scan_all().iter().map(|rid| table.table.get_tuple(*rid).unwrap().1.get_value(&table.schema, 0).as_i64().unwrap() as i32).collect();
        let mut want: Vec<i32> = model_rows.iter().map(|r| r[0].unwrap() as i32).collect();
        keys.sort();
        want.sort();
        prop_assert_eq!(keys, want, "the index holds one entry for every row");
    }
}

/// A statement that changes the table.
#[derive(Clone, Debug)]
enum Change {
    Delete(bustub::sql::ast::Expr),
    SetB(bustub::sql::ast::Expr, bustub::sql::ast::Expr),
    SetC(bustub::sql::ast::Expr, bustub::sql::ast::Expr),
    ShiftA(bustub::sql::ast::Expr),
}

fn change_strategy() -> impl Strategy<Value = Change> {
    let any_column = model::predicate(&model::COLUMNS).boxed();
    prop_oneof![
        2 => any_column.clone().prop_map(Change::Delete),
        2 => (model::arith(&model::COLUMNS, 2), any_column.clone()).prop_map(|(e, p)| Change::SetB(e, p)),
        1 => (model::arith(&model::COLUMNS, 1), any_column.clone()).prop_map(|(e, p)| Change::SetC(e, p)),
        1 => any_column.prop_map(Change::ShiftA),
    ]
}

/// Applies `change` to the model and returns how many rows it touched.
fn apply(change: &Change, rows: &mut Vec<Row>) -> usize {
    match change {
        Change::Delete(p) => {
            let before = rows.len();
            rows.retain(|r| !model::keeps(p, r));
            before - rows.len()
        }
        Change::SetB(e, p) | Change::SetC(e, p) => {
            let target = if matches!(change, Change::SetB(..)) { 1 } else { 2 };
            let mut n = 0;
            for r in rows.iter_mut() {
                if model::keeps(p, r) {
                    r[target] = model::as_int(model::eval(e, r));
                    n += 1;
                }
            }
            n
        }
        Change::ShiftA(p) => {
            let mut n = 0;
            for r in rows.iter_mut() {
                if model::keeps(p, r) {
                    r[0] = r[0].map(|a| a + 1000);
                    n += 1;
                }
            }
            n
        }
    }
}

fn statement(change: &Change) -> String {
    match change {
        Change::Delete(p) => format!("delete from t where {}", model::show(p)),
        Change::SetB(e, p) => format!("update t set b = {} where {}", model::show(e), model::show(p)),
        Change::SetC(e, p) => format!("update t set c = {} where {}", model::show(e), model::show(p)),
        Change::ShiftA(p) => format!("update t set a = a + 1000 where {}", model::show(p)),
    }
}

/// Every live row has exactly one entry in the index of `a`, and every entry leads to a live row with that key.
fn check_index(db: &BusTubInstance, rows: &[Row]) -> Result<(), TestCaseError> {
    let catalog = db.catalog.read().unwrap();
    let table = catalog.get_table("t").unwrap();
    let index = catalog.get_index("ia", "t").unwrap();
    let mut found: Vec<(i32, String)> = vec![];
    for rid in index.index.scan_all() {
        let (meta, tuple) = table.table.get_tuple(rid).unwrap();
        prop_assert!(!meta.is_deleted, "an index entry leads to a deleted row");
        let row: Row = (0..3).map(|i| tuple.get_value(&table.schema, i).as_i64()).collect();
        found.push((row[0].unwrap() as i32, model::line(&row)));
    }
    let mut want: Vec<(i32, String)> = rows.iter().map(|r| (r[0].unwrap() as i32, model::line(r))).collect();
    found.sort();
    want.sort();
    prop_assert_eq!(found, want, "the index and the table disagree");
    Ok(())
}

proptest! {
    #![proptest_config(pconfig())]

    /// Deletes and updates answer with how many rows they changed, change exactly those rows (computing every new value from the OLD
    /// row), and keep the index of `a` in step with the table, including when `a` itself changes.
    #[test]
    fn s3e_03_deletes_and_updates_agree_with_a_vector_of_rows_and_keep_the_index(start in keyed_rows(25), changes in prop::collection::vec(change_strategy(), 1..10)) {
        let db = new_db();
        sql(&db, "create table t(a int, b int, c int)");
        sql(&db, "create index ia on t(a)");
        if !start.is_empty() {
            sql(&db, &format!("insert into t values {}", start.iter().map(model::values).collect::<Vec<_>>().join(", ")));
        }
        let mut rows = start;
        for change in &changes {
            let touched = apply(change, &mut rows);
            prop_assert_eq!(sql(&db, &statement(change)), vec![touched.to_string()], "{}", statement(change));
            prop_assert_eq!(rows_of(&db), model::sorted_lines(&rows), "after {}", statement(change));
            check_index(&db, &rows)?;
        }
    }

    /// An index scan with no keys returns the rows in the order of the key (negative keys first), and with keys returns the rows of
    /// those keys in the order the keys were given; a key that is not there finds nothing; a filter applies to what the index finds.
    #[test]
    fn s3e_04_an_index_scan_is_in_key_order_and_a_point_lookup_finds_its_rows(keys in prop::collection::btree_set(-40i32..40, 0..40), order in any::<u64>(), probes in prop::collection::vec(-45i32..45, 0..12), limit in -40i32..40) {
        let mut keys: Vec<i32> = keys.into_iter().collect();
        // insert in a scrambled order
        let mut x = order | 1;
        let mut tagged: Vec<(u64, i32)> = keys.iter().map(|k| { x = x.wrapping_mul(6364136223846793005).wrapping_add(1442695040888963407); (x >> 33, *k) }).collect();
        tagged.sort();
        keys = tagged.into_iter().map(|t| t.1).collect();
        let rows: Vec<Vec<i32>> = keys.iter().map(|k| vec![*k, k * 10]).collect();
        let (db, table_oid, index_oid) = db_with_index(&rows);
        let info = db.catalog.read().unwrap().get_table_by_oid(table_oid).unwrap();
        let mut sorted = keys.clone();
        sorted.sort();
        let all: Vec<i32> = execute(&db, &index_scan_plan(&info, index_oid, None, vec![])).iter().map(|t| t.get_value(&info.schema, 0).as_i64().unwrap() as i32).collect();
        prop_assert_eq!(&all, &sorted, "an index scan is in key order");
        let filtered: Vec<i32> = execute(&db, &index_scan_plan(&info, index_oid, Some(cmp(0, ComparisonType::GreaterThan, limit)), vec![])).iter().map(|t| t.get_value(&info.schema, 0).as_i64().unwrap() as i32).collect();
        prop_assert_eq!(filtered, sorted.iter().copied().filter(|k| *k > limit).collect::<Vec<_>>(), "the filter applies after the index");
        prop_assume!(!probes.is_empty()); // no keys at all means "scan everything", checked above
        let found: Vec<(i32, i32)> = execute(&db, &index_scan_plan(&info, index_oid, None, probes.iter().map(|k| key(*k)).collect()))
            .iter().map(|t| (t.get_value(&info.schema, 0).as_i64().unwrap() as i32, t.get_value(&info.schema, 1).as_i64().unwrap() as i32)).collect();
        let want: Vec<(i32, i32)> = probes.iter().filter(|k| keys.contains(k)).map(|k| (*k, k * 10)).collect();
        prop_assert_eq!(found, want, "point lookups in the order given; absent keys find nothing");
    }
}

// ---- 3e-05 · boss: whole statements against a model ----------------------------------------------------------------------------

#[derive(Clone, Debug)]
enum Step {
    Insert(Vec<Row>),
    Change(Change),
    Select(bustub::sql::ast::Expr),
    IndexCheck,
}

fn step_strategy() -> impl Strategy<Value = Step> {
    prop_oneof![
        3 => prop::collection::vec((model::cell(), model::cell()), 1..5).prop_map(|bc| Step::Insert(bc.into_iter().map(|(b, c)| vec![Some(0), b, c]).collect())),
        3 => change_strategy().prop_map(Step::Change),
        3 => model::predicate(&model::COLUMNS).prop_map(Step::Select),
        1 => Just(Step::IndexCheck),
    ]
}

proptest! {
    #![proptest_config(ProptestConfig { cases: 32, max_shrink_iters: 1000, ..ProptestConfig::default() })]

    /// A random session of inserts, deletes, updates and selects, with an index created at a random moment, agrees with a vector of
    /// rows after every statement; the index agrees with the table; and once the index exists `order by a` comes back in key order
    /// (through the index scan the optimizer rewrites it to).
    #[test]
    fn s3e_05_a_random_session_agrees_with_a_vector_of_rows(steps in prop::collection::vec(step_strategy(), 1..24), index_at in 0usize..24) {
        let db = new_db();
        sql(&db, "create table t(a int, b int, c int)");
        sql(&db, "set force_optimizer_starter_rule=yes");
        let mut rows: Vec<Row> = vec![];
        let mut next_key = 0i64;
        let mut indexed = false;
        for (i, step) in steps.iter().enumerate() {
            if i == index_at && !indexed {
                sql(&db, "create index ia on t(a)");
                indexed = true;
            }
            match step {
                Step::Insert(new_rows) => {
                    let mut new_rows = new_rows.clone();
                    for r in new_rows.iter_mut() { r[0] = Some(next_key); next_key += 1; }
                    let text = format!("insert into t values {}", new_rows.iter().map(model::values).collect::<Vec<_>>().join(", "));
                    prop_assert_eq!(sql(&db, &text), vec![new_rows.len().to_string()]);
                    rows.extend(new_rows);
                }
                Step::Change(c) => {
                    let touched = apply(c, &mut rows);
                    prop_assert_eq!(sql(&db, &statement(c)), vec![touched.to_string()], "{}", statement(c));
                }
                Step::Select(p) => {
                    let mut got = sql(&db, &format!("select * from t where {}", model::show(p)));
                    got.sort();
                    let kept: Vec<Row> = rows.iter().filter(|r| model::keeps(p, r)).cloned().collect();
                    prop_assert_eq!(got, model::sorted_lines(&kept), "select where {}", model::show(p));
                }
                Step::IndexCheck => {}
            }
            prop_assert_eq!(rows_of(&db), model::sorted_lines(&rows), "after step {}: {:?}", i, step);
            if indexed {
                check_index(&db, &rows)?;
                let mut by_key = rows.clone();
                by_key.sort_by_key(|r| r[0]);
                prop_assert_eq!(sql(&db, "select * from t order by a"), by_key.iter().map(model::line).collect::<Vec<_>>(), "order by a, after step {}", i);
            }
        }
    }
}
