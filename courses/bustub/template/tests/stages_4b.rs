//! Tests for module 4b: MVCC writes, abort, garbage collection, the primary-key index and serializable validation.

use std::sync::Arc;

use bustub::catalog::catalog::TableInfo;
use bustub::common::bustub_instance::BusTubInstance;
use bustub::common::result_writer::SimpleStreamWriter;
use bustub::concurrency::transaction::{IsolationLevel, Transaction, TransactionState, TXN_START_ID};
use bustub::execution::execution_common::is_write_write_conflict;
use bustub::storage::table::tuple::TupleMeta;

fn new_db() -> BusTubInstance {
    BusTubInstance::new(256)
}

/// A statement outside any transaction (DDL).
fn exec(db: &BusTubInstance, sql: &str) {
    let mut out = String::new();
    assert!(db.execute_sql(sql, &mut SimpleStreamWriter::new(&mut out, true, " "), None).unwrap_or_else(|e| panic!("{sql}: {e}")), "{sql} failed");
}

fn begin(db: &BusTubInstance) -> Arc<Transaction> {
    db.txn_manager.begin(IsolationLevel::SnapshotIsolation).unwrap()
}

fn begin_serializable(db: &BusTubInstance) -> Arc<Transaction> {
    db.txn_manager.begin(IsolationLevel::Serializable).unwrap()
}

fn commit(db: &BusTubInstance, txn: &Arc<Transaction>) {
    assert!(db.txn_manager.commit(txn).unwrap(), "commit failed");
    assert_eq!(txn.state(), TransactionState::Committed);
}

fn abort(db: &BusTubInstance, txn: &Arc<Transaction>) {
    db.txn_manager.abort(txn).unwrap();
    assert_eq!(txn.state(), TransactionState::Aborted);
}

/// Runs a statement in a transaction; its success.
fn try_run(db: &BusTubInstance, txn: &Arc<Transaction>, sql: &str) -> (bool, String) {
    let mut out = String::new();
    let ok = db.execute_sql_txn(sql, &mut SimpleStreamWriter::new(&mut out, true, " "), txn).unwrap_or_else(|e| panic!("{sql}: {e}"));
    (ok, out)
}

fn run(db: &BusTubInstance, txn: &Arc<Transaction>, sql: &str) {
    let (ok, _) = try_run(db, txn, sql);
    assert!(ok, "{sql} failed");
}

/// The statement must fail with a write-write conflict that taints the transaction.
fn run_tainted(db: &BusTubInstance, txn: &Arc<Transaction>, sql: &str) {
    let (ok, _) = try_run(db, txn, sql);
    assert!(!ok, "{sql} should have failed");
    assert_eq!(txn.state(), TransactionState::Tainted, "{sql}");
}

/// The rows of a query, one string per row, sorted.
fn rows(db: &BusTubInstance, txn: &Arc<Transaction>, sql: &str) -> Vec<String> {
    let (ok, out) = try_run(db, txn, sql);
    assert!(ok, "{sql} failed");
    let mut rows: Vec<String> = out.lines().map(|l| l.trim_end().to_string()).filter(|l| !l.is_empty()).collect();
    rows.sort();
    rows
}

fn expect(db: &BusTubInstance, txn: &Arc<Transaction>, sql: &str, expected: &[&str]) {
    let mut want: Vec<String> = expected.iter().map(|s| s.to_string()).collect();
    want.sort();
    assert_eq!(rows(db, txn, sql), want, "{sql} in txn{}", txn.human_readable_id());
}

fn table(db: &BusTubInstance, name: &str) -> Arc<TableInfo<'static>> {
    db.catalog.read().unwrap().get_table(name).unwrap()
}

/// How many tuples (live or dead) the heap holds.
fn heap_entries(table: &TableInfo<'_>) -> usize {
    let mut iter = table.table.make_eager_iterator();
    let mut n = 0;
    while !iter.is_end() {
        iter.advance();
        n += 1;
    }
    n
}

fn undo_log_num(txn: &Transaction) -> usize {
    txn.undo_log_num()
}

/// The number of columns the transaction's only undo log restores.
fn undo_log_columns(txn: &Transaction) -> usize {
    assert_eq!(txn.undo_log_num(), 1, "one transaction holds at most one undo log for a tuple");
    txn.get_undo_log(0).modified_fields.iter().filter(|m| **m).count()
}

fn bump_commit_ts(db: &BusTubInstance, by: usize) {
    for _ in 0..by {
        let t = begin(db);
        commit(db, &t);
    }
}

fn txn_exists(db: &BusTubInstance, txn: &Transaction) -> bool {
    db.txn_manager.txn_map.read().unwrap().contains_key(&txn.id())
}

fn ensure_index_scan(db: &BusTubInstance) {
    exec(db, "CREATE TABLE pk_test_table_n(pk int primary key)");
    exec(db, "set force_optimizer_starter_rule=yes");
    let t = begin(db);
    let (_, plan) = try_run(db, &t, "EXPLAIN SELECT * FROM pk_test_table_n WHERE pk = 1");
    assert!(plan.contains("IndexScan"), "the point lookup should plan as an index scan:\n{plan}");
    abort(db, &t);
}

// ---- 4b-01: insert ----------------------------------------------------------------------------------------------------------------------

#[test]
fn s4b_01_an_inserted_tuple_is_visible_only_to_its_transaction() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int)");
    let (t1, t2, t_ref) = (begin(&db), begin(&db), begin(&db));
    run(&db, &t1, "INSERT INTO maintable VALUES (1)");
    run(&db, &t2, "INSERT INTO maintable VALUES (2)");
    expect(&db, &t1, "SELECT a FROM maintable", &["1"]);
    expect(&db, &t2, "SELECT a FROM maintable", &["2"]);
    let t3 = begin(&db);
    expect(&db, &t3, "SELECT a FROM maintable", &[]);
    expect(&db, &t_ref, "SELECT a FROM maintable", &[]);
}

#[test]
fn s4b_01_insert_reports_how_many_rows_it_inserted() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int)");
    let t = begin(&db);
    let (ok, out) = try_run(&db, &t, "INSERT INTO maintable VALUES (1), (2), (3)");
    assert!(ok);
    assert_eq!(out.trim(), "3");
}

#[test]
fn s4b_01_the_tuple_carries_the_temporary_timestamp_until_commit() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int)");
    let info = table(&db, "maintable");
    let t = begin(&db);
    run(&db, &t, "INSERT INTO maintable VALUES (1)");
    let rid = *t.write_sets().get(&info.oid).unwrap().iter().next().expect("the insert joined the write set");
    assert_eq!(info.table.get_tuple_meta(rid).unwrap(), TupleMeta { ts: t.temp_ts(), is_deleted: false });
    assert_eq!(undo_log_num(&t), 0, "a new tuple needs no undo log");
    commit(&db, &t);
    assert_eq!(info.table.get_tuple_meta(rid).unwrap(), TupleMeta { ts: t.commit_ts(), is_deleted: false });
}

