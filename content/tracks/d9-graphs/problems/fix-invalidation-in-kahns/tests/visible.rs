use solution::*;

#[test]
fn chain() {
    check!(r#"n = 3, edges = [(0, 1), (1, 2)]"#, topo_order(3, &[(0, 1), (1, 2)]), Some(vec![0, 1, 2]));
}

#[test]
fn join() {
    check!(r#"n = 4, edges = [(0, 2), (1, 2), (2, 3)]"#, topo_order(4, &[(0, 2), (1, 2), (2, 3)]), Some(vec![0, 1, 2, 3]));
}
