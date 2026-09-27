use solution::*;

#[test]
fn leetcode_three() {
    check!(r#"costs = [[17, 2, 17], [16, 16, 5], [14, 3, 19]]"#, min_cost(&[[17, 2, 17], [16, 16, 5], [14, 3, 19]]), 10);
}

#[test]
fn leetcode_one() {
    check!(r#"costs = [[7, 6, 2]]"#, min_cost(&[[7, 6, 2]]), 2);
}

#[test]
fn no_houses() {
    check!(r#"costs = []"#, min_cost(&[]), 0);
}

#[test]
fn neighbours_differ() {
    check!(r#"costs = [[1, 2, 3], [1, 2, 3]]"#, min_cost(&[[1, 2, 3], [1, 2, 3]]), 3);
}

#[test]
fn cheapest_first_is_a_trap() {
    check!(r#"costs = [[1, 100, 100], [1, 100, 100], [100, 1, 100]]"#, min_cost(&[[1, 100, 100], [1, 100, 100], [100, 1, 100]]), 102);
}