#[test]
fn s4b_01_a_commit_makes_the_tuple_visible_to_later_transactions_only() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int)");
    let (t1, t2) = (begin(&db), begin(&db));
    run(&db, &t1, "INSERT INTO maintable VALUES (1)");
    run(&db, &t2, "INSERT INTO maintable VALUES (2)");
    commit(&db, &t1);
    let t_ref = begin(&db);
    let t3 = begin(&db);
    expect(&db, &t3, "SELECT a FROM maintable", &["1"]);
    expect(&db, &t2, "SELECT a FROM maintable", &["2"]);
    run(&db, &t3, "INSERT INTO maintable VALUES (3)");
    expect(&db, &t3, "SELECT a FROM maintable", &["1", "3"]);
    expect(&db, &t2, "SELECT a FROM maintable", &["2"]);
    commit(&db, &t3);
    commit(&db, &t2);
    let t4 = begin(&db);
    expect(&db, &t4, "SELECT a FROM maintable", &["1", "2", "3"]);
    expect(&db, &t_ref, "SELECT a FROM maintable", &["1"]);
}

#[test]
fn s4b_01_an_insert_select_in_a_transaction_does_not_see_its_own_new_rows() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int)");
    let t = begin(&db);
    run(&db, &t, "INSERT INTO maintable VALUES (1), (2)");
    run(&db, &t, "INSERT INTO maintable SELECT a + 10 FROM maintable");
    expect(&db, &t, "SELECT a FROM maintable", &["1", "2", "11", "12"]);
}

// ---- 4b-02: delete and write-write conflicts -------------------------------------------------------------------------------------------

fn meta(ts: i64) -> TupleMeta {
    TupleMeta { ts, is_deleted: false }
}

#[test]
fn s4b_02_a_tuple_is_in_conflict_if_it_is_newer_than_the_reader_and_not_its_own() {
    let db = new_db();
    bump_commit_ts(&db, 2);
    let t = begin(&db); // read ts 2
    assert!(!is_write_write_conflict(&meta(0), &t));
    assert!(!is_write_write_conflict(&meta(2), &t), "committed at the read timestamp: seen");
    assert!(is_write_write_conflict(&meta(3), &t), "committed after the transaction began");
    assert!(is_write_write_conflict(&meta(TXN_START_ID + 99), &t), "another transaction's uncommitted write");
    assert!(!is_write_write_conflict(&meta(t.temp_ts()), &t), "its own write");
}

#[test]
fn s4b_02_delete_hides_the_tuple_from_the_deleter_only() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int)");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO maintable VALUES (1), (2), (3)");
    commit(&db, &t0);
    let (t1, t2) = (begin(&db), begin(&db));
    let (_, out) = try_run(&db, &t1, "DELETE FROM maintable WHERE a = 2");
    assert_eq!(out.trim(), "1");
    expect(&db, &t1, "SELECT a FROM maintable", &["1", "3"]);
    expect(&db, &t2, "SELECT a FROM maintable", &["1", "2", "3"]);
    commit(&db, &t1);
    expect(&db, &t2, "SELECT a FROM maintable", &["1", "2", "3"]);
    expect(&db, &begin(&db), "SELECT a FROM maintable", &["1", "3"]);
}

#[test]
fn s4b_02_deleting_a_committed_tuple_leaves_one_full_undo_log() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int, b int)");
    let info = table(&db, "maintable");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO maintable VALUES (1, 10)");
    commit(&db, &t0);
    let t1 = begin(&db);
    run(&db, &t1, "DELETE FROM maintable");
    assert_eq!(undo_log_columns(&t1), 2, "a delete logs every column");
    let rid = *t1.write_sets().get(&info.oid).unwrap().iter().next().unwrap();
    assert!(info.table.get_tuple_meta(rid).unwrap().is_deleted);
    assert_eq!(db.txn_manager.get_undo_link(rid).unwrap().prev_txn, t1.id());
    assert_eq!(t1.get_undo_log(0).ts, t0.commit_ts(), "the log restores the version committed by t0");
}

#[test]
fn s4b_02_deleting_a_tuple_the_transaction_inserted_needs_no_log() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int)");
    let t = begin(&db);
    run(&db, &t, "INSERT INTO maintable VALUES (1)");
    run(&db, &t, "INSERT INTO maintable VALUES (2)");
    run(&db, &t, "INSERT INTO maintable VALUES (3)");
    run(&db, &t, "DELETE FROM maintable WHERE a = 3");
    assert_eq!(undo_log_num(&t), 0);
    expect(&db, &t, "SELECT a FROM maintable", &["1", "2"]);
    commit(&db, &t);
    expect(&db, &begin(&db), "SELECT a FROM maintable", &["1", "2"]);
}

#[test]
fn s4b_02_a_second_deleter_conflicts_and_is_tainted() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int)");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO maintable VALUES (1), (2)");
    commit(&db, &t0);
    let (t1, t2) = (begin(&db), begin(&db));
    run(&db, &t1, "DELETE FROM maintable WHERE a = 2");
    run_tainted(&db, &t2, "DELETE FROM maintable WHERE a = 2");
    expect(&db, &t1, "SELECT a FROM maintable", &["1"]);
}

#[test]
fn s4b_02_a_delete_of_a_tuple_committed_after_the_transaction_began_conflicts() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int)");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO maintable VALUES (1), (2)");
    commit(&db, &t0);
    let (t1, t2) = (begin(&db), begin(&db));
    run(&db, &t1, "DELETE FROM maintable WHERE a = 2");
    commit(&db, &t1);
    // t2 still sees (2) but the tuple was deleted by a commit after its read timestamp
    expect(&db, &t2, "SELECT a FROM maintable", &["1", "2"]);
    run_tainted(&db, &t2, "DELETE FROM maintable WHERE a = 2");
}

#[test]
fn s4b_02_a_tainted_transaction_can_not_commit_or_run_more_statements() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int)");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO maintable VALUES (1)");
    commit(&db, &t0);
    let (t1, t2) = (begin(&db), begin(&db));
    run(&db, &t1, "DELETE FROM maintable");
    run_tainted(&db, &t2, "DELETE FROM maintable");
    assert!(!db.txn_manager.commit(&t2).unwrap());
    assert_eq!(t2.state(), TransactionState::Tainted);
    let mut out = String::new();
    assert!(db.execute_sql_txn("SELECT a FROM maintable", &mut SimpleStreamWriter::new(&mut out, true, " "), &t2).is_err());
}

// ---- 4b-03: update ---------------------------------------------------------------------------------------------------------------------

#[test]
fn s4b_03_an_update_is_in_place_and_the_old_version_stays_for_older_readers() {
    let db = new_db();
    exec(&db, "CREATE TABLE table2(a int, b int, c int)");
    let info = table(&db, "table2");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO table2 VALUES (1, 1, 1)");
    commit(&db, &t0);
    let (t1, t_ref) = (begin(&db), begin(&db));
    run(&db, &t1, "UPDATE table2 SET b = 2");
    expect(&db, &t1, "SELECT * FROM table2", &["1 2 1"]);
    expect(&db, &t_ref, "SELECT * FROM table2", &["1 1 1"]);
    assert_eq!(undo_log_columns(&t1), 1);
    assert_eq!(heap_entries(&info), 1, "the tuple was updated in place, not re-inserted");
}

#[test]
fn s4b_03_a_tuple_the_transaction_inserted_is_updated_without_any_log() {
    let db = new_db();
    exec(&db, "CREATE TABLE table1(a int, b int, c int)");
    let t_ref = begin(&db);
    let t1 = begin(&db);
    run(&db, &t1, "INSERT INTO table1 VALUES (1, 1, 1)");
    run(&db, &t1, "UPDATE table1 SET b = 2");
    run(&db, &t1, "UPDATE table1 SET a = 4, b = 4, c = 4");
    expect(&db, &t1, "SELECT * FROM table1", &["4 4 4"]);
    expect(&db, &t_ref, "SELECT * FROM table1", &[]);
    assert_eq!(undo_log_num(&t1), 0);
}

