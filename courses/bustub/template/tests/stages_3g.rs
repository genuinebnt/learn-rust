//! Tests for module 3g: sorting, limits, top-N and window functions.

use std::cmp::Ordering;
use std::sync::atomic::{AtomicUsize, Ordering as AtomicOrdering};
use std::sync::Arc;

use bustub::binder::bound_order_by::{OrderBy, OrderByNullType, OrderByType};
use bustub::catalog::column::Column;
use bustub::catalog::schema::Schema;
use bustub::common::bustub_instance::BusTubInstance;
use bustub::common::exception::ExceptionType;
use bustub::common::result_writer::SimpleStreamWriter;
use bustub::common::rid::Rid;
use bustub::execution::check_options::{CheckOption, CheckOptions};
use bustub::execution::execution_common::{generate_sort_key, SortEntry, TupleComparator};
use bustub::execution::execution_engine::ExecutionEngine;
use bustub::execution::executor_context::ExecutorContext;
use bustub::execution::executor_factory::create_executor;
use bustub::execution::executors::abstract_executor::Executor;
use bustub::execution::executors::external_merge_sort_executor::{ExternalMergeSortExecutor, MergeSortRun, RunBuilder};
use bustub::execution::executors::topn_executor::TopNExecutor;
use bustub::execution::expressions::abstract_expression::ExprRef;
use bustub::execution::expressions::column_value_expression::ColumnValueExpression;
use bustub::execution::plans::plan_node::{PlanKind, PlanNode, PlanRef};
use bustub::storage::table::tuple::Tuple;
use bustub::types::type_id::TypeId;
use bustub::types::value::Value;

fn int(v: i32) -> Value {
    Value::integer(v)
}

fn null() -> Value {
    Value::null(TypeId::Integer)
}

fn new_db() -> BusTubInstance {
    BusTubInstance::new(128)
}

fn sql(db: &BusTubInstance, sql: &str) -> Vec<String> {
    let mut out = String::new();
    db.execute_sql(sql, &mut SimpleStreamWriter::new(&mut out, true, " "), None).unwrap_or_else(|e| panic!("{sql}: {e}"));
    out.lines().map(|l| l.trim_end().to_string()).collect()
}

fn sql_err(db: &BusTubInstance, sql: &str) -> bool {
    let mut out = String::new();
    db.execute_sql(sql, &mut SimpleStreamWriter::new(&mut out, true, " "), None).is_err()
}

fn sorted(mut v: Vec<String>) -> Vec<String> {
    v.sort();
    v
}

fn insert_rows(db: &BusTubInstance, table: &str, rows: &[String]) {
    for chunk in rows.chunks(500) {
        sql(db, &format!("insert into {table} values {}", chunk.join(", ")));
    }
}

fn col(idx: u32, type_id: TypeId) -> ExprRef {
    let c = if type_id == TypeId::Varchar { Column::new_varchar("c", 100) } else { Column::new("c", type_id) };
    Arc::new(ColumnValueExpression::new(0, idx, c))
}

fn ob(idx: u32, ty: OrderByType, nulls: OrderByNullType) -> OrderBy {
    OrderBy::new(ty, nulls, col(idx, TypeId::Integer))
}

fn asc(idx: u32) -> OrderBy {
    ob(idx, OrderByType::Asc, OrderByNullType::Default)
}

fn desc(idx: u32) -> OrderBy {
    ob(idx, OrderByType::Desc, OrderByNullType::Default)
}

fn entry(keys: Vec<Value>) -> SortEntry {
    (keys, Tuple::empty())
}

// ---- 3g-01 · sort keys and the comparator ---------------------------------------------------------------------------------------

#[test]
fn s3g_01_the_sort_key_is_the_values_of_the_order_by_expressions() {
    let schema = Schema::new(vec![Column::new("a", TypeId::Integer), Column::new_varchar("b", 20), Column::new("c", TypeId::Integer)]);
    let tuple = Tuple::new(&[int(1), Value::varchar("x"), int(3)], &schema);
    let key = generate_sort_key(&tuple, &[desc(2), asc(0)], &schema).unwrap();
    assert_eq!(key, vec![int(3), int(1)], "the sort key is the values of the order by expressions");
    assert!(generate_sort_key(&tuple, &[], &schema).unwrap().is_empty(), "the sort key is the values of the order by expressions: expected `generate_sort_key(&tuple, &[], &schema).unwrap().is_empty()`");
}

#[test]
fn s3g_01_ascending_descending_and_default_directions() {
    let (a, b) = (entry(vec![int(1)]), entry(vec![int(2)]));
    assert_eq!(TupleComparator::new(vec![asc(0)]).compare(&a, &b), Ordering::Less, "ascending descending and default directions");
    assert_eq!(TupleComparator::new(vec![asc(0)]).compare(&b, &a), Ordering::Greater, "ascending descending and default directions");
    assert_eq!(TupleComparator::new(vec![desc(0)]).compare(&a, &b), Ordering::Greater, "ascending descending and default directions");
    assert_eq!(TupleComparator::new(vec![ob(0, OrderByType::Default, OrderByNullType::Default)]).compare(&a, &b), Ordering::Less, "no direction means ascending");
    assert_eq!(TupleComparator::new(vec![asc(0)]).compare(&a, &entry(vec![int(1)])), Ordering::Equal, "ascending descending and default directions");
}

#[test]
fn s3g_01_the_first_key_that_differs_decides() {
    let cmp = TupleComparator::new(vec![asc(0), desc(1)]);
    assert_eq!(cmp.compare(&entry(vec![int(1), int(5)]), &entry(vec![int(2), int(9)])), Ordering::Less, "the first key decides");
    assert_eq!(cmp.compare(&entry(vec![int(1), int(5)]), &entry(vec![int(1), int(9)])), Ordering::Greater, "tie on the first: the second, descending");
    assert_eq!(cmp.compare(&entry(vec![int(1), int(5)]), &entry(vec![int(1), int(5)])), Ordering::Equal, "the first key that differs decides");
}

