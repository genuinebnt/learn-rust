use solution::*;

#[test]
fn cycle() {
    check!(r#"n = 3, edges = [(0, 1), (1, 2), (2, 1)]"#, topo_order(3, &[(0, 1), (1, 2), (2, 1)]), None);
}

#[test]
fn fifo() {
    check!(r#"n = 4, edges = [(0, 3), (1, 2)]"#, topo_order(4, &[(0, 3), (1, 2)]), Some(vec![0, 1, 3, 2]));
}