#[test]
fn s4b_03_changing_the_same_tuple_again_widens_its_log_instead_of_adding_one() {
    let db = new_db();
    exec(&db, "CREATE TABLE table2(a int, b int, c int)");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO table2 VALUES (1, 1, 1)");
    commit(&db, &t0);
    let (t1, t_ref) = (begin(&db), begin(&db));
    run(&db, &t1, "UPDATE table2 SET b = 2");
    assert_eq!(undo_log_columns(&t1), 1);
    run(&db, &t1, "UPDATE table2 SET b = 3");
    assert_eq!(undo_log_columns(&t1), 1, "the same column again");
    run(&db, &t1, "UPDATE table2 SET a = 1");
    assert_eq!(undo_log_columns(&t1), 1, "not a real change");
    run(&db, &t1, "UPDATE table2 SET a = 2");
    assert_eq!(undo_log_columns(&t1), 2);
    run(&db, &t1, "UPDATE table2 SET a = 4, b = 4, c = 4");
    assert_eq!(undo_log_columns(&t1), 3);
    expect(&db, &t1, "SELECT * FROM table2", &["4 4 4"]);
    expect(&db, &t_ref, "SELECT * FROM table2", &["1 1 1"]);
}

#[test]
fn s4b_03_a_delete_after_updates_makes_the_log_cover_every_column() {
    let db = new_db();
    exec(&db, "CREATE TABLE table2(a int, b int, c int)");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO table2 VALUES (1, 1, 1)");
    commit(&db, &t0);
    let (t1, t_ref) = (begin(&db), begin(&db));
    run(&db, &t1, "UPDATE table2 SET b = 2");
    run(&db, &t1, "DELETE FROM table2");
    assert_eq!(undo_log_columns(&t1), 3);
    expect(&db, &t1, "SELECT * FROM table2", &[]);
    expect(&db, &t_ref, "SELECT * FROM table2", &["1 1 1"]);
    commit(&db, &t1);
    expect(&db, &begin(&db), "SELECT * FROM table2", &[]);
    expect(&db, &t_ref, "SELECT * FROM table2", &["1 1 1"]);
}

#[test]
fn s4b_03_updates_on_top_of_a_version_chain_keep_every_older_snapshot() {
    let db = new_db();
    exec(&db, "CREATE TABLE table2(a int, b int, c int)");
    let info = table(&db, "table2");
    let t00 = begin(&db);
    run(&db, &t00, "INSERT INTO table2 VALUES (0, 0, 0)");
    commit(&db, &t00);
    let ref0 = begin(&db);
    let t01 = begin(&db);
    run(&db, &t01, "UPDATE table2 SET a = 1, b = 1, c = 1");
    commit(&db, &t01);
    let (t1, ref1) = (begin(&db), begin(&db));
    run(&db, &t1, "UPDATE table2 SET b = 2");
    run(&db, &t1, "UPDATE table2 SET a = 2");
    run(&db, &t1, "DELETE FROM table2");
    commit(&db, &t1);
    expect(&db, &ref0, "SELECT * FROM table2", &["0 0 0"]);
    expect(&db, &ref1, "SELECT * FROM table2", &["1 1 1"]);
    expect(&db, &begin(&db), "SELECT * FROM table2", &[]);
    assert_eq!(heap_entries(&info), 1);
}

#[test]
fn s4b_03_a_conflicting_updater_is_tainted_and_the_winner_commits() {
    let db = new_db();
    exec(&db, "CREATE TABLE table1(a int, b int, c int)");
    let info = table(&db, "table1");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO table1 VALUES (0, 0, 0)");
    commit(&db, &t0);
    let t_ref = begin(&db);
    let (t1, t2) = (begin(&db), begin(&db));
    run(&db, &t1, "UPDATE table1 SET a = 1");
    run_tainted(&db, &t2, "UPDATE table1 SET b = 2");
    commit(&db, &t1);
    expect(&db, &t_ref, "SELECT * FROM table1", &["0 0 0"]);
    assert_eq!(heap_entries(&info), 1);
}

// ---- 4b-04: abort ----------------------------------------------------------------------------------------------------------------------

#[test]
fn s4b_04_aborting_an_insert_leaves_nothing_behind() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int, b int)");
    let t1 = begin(&db);
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 10), (1, 11), (2, 20)");
    expect(&db, &t1, "SELECT a, b FROM maintable ORDER BY a, b", &["1 10", "1 11", "2 20"]);
    abort(&db, &t1);
    let check = begin(&db);
    expect(&db, &check, "SELECT a, b FROM maintable ORDER BY a, b", &[]);
}

#[test]
fn s4b_04_aborting_an_update_restores_the_values_and_the_timestamp() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int, b int)");
    let info = table(&db, "maintable");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO maintable VALUES (1, 10), (2, 200), (3, 300)");
    commit(&db, &t0);
    let t3 = begin(&db);
    run(&db, &t3, "UPDATE maintable SET b = 0 WHERE a >= 2");
    expect(&db, &t3, "SELECT a, b FROM maintable", &["1 10", "2 0", "3 0"]);
    abort(&db, &t3);
    expect(&db, &begin(&db), "SELECT a, b FROM maintable", &["1 10", "2 200", "3 300"]);
    let mut iter = info.table.make_eager_iterator();
    while !iter.is_end() {
        let rid = iter.get_rid();
        iter.advance();
        assert_eq!(info.table.get_tuple_meta(rid).unwrap().ts, t0.commit_ts(), "the committed timestamp is back");
        assert!(db.txn_manager.get_undo_link(rid).is_none(), "the chain is as it was");
    }
}

#[test]
fn s4b_04_aborting_a_delete_brings_the_rows_back() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int, b int)");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO maintable VALUES (1, 10), (2, 200)");
    commit(&db, &t0);
    let t4 = begin(&db);
    run(&db, &t4, "DELETE FROM maintable");
    expect(&db, &t4, "SELECT a, b FROM maintable", &[]);
    abort(&db, &t4);
    expect(&db, &begin(&db), "SELECT a, b FROM maintable", &["1 10", "2 200"]);
}

#[test]
fn s4b_04_an_abort_after_several_changes_restores_the_version_before_the_transaction() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int, b int)");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO maintable VALUES (1, 10)");
    commit(&db, &t0);
    let reader = begin(&db);
    let t = begin(&db);
    run(&db, &t, "UPDATE maintable SET a = 5");
    run(&db, &t, "UPDATE maintable SET b = 6");
    run(&db, &t, "DELETE FROM maintable");
    abort(&db, &t);
    expect(&db, &reader, "SELECT a, b FROM maintable", &["1 10"]);
    expect(&db, &begin(&db), "SELECT a, b FROM maintable", &["1 10"]);
}

#[test]
fn s4b_04_a_tainted_transaction_is_aborted_like_any_other_and_commits_nothing() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int, b int)");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO maintable VALUES (1, 10), (2, 20)");
    commit(&db, &t0);
    let (t1, t2) = (begin(&db), begin(&db));
    run(&db, &t2, "UPDATE maintable SET b = 0 WHERE a = 1");
    run(&db, &t1, "UPDATE maintable SET b = 1 WHERE a = 2");
    run_tainted(&db, &t1, "UPDATE maintable SET b = 1 WHERE a = 1");
    abort(&db, &t1);
    commit(&db, &t2);
    expect(&db, &begin(&db), "SELECT a, b FROM maintable", &["1 0", "2 20"]);
}

