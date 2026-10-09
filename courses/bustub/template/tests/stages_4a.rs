//! Tests for module 4a: timestamps, transactions and version chains.

use std::sync::Arc;

use bustub::catalog::catalog::TableInfo;
use bustub::catalog::column::Column;
use bustub::catalog::schema::Schema;
use bustub::common::bustub_instance::BusTubInstance;
use bustub::common::result_writer::SimpleStreamWriter;
use bustub::common::rid::Rid;
use bustub::concurrency::transaction::{IsolationLevel, Transaction, TransactionState, UndoLink, UndoLog, INVALID_TS, TXN_START_ID};
use bustub::concurrency::watermark::Watermark;
use bustub::execution::execution_common::{txn_mgr_dbg, collect_undo_logs, generate_new_undo_log, generate_updated_undo_log, get_undo_log_schema, reconstruct_tuple};
use bustub::storage::table::tuple::{Tuple, TupleMeta};
use bustub::types::type_id::TypeId;
use bustub::types::value::Value;

const SI: IsolationLevel = IsolationLevel::SnapshotIsolation;

fn int(v: i32) -> Value {
    Value::integer(v)
}
fn int_null() -> Value {
    Value::null(TypeId::Integer)
}
fn dbl(v: f64) -> Value {
    Value::decimal(v)
}
fn dbl_null() -> Value {
    Value::null(TypeId::Decimal)
}
fn boolean(v: bool) -> Value {
    Value::boolean(v)
}
fn bool_null() -> Value {
    Value::null(TypeId::Boolean)
}

/// `a integer, b double, c boolean`
fn abc() -> Schema {
    Schema::new(vec![Column::new("a", TypeId::Integer), Column::new("b", TypeId::Decimal), Column::new("c", TypeId::Boolean)])
}
fn schema_of(cols: &[(&str, TypeId)]) -> Schema {
    Schema::new(cols.iter().map(|(n, t)| Column::new(n, *t)).collect())
}

fn new_db() -> BusTubInstance {
    BusTubInstance::new(64)
}

fn begin(db: &BusTubInstance) -> Arc<Transaction> {
    db.txn_manager.begin(SI).unwrap()
}

fn commit(db: &BusTubInstance, txn: &Arc<Transaction>) {
    assert!(db.txn_manager.commit(txn).unwrap(), "commit failed");
}

fn maintable(db: &BusTubInstance) -> Arc<TableInfo<'static>> {
    db.catalog.write().unwrap().create_table("maintable", &abc()).unwrap()
}

fn meta(ts: i64, is_deleted: bool) -> TupleMeta {
    TupleMeta { ts, is_deleted }
}

fn insert(table: &TableInfo<'_>, m: TupleMeta, values: &[Value]) -> Rid {
    table.table.insert_tuple(&m, &Tuple::new(values, &table.schema)).unwrap()
}

/// Runs SQL inside a transaction and returns the rows as lines of space separated cells (sorted).
fn query(db: &BusTubInstance, txn: &Arc<Transaction>, sql: &str) -> Vec<String> {
    let mut out = String::new();
    assert!(db.execute_sql_txn(sql, &mut SimpleStreamWriter::new(&mut out, true, " "), txn).unwrap_or_else(|e| panic!("{sql}: {e}")), "{sql} failed");
    let mut rows: Vec<String> = out.lines().map(|l| l.trim_end().to_string()).collect();
    rows.sort();
    rows
}

fn verify(schema: &Schema, tuple: &Tuple, expected: &[Value]) {
    for (i, want) in expected.iter().enumerate() {
        let got = tuple.get_value(schema, i as u32);
        let same = (got.is_null() && want.is_null()) || got.compare_equals(want) == Ok(bustub::types::value::CmpBool::True);
        assert!(same, "column {i}: got {got}, expected {want} (tuple {})", tuple.to_string(schema));
    }
}

fn undo_log(is_deleted: bool, modified: &[bool], partial: &Schema, values: &[Value], ts: i64, prev: UndoLink) -> UndoLog {
    UndoLog { is_deleted, modified_fields: modified.to_vec(), tuple: Tuple::new(values, partial), ts, prev_version: prev }
}

// ---- 4a-01: the watermark ----------------------------------------------------------------------------------------------------------

#[test]
fn s4a_01_with_no_readers_the_watermark_is_the_last_commit() {
    let mut w = Watermark::new(0);
    assert_eq!(w.get_watermark(), 0);
    w.update_commit_ts(7);
    assert_eq!(w.get_watermark(), 7);
}

#[test]
fn s4a_01_the_watermark_is_the_smallest_read_timestamp() {
    let mut w = Watermark::new(0);
    w.add_txn(3).unwrap();
    w.add_txn(1).unwrap();
    w.add_txn(2).unwrap();
    assert_eq!(w.get_watermark(), 1);
}

#[test]
fn s4a_01_removing_the_smallest_moves_the_watermark_up() {
    let mut w = Watermark::new(0);
    for ts in [1, 2, 5] {
        w.add_txn(ts).unwrap();
    }
    w.remove_txn(1);
    assert_eq!(w.get_watermark(), 2);
    w.remove_txn(2);
    assert_eq!(w.get_watermark(), 5);
}

#[test]
fn s4a_01_removing_another_reader_leaves_the_watermark_alone() {
    let mut w = Watermark::new(0);
    for ts in [1, 2, 5] {
        w.add_txn(ts).unwrap();
    }
    w.remove_txn(5);
    w.remove_txn(2);
    assert_eq!(w.get_watermark(), 1);
}

#[test]
fn s4a_01_two_readers_at_the_same_timestamp_are_counted() {
    let mut w = Watermark::new(0);
    w.add_txn(4).unwrap();
    w.add_txn(4).unwrap();
    w.remove_txn(4);
    assert_eq!(w.get_watermark(), 4, "one reader is still there");
    w.update_commit_ts(9);
    w.remove_txn(4);
    assert_eq!(w.get_watermark(), 9, "none is left");
}

#[test]
fn s4a_01_a_reader_older_than_the_last_commit_is_refused() {
    let mut w = Watermark::new(5);
    let err = w.add_txn(4).unwrap_err();
    assert!(err.message.contains("read ts < commit ts"), "{err}");
    assert!(w.add_txn(5).is_ok());
}

#[test]
fn s4a_01_a_million_transactions_in_either_order() {
    let n = 1_000_000;
    let mut w = Watermark::new(0);
    for i in 0..n {
        w.add_txn(i).unwrap();
        assert_eq!(w.get_watermark(), 0);
    }
    for i in 0..n {
        w.update_commit_ts(i + 1);
        w.remove_txn(i);
        assert_eq!(w.get_watermark(), i + 1);
    }
    let mut w = Watermark::new(0);
    for i in 0..n {
        w.add_txn(i).unwrap();
    }
    for i in 0..n {
        w.update_commit_ts(i + 1);
        w.remove_txn(n - i - 1);
        assert_eq!(w.get_watermark(), if i == n - 1 { n } else { 0 });
    }
}

