use solution::*;

#[test]
fn leetcode_example() {
    check!(r#"points = [(0,0), (2,2), (3,10), (5,2), (7,0)]"#, min_cost_connect_points(&[(0, 0), (2, 2), (3, 10), (5, 2), (7, 0)]), 20);
}

#[test]
fn negative_coordinates() {
    check!(r#"points = [(3,12), (-2,5), (-4,1)]"#, min_cost_connect_points(&[(3, 12), (-2, 5), (-4, 1)]), 18);
}

#[test]
fn one_point() {
    check!(r#"points = [(0,0)]"#, min_cost_connect_points(&[(0, 0)]), 0);
}

#[test]
fn two_points() {
    check!(r#"points = [(1,1), (4,-3)]"#, min_cost_connect_points(&[(1, 1), (4, -3)]), 7);
}

#[test]
fn not_a_chain_in_input_order() {
    check!(r#"points = [(0,0), (10,0), (1,0)]"#, min_cost_connect_points(&[(0, 0), (10, 0), (1, 0)]), 10);
}