#[test]
fn s4b_04_after_an_abort_another_transaction_may_write_the_tuple() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int, b int)");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO maintable VALUES (1, 10)");
    commit(&db, &t0);
    let (t1, t2) = (begin(&db), begin(&db));
    run(&db, &t1, "UPDATE maintable SET b = 1");
    abort(&db, &t1);
    run(&db, &t2, "UPDATE maintable SET b = 2");
    commit(&db, &t2);
    expect(&db, &begin(&db), "SELECT a, b FROM maintable", &["1 2"]);
}

// ---- 4b-05: garbage collection ------------------------------------------------------------------------------------------------------------

#[test]
fn s4b_05_a_finished_transaction_without_undo_logs_is_forgotten() {
    let db = new_db();
    exec(&db, "CREATE TABLE table1(a int, b int, c int)");
    let t_a = begin(&db);
    run(&db, &t_a, "INSERT INTO table1 VALUES (0, 0, 0)");
    commit(&db, &t_a);
    let running = begin(&db);
    db.txn_manager.garbage_collection();
    assert!(!txn_exists(&db, &t_a), "committed, no logs");
    assert!(txn_exists(&db, &running), "still running");
}

#[test]
fn s4b_05_a_transaction_whose_logs_a_reader_may_still_need_stays() {
    let db = new_db();
    exec(&db, "CREATE TABLE table1(a int, b int, c int)");
    let t_a = begin(&db);
    run(&db, &t_a, "INSERT INTO table1 VALUES (0, 0, 0)");
    commit(&db, &t_a);
    let old_reader = begin(&db);
    let t_b = begin(&db);
    run(&db, &t_b, "UPDATE table1 SET a = 1");
    commit(&db, &t_b);
    db.txn_manager.garbage_collection();
    assert!(txn_exists(&db, &t_b), "old_reader may need its undo log");
    expect(&db, &old_reader, "SELECT * FROM table1", &["0 0 0"]);
    commit(&db, &old_reader);
    db.txn_manager.garbage_collection();
    assert!(!txn_exists(&db, &t_b), "nobody reads at a timestamp before its commit now");
    expect(&db, &begin(&db), "SELECT * FROM table1", &["1 0 0"]);
}

#[test]
fn s4b_05_only_the_logs_below_the_oldest_needed_version_go() {
    let db = new_db();
    exec(&db, "CREATE TABLE table1(a int, b int, c int)");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO table1 VALUES (0, 0, 0)");
    commit(&db, &t0);
    let t1 = begin(&db);
    run(&db, &t1, "UPDATE table1 SET a = 1");
    commit(&db, &t1);
    let mid_reader = begin(&db); // reads the version of t1
    let t2 = begin(&db);
    run(&db, &t2, "UPDATE table1 SET a = 2");
    commit(&db, &t2);
    db.txn_manager.garbage_collection();
    assert!(txn_exists(&db, &t2), "mid_reader needs t2's log to see a = 1");
    assert!(!txn_exists(&db, &t1), "t1's log restores a = 0, older than anything a reader can ask for");
    expect(&db, &mid_reader, "SELECT * FROM table1", &["1 0 0"]);
}

#[test]
fn s4b_05_tainted_and_running_transactions_are_never_collected() {
    let db = new_db();
    exec(&db, "CREATE TABLE table1(a int, b int, c int)");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO table1 VALUES (0, 0, 0)");
    commit(&db, &t0);
    let (t5, t6) = (begin(&db), begin(&db));
    run(&db, &t5, "DELETE FROM table1");
    run_tainted(&db, &t6, "DELETE FROM table1");
    db.txn_manager.garbage_collection();
    assert!(txn_exists(&db, &t5) && txn_exists(&db, &t6));
    abort(&db, &t6);
    db.txn_manager.garbage_collection();
    assert!(!txn_exists(&db, &t6), "aborted, and it left no logs in any chain");
}

#[test]
fn s4b_05_collecting_twice_changes_nothing_and_every_snapshot_still_reads_right() {
    let db = new_db();
    exec(&db, "CREATE TABLE table1(a int, b int, c int)");
    let t_a = begin(&db);
    run(&db, &t_a, "INSERT INTO table1 VALUES (0, 0, 0), (1, 1, 1)");
    commit(&db, &t_a);
    let r1 = begin(&db);
    let t2 = begin(&db);
    run(&db, &t2, "UPDATE table1 SET a = a + 10");
    commit(&db, &t2);
    let r2 = begin(&db);
    db.txn_manager.garbage_collection();
    db.txn_manager.garbage_collection();
    expect(&db, &r1, "SELECT * FROM table1", &["0 0 0", "1 1 1"]);
    expect(&db, &r2, "SELECT * FROM table1", &["10 0 0", "11 1 1"]);
}

// ---- 4b-06: the primary-key index ---------------------------------------------------------------------------------------------------------

#[test]
fn s4b_06_a_duplicate_primary_key_fails_and_taints_the_transaction() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int primary key, b int)");
    let info = table(&db, "maintable");
    let t1 = begin(&db);
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 0)");
    expect(&db, &t1, "SELECT * FROM maintable", &["1 0"]);
    run_tainted(&db, &t1, "INSERT INTO maintable VALUES (1, 1)");
    assert_eq!(heap_entries(&info), 1);
}

#[test]
fn s4b_06_a_key_committed_by_somebody_else_is_a_duplicate_too() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int primary key, b int)");
    let t2 = begin(&db);
    run(&db, &t2, "INSERT INTO maintable VALUES (2, 2)");
    commit(&db, &t2);
    let (t3, t4) = (begin(&db), begin(&db));
    run(&db, &t3, "INSERT INTO maintable VALUES (3, 3)");
    commit(&db, &t3);
    expect(&db, &t4, "SELECT * FROM maintable", &["2 2"]);
    run_tainted(&db, &t4, "INSERT INTO maintable VALUES (3, 4)");
    let t5 = begin(&db);
    run(&db, &t5, "INSERT INTO maintable VALUES (4, 4)");
    expect(&db, &t5, "SELECT * FROM maintable", &["2 2", "3 3", "4 4"]);
    expect(&db, &begin(&db), "SELECT * FROM maintable", &["2 2", "3 3"]);
}

#[test]
fn s4b_06_a_deleted_key_is_reused_without_a_second_tuple() {
    let db = new_db();
    ensure_index_scan(&db);
    exec(&db, "CREATE TABLE maintable(col1 int primary key, col2 int)");
    let info = table(&db, "maintable");
    let t1 = begin(&db);
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 0), (2, 0), (3, 0), (4, 0)");
    commit(&db, &t1);
    let reverify = begin(&db);
    let t2 = begin(&db);
    run(&db, &t2, "DELETE FROM maintable");
    expect(&db, &t2, "SELECT * FROM maintable", &[]);
    commit(&db, &t2);
    let t3 = begin(&db);
    run(&db, &t3, "INSERT INTO maintable VALUES (2, 9)");
    expect(&db, &t3, "SELECT * FROM maintable", &["2 9"]);
    assert_eq!(heap_entries(&info), 4, "the tombstone of key 2 was reused");
    expect(&db, &reverify, "SELECT * FROM maintable", &["1 0", "2 0", "3 0", "4 0"]);
}