// ---- 4a-02: beginning a transaction ------------------------------------------------------------------------------------------------

#[test]
fn s4a_02_transaction_ids_start_at_two_to_the_62_and_count_up() {
    let db = new_db();
    let (t0, t1, t2) = (begin(&db), begin(&db), begin(&db));
    assert_eq!(t0.id(), TXN_START_ID);
    assert_eq!(t1.id(), TXN_START_ID + 1);
    assert_eq!(t2.id(), TXN_START_ID + 2);
    assert_eq!((t0.human_readable_id(), t2.human_readable_id()), (0, 2));
}

#[test]
fn s4a_02_a_new_transaction_is_running_and_has_not_committed() {
    let db = new_db();
    let t = db.txn_manager.begin(IsolationLevel::Serializable).unwrap();
    assert_eq!(t.state(), TransactionState::Running);
    assert_eq!(t.commit_ts(), INVALID_TS);
    assert_eq!(t.isolation_level(), IsolationLevel::Serializable);
    assert_eq!(t.temp_ts(), t.id());
}

#[test]
fn s4a_02_in_a_new_database_everything_reads_at_timestamp_zero() {
    let db = new_db();
    assert_eq!(begin(&db).read_ts(), 0);
    assert_eq!(begin(&db).read_ts(), 0);
}

#[test]
fn s4a_02_the_transaction_manager_remembers_the_transaction() {
    let db = new_db();
    let t = begin(&db);
    let found = db.txn_manager.get_txn(t.id()).expect("begin puts the transaction in txn_map");
    assert!(Arc::ptr_eq(&t, &found));
    assert!(db.txn_manager.get_txn(t.id() + 1).is_none());
}

#[test]
fn s4a_02_a_running_transaction_is_registered_with_the_watermark() {
    let db = new_db();
    assert_eq!(db.txn_manager.get_watermark(), 0);
    let _t = begin(&db);
    // a second transaction cannot move the watermark above the first: both read at 0
    let _u = begin(&db);
    assert_eq!(db.txn_manager.get_watermark(), 0);
}

// ---- 4a-03: committing and aborting ---------------------------------------------------------------------------------------------------

#[test]
fn s4a_03_commit_timestamps_count_up_from_one() {
    let db = new_db();
    for expected in 1..=3 {
        let t = begin(&db);
        commit(&db, &t);
        assert_eq!(t.commit_ts(), expected);
        assert_eq!(t.state(), TransactionState::Committed);
    }
}

#[test]
fn s4a_03_a_transaction_that_begins_after_a_commit_reads_it() {
    let db = new_db();
    let early = begin(&db);
    let t = begin(&db);
    commit(&db, &t);
    let late = begin(&db);
    assert_eq!((early.read_ts(), late.read_ts()), (0, 1));
}

#[test]
fn s4a_03_commit_stamps_the_tuples_in_the_write_set() {
    let db = new_db();
    let table = maintable(&db);
    let t = begin(&db);
    let r1 = insert(&table, meta(t.temp_ts(), false), &[int(1), dbl(1.0), bool_null()]);
    let r2 = insert(&table, meta(t.temp_ts(), true), &[int(2), dbl(2.0), bool_null()]);
    t.append_write_set(table.oid, r1);
    t.append_write_set(table.oid, r2);
    commit(&db, &t);
    assert_eq!(table.table.get_tuple_meta(r1).unwrap(), meta(1, false));
    assert_eq!(table.table.get_tuple_meta(r2).unwrap(), meta(1, true), "a deleted tuple stays deleted");
}

#[test]
fn s4a_03_commit_leaves_other_tuples_alone() {
    let db = new_db();
    let table = maintable(&db);
    let t = begin(&db);
    let mine = insert(&table, meta(t.temp_ts(), false), &[int(1), dbl(1.0), bool_null()]);
    let other = insert(&table, meta(77, false), &[int(2), dbl(2.0), bool_null()]);
    t.append_write_set(table.oid, mine);
    commit(&db, &t);
    assert_eq!(table.table.get_tuple_meta(other).unwrap().ts, 77);
}

#[test]
fn s4a_03_a_tainted_transaction_cannot_commit() {
    let db = new_db();
    let t = begin(&db);
    t.set_tainted();
    assert_eq!(db.txn_manager.commit(&t).unwrap(), false);
    assert_eq!(t.state(), TransactionState::Tainted);
    assert_eq!(db.txn_manager.get_watermark(), 0);
}

#[test]
fn s4a_03_committing_twice_is_an_error() {
    let db = new_db();
    let t = begin(&db);
    commit(&db, &t);
    assert!(db.txn_manager.commit(&t).is_err());
}

#[test]
fn s4a_03_commit_moves_the_watermark() {
    let db = new_db();
    let a = begin(&db);
    let b = begin(&db);
    commit(&db, &b);
    assert_eq!(db.txn_manager.get_watermark(), 0, "a still reads at 0");
    commit(&db, &a);
    assert_eq!(db.txn_manager.get_watermark(), 2);
}

#[test]
fn s4a_03_abort_ends_the_transaction_and_releases_its_read_timestamp() {
    let db = new_db();
    let a = begin(&db);
    let b = begin(&db);
    commit(&db, &b);
    db.txn_manager.abort(&a).unwrap();
    assert_eq!(a.state(), TransactionState::Aborted);
    assert_eq!(db.txn_manager.get_watermark(), 1);
}

#[test]
fn s4a_03_a_tainted_transaction_can_be_aborted_but_a_finished_one_cannot() {
    let db = new_db();
    let t = begin(&db);
    t.set_tainted();
    db.txn_manager.abort(&t).unwrap();
    assert_eq!(t.state(), TransactionState::Aborted);
    assert!(db.txn_manager.abort(&t).is_err());
    let u = begin(&db);
    commit(&db, &u);
    assert!(db.txn_manager.abort(&u).is_err());
}

// ---- 4a-04: reconstructing a tuple ----------------------------------------------------------------------------------------------------

#[test]
fn s4a_04_no_logs_gives_the_base_tuple() {
    let s = abc();
    let base = Tuple::new(&[int(0), dbl(1.0), bool_null()], &s);
    let t = reconstruct_tuple(&s, &base, &meta(2333, false), &[]).unwrap();
    verify(&s, &t, &[int(0), dbl(1.0), bool_null()]);
}

#[test]
fn s4a_04_a_deleted_base_with_no_logs_does_not_exist() {
    let s = abc();
    let base = Tuple::new(&[int_null(), dbl_null(), bool_null()], &s);
    assert!(reconstruct_tuple(&s, &base, &meta(2333, true), &[]).is_none());
}

