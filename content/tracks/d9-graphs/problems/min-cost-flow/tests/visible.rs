use solution::*;

#[test]
fn two_units() {
    check!(r#"n = 4, edges = [(0,1,2,1), (0,2,1,2), (1,2,1,1), (1,3,1,3), (2,3,2,1)], want = 2"#, min_cost_flow(4, &[(0, 1, 2, 1), (0, 2, 1, 2), (1, 2, 1, 1), (1, 3, 1, 3), (2, 3, 2, 1)], 0, 3, 2), Some(6));
}

#[test]
fn too_much() {
    check!(r#"same network, want = 4"#, min_cost_flow(4, &[(0, 1, 2, 1), (0, 2, 1, 2), (1, 2, 1, 1), (1, 3, 1, 3), (2, 3, 2, 1)], 0, 3, 4), None);
}