#[test]
fn s3g_01_null_is_the_smallest_value_by_default() {
    let (n, one) = (entry(vec![null()]), entry(vec![int(1)]));
    assert_eq!(TupleComparator::new(vec![asc(0)]).compare(&n, &one), Ordering::Less, "ascending: NULLs first");
    assert_eq!(TupleComparator::new(vec![desc(0)]).compare(&n, &one), Ordering::Greater, "descending: NULLs last");
    assert_eq!(TupleComparator::new(vec![asc(0)]).compare(&n, &entry(vec![null()])), Ordering::Equal, "null is the smallest value by default");
}

#[test]
fn s3g_01_nulls_first_and_nulls_last_win_over_the_direction() {
    let (n, one) = (entry(vec![null()]), entry(vec![int(1)]));
    let desc_nulls_first = TupleComparator::new(vec![ob(0, OrderByType::Desc, OrderByNullType::NullsFirst)]);
    let asc_nulls_last = TupleComparator::new(vec![ob(0, OrderByType::Asc, OrderByNullType::NullsLast)]);
    assert_eq!(desc_nulls_first.compare(&n, &one), Ordering::Less, "nulls first and nulls last win over the direction");
    assert_eq!(desc_nulls_first.compare(&one, &n), Ordering::Greater, "nulls first and nulls last win over the direction");
    assert_eq!(asc_nulls_last.compare(&n, &one), Ordering::Greater, "nulls first and nulls last win over the direction");
    assert_eq!(asc_nulls_last.compare(&one, &n), Ordering::Less, "nulls first and nulls last win over the direction");
}

#[test]
fn s3g_01_strings_compare_bytewise_and_the_comparator_orders_a_whole_vector() {
    let s = |x: &str| entry(vec![Value::varchar(x)]);
    let by_string = TupleComparator::new(vec![OrderBy::new(OrderByType::Asc, OrderByNullType::Default, col(0, TypeId::Varchar))]);
    assert_eq!(by_string.compare(&s("apple"), &s("banana")), Ordering::Less, "strings compare bytewise and the comparator orders a whole vector");
    assert_eq!(by_string.compare(&s("Zebra"), &s("apple")), Ordering::Less, "upper case sorts before lower case");
    assert_eq!(by_string.compare(&s("ab"), &s("abc")), Ordering::Less, "a prefix is smaller");

    let mut rows: Vec<SortEntry> = vec![vec![int(3), null()], vec![int(1), int(2)], vec![null(), int(0)], vec![int(1), int(1)], vec![int(3), int(5)]].into_iter().map(entry).collect();
    let cmp = TupleComparator::new(vec![asc(0), desc(1)]);
    rows.sort_by(|a, b| cmp.compare(a, b));
    let keys: Vec<Vec<Value>> = rows.into_iter().map(|r| r.0).collect();
    assert_eq!(keys, vec![vec![null(), int(0)], vec![int(1), int(2)], vec![int(1), int(1)], vec![int(3), int(5)], vec![int(3), null()]], "strings compare bytewise and the comparator orders a whole vector");
}

// ---- helpers for the plan-level tests --------------------------------------------------------------------------------------------

fn scan(db: &BusTubInstance, name: &str) -> PlanRef {
    let catalog = db.catalog.read().unwrap();
    let info = catalog.get_table(name).unwrap();
    let schema = Schema::new(info.schema.columns().iter().map(|c| c.with_column_name(&format!("{name}.{}", c.name()))).collect());
    PlanNode::new(Arc::new(schema), vec![], PlanKind::SeqScan { table_oid: info.oid, table_name: name.to_string(), filter_predicate: None })
}

fn sort_plan(db: &BusTubInstance, table: &str, order_bys: Vec<OrderBy>) -> PlanRef {
    let child = scan(db, table);
    PlanNode::new(child.output_schema.clone(), vec![child], PlanKind::Sort { order_bys })
}

fn first_ints(tuples: &[Tuple], schema: &Schema) -> Vec<Value> {
    tuples.iter().map(|t| t.get_value(schema, 0)).collect()
}

fn pages_db() -> BusTubInstance {
    BusTubInstance::new(24)
}

/// A table `t(a int, tag int)` with the given `a` values; `tag` is the position of the row.
fn table_a_tag(db: &BusTubInstance, name: &str, a: &[i32]) {
    sql(db, &format!("create table {name}(a int, tag int)"));
    let rows: Vec<String> = a.iter().enumerate().map(|(i, v)| format!("({v}, {i})")).collect();
    insert_rows(db, name, &rows);
}

// ---- 3g-02 · runs on pages -------------------------------------------------------------------------------------------------------

fn int_tuple(v: i32) -> Tuple {
    Tuple::new(&[int(v)], &Schema::new(vec![Column::new("a", TypeId::Integer)]))
}

fn blob(byte: u8, len: usize) -> Tuple {
    Tuple::from_bytes(Rid::default(), &vec![byte; len])
}

#[test]
fn s3g_02_a_few_tuples_fit_one_page_and_read_back_in_order() {
    let db = pages_db();
    let tuples: Vec<Tuple> = (0..10).map(int_tuple).collect();
    let run = MergeSortRun::from_tuples(db.buffer_pool_manager, tuples.iter()).unwrap();
    assert_eq!(run.page_count(), 1, "a few tuples fit one page and read back in order");
    let back: Vec<Tuple> = run.iter().collect();
    assert_eq!(back.len(), 10, "a few tuples fit one page and read back in order");
    for (i, t) in back.iter().enumerate() {
        assert_eq!(t.data(), tuples[i].data(), "a few tuples fit one page and read back in order");
    }
}

#[test]
fn s3g_02_a_full_page_starts_the_next_one() {
    let db = pages_db();
    // a 1000-byte tuple takes 1004 bytes in a page; 4 bytes of count + 8 * 1004 fit in 8192, a ninth does not
    let tuples: Vec<Tuple> = (0..20).map(|i| blob(i as u8, 1000)).collect();
    let run = MergeSortRun::from_tuples(db.buffer_pool_manager, tuples.iter()).unwrap();
    assert_eq!(run.page_count(), 3, "a full page starts the next one");
    assert_eq!(run.read_page(0).len(), 8, "a full page starts the next one");
    assert_eq!(run.read_page(1).len(), 8, "a full page starts the next one");
    assert_eq!(run.read_page(2).len(), 4, "a full page starts the next one");
    let back: Vec<Tuple> = run.iter().collect();
    assert_eq!(back.len(), 20, "a full page starts the next one");
    assert!(back.iter().enumerate().all(|(i, t)| t.data() == &vec![i as u8; 1000][..]), "order and contents survive");
}