#[test]
fn s4a_04_a_full_log_over_a_deleted_base_brings_the_tuple_back() {
    let s = abc();
    let base = Tuple::new(&[int_null(), dbl_null(), bool_null()], &s);
    let log = undo_log(false, &[true, true, true], &s, &[int(1), dbl(2.0), boolean(false)], 1, UndoLink::default());
    let t = reconstruct_tuple(&s, &base, &meta(2333, true), &[log]).unwrap();
    verify(&s, &t, &[int(1), dbl(2.0), boolean(false)]);
}

#[test]
fn s4a_04_partial_logs_restore_only_their_columns() {
    let s = abc();
    let base = Tuple::new(&[int(0), dbl(1.0), bool_null()], &s);
    let none = undo_log(false, &[false, false, false], &schema_of(&[]), &[], 1, UndoLink::default());
    let b_only = undo_log(false, &[false, true, false], &schema_of(&[("b", TypeId::Decimal)]), &[dbl(2.0)], 1, UndoLink::default());
    let a_and_c = undo_log(false, &[true, false, true], &schema_of(&[("a", TypeId::Integer), ("c", TypeId::Boolean)]), &[int(3), boolean(false)], 1, UndoLink::default());
    let m = meta(2333, false);
    verify(&s, &reconstruct_tuple(&s, &base, &m, &[none.clone()]).unwrap(), &[int(0), dbl(1.0), bool_null()]);
    verify(&s, &reconstruct_tuple(&s, &base, &m, &[none.clone(), b_only.clone()]).unwrap(), &[int(0), dbl(2.0), bool_null()]);
    verify(&s, &reconstruct_tuple(&s, &base, &m, &[none, b_only, a_and_c]).unwrap(), &[int(3), dbl(2.0), boolean(false)]);
}

#[test]
fn s4a_04_the_logs_are_applied_in_order_so_the_last_one_wins() {
    let s = abc();
    let base = Tuple::new(&[int(0), dbl(1.0), bool_null()], &s);
    let mk = |a: i32| undo_log(false, &[true, true, true], &s, &[int(a), dbl(a as f64), boolean(true)], 1, UndoLink::default());
    let t = reconstruct_tuple(&s, &base, &meta(9, false), &[mk(1), mk(2), mk(4)]).unwrap();
    verify(&s, &t, &[int(4), dbl(4.0), boolean(true)]);
}

#[test]
fn s4a_04_a_deleting_log_makes_the_tuple_not_exist_until_a_later_log_restores_it() {
    let s = abc();
    let base = Tuple::new(&[int(0), dbl(1.0), bool_null()], &s);
    let m = meta(9, false);
    let del = undo_log(true, &[false, false, false], &schema_of(&[]), &[], 1, UndoLink::default());
    let full = undo_log(false, &[true, true, true], &s, &[int(1), dbl(1.0), boolean(false)], 1, UndoLink::default());
    let nulls = undo_log(false, &[true, true, true], &s, &[int_null(), dbl_null(), bool_null()], 1, UndoLink::default());
    assert!(reconstruct_tuple(&s, &base, &m, &[del.clone()]).is_none());
    verify(&s, &reconstruct_tuple(&s, &base, &m, &[del.clone(), full.clone()]).unwrap(), &[int(1), dbl(1.0), boolean(false)]);
    assert!(reconstruct_tuple(&s, &base, &m, &[del.clone(), full.clone(), del.clone()]).is_none());
    verify(&s, &reconstruct_tuple(&s, &base, &m, &[del.clone(), full, del, nulls]).unwrap(), &[int_null(), dbl_null(), bool_null()]);
}

// ---- 4a-05: collecting the undo logs a transaction needs ---------------------------------------------------------------------------------

/// A table row at `ts` with an optional chain of (ts, value of a) undo logs, newest first, stored in `owner`.
fn row_with_chain(db: &BusTubInstance, table: &TableInfo<'_>, owner: &Arc<Transaction>, ts: i64, a: i32, chain: &[(i64, i32)]) -> Rid {
    let rid = insert(table, meta(ts, false), &[int(a), dbl(a as f64), bool_null()]);
    let partial = schema_of(&[("a", TypeId::Integer)]);
    let mut link = UndoLink::default();
    for &(log_ts, value) in chain.iter().rev() {
        link = owner.append_undo_log(undo_log(false, &[true, false, false], &partial, &[int(value)], log_ts, link));
    }
    if link.is_valid() {
        db.txn_manager.update_undo_link(rid, Some(link), None);
    }
    rid
}

fn collect(db: &BusTubInstance, table: &TableInfo<'_>, rid: Rid, txn: &Transaction) -> Option<Vec<UndoLog>> {
    let (m, tuple) = table.table.get_tuple(rid).unwrap();
    collect_undo_logs(rid, &m, &tuple, db.txn_manager.get_undo_link(rid), txn, &db.txn_manager)
}

#[test]
fn s4a_05_a_tuple_committed_at_or_before_the_read_timestamp_needs_no_logs() {
    let db = new_db();
    let table = maintable(&db);
    let owner = begin(&db);
    let t1 = begin(&db);
    commit(&db, &t1);
    let reader = begin(&db);
    assert_eq!(reader.read_ts(), 1);
    let old = row_with_chain(&db, &table, &owner, 0, 1, &[]);
    let exact = row_with_chain(&db, &table, &owner, 1, 2, &[]);
    assert_eq!(collect(&db, &table, old, &reader).unwrap().len(), 0);
    assert_eq!(collect(&db, &table, exact, &reader).unwrap().len(), 0);
}

#[test]
fn s4a_05_a_tuple_the_transaction_wrote_itself_needs_no_logs() {
    let db = new_db();
    let table = maintable(&db);
    let owner = begin(&db);
    let reader = begin(&db);
    let own = row_with_chain(&db, &table, &reader, reader.temp_ts(), 1, &[(0, 5)]);
    assert_eq!(collect(&db, &table, own, &reader).unwrap().len(), 0, "the newest version is its own");
}

#[test]
fn s4a_05_a_newer_tuple_without_a_chain_did_not_exist_yet() {
    let db = new_db();
    let table = maintable(&db);
    let owner = begin(&db);
    let reader = begin(&db);
    let newer = row_with_chain(&db, &table, &owner, 5, 1, &[]);
    assert!(collect(&db, &table, newer, &reader).is_none());
}

#[test]
fn s4a_05_another_transactions_uncommitted_tuple_is_not_visible() {
    let db = new_db();
    let table = maintable(&db);
    let writer = begin(&db);
    let reader = begin(&db);
    let theirs = row_with_chain(&db, &table, &writer, writer.temp_ts(), 1, &[]);
    assert!(collect(&db, &table, theirs, &reader).is_none());
}

