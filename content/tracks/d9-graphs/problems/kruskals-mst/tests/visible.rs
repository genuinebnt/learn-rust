use solution::*;

#[test]
fn seven() {
    check!(r#"n = 4, edges = [(0,1,1), (1,2,2), (0,2,3), (2,3,4), (1,3,5)]"#, mst_weight(4, &[(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 4), (1, 3, 5)]), Some(7));
}

#[test]
fn disconnected() {
    check!(r#"n = 3, edges = [(0,1,1)]"#, mst_weight(3, &[(0, 1, 1)]), None);
}