#[test]
fn s3g_02_an_empty_run_has_no_pages() {
    let db = pages_db();
    let run = MergeSortRun::from_tuples(db.buffer_pool_manager, std::iter::empty()).unwrap();
    assert_eq!(run.page_count(), 0, "an empty run has no pages");
    assert_eq!(run.iter().count(), 0, "an empty run has no pages");
}

#[test]
fn s3g_02_a_tuple_that_cannot_fit_in_a_page_is_an_error() {
    let db = pages_db();
    let mut b = RunBuilder::new(db.buffer_pool_manager);
    b.push(&blob(1, 100)).unwrap();
    let e = b.push(&blob(2, 9000)).unwrap_err();
    assert_eq!(e.kind, ExceptionType::Execution, "a tuple that cannot fit in a page is an error");
    // a tuple that exactly fills a page (4 bytes count + 4 bytes length + data) is fine
    let mut b = RunBuilder::new(db.buffer_pool_manager);
    b.push(&blob(3, 8192 - 8)).unwrap();
    assert_eq!(b.finish().page_count(), 1, "a tuple that cannot fit in a page is an error");
}

#[test]
fn s3g_02_a_builder_can_be_filled_tuple_by_tuple_and_the_pages_are_in_the_pool() {
    let db = pages_db();
    let mut b = RunBuilder::new(db.buffer_pool_manager);
    for i in 0..5000 {
        b.push(&int_tuple(i)).unwrap();
    }
    let run = b.finish();
    assert!(run.page_count() >= 5, "5000 small tuples need several pages, more than the pool of 24 frames holds along with a table: they are written out");
    assert_eq!(run.iter().count(), 5000, "a builder can be filled tuple by tuple and the pages are in the pool");
    let sum: i64 = run.iter().map(|t| t.get_value(&Schema::new(vec![Column::new("a", TypeId::Integer)]), 0).as_i64().unwrap()).sum();
    assert_eq!(sum, (0..5000i64).sum::<i64>(), "a builder can be filled tuple by tuple and the pages are in the pool");
    run.delete_pages();
}

#[test]
fn s3g_02_page_by_page_reading_matches_the_iterator() {
    let db = pages_db();
    let tuples: Vec<Tuple> = (0..3000).map(int_tuple).collect();
    let run = MergeSortRun::from_tuples(db.buffer_pool_manager, tuples.iter()).unwrap();
    let by_page: usize = (0..run.page_count()).map(|i| run.read_page(i).len()).sum();
    assert_eq!(by_page, 3000, "page by page reading matches the iterator");
    assert_eq!(run.iter().count(), 3000, "page by page reading matches the iterator");
}

// ---- 3g-03 · initial runs -------------------------------------------------------------------------------------------------------

fn executor_for<'e>(ctx: &'e ExecutorContext<'e>, plan: &PlanRef) -> ExternalMergeSortExecutor<'e, 2> {
    let child = create_executor(ctx, &plan.children[0]).unwrap();
    ExternalMergeSortExecutor::<2>::new(ctx, plan.clone(), child)
}

fn run_values(run: &MergeSortRun<'_>, schema: &Schema) -> Vec<(i64, i64)> {
    run.iter().map(|t| (t.get_value(schema, 0).as_i64().unwrap(), t.get_value(schema, 1).as_i64().unwrap())).collect()
}

#[test]
fn s3g_03_an_empty_input_makes_no_runs() {
    let db = pages_db();
    table_a_tag(&db, "t", &[]);
    let plan = sort_plan(&db, "t", vec![asc(0)]);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    assert!(executor_for(&ctx, &plan).generate_initial_runs().unwrap().is_empty(), "an empty input makes no runs: expected `executor_for(&ctx, &plan).generate_initial_runs().unwrap().is_empty()`");
}

#[test]
fn s3g_03_a_small_input_is_one_sorted_run_of_one_page() {
    let db = pages_db();
    table_a_tag(&db, "t", &[5, 3, 9, 1, 7]);
    let plan = sort_plan(&db, "t", vec![asc(0)]);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let runs = executor_for(&ctx, &plan).generate_initial_runs().unwrap();
    assert_eq!(runs.len(), 1, "a small input is one sorted run of one page");
    assert_eq!(runs[0].page_count(), 1, "a small input is one sorted run of one page");
    let values = run_values(&runs[0], &plan.output_schema);
    assert_eq!(values.iter().map(|v| v.0).collect::<Vec<_>>(), vec![1, 3, 5, 7, 9], "a small input is one sorted run of one page");
}

#[test]
fn s3g_03_a_big_input_is_cut_into_runs_of_one_page_each_sorted_inside() {
    let db = pages_db();
    let a: Vec<i32> = (0..4000).map(|i| (i * 7919) % 4001).collect(); // a permutation-ish
    table_a_tag(&db, "t", &a);
    let plan = sort_plan(&db, "t", vec![asc(0)]);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let runs = executor_for(&ctx, &plan).generate_initial_runs().unwrap();
    assert!(runs.len() > 1, "4000 rows of 8 bytes (+4 each in a page) do not fit in one page");
    let mut total = 0;
    let mut tags = vec![];
    for r in &runs {
        assert_eq!(r.page_count(), 1, "pass 0 makes runs of exactly one page");
        let v = run_values(r, &plan.output_schema);
        assert!(v.windows(2).all(|w| w[0].0 <= w[1].0), "each run is sorted");
        total += v.len();
        tags.extend(v.iter().map(|x| x.1));
    }
    assert_eq!(total, 4000, "a big input is cut into runs of one page each sorted inside");
    tags.sort();
    assert_eq!(tags, (0..4000).collect::<Vec<_>>(), "every row is in exactly one run");
}