#[test]
fn s4a_05_the_chain_is_followed_until_a_version_old_enough() {
    let db = new_db();
    let table = maintable(&db);
    let owner = begin(&db);
    for _ in 0..3 {
        let t = begin(&db);
        commit(&db, &t);
    }
    let reader = begin(&db);
    assert_eq!(reader.read_ts(), 3);
    // table ts 9, then logs for versions at 7, 3 (visible), 1
    let rid = row_with_chain(&db, &table, &owner, 9, 100, &[(7, 70), (3, 30), (1, 10)]);
    let logs = collect(&db, &table, rid, &reader).unwrap();
    assert_eq!(logs.iter().map(|l| l.ts).collect::<Vec<_>>(), vec![7, 3], "stop at the first log with ts <= 3");
    let s = abc();
    let (m, base) = table.table.get_tuple(rid).unwrap();
    verify(&s, &reconstruct_tuple(&s, &base, &m, &logs).unwrap(), &[int(30), dbl(100.0), bool_null()]);
}

#[test]
fn s4a_05_a_chain_of_only_newer_versions_means_the_tuple_did_not_exist() {
    let db = new_db();
    let table = maintable(&db);
    let owner = begin(&db);
    let reader = begin(&db);
    let rid = row_with_chain(&db, &table, &owner, 9, 1, &[(7, 2), (4, 3)]);
    assert!(collect(&db, &table, rid, &reader).is_none());
}

#[test]
fn s4a_05_a_log_that_has_been_garbage_collected_ends_the_search() {
    let db = new_db();
    let table = maintable(&db);
    let reader = begin(&db);
    let rid = insert(&table, meta(9, false), &[int(1), dbl(1.0), bool_null()]);
    db.txn_manager.update_undo_link(rid, Some(UndoLink { prev_txn: TXN_START_ID + 999, prev_log_idx: 0 }), None);
    assert!(collect(&db, &table, rid, &reader).is_none());
}

// ---- 4a-06: the undo log for a first change ---------------------------------------------------------------------------------------------

fn tup(s: &Schema, values: &[Value]) -> Tuple {
    Tuple::new(values, s)
}

#[test]
fn s4a_06_changing_some_columns_logs_those_columns_with_their_old_values() {
    let s = abc();
    let base = tup(&s, &[int(1), dbl(2.0), boolean(true)]);
    let target = tup(&s, &[int(1), dbl(5.0), boolean(false)]);
    let log = generate_new_undo_log(&s, Some(&base), Some(&target), 4, UndoLink::default());
    assert!(!log.is_deleted);
    assert_eq!(log.modified_fields, vec![false, true, true]);
    verify(&get_undo_log_schema(&s, &log.modified_fields), &log.tuple, &[dbl(2.0), boolean(true)]);
}

#[test]
fn s4a_06_the_log_remembers_the_timestamp_and_the_previous_version() {
    let s = abc();
    let base = tup(&s, &[int(1), dbl(2.0), boolean(true)]);
    let target = tup(&s, &[int(2), dbl(2.0), boolean(true)]);
    let prev = UndoLink { prev_txn: TXN_START_ID + 3, prev_log_idx: 2 };
    let log = generate_new_undo_log(&s, Some(&base), Some(&target), 4, prev);
    assert_eq!((log.ts, log.prev_version), (4, prev));
}

#[test]
fn s4a_06_deleting_logs_every_column() {
    let s = abc();
    let base = tup(&s, &[int(1), dbl_null(), boolean(true)]);
    let log = generate_new_undo_log(&s, Some(&base), None, 4, UndoLink::default());
    assert!(!log.is_deleted);
    assert_eq!(log.modified_fields, vec![true, true, true]);
    verify(&s, &log.tuple, &[int(1), dbl_null(), boolean(true)]);
}

#[test]
fn s4a_06_a_tuple_that_did_not_exist_gets_a_deleting_log() {
    let s = abc();
    let target = tup(&s, &[int(1), dbl(2.0), boolean(true)]);
    let log = generate_new_undo_log(&s, None, Some(&target), 4, UndoLink::default());
    assert!(log.is_deleted);
    assert_eq!(log.modified_fields, vec![false, false, false]);
    assert_eq!(log.tuple.get_length(), 0);
}

#[test]
fn s4a_06_a_null_that_stays_null_is_not_a_change() {
    let s = abc();
    let base = tup(&s, &[int(1), dbl_null(), boolean(true)]);
    let target = tup(&s, &[int(1), dbl_null(), boolean(true)]);
    let log = generate_new_undo_log(&s, Some(&base), Some(&target), 4, UndoLink::default());
    assert_eq!(log.modified_fields, vec![false, false, false]);
}

#[test]
fn s4a_06_going_to_or_from_null_is_a_change() {
    let s = abc();
    let base = tup(&s, &[int_null(), dbl(1.0), bool_null()]);
    let target = tup(&s, &[int(0), dbl(1.0), boolean(false)]);
    let log = generate_new_undo_log(&s, Some(&base), Some(&target), 4, UndoLink::default());
    assert_eq!(log.modified_fields, vec![true, false, true]);
    verify(&get_undo_log_schema(&s, &log.modified_fields), &log.tuple, &[int_null(), bool_null()]);
    let back = generate_new_undo_log(&s, Some(&target), Some(&base), 4, UndoLink::default());
    verify(&get_undo_log_schema(&s, &back.modified_fields), &back.tuple, &[int(0), boolean(false)]);
}

#[test]
fn s4a_06_a_log_reconstructs_the_version_it_was_made_from() {
    let s = abc();
    let base = tup(&s, &[int(1), dbl(2.0), boolean(true)]);
    let target = tup(&s, &[int(9), dbl(2.0), bool_null()]);
    let log = generate_new_undo_log(&s, Some(&base), Some(&target), 4, UndoLink::default());
    let back = reconstruct_tuple(&s, &target, &meta(5, false), &[log]).unwrap();
    verify(&s, &back, &[int(1), dbl(2.0), boolean(true)]);
}

// ---- 4a-07: updating the log of a tuple the transaction changed before -------------------------------------------------------------------

#[test]
fn s4a_07_a_second_change_adds_the_new_columns_and_keeps_the_old_values() {
    let s = abc();
    let v0 = tup(&s, &[int(1), dbl(2.0), boolean(true)]);
    let v1 = tup(&s, &[int(5), dbl(2.0), boolean(true)]); // first change: a
    let v2 = tup(&s, &[int(5), dbl(7.0), boolean(true)]); // second change: b
    let first = generate_new_undo_log(&s, Some(&v0), Some(&v1), 3, UndoLink::default());
    let second = generate_updated_undo_log(&s, Some(&v1), Some(&v2), &first);
    assert_eq!(second.modified_fields, vec![true, true, false]);
    verify(&get_undo_log_schema(&s, &second.modified_fields), &second.tuple, &[int(1), dbl(2.0)]);
}

