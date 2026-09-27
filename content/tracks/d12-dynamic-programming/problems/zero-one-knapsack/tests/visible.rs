use solution::*;

#[test]
fn four_items() {
    check!(r#"items = [(1, 1), (3, 4), (4, 5), (5, 7)], capacity = 7"#, knapsack(&[(1, 1), (3, 4), (4, 5), (5, 7)], 7), 9);
}

#[test]
fn no_items() {
    check!(r#"items = [], capacity = 10"#, knapsack(&[], 10), 0);
}

#[test]
fn no_capacity() {
    check!(r#"items = [(1, 1)], capacity = 0"#, knapsack(&[(1, 1)], 0), 0);
}

#[test]
fn each_item_once() {
    check!(r#"items = [(1, 10)], capacity = 5"#, knapsack(&[(1, 10)], 5), 10);
}

#[test]
fn best_ratio_is_a_trap() {
    check!(r#"items = [(10, 60), (20, 100), (30, 120)], capacity = 50"#, knapsack(&[(10, 60), (20, 100), (30, 120)], 50), 220);
}