#[test]
fn s3g_03_a_page_is_filled_before_a_new_run_starts() {
    let db = pages_db();
    let a: Vec<i32> = (0..3000).collect();
    table_a_tag(&db, "t", &a);
    let plan = sort_plan(&db, "t", vec![asc(0)]);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let runs = executor_for(&ctx, &plan).generate_initial_runs().unwrap();
    // each tuple is 8 bytes of data + 4 of length; a page holds (8192 - 4) / 12 = 682 of them
    let sizes: Vec<usize> = runs.iter().map(|r| r.iter().count()).collect();
    assert_eq!(sizes, vec![682, 682, 682, 682, 272], "a page is filled before a new run starts");
}

#[test]
fn s3g_03_descending_order_and_stability_inside_a_run() {
    let db = pages_db();
    table_a_tag(&db, "t", &[2, 1, 2, 1, 2]);
    let plan = sort_plan(&db, "t", vec![desc(0)]);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let runs = executor_for(&ctx, &plan).generate_initial_runs().unwrap();
    assert_eq!(run_values(&runs[0], &plan.output_schema), vec![(2, 0), (2, 2), (2, 4), (1, 1), (1, 3)], "equal keys keep their input order");
}

#[test]
fn s3g_03_the_sort_can_be_started_again() {
    let db = pages_db();
    table_a_tag(&db, "t", &[3, 1, 2]);
    let plan = sort_plan(&db, "t", vec![asc(0)]);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let mut e = executor_for(&ctx, &plan);
    let first = run_values(&e.generate_initial_runs().unwrap()[0], &plan.output_schema);
    let second = run_values(&e.generate_initial_runs().unwrap()[0], &plan.output_schema);
    assert_eq!(first, second, "the sort can be started again");
}

// ---- 3g-04 · merging runs ---------------------------------------------------------------------------------------------------------

fn pair(a: i32, tag: i32) -> Tuple {
    Tuple::new(&[int(a), int(tag)], &Schema::new(vec![Column::new("a", TypeId::Integer), Column::new("tag", TypeId::Integer)]))
}

fn make_run<'e>(db: &'e BusTubInstance, rows: &[(i32, i32)]) -> MergeSortRun<'e> {
    let tuples: Vec<Tuple> = rows.iter().map(|(a, t)| pair(*a, *t)).collect();
    MergeSortRun::from_tuples(db.buffer_pool_manager, tuples.iter()).unwrap()
}

#[test]
fn s3g_04_two_runs_merge_into_one_sorted_run() {
    let db = pages_db();
    table_a_tag(&db, "t", &[]);
    let plan = sort_plan(&db, "t", vec![asc(0)]);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let e = executor_for(&ctx, &plan);
    let merged = e.merge_runs(vec![make_run(&db, &[(1, 0), (4, 0), (6, 0)]), make_run(&db, &[(2, 1), (3, 1), (9, 1)])]).unwrap();
    assert_eq!(run_values(&merged, &plan.output_schema).iter().map(|v| v.0).collect::<Vec<_>>(), vec![1, 2, 3, 4, 6, 9], "two runs merge into one sorted run");
}

#[test]
fn s3g_04_many_runs_at_once_and_runs_of_different_lengths() {
    let db = pages_db();
    table_a_tag(&db, "t", &[]);
    let plan = sort_plan(&db, "t", vec![asc(0)]);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let e = executor_for(&ctx, &plan);
    let runs = vec![make_run(&db, &[(5, 0)]), make_run(&db, &[(1, 1), (2, 1), (3, 1), (4, 1)]), make_run(&db, &[]), make_run(&db, &[(0, 3), (9, 3)]), make_run(&db, &[(7, 4), (8, 4)])];
    let merged = e.merge_runs(runs).unwrap();
    assert_eq!(run_values(&merged, &plan.output_schema).iter().map(|v| v.0).collect::<Vec<_>>(), vec![0, 1, 2, 3, 4, 5, 7, 8, 9], "many runs at once and runs of different lengths");
}

#[test]
fn s3g_04_equal_keys_come_from_the_earlier_run_first() {
    let db = pages_db();
    table_a_tag(&db, "t", &[]);
    let plan = sort_plan(&db, "t", vec![asc(0)]);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let e = executor_for(&ctx, &plan);
    let merged = e.merge_runs(vec![make_run(&db, &[(1, 10), (2, 10)]), make_run(&db, &[(1, 20), (2, 20)]), make_run(&db, &[(1, 30)])]).unwrap();
    assert_eq!(run_values(&merged, &plan.output_schema), vec![(1, 10), (1, 20), (1, 30), (2, 10), (2, 20)], "ties: run order");
}

#[test]
fn s3g_04_merging_respects_descending_order_and_nulls() {
    let db = pages_db();
    sql(&db, "create table t(a int, tag int)");
    let plan = sort_plan(&db, "t", vec![ob(0, OrderByType::Desc, OrderByNullType::NullsFirst)]);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let e = executor_for(&ctx, &plan);
    let nullish = Tuple::new(&[null(), int(0)], &Schema::new(vec![Column::new("a", TypeId::Integer), Column::new("tag", TypeId::Integer)]));
    let r1 = MergeSortRun::from_tuples(db.buffer_pool_manager, [nullish.clone(), pair(9, 0), pair(3, 0)].iter()).unwrap();
    let r2 = make_run(&db, &[(8, 1), (3, 1), (1, 1)]);
    let merged = e.merge_runs(vec![r1, r2]).unwrap();
    let out: Vec<Value> = merged.iter().map(|t| t.get_value(&plan.output_schema, 0)).collect();
    assert_eq!(out, vec![null(), int(9), int(8), int(3), int(3), int(1)], "merging respects descending order and nulls");
}

#[test]
fn s3g_04_a_merged_run_is_a_run_like_any_other_and_can_be_merged_again() {
    let db = pages_db();
    table_a_tag(&db, "t", &[]);
    let plan = sort_plan(&db, "t", vec![asc(0)]);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let e = executor_for(&ctx, &plan);
    let ab = e.merge_runs(vec![make_run(&db, &[(1, 0), (5, 0)]), make_run(&db, &[(2, 1), (6, 1)])]).unwrap();
    let cd = e.merge_runs(vec![make_run(&db, &[(0, 2), (7, 2)]), make_run(&db, &[(3, 3), (4, 3)])]).unwrap();
    let all = e.merge_runs(vec![ab, cd]).unwrap();
    assert_eq!(run_values(&all, &plan.output_schema).iter().map(|v| v.0).collect::<Vec<_>>(), (0..=7).collect::<Vec<_>>(), "a merged run is a run like any other and can be merged again");
}