#[test]
fn s4a_07_changing_a_column_again_keeps_its_original_value() {
    let s = abc();
    let v0 = tup(&s, &[int(1), dbl(2.0), boolean(true)]);
    let v1 = tup(&s, &[int(5), dbl(2.0), boolean(true)]);
    let v2 = tup(&s, &[int(6), dbl(2.0), boolean(true)]);
    let first = generate_new_undo_log(&s, Some(&v0), Some(&v1), 3, UndoLink::default());
    let second = generate_updated_undo_log(&s, Some(&v1), Some(&v2), &first);
    assert_eq!(second.modified_fields, vec![true, false, false]);
    verify(&get_undo_log_schema(&s, &second.modified_fields), &second.tuple, &[int(1)]);
}

#[test]
fn s4a_07_the_timestamp_and_previous_version_do_not_change() {
    let s = abc();
    let prev = UndoLink { prev_txn: TXN_START_ID + 1, prev_log_idx: 0 };
    let v0 = tup(&s, &[int(1), dbl(2.0), boolean(true)]);
    let v1 = tup(&s, &[int(5), dbl(2.0), boolean(true)]);
    let v2 = tup(&s, &[int(5), dbl(3.0), boolean(true)]);
    let first = generate_new_undo_log(&s, Some(&v0), Some(&v1), 3, prev);
    let second = generate_updated_undo_log(&s, Some(&v1), Some(&v2), &first);
    assert_eq!((second.ts, second.prev_version), (3, prev));
}

#[test]
fn s4a_07_deleting_after_a_partial_change_makes_the_log_cover_every_column() {
    let s = abc();
    let v0 = tup(&s, &[int(1), dbl(2.0), boolean(true)]);
    let v1 = tup(&s, &[int(5), dbl(2.0), boolean(true)]);
    let first = generate_new_undo_log(&s, Some(&v0), Some(&v1), 3, UndoLink::default());
    let second = generate_updated_undo_log(&s, Some(&v1), None, &first);
    assert_eq!(second.modified_fields, vec![true, true, true]);
    verify(&s, &second.tuple, &[int(1), dbl(2.0), boolean(true)]);
}

#[test]
fn s4a_07_a_log_that_says_did_not_exist_stays() {
    let s = abc();
    let v1 = tup(&s, &[int(5), dbl(2.0), boolean(true)]);
    let v2 = tup(&s, &[int(6), dbl(2.0), boolean(true)]);
    let first = generate_new_undo_log(&s, None, Some(&v1), 3, UndoLink::default());
    let second = generate_updated_undo_log(&s, Some(&v1), Some(&v2), &first);
    assert!(second.is_deleted);
    assert_eq!(second.modified_fields, vec![false, false, false]);
}

#[test]
fn s4a_07_changing_a_tuple_this_transaction_deleted_leaves_the_full_log() {
    let s = abc();
    let v0 = tup(&s, &[int(1), dbl(2.0), boolean(true)]);
    let first = generate_new_undo_log(&s, Some(&v0), None, 3, UndoLink::default());
    let v2 = tup(&s, &[int(8), dbl(8.0), boolean(false)]);
    let second = generate_updated_undo_log(&s, None, Some(&v2), &first);
    assert_eq!(second.modified_fields, vec![true, true, true]);
    verify(&s, &second.tuple, &[int(1), dbl(2.0), boolean(true)]);
}

// ---- 4a-08: the sequential scan reads versions --------------------------------------------------------------------------------------------

#[test]
fn s4a_08_a_transaction_sees_tuples_committed_before_it_began() {
    let db = new_db();
    let table = maintable(&db);
    let w = begin(&db);
    let rid = insert(&table, meta(w.temp_ts(), false), &[int(1), dbl(1.0), bool_null()]);
    w.append_write_set(table.oid, rid);
    commit(&db, &w);
    let r = begin(&db);
    assert_eq!(query(&db, &r, "SELECT a FROM maintable"), vec!["1"]);
}

#[test]
fn s4a_08_a_transaction_does_not_see_tuples_committed_after_it_began() {
    let db = new_db();
    let table = maintable(&db);
    let early = begin(&db);
    let w = begin(&db);
    let rid = insert(&table, meta(w.temp_ts(), false), &[int(1), dbl(1.0), bool_null()]);
    w.append_write_set(table.oid, rid);
    commit(&db, &w);
    assert!(query(&db, &early, "SELECT a FROM maintable").is_empty());
    assert_eq!(query(&db, &begin(&db), "SELECT a FROM maintable"), vec!["1"]);
}

#[test]
fn s4a_08_uncommitted_tuples_are_visible_only_to_their_writer() {
    let db = new_db();
    let table = maintable(&db);
    let w = begin(&db);
    let other = begin(&db);
    insert(&table, meta(w.temp_ts(), false), &[int(1), dbl(1.0), bool_null()]);
    assert_eq!(query(&db, &w, "SELECT a FROM maintable"), vec!["1"]);
    assert!(query(&db, &other, "SELECT a FROM maintable").is_empty());
}

#[test]
fn s4a_08_an_older_version_is_rebuilt_from_the_undo_logs() {
    let db = new_db();
    let table = maintable(&db);
    let owner = begin(&db);
    let t = begin(&db);
    commit(&db, &t); // ts 1
    let old_reader = db.txn_manager.begin(SI).unwrap();
    assert_eq!(old_reader.read_ts(), 1);
    let t = begin(&db);
    commit(&db, &t); // ts 2
    let new_reader = begin(&db);
    row_with_chain(&db, &table, &owner, 2, 20, &[(1, 10)]);
    assert_eq!(query(&db, &old_reader, "SELECT a FROM maintable"), vec!["10"]);
    assert_eq!(query(&db, &new_reader, "SELECT a FROM maintable"), vec!["20"]);
}

#[test]
fn s4a_08_a_deleted_tuple_is_gone_only_for_those_who_see_the_delete() {
    let db = new_db();
    let table = maintable(&db);
    let owner = begin(&db);
    let t = begin(&db);
    commit(&db, &t); // ts 1
    let before = begin(&db);
    let t = begin(&db);
    commit(&db, &t); // ts 2
    let after = begin(&db);
    let rid = insert(&table, meta(2, true), &[int(7), dbl(7.0), bool_null()]);
    let full = undo_log(false, &[true, true, true], &abc(), &[int(7), dbl(7.0), bool_null()], 1, UndoLink::default());
    let link = owner.append_undo_log(full);
    db.txn_manager.update_undo_link(rid, Some(link), None);
    assert_eq!(query(&db, &before, "SELECT a FROM maintable"), vec!["7"]);
    assert!(query(&db, &after, "SELECT a FROM maintable").is_empty());
}

