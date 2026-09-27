use solution::*;

#[test]
fn triangle() {
    check!(r#"n = 3, edges = [(0, 1), (0, 2), (1, 2)]"#, (degrees(3, &[(0, 1), (0, 2), (1, 2)]), sources(3, &[(0, 1), (0, 2), (1, 2)])), (vec![(0, 2), (1, 1), (2, 0)], vec![0]));
}

#[test]
fn isolated() {
    check!(r#"n = 2, edges = []"#, (degrees(2, &[]), sources(2, &[])), (vec![(0, 0), (0, 0)], vec![0, 1]));
}