#[test]
fn s3g_04_merging_a_lot_of_data_through_a_small_pool() {
    let db = pages_db();
    table_a_tag(&db, "t", &[]);
    let plan = sort_plan(&db, "t", vec![asc(0)]);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let e = executor_for(&ctx, &plan);
    let evens: Vec<(i32, i32)> = (0..6000).filter(|v| v % 2 == 0).map(|v| (v, 0)).collect();
    let odds: Vec<(i32, i32)> = (0..6000).filter(|v| v % 2 == 1).map(|v| (v, 1)).collect();
    let merged = e.merge_runs(vec![make_run(&db, &evens), make_run(&db, &odds)]).unwrap();
    let values = run_values(&merged, &plan.output_schema);
    assert_eq!(values.len(), 6000, "merging a lot of data through a small pool");
    assert!(values.iter().enumerate().all(|(i, v)| v.0 == i as i64), "merging a lot of data through a small pool: expected `values.iter().enumerate().all(|(i, v)| v.0 == i as i64)`");
}

// ---- 3g-05 · the external merge sort executor --------------------------------------------------------------------------------------

#[test]
fn s3g_05_order_by_sorts_ascending_and_descending() {
    let db = new_db();
    sql(&db, "create table t(a int, b int)");
    sql(&db, "insert into t values (3, 30), (1, 10), (2, 20), (5, 50), (4, 40)");
    assert_eq!(sql(&db, "select * from t order by a"), vec!["1 10", "2 20", "3 30", "4 40", "5 50"], "order by sorts ascending and descending");
    assert_eq!(sql(&db, "select * from t order by a desc"), vec!["5 50", "4 40", "3 30", "2 20", "1 10"], "order by sorts ascending and descending");
    assert_eq!(sql(&db, "select b from t order by b desc"), vec!["50", "40", "30", "20", "10"], "order by sorts ascending and descending");
}

#[test]
fn s3g_05_several_keys_expressions_and_nulls() {
    let db = new_db();
    sql(&db, "create table t(a int, b int)");
    sql(&db, "insert into t values (1, 2), (null, 5), (1, 1), (2, null), (null, 1)");
    assert_eq!(sql(&db, "select * from t order by a, b desc"), vec!["integer_null 5", "integer_null 1", "1 2", "1 1", "2 integer_null"], "several keys expressions and nulls");
    assert_eq!(sql(&db, "select * from t order by a desc nulls first, b nulls last"), vec!["integer_null 1", "integer_null 5", "2 integer_null", "1 1", "1 2"], "several keys expressions and nulls");
    assert_eq!(sql(&db, "select * from t where a = 1 order by a + b desc, b"), vec!["1 2", "1 1"], "several keys expressions and nulls");
}

#[test]
fn s3g_05_a_sort_bigger_than_the_buffer_pool() {
    let db = BusTubInstance::new(16);
    sql(&db, "create table t(a int, tag int)");
    let a: Vec<i32> = (0..20000).map(|i| ((i as i64 * 7919) % 20011) as i32).collect();
    let rows: Vec<String> = a.iter().enumerate().map(|(i, v)| format!("({v}, {i})")).collect();
    insert_rows(&db, "t", &rows);
    let out = sql(&db, "select * from t order by a");
    assert_eq!(out.len(), 20000, "a sort bigger than the buffer pool");
    let firsts: Vec<i64> = out.iter().map(|l| l.split(' ').next().unwrap().parse().unwrap()).collect();
    assert!(firsts.windows(2).all(|w| w[0] <= w[1]), "sorted");
}

#[test]
fn s3g_05_equal_keys_keep_their_input_order() {
    let db = pages_db();
    let a: Vec<i32> = (0..3000).map(|i| i % 3).collect();
    table_a_tag(&db, "t", &a);
    let out = sql(&db, "select * from t order by a");
    let tags_of_zero: Vec<i64> = out.iter().filter(|l| l.starts_with("0 ")).map(|l| l.split(' ').nth(1).unwrap().parse().unwrap()).collect();
    assert_eq!(tags_of_zero, (0..3000).step_by(3).collect::<Vec<_>>(), "a stable sort");
}

#[test]
fn s3g_05_an_empty_table_and_a_single_row() {
    let db = new_db();
    sql(&db, "create table t(a int)");
    assert!(sql(&db, "select * from t order by a").is_empty(), "an empty table and a single row: expected `sql(&db, \"select * from t order by a\").is_empty()`");
    sql(&db, "insert into t values (7)");
    assert_eq!(sql(&db, "select * from t order by a"), vec!["7"], "an empty table and a single row");
}

#[test]
fn s3g_05_strings_sort_and_the_sort_can_run_twice() {
    let db = new_db();
    sql(&db, "create table t(s varchar(20))");
    sql(&db, "insert into t values ('pear'), ('Apple'), ('apple'), ('banana')");
    assert_eq!(sql(&db, "select * from t order by s"), vec!["Apple", "apple", "banana", "pear"], "strings sort and the sort can run twice");
    assert_eq!(sql(&db, "select * from t order by s"), vec!["Apple", "apple", "banana", "pear"], "strings sort and the sort can run twice");
    let plan = sort_plan(&db, "t", vec![OrderBy::new(OrderByType::Asc, OrderByNullType::Default, col(0, TypeId::Varchar))]);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let (_, rows) = ExecutionEngine::execute(&plan, &ctx).unwrap();
    assert_eq!(rows.len(), 4, "strings sort and the sort can run twice");
}

