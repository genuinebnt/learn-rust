use solution::*;

#[test]
fn two_units() {
    check!(r#"n = 4, edges = [(0,1,2,1), (0,2,1,2), (1,2,1,1), (1,3,1,3), (2,3,2,1)], want = 2"#, min_cost_flow(4, &[(0, 1, 2, 1), (0, 2, 1, 2), (1, 2, 1, 1), (1, 3, 1, 3), (2, 3, 2, 1)], 0, 3, 2), Some(6));
}

#[test]
fn too_much() {
    check!(r#"same network, want = 4"#, min_cost_flow(4, &[(0, 1, 2, 1), (0, 2, 1, 2), (1, 2, 1, 1), (1, 3, 1, 3), (2, 3, 2, 1)], 0, 3, 4), None);
}

#[test]
fn one_unit() {
    check!(r#"same network, want = 1"#, min_cost_flow(4, &[(0, 1, 2, 1), (0, 2, 1, 2), (1, 2, 1, 1), (1, 3, 1, 3), (2, 3, 2, 1)], 0, 3, 1), Some(3));
}

#[test]
fn nothing_wanted() {
    check!(r#"n = 3, edges = [], want = 0"#, min_cost_flow(3, &[], 0, 2, 0), Some(0));
}

#[test]
fn cheap_edge_fills_first() {
    check!(r#"n = 2, edges = [(0,1,1,5), (0,1,2,3)], want = 3"#, min_cost_flow(2, &[(0, 1, 1, 5), (0, 1, 2, 3)], 0, 1, 3), Some(11));
}
