use solution::*;

#[test]
fn chain() {
    check!(r#"n = 3, edges = [(0, 1), (1, 2)]"#, topo_order(3, &[(0, 1), (1, 2)]), Some(vec![0, 1, 2]));
}

#[test]
fn join() {
    check!(r#"n = 4, edges = [(0, 2), (1, 2), (2, 3)]"#, topo_order(4, &[(0, 2), (1, 2), (2, 3)]), Some(vec![0, 1, 2, 3]));
}

#[test]
fn single() {
    check!(r#"n = 1, edges = []"#, topo_order(1, &[]), Some(vec![0]));
}

#[test]
fn two_cycle() {
    check!(r#"n = 2, edges = [(0, 1), (1, 0)]"#, topo_order(2, &[(0, 1), (1, 0)]), None);
}

#[test]
fn processed_in_ready_order() {
    check!(r#"n = 5, edges = [(0, 4), (1, 2), (2, 3)]"#, topo_order(5, &[(0, 4), (1, 2), (2, 3)]), Some(vec![0, 1, 4, 2, 3]));
}