#[test]
fn s3g_05_the_sorted_output_comes_in_batches() {
    let db = new_db();
    table_a_tag(&db, "t", &(0..45).rev().collect::<Vec<_>>());
    let plan = sort_plan(&db, "t", vec![asc(0)]);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let mut e = create_executor(&ctx, &plan).unwrap();
    e.init().unwrap();
    let (mut tuples, mut rids) = (vec![], vec![]);
    let mut sizes = vec![];
    while e.next(&mut tuples, &mut rids, 20).unwrap() {
        sizes.push(tuples.len());
        assert_eq!(tuples.len(), rids.len(), "the sorted output comes in batches");
    }
    assert_eq!(sizes, vec![20, 20, 5], "the sorted output comes in batches");
}

// ---- 3g-06 · limit ---------------------------------------------------------------------------------------------------------------------

#[test]
fn s3g_06_limit_returns_the_first_n_rows() {
    let db = new_db();
    table_a_tag(&db, "t", &(0..100).collect::<Vec<_>>());
    assert_eq!(sql(&db, "select a from t limit 3"), vec!["0", "1", "2"], "limit returns the first n rows");
    assert_eq!(sql(&db, "select a from t limit 1"), vec!["0"], "limit returns the first n rows");
    assert_eq!(sql(&db, "select a from t limit 0").len(), 0, "limit returns the first n rows");
}

#[test]
fn s3g_06_a_limit_larger_than_the_input_returns_everything() {
    let db = new_db();
    table_a_tag(&db, "t", &[1, 2, 3]);
    assert_eq!(sql(&db, "select a from t limit 1000"), vec!["1", "2", "3"], "a limit larger than the input returns everything");
}

#[test]
fn s3g_06_limits_that_are_not_a_multiple_of_the_batch_size() {
    let db = new_db();
    table_a_tag(&db, "t", &(0..100).collect::<Vec<_>>());
    assert_eq!(sql(&db, "select a from t limit 20").len(), 20, "limits that are not a multiple of the batch size");
    assert_eq!(sql(&db, "select a from t limit 21").len(), 21, "limits that are not a multiple of the batch size");
    assert_eq!(sql(&db, "select a from t limit 45").len(), 45, "limits that are not a multiple of the batch size");
    assert_eq!(sql(&db, "select a from t limit 99").len(), 99, "limits that are not a multiple of the batch size");
}

#[test]
fn s3g_06_the_rest_of_the_child_is_never_read() {
    // __mock_t9 has 10,000,000 rows: reading them all would take far longer than this test
    let db = new_db();
    db.generate_mock_table();
    let started = std::time::Instant::now();
    assert_eq!(sql(&db, "select * from __mock_t9 limit 5").len(), 5, "the rest of the child is never read");
    assert!(started.elapsed() < std::time::Duration::from_secs(5), "the limit must stop pulling from its child");
}

#[test]
fn s3g_06_limit_after_order_by_and_inside_a_subquery() {
    let db = new_db();
    table_a_tag(&db, "t", &[5, 3, 9, 1, 7]);
    assert_eq!(sql(&db, "select a from t order by a desc limit 2"), vec!["9", "7"], "limit after order by and inside a subquery");
    assert_eq!(sql(&db, "select * from (select a from t order by a limit 3) order by a desc limit 2"), vec!["5", "3"], "limit after order by and inside a subquery");
}

#[test]
fn s3g_06_init_starts_the_count_over() {
    let db = new_db();
    table_a_tag(&db, "t", &(0..50).collect::<Vec<_>>());
    let child = scan(&db, "t");
    let plan = PlanNode::new(child.output_schema.clone(), vec![child], PlanKind::Limit { limit: 5 });
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let mut e = create_executor(&ctx, &plan).unwrap();
    let (mut tuples, mut rids) = (vec![], vec![]);
    for _ in 0..2 {
        e.init().unwrap();
        let mut n = 0;
        while e.next(&mut tuples, &mut rids, 20).unwrap() {
            n += tuples.len();
        }
        assert_eq!(n, 5, "each run yields 5 rows");
    }
}

// ---- 3g-07 · top-N ----------------------------------------------------------------------------------------------------------------------

fn topn_plan(db: &BusTubInstance, table: &str, order_bys: Vec<OrderBy>, n: usize) -> PlanRef {
    let child = scan(db, table);
    PlanNode::new(child.output_schema.clone(), vec![child], PlanKind::TopN { order_bys, n })
}

fn run_topn(db: &BusTubInstance, plan: &PlanRef, check: bool) -> Vec<Tuple> {
    let catalog = db.catalog.read().unwrap();
    let mut options = CheckOptions::default();
    if check {
        options.check_options_set.insert(CheckOption::EnableTopnCheck);
    }
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false).with_check_options(options);
    let (ok, tuples) = ExecutionEngine::execute(plan, &ctx).unwrap();
    assert!(ok, "in helper `run_topn`: expected `ok`");
    tuples
}

#[test]
fn s3g_07_the_best_n_rows_in_order() {
    let db = new_db();
    table_a_tag(&db, "t", &[5, 9, 1, 7, 8, 3, 6]);
    let plan = topn_plan(&db, "t", vec![desc(0)], 3);
    assert_eq!(first_ints(&run_topn(&db, &plan, true), &plan.output_schema), vec![int(9), int(8), int(7)], "the best n rows in order");
    let plan = topn_plan(&db, "t", vec![asc(0)], 2);
    assert_eq!(first_ints(&run_topn(&db, &plan, true), &plan.output_schema), vec![int(1), int(3)], "the best n rows in order");
}

#[test]
fn s3g_07_n_larger_than_the_input_and_n_zero() {
    let db = new_db();
    table_a_tag(&db, "t", &[2, 3, 1]);
    let plan = topn_plan(&db, "t", vec![asc(0)], 10);
    assert_eq!(first_ints(&run_topn(&db, &plan, true), &plan.output_schema), vec![int(1), int(2), int(3)], "n larger than the input and n zero");
    let plan = topn_plan(&db, "t", vec![asc(0)], 0);
    assert!(run_topn(&db, &plan, true).is_empty(), "n larger than the input and n zero: expected `run_topn(&db, &plan, true).is_empty()`");
    table_a_tag(&db, "e", &[]);
    assert!(run_topn(&db, &topn_plan(&db, "e", vec![asc(0)], 5), true).is_empty(), "n larger than the input and n zero: expected `run_topn(&db, &topn_plan(&db, \"e\", vec![asc(0)], 5), true).is_empty()`");
}

