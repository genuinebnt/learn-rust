use solution::*;

#[test]
fn layout() {
    let g = Csr::from_edges(3, &[(1, 2), (0, 1), (1, 0)]);
    check!(r#"n = 3, edges = [(1, 2), (0, 1), (1, 0)]"#, g.parts(), (&[0, 1, 3, 3][..], &[1, 2, 0][..]));
}

#[test]
fn neighbours() {
    let g = Csr::from_edges(3, &[(1, 2), (0, 1), (1, 0)]);
    check!(r#"n = 3, edges = [(1, 2), (0, 1), (1, 0)]; neighbors(1)"#, g.neighbors(1), &[2, 0]);
}
