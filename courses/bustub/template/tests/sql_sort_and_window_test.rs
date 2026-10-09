//! BusTub's SQL tests for sorting, limits and window functions (`test/sql/p3.16`, `p3.18` to `p3.20`). `p3.16` also asks for hash joins and
//! `p3.17` for top-N plans; both need optimizer rules of module 3h, so here the `+ensure:hash_join` checks are skipped.

mod slt;

#[test]
fn p3_16_sort_limit() {
    slt::run_slt_skipping("p3.16-sort-limit.slt", 128, &["hash_join"]);
}

#[test]
fn p3_18_integration_1() {
    slt::run_slt("p3.18-integration-1.slt", 128);
}

#[test]
fn p3_19_integration_2() {
    slt::run_slt("p3.19-integration-2.slt", 128);
}

#[test]
fn p3_20_window_function() {
    slt::run_slt("p3.20-window-function.slt", 128);
}