#[test]
fn s3g_07_ties_keep_the_earlier_rows() {
    let db = new_db();
    table_a_tag(&db, "t", &[1, 1, 1, 1, 1, 0]);
    let plan = topn_plan(&db, "t", vec![desc(0)], 3);
    let out = run_topn(&db, &plan, true);
    let tags: Vec<Value> = out.iter().map(|t| t.get_value(&plan.output_schema, 1)).collect();
    assert_eq!(tags, vec![int(0), int(1), int(2)], "what a stable sort followed by a limit would return");
}

#[test]
fn s3g_07_several_keys_nulls_and_a_big_input() {
    let db = new_db();
    sql(&db, "create table t(a int, b int)");
    sql(&db, "insert into t values (1, 3), (1, 5), (null, 9), (2, 1), (2, 7)");
    let plan = topn_plan(&db, "t", vec![asc(0), desc(1)], 4);
    let out = run_topn(&db, &plan, true);
    let rows: Vec<(Value, Value)> = out.iter().map(|t| (t.get_value(&plan.output_schema, 0), t.get_value(&plan.output_schema, 1))).collect();
    assert_eq!(rows, vec![(null(), int(9)), (int(1), int(5)), (int(1), int(3)), (int(2), int(7))], "several keys nulls and a big input");

    let big: Vec<i32> = (0..5000).map(|i| ((i as i64 * 7919) % 5003) as i32).collect();
    table_a_tag(&db, "big", &big);
    let plan = topn_plan(&db, "big", vec![desc(0)], 5);
    let top = first_ints(&run_topn(&db, &plan, true), &plan.output_schema);
    let mut expect = big.clone();
    expect.sort_by(|a, b| b.cmp(a));
    assert_eq!(top, expect[..5].iter().map(|v| int(*v)).collect::<Vec<_>>(), "several keys nulls and a big input");
}

#[test]
fn s3g_07_the_heap_never_holds_more_than_n_tuples() {
    let db = new_db();
    table_a_tag(&db, "t", &(0..1000).collect::<Vec<_>>());
    let plan = topn_plan(&db, "t", vec![desc(0)], 7);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let child = create_executor(&ctx, &plan.children[0]).unwrap();
    let counter = Arc::new(AtomicUsize::new(0));
    let mut e = TopNExecutor::new(plan.clone(), child, counter.clone());
    e.init().unwrap();
    assert_eq!(e.get_num_in_heap(), 7, "the heap never holds more than n tuples");
    assert_eq!(counter.load(AtomicOrdering::SeqCst), 7, "the heap never holds more than n tuples");
    let (mut tuples, mut rids) = (vec![], vec![]);
    assert!(e.next(&mut tuples, &mut rids, 20).unwrap(), "the heap never holds more than n tuples: expected `e.next(&mut tuples, &mut rids, 20).unwrap()`");
    assert_eq!(tuples.len(), 7, "the heap never holds more than n tuples");
    assert!(!e.next(&mut tuples, &mut rids, 20).unwrap(), "the heap never holds more than n tuples: expected `!e.next(&mut tuples, &mut rids, 20).unwrap()`");
}

#[test]
fn s3g_07_the_executor_can_be_initialised_again() {
    let db = new_db();
    table_a_tag(&db, "t", &[4, 8, 2, 6]);
    let plan = topn_plan(&db, "t", vec![asc(0)], 2);
    let catalog = db.catalog.read().unwrap();
    let ctx = ExecutorContext::new(&catalog, db.buffer_pool_manager, false);
    let mut e = create_executor(&ctx, &plan).unwrap();
    for _ in 0..2 {
        e.init().unwrap();
        let (mut tuples, mut rids) = (vec![], vec![]);
        assert!(e.next(&mut tuples, &mut rids, 20).unwrap(), "the executor can be initialised again: expected `e.next(&mut tuples, &mut rids, 20).unwrap()`");
        assert_eq!(first_ints(&tuples, &plan.output_schema), vec![int(2), int(4)], "the executor can be initialised again");
    }
}

// ---- 3g-08 · window functions: partitions ---------------------------------------------------------------------------------------------

fn window_db() -> BusTubInstance {
    let db = new_db();
    sql(&db, "create table t(g int, v int)");
    sql(&db, "insert into t values (1, 100), (1, 200), (1, 300), (2, 400), (2, 500), (3, null)");
    db
}

#[test]
fn s3g_08_an_empty_window_covers_the_whole_table_on_every_row() {
    let db = window_db();
    let rows = sql(&db, "select count(*) over (), sum(v) over (), min(v) over (), max(v) over (), count(v) over () from t");
    assert_eq!(rows.len(), 6, "a window function keeps every row");
    assert!(rows.iter().all(|r| r == "6 1500 100 500 5"), "{rows:?}");
}

#[test]
fn s3g_08_partition_by_gives_each_group_its_own_aggregate() {
    let db = window_db();
    assert_eq!(
        sorted(sql(&db, "select g, v, sum(v) over (partition by g), count(*) over (partition by g) from t")),
        vec!["1 100 600 3", "1 200 600 3", "1 300 600 3", "2 400 900 2", "2 500 900 2", "3 integer_null integer_null 1"], "partition by gives each group its own aggregate"
    );
}

#[test]
fn s3g_08_nulls_in_the_argument_are_ignored_and_a_null_partition_is_a_partition() {
    let db = new_db();
    sql(&db, "create table t(g int, v int)");
    sql(&db, "insert into t values (null, 1), (null, 2), (1, null), (1, null)");
    assert_eq!(
        sorted(sql(&db, "select g, count(v) over (partition by g), sum(v) over (partition by g), count(*) over (partition by g) from t")),
        vec!["1 integer_null integer_null 2", "1 integer_null integer_null 2", "integer_null 2 3 2", "integer_null 2 3 2"], "nulls in the argument are ignored and a null partition is a partition"
    );
}

