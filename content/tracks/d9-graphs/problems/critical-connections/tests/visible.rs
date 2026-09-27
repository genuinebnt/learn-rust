use solution::*;

#[test]
fn one_bridge() {
    check!(r#"n = 4, edges = [(0,1), (1,2), (2,0), (1,3)]"#, critical_connections(4, &[(0, 1), (1, 2), (2, 0), (1, 3)]), vec![(1, 3)]);
}

#[test]
fn single_edge() {
    check!(r#"n = 2, edges = [(1,0)]"#, critical_connections(2, &[(1, 0)]), vec![(0, 1)]);
}
