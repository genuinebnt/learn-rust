use solution::*;

#[test]
fn parallel_edges() {
    check!(r#"n = 2, edges = [(0,1), (1,0)]"#, critical_connections(2, &[(0, 1), (1, 0)]), Vec::<(usize, usize)>::new());
}

#[test]
fn two_triangles() {
    check!(r#"triangles 0-1-2 and 3-4-5 joined by 2-3"#, critical_connections(6, &[(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (2, 3)]), vec![(2, 3)]);
}

#[test]
fn path() {
    check!(r#"n = 4, path 0-1-2-3"#, critical_connections(4, &[(0, 1), (1, 2), (2, 3)]), vec![(0, 1), (1, 2), (2, 3)]);
}
