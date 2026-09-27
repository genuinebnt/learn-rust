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

#[test]
fn node_without_edges() {
    let g = Csr::from_edges(3, &[(1, 2), (0, 1), (1, 0)]);
    check!(r#"n = 3, edges = [(1, 2), (0, 1), (1, 0)]; neighbors(2)"#, g.neighbors(2), &[]);
}

#[test]
fn targets_keep_input_order() {
    let g = Csr::from_edges(2, &[(0, 1), (0, 0), (0, 1)]);
    check!(r#"n = 2, edges = [(0, 1), (0, 0), (0, 1)]; neighbors(0)"#, g.neighbors(0), &[1, 0, 1]);
}

#[test]
fn empty_graph() {
    let g = Csr::from_edges(0, &[]);
    check!(r#"n = 0, edges = []; parts()"#, g.parts(), (&[0][..], &[][..]));
}