#[test]
fn s4a_08_the_filter_sees_the_rebuilt_values() {
    let db = new_db();
    let table = maintable(&db);
    let owner = begin(&db);
    let t = begin(&db);
    commit(&db, &t);
    let reader = begin(&db);
    let t = begin(&db);
    commit(&db, &t);
    row_with_chain(&db, &table, &owner, 2, 20, &[(1, 10)]);
    assert_eq!(query(&db, &reader, "SELECT a FROM maintable WHERE a = 10"), vec!["10"]);
    assert!(query(&db, &reader, "SELECT a FROM maintable WHERE a = 20").is_empty());
}

#[test]
fn s4a_08_each_tuple_is_judged_on_its_own_chain() {
    let db = new_db();
    let table = maintable(&db);
    let owner = begin(&db);
    let t = begin(&db);
    commit(&db, &t);
    let reader = begin(&db);
    let t = begin(&db);
    commit(&db, &t);
    row_with_chain(&db, &table, &owner, 0, 1, &[]); // old enough
    row_with_chain(&db, &table, &owner, 2, 2, &[(1, 22)]); // rebuilt
    row_with_chain(&db, &table, &owner, 2, 3, &[]); // too new
    assert_eq!(query(&db, &reader, "SELECT a FROM maintable"), vec!["1", "22"]);
}

// ---- 4a-09: BusTub's tests ----------------------------------------------------------------------------------------------------------------

#[test]
fn s4a_09_timestamp_tracking() {
    let db = new_db();
    let m = &db.txn_manager;
    let txn0 = begin(&db);
    assert_eq!((txn0.read_ts(), m.get_watermark()), (0, 0));
    let store = |expect_read: i64, expect_commit: i64| {
        let t = begin(&db);
        assert_eq!(t.read_ts(), expect_read);
        commit(&db, &t);
        assert_eq!(t.commit_ts(), expect_commit);
    };
    store(0, 1);
    assert_eq!(m.get_watermark(), 0);
    let txn1 = begin(&db);
    assert_eq!(txn1.read_ts(), 1);
    assert_eq!(m.get_watermark(), 0);
    store(1, 2);
    assert_eq!(m.get_watermark(), 0);
    let txn2 = begin(&db);
    assert_eq!(txn2.read_ts(), 2);
    assert_eq!(m.get_watermark(), 0);
    m.abort(&txn0).unwrap();
    assert_eq!(m.get_watermark(), 1);
    store(2, 3);
    assert_eq!(m.get_watermark(), 1);
    let txn3 = begin(&db);
    assert_eq!(txn3.read_ts(), 3);
    assert_eq!(m.get_watermark(), 1);
    m.abort(&txn1).unwrap();
    assert_eq!(m.get_watermark(), 2);
    m.abort(&txn2).unwrap();
    assert_eq!(m.get_watermark(), 3);
    store(3, 4);
    assert_eq!(m.get_watermark(), 3);
    let txn4 = begin(&db);
    assert_eq!(txn4.read_ts(), 4);
    assert_eq!(m.get_watermark(), 3);
    m.abort(&txn3).unwrap();
    assert_eq!(m.get_watermark(), 4);
    m.abort(&txn4).unwrap();
    assert_eq!(m.get_watermark(), 4);
    let t5 = begin(&db);
    assert_eq!((t5.state(), t5.read_ts()), (TransactionState::Running, 4));
    commit(&db, &t5);
    assert_eq!(t5.state(), TransactionState::Committed);
    assert_eq!(m.get_watermark(), 5);
    let txn5 = begin(&db);
    assert_eq!((txn5.state(), txn5.read_ts(), m.get_watermark()), (TransactionState::Running, 5, 5));
    m.abort(&txn5).unwrap();
    assert_eq!(txn5.state(), TransactionState::Aborted);
    assert_eq!(m.get_watermark(), 5);
}

#[test]
fn s4a_09_tuple_reconstruct() {
    // BusTub's TxnScanTest.TupleReconstructTest, in the pieces of the earlier stages: here the combined chains of its cases C and D
    let s = abc();
    let base = Tuple::new(&[int(0), dbl(1.0), bool_null()], &s);
    let m = meta(2333, false);
    let l1 = undo_log(false, &[false, false, false], &schema_of(&[]), &[], 0, UndoLink::default());
    let l2 = undo_log(false, &[false, true, false], &schema_of(&[("b", TypeId::Decimal)]), &[dbl(2.0)], 0, UndoLink::default());
    let l3 = undo_log(false, &[true, false, true], &schema_of(&[("a", TypeId::Integer), ("c", TypeId::Boolean)]), &[int(3), boolean(false)], 0, UndoLink::default());
    let l4 = undo_log(false, &[true, true, true], &s, &[int(4), dbl(4.0), boolean(true)], 0, UndoLink::default());
    verify(&s, &reconstruct_tuple(&s, &base, &m, &[l1.clone()]).unwrap(), &[int(0), dbl(1.0), bool_null()]);
    verify(&s, &reconstruct_tuple(&s, &base, &m, &[l1.clone(), l2.clone()]).unwrap(), &[int(0), dbl(2.0), bool_null()]);
    verify(&s, &reconstruct_tuple(&s, &base, &m, &[l1.clone(), l2.clone(), l3.clone()]).unwrap(), &[int(3), dbl(2.0), boolean(false)]);
    verify(&s, &reconstruct_tuple(&s, &base, &m, &[l1, l2, l3, l4]).unwrap(), &[int(4), dbl(4.0), boolean(true)]);
    let del = undo_log(true, &[false, false, false], &schema_of(&[]), &[], 0, UndoLink::default());
    let one = undo_log(false, &[true, true, true], &s, &[int(1), dbl(1.0), boolean(false)], 0, UndoLink::default());
    let nulls = undo_log(false, &[true, true, true], &s, &[int_null(), dbl_null(), bool_null()], 0, UndoLink::default());
    assert!(reconstruct_tuple(&s, &base, &m, &[del.clone()]).is_none());
    verify(&s, &reconstruct_tuple(&s, &base, &m, &[del.clone(), one.clone()]).unwrap(), &[int(1), dbl(1.0), boolean(false)]);
    assert!(reconstruct_tuple(&s, &base, &m, &[del.clone(), one.clone(), del.clone()]).is_none());
    verify(&s, &reconstruct_tuple(&s, &base, &m, &[del.clone(), one, del, nulls]).unwrap(), &[int_null(), dbl_null(), bool_null()]);
}