#[test]
fn s3g_08_several_window_functions_with_different_partitions_are_independent() {
    let db = window_db();
    assert_eq!(
        sorted(sql(&db, "select v, sum(v) over (partition by g), sum(v) over () from t where v >= 200")),
        vec!["200 500 1400", "300 500 1400", "400 900 1400", "500 900 1400"], "several window functions with different partitions are independent"
    );
}

#[test]
fn s3g_08_input_order_is_kept_without_an_order_by() {
    let db = new_db();
    sql(&db, "create table t(g int, v int)");
    sql(&db, "insert into t values (2, 1), (1, 2), (2, 3), (1, 4)");
    assert_eq!(sql(&db, "select g, v, count(*) over (partition by g) from t"), vec!["2 1 2", "1 2 2", "2 3 2", "1 4 2"], "input order is kept without an order by");
}

#[test]
fn s3g_08_empty_table_and_expressions_in_the_select_list() {
    let db = new_db();
    sql(&db, "create table e(g int, v int)");
    assert!(sql(&db, "select count(*) over (), sum(v) over (partition by g) from e").is_empty(), "no rows, no window rows");
    let db = window_db();
    assert_eq!(sql(&db, "select g + 1, sum(v) over (partition by g) from t where g = 2").len(), 2, "empty table and expressions in the select list");
}

#[test]
fn s3g_08_the_planner_refuses_a_group_by_next_to_a_window_function() {
    let db = window_db();
    assert!(sql_err(&db, "select g, count(*) over () from t group by g"), "the planner refuses a group by next to a window function: expected `sql_err(&db, \"select g, count(*) over () from t group by g\")`");
    assert!(sql_err(&db, "select count(*), count(*) over () from t"), "the planner refuses a group by next to a window function: expected `sql_err(&db, \"select count(*), count(*) over () from t\")`");
}

// ---- 3g-09 · window functions: order by, running aggregates and rank -------------------------------------------------------------

#[test]
fn s3g_09_with_an_order_by_the_aggregate_runs_up_to_the_current_row() {
    let db = new_db();
    sql(&db, "create table t(v int)");
    sql(&db, "insert into t values (3), (1), (2), (5), (4)");
    assert_eq!(
        sql(&db, "select v, count(*) over (order by v), sum(v) over (order by v), min(v) over (order by v), max(v) over (order by v) from t"),
        vec!["1 1 1 1 1", "2 2 3 1 2", "3 3 6 1 3", "4 4 10 1 4", "5 5 15 1 5"],
        "rows come out in the window's order"
    );
}

#[test]
fn s3g_09_peers_share_the_value_of_the_last_peer() {
    let db = new_db();
    sql(&db, "create table t(v int)");
    sql(&db, "insert into t values (1), (1), (2), (3), (3), (3)");
    assert_eq!(sql(&db, "select v, sum(v) over (order by v), count(*) over (order by v) from t"), vec!["1 2 2", "1 2 2", "2 4 3", "3 13 6", "3 13 6", "3 13 6"], "peers share the value of the last peer");
}

#[test]
fn s3g_09_rank_numbers_peers_alike_and_leaves_gaps() {
    let db = new_db();
    sql(&db, "create table t(v int)");
    sql(&db, "insert into t values (-99999), (99999), (0), (1), (2), (3)");
    assert_eq!(sorted(sql(&db, "select v, rank() over (order by v) from t")), sorted(vec!["-99999 1".into(), "0 2".into(), "1 3".into(), "2 4".into(), "3 5".into(), "99999 6".into()]), "rank numbers peers alike and leaves gaps");
    sql(&db, "insert into t values (1), (3)");
    assert_eq!(
        sql(&db, "select v, rank() over (order by v) from t"),
        vec!["-99999 1", "0 2", "1 3", "1 3", "2 5", "3 6", "3 6", "99999 8"], "rank numbers peers alike and leaves gaps"
    );
}

#[test]
fn s3g_09_partition_by_with_order_by_restarts_in_each_partition() {
    let db = new_db();
    sql(&db, "create table t(g int, v int)");
    sql(&db, "insert into t values (1, 100), (1, 200), (1, 300), (2, 400), (2, 500)");
    assert_eq!(
        sorted(sql(&db, "select g, v, sum(v) over (partition by g order by v), rank() over (partition by g order by v) from t")),
        vec!["1 100 100 1", "1 200 300 2", "1 300 600 3", "2 400 400 1", "2 500 900 2"], "partition by with order by restarts in each partition"
    );
}

#[test]
fn s3g_09_descending_order_and_nulls() {
    let db = new_db();
    sql(&db, "create table t(v int)");
    sql(&db, "insert into t values (1), (null), (2)");
    assert_eq!(sql(&db, "select v, count(v) over (order by v desc), rank() over (order by v desc) from t"), vec!["2 1 1", "1 2 2", "integer_null 2 3"], "descending order and nulls");
    assert_eq!(sql(&db, "select v, count(*) over (order by v) from t"), vec!["integer_null 1", "1 2", "2 3"], "NULL is smallest ascending");
}

#[test]
fn s3g_09_one_order_by_serves_every_function_that_has_one() {
    let db = new_db();
    sql(&db, "create table t(v int)");
    sql(&db, "insert into t values (2), (1), (3)");
    assert_eq!(sql(&db, "select v, sum(v) over (order by v), count(*) over (order by v) from t"), vec!["1 1 1", "2 3 2", "3 6 3"], "one order by serves every function that has one");
    assert!(sql_err(&db, "select v, sum(v) over (), sum(v) over (order by v) from t"), "BusTub's planner refuses to mix windows with and without order by");
}

#[test]
fn s3g_09_rank_needs_an_order_by_and_other_frames_are_refused() {
    let db = new_db();
    sql(&db, "create table t(v int)");
    assert!(sql_err(&db, "select rank() over () from t"), "rank needs an order by and other frames are refused: expected `sql_err(&db, \"select rank() over () from t\")`");
    assert!(sql_err(&db, "select sum(v) over (order by v rows between 1 preceding and current row) from t"), "rank needs an order by and other frames are refused: expected `sql_err(&db, \"select sum(v) over (order by v rows between 1 preceding and current row) from t\")`");
    assert!(sql_err(&db, "select sum(v) over (order by v), sum(v) over (order by v desc) from t"), "the order-by clauses must agree");
}