#[test]
fn s4b_06_index_scans_see_the_version_of_their_snapshot() {
    let db = new_db();
    ensure_index_scan(&db);
    exec(&db, "CREATE TABLE maintable(col1 int primary key, col2 int)");
    let t1 = begin(&db);
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 0), (2, 0), (3, 0), (4, 0)");
    for k in 1..=4 {
        expect(&db, &t1, &format!("SELECT * FROM maintable WHERE col1 = {k}"), &[&format!("{k} 0")]);
    }
    commit(&db, &t1);
    let reverify = begin(&db);
    let t2 = begin(&db);
    run(&db, &t2, "DELETE FROM maintable");
    commit(&db, &t2);
    for k in 1..=4 {
        expect(&db, &reverify, &format!("SELECT * FROM maintable WHERE col1 = {k}"), &[&format!("{k} 0")]);
        expect(&db, &begin(&db), &format!("SELECT * FROM maintable WHERE col1 = {k}"), &[]);
    }
}

#[test]
fn s4b_06_aborting_an_insert_keeps_the_entry_and_the_next_insert_reuses_it() {
    let db = new_db();
    ensure_index_scan(&db);
    exec(&db, "CREATE TABLE maintable(a int primary key, b int)");
    let info = table(&db, "maintable");
    let t1 = begin(&db);
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 233), (2, 2333)");
    abort(&db, &t1);
    let t2 = begin(&db);
    run(&db, &t2, "INSERT INTO maintable VALUES (1, 2333), (2, 23333), (3, 233)");
    expect(&db, &t2, "SELECT * FROM maintable", &["1 2333", "2 23333", "3 233"]);
    commit(&db, &t2);
    expect(&db, &begin(&db), "SELECT * FROM maintable", &["1 2333", "2 23333", "3 233"]);
    assert_eq!(heap_entries(&info), 3);
}

#[test]
fn s4b_06_delete_then_insert_in_one_transaction_reuses_the_tuple() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int primary key, b int)");
    let info = table(&db, "maintable");
    let t0 = begin(&db);
    run(&db, &t0, "INSERT INTO maintable VALUES (1, 1)");
    commit(&db, &t0);
    let reader = begin(&db);
    let t = begin(&db);
    run(&db, &t, "DELETE FROM maintable WHERE a = 1");
    run(&db, &t, "INSERT INTO maintable VALUES (1, 2)");
    expect(&db, &t, "SELECT * FROM maintable", &["1 2"]);
    assert_eq!(undo_log_columns(&t), 2, "one log, from the delete");
    commit(&db, &t);
    expect(&db, &reader, "SELECT * FROM maintable", &["1 1"]);
    expect(&db, &begin(&db), "SELECT * FROM maintable", &["1 2"]);
    assert_eq!(heap_entries(&info), 1);
}

// ---- 4b-07: updating a primary key ---------------------------------------------------------------------------------------------------------

#[test]
fn s4b_07_updating_the_key_moves_the_row_to_the_new_key() {
    let db = new_db();
    ensure_index_scan(&db);
    exec(&db, "CREATE TABLE maintable(col1 int primary key, col2 int)");
    let t1 = begin(&db);
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 0), (2, 0), (3, 0), (4, 0)");
    commit(&db, &t1);
    let t2 = begin(&db);
    run(&db, &t2, "UPDATE maintable SET col1 = col1 + 1");
    expect(&db, &t2, "SELECT * FROM maintable", &["2 0", "3 0", "4 0", "5 0"]);
    expect(&db, &t2, "SELECT * FROM maintable WHERE col1 = 1", &[]);
    expect(&db, &t2, "SELECT * FROM maintable WHERE col1 = 5", &["5 0"]);
    commit(&db, &t2);
}

#[test]
fn s4b_07_shifting_every_key_reuses_the_tombstones_it_just_made() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(col1 int primary key, col2 int)");
    let info = table(&db, "maintable");
    let t1 = begin(&db);
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 0), (2, 0), (3, 0), (4, 0)");
    commit(&db, &t1);
    let t2 = begin(&db);
    run(&db, &t2, "UPDATE maintable SET col1 = col1 + 1");
    commit(&db, &t2);
    assert_eq!(heap_entries(&info), 5, "four rows plus one new key");
    let t3 = begin(&db);
    run(&db, &t3, "UPDATE maintable SET col1 = col1 - 2");
    expect(&db, &t3, "SELECT * FROM maintable", &["0 0", "1 0", "2 0", "3 0"]);
    commit(&db, &t3);
    expect(&db, &begin(&db), "SELECT * FROM maintable", &["0 0", "1 0", "2 0", "3 0"]);
}

#[test]
fn s4b_07_older_snapshots_still_see_the_old_keys() {
    let db = new_db();
    ensure_index_scan(&db);
    exec(&db, "CREATE TABLE maintable(col1 int primary key, col2 int)");
    let t1 = begin(&db);
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 0), (2, 0), (3, 0), (4, 0)");
    commit(&db, &t1);
    let old = begin(&db);
    let t2 = begin(&db);
    run(&db, &t2, "UPDATE maintable SET col1 = col1 + 1");
    commit(&db, &t2);
    expect(&db, &old, "SELECT * FROM maintable", &["1 0", "2 0", "3 0", "4 0"]);
    for k in 1..=4 {
        expect(&db, &old, &format!("SELECT * FROM maintable WHERE col1 = {k}"), &[&format!("{k} 0")]);
    }
    expect(&db, &old, "SELECT * FROM maintable WHERE col1 = 5", &[]);
}

#[test]
fn s4b_07_a_non_key_update_of_a_table_with_a_key_stays_in_place() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(col1 int primary key, col2 int)");
    let info = table(&db, "maintable");
    let t1 = begin(&db);
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 0), (2, 0)");
    commit(&db, &t1);
    let t2 = begin(&db);
    run(&db, &t2, "UPDATE maintable SET col2 = col2 + 10");
    assert_eq!(undo_log_num(&t2), 2, "one log per tuple");
    commit(&db, &t2);
    assert_eq!(heap_entries(&info), 2);
    expect(&db, &begin(&db), "SELECT * FROM maintable", &["1 10", "2 10"]);
}

#[test]
fn s4b_07_updating_a_key_onto_an_existing_live_key_fails() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(col1 int primary key, col2 int)");
    let t1 = begin(&db);
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 0), (2, 0)");
    commit(&db, &t1);
    let t2 = begin(&db);
    run_tainted(&db, &t2, "UPDATE maintable SET col1 = 2 WHERE col1 = 1");
}

// ---- 4b-08: serializable -------------------------------------------------------------------------------------------------------------------

#[test]
fn s4b_08_a_serializable_transaction_whose_reads_changed_fails_to_commit() {
    let db = new_db();
    ensure_index_scan(&db);
    exec(&db, "CREATE TABLE maintable(a int, b int primary key)");
    let t1 = db.txn_manager.begin(IsolationLevel::Serializable).unwrap();
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 100), (1, 101), (0, 102), (0, 103)");
    commit(&db, &t1);
    let (t2, t3, t_read) = (begin_serializable(&db), begin_serializable(&db), begin_serializable(&db));
    run(&db, &t2, "UPDATE maintable SET a = 0 WHERE a = 1");
    run(&db, &t3, "UPDATE maintable SET a = 1 WHERE a = 0");
    run(&db, &t_read, "SELECT * FROM maintable WHERE a = 0");
    commit(&db, &t2);
    assert!(!db.txn_manager.commit(&t3).unwrap(), "t3 scanned a = 0, which t2 changed");
    assert_eq!(t3.state(), TransactionState::Aborted);
    commit(&db, &t_read); // read-only: serialised at its read timestamp
}