#[test]
fn s4a_09_collect_undo_log_test() {
    // BusTub's TxnScanTest.CollectUndoLogTest
    let db = new_db();
    let s = abc();
    let modify = schema_of(&[("a", TypeId::Integer), ("b", TypeId::Decimal)]);
    let table = maintable(&db);
    let m = &db.txn_manager;
    let txn0 = begin(&db);
    assert_eq!(txn0.read_ts(), 0);
    commit(&db, &txn0);
    let rid0 = insert(&table, meta(txn0.commit_ts(), false), &[int(1), dbl(1.0), bool_null()]);
    let txn1 = begin(&db);
    assert_eq!(txn1.read_ts(), 1);
    commit(&db, &txn1);
    let txn_to_inspect = begin(&db);
    assert_eq!(txn_to_inspect.read_ts(), 2);
    let rid1 = insert(&table, meta(txn1.commit_ts(), false), &[int(2), dbl(2.0), bool_null()]);
    let link1 = txn1.append_undo_log(undo_log(false, &[true, true, false], &modify, &[int(1), dbl(1.0)], txn0.commit_ts(), UndoLink::default()));
    m.update_undo_link(rid1, Some(link1), None);
    let txn2 = begin(&db);
    assert_eq!(txn2.read_ts(), 2);
    commit(&db, &txn2);
    let rid2 = insert(&table, meta(txn2.commit_ts(), false), &[int(3), dbl(3.0), bool_null()]);
    let link2 = txn1.append_undo_log(undo_log(false, &[true, true, false], &modify, &[int(1), dbl(1.0)], txn0.commit_ts(), UndoLink::default()));
    let link3 = txn2.append_undo_log(undo_log(false, &[true, true, false], &modify, &[int(2), dbl(2.0)], txn1.commit_ts(), link2));
    m.update_undo_link(rid2, Some(link3), None);
    let rid3 = insert(&table, meta(txn2.commit_ts(), false), &[int(3), dbl(3.0), bool_null()]);
    let txn3 = begin(&db);
    assert_eq!(txn3.read_ts(), 3);
    commit(&db, &txn3);
    let rid4 = insert(&table, meta(txn3.commit_ts(), false), &[int(4), dbl(4.0), bool_null()]);
    let link4 = txn3.append_undo_log(undo_log(false, &[true, true, false], &modify, &[int(3), dbl(3.0)], txn2.commit_ts(), UndoLink::default()));
    m.update_undo_link(rid4, Some(link4), None);
    let rid5 = insert(&table, meta(txn3.commit_ts(), true), &[int(2), dbl(2.0), bool_null()]);
    let link5 = txn3.append_undo_log(undo_log(false, &[true, true, false], &modify, &[int(2), dbl(2.0)], txn1.commit_ts(), UndoLink::default()));
    m.update_undo_link(rid5, Some(link5), None);
    let rid6 = insert(&table, meta(txn3.commit_ts(), false), &[int(4), dbl(4.0), bool_null()]);
    let link6 = txn1.append_undo_log(undo_log(false, &[true, true, true], &s, &[int(1), dbl(1.0), bool_null()], txn0.commit_ts(), UndoLink::default()));
    let del = UndoLog { is_deleted: true, modified_fields: vec![false, false, false], tuple: Tuple::empty(), ts: txn1.commit_ts(), prev_version: link6 };
    let link7 = txn3.append_undo_log(del);
    m.update_undo_link(rid6, Some(link7), None);
    let rid7 = insert(&table, meta(txn_to_inspect.temp_ts(), false), &[int(100), dbl(100.0), bool_null()]);
    let rid8 = insert(&table, meta(txn_to_inspect.temp_ts(), false), &[int(100), dbl(100.0), bool_null()]);
    let link8 = txn_to_inspect.append_undo_log(undo_log(false, &[true, true, false], &modify, &[int(1), dbl(1.0)], txn0.commit_ts(), UndoLink::default()));
    m.update_undo_link(rid8, Some(link8), None);
    let txn4 = begin(&db);
    assert_eq!(txn4.read_ts(), 4);
    let rid9 = insert(&table, meta(txn4.temp_ts(), false), &[int(400), dbl(400.0), bool_null()]);
    let link9 = txn1.append_undo_log(undo_log(false, &[true, true, false], &modify, &[int(1), dbl(1.0)], txn0.commit_ts(), UndoLink::default()));
    let link10 = txn4.append_undo_log(undo_log(false, &[true, true, false], &modify, &[int(4), dbl(4.0)], txn3.commit_ts(), link9));
    m.update_undo_link(rid9, Some(link10), None);

    let rebuilt = |rid: Rid| -> Option<Option<Tuple>> {
        let (bm, bt) = table.table.get_tuple(rid).unwrap();
        let logs = collect_undo_logs(rid, &bm, &bt, m.get_undo_link(rid), &txn_to_inspect, m)?;
        Some(reconstruct_tuple(&s, &bt, &bm, &logs))
    };
    verify(&s, &rebuilt(rid0).unwrap().unwrap(), &[int(1), dbl(1.0), bool_null()]);
    verify(&s, &rebuilt(rid1).unwrap().unwrap(), &[int(2), dbl(2.0), bool_null()]);
    verify(&s, &rebuilt(rid2).unwrap().unwrap(), &[int(2), dbl(2.0), bool_null()]);
    assert!(rebuilt(rid3).is_none());
    assert!(rebuilt(rid4).is_none());
    verify(&s, &rebuilt(rid5).unwrap().unwrap(), &[int(2), dbl(2.0), bool_null()]);
    assert!(rebuilt(rid6).unwrap().is_none(), "the version at ts 2 is a deleted tuple");
    verify(&s, &rebuilt(rid7).unwrap().unwrap(), &[int(100), dbl(100.0), bool_null()]);
    verify(&s, &rebuilt(rid8).unwrap().unwrap(), &[int(100), dbl(100.0), bool_null()]);
    verify(&s, &rebuilt(rid9).unwrap().unwrap(), &[int(1), dbl(1.0), bool_null()]);
}

