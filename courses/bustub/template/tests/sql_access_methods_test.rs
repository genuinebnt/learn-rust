//! BusTub's SQL tests for the access-method executors: scans, inserts, updates and deletes (`test/sql/p3.00` to `p3.04`).
//! `p3.05` and `p3.06` (index scans) also need the optimizer rule of module 3h.

mod slt;

#[test]
fn p3_00_primer() {
    slt::run_slt("p3.00-primer.slt", 128);
}

#[test]
fn p3_01_seqscan() {
    slt::run_slt("p3.01-seqscan.slt", 128);
}

#[test]
fn p3_02_insert() {
    slt::run_slt("p3.02-insert.slt", 128);
}

#[test]
fn p3_03_update() {
    slt::run_slt("p3.03-update.slt", 128);
}

#[test]
fn p3_04_delete() {
    slt::run_slt("p3.04-delete.slt", 128);
}
