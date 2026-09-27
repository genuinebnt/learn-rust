use solution::*;

#[test]
fn seven() {
    check!(r#"n = 4, edges = [(0,1,1), (1,2,2), (0,2,3), (2,3,4), (1,3,5)]"#, mst_weight(4, &[(0, 1, 1), (1, 2, 2), (0, 2, 3), (2, 3, 4), (1, 3, 5)]), Some(7));
}

#[test]
fn disconnected() {
    check!(r#"n = 3, edges = [(0,1,1)]"#, mst_weight(3, &[(0, 1, 1)]), None);
}

#[test]
fn skip_the_heaviest_triangle_edge() {
    check!(r#"n = 3, edges = [(0,1,5), (1,2,1), (0,2,2)]"#, mst_weight(3, &[(0, 1, 5), (1, 2, 1), (0, 2, 2)]), Some(3));
}

#[test]
fn self_loop_ignored() {
    check!(r#"n = 2, edges = [(0,0,1), (0,1,7)]"#, mst_weight(2, &[(0, 0, 1), (0, 1, 7)]), Some(7));
}

#[test]
fn equal_weights() {
    check!(r#"n = 3, edges = [(0,1,2), (1,2,2), (0,2,2)]"#, mst_weight(3, &[(0, 1, 2), (1, 2, 2), (0, 2, 2)]), Some(4));
}