#[test]
fn s4b_08_a_failed_validation_undoes_the_transactions_writes() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int, b int)");
    let t1 = begin_serializable(&db);
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 1), (0, 2)");
    commit(&db, &t1);
    let (t2, t3) = (begin_serializable(&db), begin_serializable(&db));
    run(&db, &t2, "UPDATE maintable SET a = 0 WHERE a = 1");
    run(&db, &t3, "UPDATE maintable SET a = 1 WHERE a = 0");
    commit(&db, &t2);
    assert!(!db.txn_manager.commit(&t3).unwrap());
    expect(&db, &begin(&db), "SELECT a, b FROM maintable", &["0 1", "0 2"]);
}

#[test]
fn s4b_08_transactions_that_read_different_things_both_commit() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int, b int)");
    let t1 = begin_serializable(&db);
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 1), (0, 2), (5, 3)");
    commit(&db, &t1);
    let (t2, t3) = (begin_serializable(&db), begin_serializable(&db));
    run(&db, &t2, "UPDATE maintable SET b = 10 WHERE a = 1");
    run(&db, &t3, "UPDATE maintable SET b = 20 WHERE a = 5");
    commit(&db, &t2);
    commit(&db, &t3);
}

#[test]
fn s4b_08_snapshot_isolation_does_not_validate() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int, b int)");
    let t1 = begin(&db);
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 1), (0, 2)");
    commit(&db, &t1);
    let (t2, t3) = (begin(&db), begin(&db));
    run(&db, &t2, "UPDATE maintable SET a = 0 WHERE a = 1");
    run(&db, &t3, "UPDATE maintable SET a = 1 WHERE a = 0");
    commit(&db, &t2);
    // different rows, no write-write conflict: write skew is allowed under snapshot isolation
    commit(&db, &t3);
}

#[test]
fn s4b_08_a_full_scan_conflicts_with_any_change_in_the_table() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int, b int)");
    let t1 = begin_serializable(&db);
    run(&db, &t1, "INSERT INTO maintable VALUES (1, 1)");
    commit(&db, &t1);
    exec(&db, "CREATE TABLE other(a int)");
    let (t2, t3) = (begin_serializable(&db), begin_serializable(&db));
    run(&db, &t2, "SELECT * FROM maintable");
    run(&db, &t2, "INSERT INTO other VALUES (1)");
    run(&db, &t3, "INSERT INTO maintable VALUES (2, 2)");
    commit(&db, &t3);
    assert!(!db.txn_manager.commit(&t2).unwrap(), "t2 scanned everything, t3 added a row");
}

#[test]
fn s4b_08_of_two_concurrent_swaps_exactly_one_commits() {
    for _ in 0..10 {
        let db = new_db();
        exec(&db, "CREATE TABLE maintable(a int, b int primary key)");
        let t1 = begin_serializable(&db);
        let values: Vec<String> = (0..100).flat_map(|i| [format!("(1, {})", 1000 + i), format!("(0, {})", 2000 + i)]).collect();
        run(&db, &t1, &format!("INSERT INTO maintable VALUES {}", values.join(", ")));
        commit(&db, &t1);
        let (t2, t3) = (begin_serializable(&db), begin_serializable(&db));
        run(&db, &t3, "UPDATE maintable SET a = 1 WHERE a = 0");
        run(&db, &t2, "UPDATE maintable SET a = 0 WHERE a = 1");
        let db = Arc::new(db);
        let handles: Vec<_> = [t2, t3]
            .into_iter()
            .map(|t| {
                let db = db.clone();
                std::thread::spawn(move || db.txn_manager.commit(&t).unwrap())
            })
            .collect();
        let committed = handles.into_iter().map(|h| h.join().unwrap()).filter(|ok| *ok).count();
        assert_eq!(committed, 1);
    }
}

// ---- 4b-09: BusTub's tests ------------------------------------------------------------------------------------------------------------------

#[test]
fn s4b_09_insert_delete_conflict_test() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int)");
    let q = "SELECT a FROM maintable";
    let txn1 = begin(&db);
    for v in 1..=3 {
        run(&db, &txn1, &format!("INSERT INTO maintable VALUES ({v})"));
    }
    run(&db, &txn1, "DELETE FROM maintable WHERE a = 3");
    expect(&db, &txn1, q, &["1", "2"]);
    commit(&db, &txn1);
    let txn2 = begin(&db);
    expect(&db, &txn2, q, &["1", "2"]);
    run(&db, &txn2, "DELETE FROM maintable WHERE a = 2");
    expect(&db, &txn2, q, &["1"]);
    let txn3 = begin(&db);
    expect(&db, &txn3, q, &["1", "2"]);
    run_tainted(&db, &txn3, "DELETE FROM maintable WHERE a = 2");
    let txn4 = begin(&db);
    expect(&db, &txn4, q, &["1", "2"]);
    for v in 4..=6 {
        run(&db, &txn4, &format!("INSERT INTO maintable VALUES ({v})"));
    }
    run(&db, &txn4, "DELETE FROM maintable WHERE a = 6");
    expect(&db, &txn4, q, &["1", "2", "4", "5"]);
    expect(&db, &txn2, q, &["1"]);
    run(&db, &txn2, "DELETE FROM maintable WHERE a = 5");
    expect(&db, &txn2, q, &["1"]);
    commit(&db, &txn2);
    commit(&db, &txn4);
    let txn5 = begin(&db);
    expect(&db, &txn5, q, &["1", "4", "5"]);
    let txn6 = begin(&db);
    run(&db, &txn6, "DELETE FROM maintable WHERE a = 5");
    commit(&db, &txn6);
    run_tainted(&db, &txn5, "DELETE FROM maintable WHERE a = 5");
    let txn7 = begin(&db);
    expect(&db, &txn7, q, &["1", "4"]);
    run(&db, &txn7, "DELETE FROM maintable");
    expect(&db, &txn7, q, &[]);
    commit(&db, &txn7);
}

