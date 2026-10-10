//! BusTub's SQL tests for aggregation and joins (`test/sql/p3.07` to `p3.13`). The hash join tests (`p3.14`, `p3.15`) need the optimizer rule
//! of module 3h.

mod slt;

#[test]
fn p3_07_simple_agg() {
    slt::run_slt("p3.07-simple-agg.slt", 128);
}

#[test]
fn p3_08_group_agg_1() {
    slt::run_slt("p3.08-group-agg-1.slt", 128);
}

#[test]
fn p3_09_group_agg_2() {
    slt::run_slt("p3.09-group-agg-2.slt", 128);
}

#[test]
fn p3_10_simple_join() {
    slt::run_slt("p3.10-simple-join.slt", 128);
}

#[test]
fn p3_11_multi_way_join() {
    slt::run_slt("p3.11-multi-way-join.slt", 128);
}

#[test]
fn p3_12_repeat_execute() {
    slt::run_slt("p3.12-repeat-execute.slt", 128);
}

#[test]
fn p3_13_nested_index_join() {
    slt::run_slt("p3.13-nested-index-join.slt", 128);
}