#[test]
fn s4a_09_scan_test() {
    // BusTub's TxnScanTest.ScanTest. record1: txn4 (val=1) -> ts=1 in txn4 (val=2); record2: ts=3 (val=3) -> ts=2 in txn_store_3 (delete)
    // -> ts=1 in txn_store_2 (val=4); record3: ts=4 (delete) -> ts=3 in txn_store_4 (val=5); record4: txn3 (delete) -> ts=2 in txn3
    // (val=6) -> ts=1 in txn_store_2 (val=7)
    let db = new_db();
    let s = abc();
    let only_a = schema_of(&[("a", TypeId::Integer)]);
    let table = maintable(&db);
    let m = &db.txn_manager;
    let txn0 = begin(&db);
    let t = begin(&db);
    commit(&db, &t);
    let txn1 = begin(&db);
    assert_eq!(txn1.read_ts(), 1);
    let store2 = begin(&db);
    let prev_log_3 = store2.append_undo_log(undo_log(false, &[true, true, true], &s, &[int(4), dbl(4.0), boolean(true)], 1, UndoLink::default()));
    let prev_log_6 = store2.append_undo_log(undo_log(false, &[true, false, false], &only_a, &[int(7)], 1, UndoLink::default()));
    commit(&db, &store2);
    let txn2 = begin(&db);
    assert_eq!(txn2.read_ts(), 2);
    let store3 = begin(&db);
    let prev_log_2 = store3.append_undo_log(UndoLog { is_deleted: true, modified_fields: vec![false; 3], tuple: Tuple::empty(), ts: 2, prev_version: prev_log_3 });
    commit(&db, &store3);
    let txn3 = begin(&db);
    assert_eq!(txn3.read_ts(), 3);
    let prev_log_5 = txn3.append_undo_log(undo_log(false, &[true, true, true], &s, &[int(6), dbl_null(), bool_null()], 2, prev_log_6));
    let store4 = begin(&db);
    let prev_log_4 = store4.append_undo_log(undo_log(false, &[true, true, true], &s, &[int(5), dbl(3.0), boolean(false)], 3, UndoLink::default()));
    commit(&db, &store4);
    let txn4 = begin(&db);
    assert_eq!(txn4.read_ts(), 4);
    let store5 = begin(&db);
    commit(&db, &store5);
    let txn5 = begin(&db);
    assert_eq!(txn5.read_ts(), 5);
    let prev_log_1 = txn4.append_undo_log(undo_log(false, &[true, false, false], &only_a, &[int(2)], 1, UndoLink::default()));
    let rid1 = insert(&table, meta(txn4.temp_ts(), false), &[int(1), dbl_null(), bool_null()]);
    m.update_undo_link(rid1, Some(prev_log_1), None);
    let rid2 = insert(&table, meta(txn3.read_ts(), false), &[int(3), dbl_null(), bool_null()]);
    m.update_undo_link(rid2, Some(prev_log_2), None);
    let rid3 = insert(&table, meta(txn4.read_ts(), true), &[int_null(), dbl_null(), bool_null()]);
    m.update_undo_link(rid3, Some(prev_log_4), None);
    let rid4 = insert(&table, meta(txn3.temp_ts(), true), &[int_null(), dbl_null(), bool_null()]);
    m.update_undo_link(rid4, Some(prev_log_5), None);

    txn_mgr_dbg("before verify scan", &db.txn_manager, &table);
    assert!(query(&db, &txn0, "SELECT * FROM maintable").is_empty());
    let a_of = |txn: &Arc<Transaction>| query(&db, txn, "SELECT a FROM maintable");
    assert_eq!(a_of(&txn1), vec!["2", "4", "7"]);
    // txn2 (read ts 2): record1 is txn4's uncommitted tuple, its log at ts 1 gives 2; record2 (ts 3) -> log ts 2 is a delete;
    // record3 (ts 4 deleted) -> log ts 3 > 2, nothing older; record4 (txn3's) -> its log at ts 2 gives 6
    assert_eq!(a_of(&txn2), vec!["2", "6"]);
    // txn3 (read ts 3): record1 as before -> 2; record2 is at ts 3: 3; record3: deleted at 4 -> log ts 3 gives 5; record4 is txn3's delete
    assert_eq!(a_of(&txn3), vec!["2", "3", "5"]);
    // txn4: record1 is its own: 1; record2: 3; record3 is deleted at ts 4: gone; record4: txn3's delete is uncommitted, log ts 2 gives 6
    assert_eq!(a_of(&txn4), vec!["1", "3", "6"]);
    // txn5: record1 uncommitted by txn4 -> 2; record2: 3; record3: deleted; record4: 6
    assert_eq!(a_of(&txn5), vec!["2", "3", "6"]);
}

#[test]
fn s4a_09_generate_undo_log_test() {
    // BusTub's TxnExecutorTest.GenerateUndoLogTest: the logs the executors of module 4b will make, applied back with reconstruct_tuple
    let s = abc();
    let none = UndoLink::default();
    let t = |a: i32, b: f64, c: bool| Tuple::new(&[int(a), dbl(b), boolean(c)], &s);
    let same = |x: &Tuple, y: &Tuple| x.data() == y.data();
    let live = meta(0, false);
    // simple update
    let (base, target) = (t(0, 0.0, true), t(0, 1.0, false));
    let log = generate_new_undo_log(&s, Some(&base), Some(&target), 0, none);
    assert!(same(&reconstruct_tuple(&s, &target, &live, &[log]).unwrap(), &base));
    // simple delete
    let log = generate_new_undo_log(&s, Some(&base), None, 0, none);
    assert!(same(&reconstruct_tuple(&s, &base, &meta(0, true), &[log]).unwrap(), &base));
    // simple insert (an insert over a tombstone)
    let target = t(0, 1.0, false);
    let log = generate_new_undo_log(&s, None, Some(&target), 0, none);
    assert!(reconstruct_tuple(&s, &target, &live, &[log]).is_none());
    // update twice in a txn
    let (base, mid, target) = (t(0, 0.0, true), t(0, 0.0, false), t(0, 1.0, false));
    let log = generate_new_undo_log(&s, Some(&base), Some(&mid), 0, none);
    let log = generate_updated_undo_log(&s, Some(&mid), Some(&target), &log);
    assert!(same(&reconstruct_tuple(&s, &target, &live, &[log]).unwrap(), &base));
    // update then delete in a txn
    let (base, target) = (t(0, 0.0, true), t(0, 1.0, false));
    let log = generate_new_undo_log(&s, Some(&base), Some(&target), 0, none);
    let log = generate_updated_undo_log(&s, Some(&target), None, &log);
    assert!(same(&reconstruct_tuple(&s, &target, &meta(0, true), &[log]).unwrap(), &base));
    // insert then update in a txn
    let (mid, target) = (t(0, 0.0, false), t(0, 1.0, false));
    let log = generate_new_undo_log(&s, None, Some(&mid), 0, none);
    let log = generate_updated_undo_log(&s, Some(&mid), Some(&target), &log);
    assert!(reconstruct_tuple(&s, &target, &live, &[log]).is_none());
    // insert then delete in a txn
    let log = generate_new_undo_log(&s, None, Some(&mid), 0, none);
    let log = generate_updated_undo_log(&s, Some(&mid), None, &log);
    assert!(reconstruct_tuple(&s, &mid, &meta(0, true), &[log]).is_none());
    // delete then insert in a txn
    let (base, target) = (t(0, 0.0, true), t(0, 1.0, false));
    let log = generate_new_undo_log(&s, Some(&base), None, 0, none);
    let log = generate_updated_undo_log(&s, None, Some(&target), &log);
    assert!(same(&reconstruct_tuple(&s, &target, &live, &[log]).unwrap(), &base));
}