#[test]
fn s4b_09_garbage_collection() {
    let db = new_db();
    exec(&db, "CREATE TABLE table1(a int, b int, c int)");
    let q = "SELECT * FROM table1";
    let all0 = ["0 0 0", "1 1 1", "2 2 2", "3 3 3"];
    let all10 = ["10 0 0", "11 1 1", "12 2 2", "13 3 3"];
    let after3 = ["20 0 0", "12 2 2", "13 3 3"];
    let w0 = begin(&db);
    bump_commit_ts(&db, 2);
    let txn_a = begin(&db);
    run(&db, &txn_a, "INSERT INTO table1 VALUES (0, 0, 0), (1, 1, 1)");
    commit(&db, &txn_a);
    let txn_b = begin(&db);
    run(&db, &txn_b, "INSERT INTO table1 VALUES (2, 2, 2), (3, 3, 3)");
    commit(&db, &txn_b);
    bump_commit_ts(&db, 2);
    let w1 = begin(&db);
    bump_commit_ts(&db, 2);
    let txn2 = begin(&db);
    run(&db, &txn2, "UPDATE table1 SET a = a + 10");
    expect(&db, &txn2, q, &all10);
    commit(&db, &txn2);
    bump_commit_ts(&db, 2);
    let w2 = begin(&db);
    bump_commit_ts(&db, 2);
    let txn3 = begin(&db);
    run(&db, &txn3, "UPDATE table1 SET a = a + 10 WHERE a < 12");
    run(&db, &txn3, "DELETE FROM table1 WHERE a = 21");
    expect(&db, &txn3, q, &after3);
    commit(&db, &txn3);
    bump_commit_ts(&db, 2);
    let w3 = begin(&db);
    bump_commit_ts(&db, 2);

    expect(&db, &w0, q, &[]);
    expect(&db, &w1, q, &all0);
    expect(&db, &w2, q, &all10);
    expect(&db, &w3, q, &after3);

    // A, B: two collections with every watermark transaction still running
    db.txn_manager.garbage_collection();
    db.txn_manager.garbage_collection();
    for w in [&w0, &w1, &w2, &w3, &txn2, &txn3] {
        assert!(txn_exists(&db, w), "txn{} should exist", w.human_readable_id());
    }
    assert!(!txn_exists(&db, &txn_a) && !txn_exists(&db, &txn_b));
    expect(&db, &w0, q, &[]);
    expect(&db, &w1, q, &all0);
    expect(&db, &w2, q, &all10);
    expect(&db, &w3, q, &after3);

    // C: the oldest reader finishes
    commit(&db, &w0);
    db.txn_manager.garbage_collection();
    assert!(!txn_exists(&db, &w0));
    for w in [&w1, &w2, &w3, &txn2, &txn3] {
        assert!(txn_exists(&db, w));
    }
    expect(&db, &w1, q, &all0);
    expect(&db, &w2, q, &all10);
    expect(&db, &w3, q, &after3);

    // D: the next one; txn2's logs are older than anything w2 can ask for
    commit(&db, &w1);
    db.txn_manager.garbage_collection();
    assert!(!txn_exists(&db, &w1) && !txn_exists(&db, &txn2));
    assert!(txn_exists(&db, &w2) && txn_exists(&db, &w3) && txn_exists(&db, &txn3));
    expect(&db, &w2, q, &all10);
    expect(&db, &w3, q, &after3);

    // E
    commit(&db, &w2);
    db.txn_manager.garbage_collection();
    assert!(!txn_exists(&db, &w2) && !txn_exists(&db, &txn3));
    assert!(txn_exists(&db, &w3));
    expect(&db, &w3, q, &after3);

    // F: nobody is left
    commit(&db, &w3);
    db.txn_manager.garbage_collection();
    for t in [&w0, &w1, &w2, &w3, &txn_a, &txn_b, &txn2, &txn3] {
        assert!(!txn_exists(&db, t), "txn{} should be collected", t.human_readable_id());
    }
}

#[test]
fn s4b_09_garbage_collection_with_tainted_transactions() {
    let db = new_db();
    exec(&db, "CREATE TABLE table1(a int, b int, c int)");
    let q = "SELECT * FROM table1";
    let all0 = ["0 0 0", "1 1 1", "2 2 2", "3 3 3"];
    let all10 = ["10 0 0", "11 1 1", "12 2 2", "13 3 3"];
    let after3 = ["20 0 0", "12 2 2", "13 3 3"];
    let w0 = begin(&db);
    bump_commit_ts(&db, 2);
    let txn_a = begin(&db);
    run(&db, &txn_a, "INSERT INTO table1 VALUES (0, 0, 0), (1, 1, 1)");
    commit(&db, &txn_a);
    let txn_b = begin(&db);
    run(&db, &txn_b, "INSERT INTO table1 VALUES (2, 2, 2), (3, 3, 3)");
    commit(&db, &txn_b);
    bump_commit_ts(&db, 2);
    let w1 = begin(&db);
    bump_commit_ts(&db, 2);
    let txn2 = begin(&db);
    run(&db, &txn2, "UPDATE table1 SET a = a + 10");
    commit(&db, &txn2);
    bump_commit_ts(&db, 2);
    let w2 = begin(&db);
    bump_commit_ts(&db, 2);
    let txn3 = begin(&db);
    run(&db, &txn3, "UPDATE table1 SET a = a + 10 WHERE a < 12");
    run(&db, &txn3, "DELETE FROM table1 WHERE a = 21");
    let (txn5, txn6) = (begin(&db), begin(&db));
    commit(&db, &txn3);
    bump_commit_ts(&db, 2);
    let w3 = begin(&db);
    bump_commit_ts(&db, 2);

    db.txn_manager.garbage_collection();
    db.txn_manager.garbage_collection();
    assert!(txn_exists(&db, &txn2) && txn_exists(&db, &txn3) && txn_exists(&db, &txn5));
    assert!(!txn_exists(&db, &txn_a) && !txn_exists(&db, &txn_b));

    // C: txn5 and txn6 conflict with the committed deletes and become tainted; they keep the watermark low
    run(&db, &txn5, "DELETE FROM table1 WHERE a = 12");
    run_tainted(&db, &txn5, "DELETE FROM table1 WHERE a = 11");
    run_tainted(&db, &txn6, "DELETE FROM table1 WHERE a = 11");
    db.txn_manager.garbage_collection();
    for t in [&w0, &w1, &w2, &w3, &txn2, &txn3, &txn5, &txn6] {
        assert!(txn_exists(&db, t), "txn{} should exist", t.human_readable_id());
    }
    expect(&db, &w0, q, &[]);
    expect(&db, &w1, q, &all0);
    expect(&db, &w2, q, &all10);
    expect(&db, &w3, q, &after3);

    // D, E, F, G: the watermark transactions finish one by one; txn5 and txn6 (still tainted) hold txn3 and everything it needs
    commit(&db, &w0);
    db.txn_manager.garbage_collection();
    assert!(!txn_exists(&db, &w0) && txn_exists(&db, &txn2) && txn_exists(&db, &txn3));
    commit(&db, &w1);
    db.txn_manager.garbage_collection();
    assert!(!txn_exists(&db, &w1) && !txn_exists(&db, &txn2));
    expect(&db, &w2, q, &all10);
    commit(&db, &w2);
    db.txn_manager.garbage_collection();
    assert!(!txn_exists(&db, &w2) && txn_exists(&db, &txn3) && txn_exists(&db, &txn5) && txn_exists(&db, &txn6));
    commit(&db, &w3);
    db.txn_manager.garbage_collection();
    assert!(!txn_exists(&db, &w3));
    assert!(txn_exists(&db, &txn3) && txn_exists(&db, &txn5) && txn_exists(&db, &txn6), "the tainted transactions still run");
}

#[test]
fn s4b_09_index_update_conflict_test() {
    let db = new_db();
    ensure_index_scan(&db);
    exec(&db, "CREATE TABLE maintable(col1 int primary key, col2 int)");
    let txn1 = begin(&db);
    run(&db, &txn1, "INSERT INTO maintable VALUES (1, 0), (2, 0), (3, 0)");
    run(&db, &txn1, "DELETE FROM maintable WHERE col1 = 2");
    commit(&db, &txn1);
    let (txn2, txn3) = (begin(&db), begin(&db));
    run(&db, &txn2, "INSERT INTO maintable VALUES (4, 0)");
    run(&db, &txn2, "DELETE FROM maintable WHERE col1 = 1");
    run(&db, &txn2, "DELETE FROM maintable WHERE col1 = 3");
    commit(&db, &txn2);
    run_tainted(&db, &txn3, "UPDATE maintable SET col2 = 2 WHERE col1 = 1");
}

