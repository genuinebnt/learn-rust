use solution::*;

#[test]
fn three_units() {
    check!(r#"same network, want = 3"#, min_cost_flow(4, &[(0, 1, 2, 1), (0, 2, 1, 2), (1, 2, 1, 1), (1, 3, 1, 3), (2, 3, 2, 1)], 0, 3, 3), Some(10));
}

#[test]
fn nothing() {
    check!(r#"want = 0"#, min_cost_flow(2, &[], 0, 1, 0), Some(0));
}

#[test]
fn reroute() {
    check!(r#"greedy first path must be partly undone"#, min_cost_flow(4, &[(0, 1, 1, 1), (0, 2, 1, 5), (1, 2, 1, 1), (1, 3, 1, 5), (2, 3, 1, 1)], 0, 3, 2), Some(12));
}
