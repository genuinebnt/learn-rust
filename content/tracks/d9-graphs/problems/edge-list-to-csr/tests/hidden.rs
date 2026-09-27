use solution::*;

#[test]
fn empty_node() {
    let g = Csr::from_edges(2, &[(1, 0)]);
    check!(r#"n = 2, edges = [(1, 0)]; neighbors(0)"#, g.neighbors(0).is_empty(), true);
}

#[test]
fn no_nodes() {
    let g = Csr::from_edges(0, &[]);
    check!(r#"n = 0, edges = []"#, g.parts(), (&[0][..], &[][..]));
}

#[test]
fn million_edges() {
    let edges: Vec<(usize, usize)> = (0..1_000_000).map(|i| (i % 1000, i / 1000)).collect();
    let g = Csr::from_edges(1000, &edges);
    check!(r#"n = 1000, 10⁶ edges"#, (g.neighbors(999).len(), g.parts().1.len()), (1000, 1_000_000));
}