#[test]
fn s4b_09_index_concurrent_insert_test() {
    for _ in 0..10 {
        let db = Arc::new(new_db());
        exec(&db, "CREATE TABLE maintable(a int primary key, b int)");
        let (threads, numbers) = (8usize, 40usize);
        let handles: Vec<_> = (0..threads)
            .map(|thread| {
                let db = db.clone();
                std::thread::spawn(move || {
                    let mut won = vec![];
                    for n in 0..numbers {
                        let txn = begin(&db);
                        let mut out = String::new();
                        if db.execute_sql_txn(&format!("INSERT INTO maintable VALUES ({n}, {thread})"), &mut SimpleStreamWriter::new(&mut out, true, " "), &txn).unwrap() {
                            assert!(db.txn_manager.commit(&txn).unwrap(), "cannot commit??");
                            won.push(true);
                        } else {
                            won.push(false);
                        }
                    }
                    won
                })
            })
            .collect();
        let results: Vec<Vec<bool>> = handles.into_iter().map(|h| h.join().unwrap()).collect();
        let mut expected = vec![];
        for n in 0..numbers {
            let winners: Vec<usize> = (0..threads).filter(|t| results[*t][n]).collect();
            assert_eq!(winners.len(), 1, "exactly one thread inserts {n}: {winners:?}");
            expected.push(format!("{n} {}", winners[0]));
        }
        let query = begin(&db);
        let mut want = expected;
        want.sort();
        assert_eq!(rows(&db, &query, "SELECT * FROM maintable"), want);
    }
}

#[test]
fn s4b_09_index_concurrent_update_test() {
    for trial in 0..10 {
        let db = Arc::new(new_db());
        ensure_index_scan(&db);
        exec(&db, "CREATE TABLE maintable(a int primary key, b int)");
        let (threads, numbers) = (8usize, 20usize);
        let values: Vec<String> = (0..numbers).map(|i| format!("({i}, 0)")).collect();
        exec(&db, &format!("INSERT INTO maintable VALUES {}", values.join(",")));
        let table_info = table(&db, "maintable");
        assert!(heap_entries(&table_info) <= numbers);
        let add_delete_insert = trial % 2 == 1;
        let handles: Vec<_> = (0..threads)
            .map(|thread| {
                let db = db.clone();
                std::thread::spawn(move || {
                    let mut won = vec![];
                    for i in 0..numbers {
                        let txn = begin(&db);
                        let mut out = String::new();
                        let mut w = SimpleStreamWriter::new(&mut out, true, " ");
                        if !db.execute_sql_txn(&format!("UPDATE maintable SET b = b + {} WHERE a = {i}", 1 << thread), &mut w, &txn).unwrap() {
                            won.push(false);
                            continue;
                        }
                        if add_delete_insert {
                            let mut out = String::new();
                            assert!(db.execute_sql_txn(&format!("SELECT b FROM maintable WHERE a = {i}"), &mut SimpleStreamWriter::new(&mut out, true, " "), &txn).unwrap());
                            let b: i32 = out.trim().parse().expect("one row with b");
                            let mut sink = String::new();
                            assert!(db.execute_sql_txn(&format!("DELETE FROM maintable WHERE a = {i}"), &mut SimpleStreamWriter::new(&mut sink, true, " "), &txn).unwrap());
                            assert!(db.execute_sql_txn(&format!("INSERT INTO maintable VALUES ({i}, {b})"), &mut SimpleStreamWriter::new(&mut sink, true, " "), &txn).unwrap());
                        }
                        assert!(db.txn_manager.commit(&txn).unwrap(), "cannot commit??");
                        won.push(true);
                    }
                    won
                })
            })
            .collect();
        let results: Vec<Vec<bool>> = handles.into_iter().map(|h| h.join().unwrap()).collect();
        let mut want: Vec<String> = (0..numbers).map(|i| format!("{i} {}", (0..threads).filter(|j| results[*j][i]).map(|j| 1 << j).sum::<i32>())).collect();
        want.sort();
        let query = begin(&db);
        assert_eq!(rows(&db, &query, "SELECT * FROM maintable"), want);
        assert!(heap_entries(&table_info) <= numbers, "updates and delete + insert reuse their tuples");
    }
}

#[test]
fn s4b_09_index_concurrent_update_abort_test() {
    for _ in 0..5 {
        let db = Arc::new(new_db());
        ensure_index_scan(&db);
        exec(&db, "CREATE TABLE maintable(a int primary key, b int)");
        let (threads, numbers, operations) = (8usize, 5usize, 60usize);
        let values: Vec<String> = (0..numbers).map(|i| format!("({i}, 0)")).collect();
        exec(&db, &format!("INSERT INTO maintable VALUES {}", values.join(",")));
        let handles: Vec<_> = (0..threads)
            .map(|seed| {
                let db = db.clone();
                std::thread::spawn(move || {
                    let mut counts = vec![0i32; numbers];
                    let mut state = 0x9E37_79B9_7F4A_7C15u64 ^ (seed as u64 + 1).wrapping_mul(0xA24B_AED4_963E_E407);
                    let mut next = move || {
                        state ^= state << 13;
                        state ^= state >> 7;
                        state ^= state << 17;
                        state
                    };
                    for _ in 0..operations {
                        let (x, mut y) = ((next() % numbers as u64) as usize, (next() % numbers as u64) as usize);
                        while y == x {
                            y = (next() % numbers as u64) as usize;
                        }
                        let txn = begin(&db);
                        let mut sink = String::new();
                        let ok = [x, y].iter().all(|n| db.execute_sql_txn(&format!("UPDATE maintable SET b = b + 1 WHERE a = {n}"), &mut SimpleStreamWriter::new(&mut sink, true, " "), &txn).unwrap());
                        if !ok {
                            db.txn_manager.abort(&txn).unwrap();
                            std::thread::sleep(std::time::Duration::from_millis(1));
                            continue;
                        }
                        assert!(db.txn_manager.commit(&txn).unwrap(), "cannot commit??");
                        counts[x] += 1;
                        counts[y] += 1;
                    }
                    counts
                })
            })
            .collect();
        let results: Vec<Vec<i32>> = handles.into_iter().map(|h| h.join().unwrap()).collect();
        let mut want: Vec<String> = (0..numbers).map(|i| format!("{i} {}", results.iter().map(|c| c[i]).sum::<i32>())).collect();
        want.sort();
        let query = begin(&db);
        assert_eq!(rows(&db, &query, "SELECT * FROM maintable"), want, "every committed increment is there, no aborted one is");
        assert!(heap_entries(&table(&db, "maintable")) <= numbers);
    }
}

#[test]
fn s4b_09_simple_abort_with_ordered_queries_and_a_duplicate_heavy_commit() {
    let db = new_db();
    exec(&db, "CREATE TABLE maintable(a int, b int)");
    let q = "SELECT a, b FROM maintable ORDER BY a, b";
    let txn2 = begin(&db);
    run(&db, &txn2, "INSERT INTO maintable VALUES (1,10), (2,200), (3,300)");
    commit(&db, &txn2);
    let txn3 = begin(&db);
    run(&db, &txn3, "UPDATE maintable SET b = 0 WHERE a >= 2");
    abort(&db, &txn3);
    let txn4 = begin(&db);
    run(&db, &txn4, "DELETE FROM maintable");
    abort(&db, &txn4);
    let txn5 = begin(&db);
    run(&db, &txn5, "INSERT INTO maintable VALUES (1,999), (1,1000)");
    run(&db, &txn5, "UPDATE maintable SET b = b + 1 WHERE a = 3");
    let (_, out) = try_run(&db, &txn5, q);
    assert_eq!(out.lines().map(|l| l.trim_end()).collect::<Vec<_>>(), vec!["1 10", "1 999", "1 1000", "2 200", "3 301"]);
    commit(&db, &txn5);
    let fin = begin(&db);
    let (_, out) = try_run(&db, &fin, q);
    assert_eq!(out.lines().map(|l| l.trim_end()).collect::<Vec<_>>(), vec!["1 10", "1 999", "1 1000", "2 200", "3 301"]);
}
