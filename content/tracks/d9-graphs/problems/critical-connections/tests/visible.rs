use solution::*;

#[test]
fn one_bridge() {
    check!(r#"n = 4, edges = [(0,1), (1,2), (2,0), (1,3)]"#, critical_connections(4, &[(0, 1), (1, 2), (2, 0), (1, 3)]), vec![(1, 3)]);
}

#[test]
fn single_edge() {
    check!(r#"n = 2, edges = [(1,0)]"#, critical_connections(2, &[(1, 0)]), vec![(0, 1)]);
}

#[test]
fn cycle_has_no_bridges() {
    check!(r#"n = 3, edges = [(0,1), (1,2), (2,0)]"#, critical_connections(3, &[(0, 1), (1, 2), (2, 0)]), Vec::<(usize, usize)>::new());
}

#[test]
fn sorted_smaller_first() {
    check!(r#"n = 3, edges = [(2,1), (1,0)]"#, critical_connections(3, &[(2, 1), (1, 0)]), vec![(0, 1), (1, 2)]);
}

#[test]
fn doubled_edge_is_not_a_bridge() {
    check!(r#"n = 3, edges = [(0,1), (1,0), (1,2)]"#, critical_connections(3, &[(0, 1), (1, 0), (1, 2)]), vec![(1, 2)]);
}
