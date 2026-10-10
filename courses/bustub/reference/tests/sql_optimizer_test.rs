//! BusTub's SQL tests that check the optimizer's plans with `+ensure:` (`test/sql/p3.05`, `p3.06`, `p3.14`, `p3.15`, `p3.16`, `p3.17`) and
//! four small ones that run `explain` and the query on joins and indexes (`hash_join`, `order_by`, `nested_index_join`, `update`).

mod slt;

#[test]
fn p3_05_index_scan_btree() {
    slt::run_slt("p3.05-index-scan-btree.slt", 128);
}

#[test]
fn p3_06_empty_table() {
    slt::run_slt("p3.06-empty-table.slt", 128);
}

#[test]
fn p3_14_hash_join() {
    slt::run_slt("p3.14-hash-join.slt", 128);
}

#[test]
fn p3_15_multi_way_hash_join() {
    slt::run_slt("p3.15-multi-way-hash-join.slt", 128);
}

#[test]
fn p3_16_sort_limit_with_its_hash_joins() {
    slt::run_slt("p3.16-sort-limit.slt", 128);
}

#[test]
fn p3_17_topn() {
    slt::run_slt("p3.17-topn.slt", 128);
}

#[test]
fn small_plans_hash_join_order_by_nested_index_join_and_update() {
    for file in ["hash_join.slt", "order_by.slt", "nested_index_join.slt", "update.slt"] {
        slt::run_slt(file, 128);
    }
}
