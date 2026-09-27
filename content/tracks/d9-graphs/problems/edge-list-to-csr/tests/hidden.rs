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

#[test]
fn no_edges() {
    let g = Csr::from_edges(3, &[]);
    check!(r#"n = 3, edges = []"#, g.parts(), (&[0, 0, 0, 0][..], &[][..]));
}

#[test]
fn all_from_last() {
    let g = Csr::from_edges(3, &[(2, 0), (2, 1), (2, 2)]);
    check!(r#"n = 3, edges = [(2, 0), (2, 1), (2, 2)]"#, g.parts(), (&[0, 0, 0, 3][..], &[0, 1, 2][..]));
}

#[test]
fn input_order_kept() {
    let g = Csr::from_edges(2, &[(0, 1), (1, 0), (0, 0), (0, 1)]);
    check!(r#"n = 2, edges = [(0, 1), (1, 0), (0, 0), (0, 1)]; neighbors(0)"#, g.neighbors(0), &[1, 0, 1]);
}

#[test]
fn trailing_empty_node() {
    let g = Csr::from_edges(4, &[(0, 3)]);
    check!(r#"n = 4, edges = [(0, 3)]; neighbors(3)"#, (g.neighbors(3).is_empty(), g.parts().0.to_vec()), (true, vec![0, 1, 1, 1, 1]));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(903);
    for _ in 0..300 {
        let n = 1 + rng.below(7);
        let m = rng.below(15);
        let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
        let g = Csr::from_edges(n, &edges);
        let got: Vec<Vec<usize>> = (0..n).map(|u| g.neighbors(u).to_vec()).collect();
        let want: Vec<Vec<usize>> = (0..n).map(|u| edges.iter().filter(|e| e.0 == u).map(|e| e.1).collect()).collect();
        let offsets: Vec<usize> = (0..=n).map(|u| edges.iter().filter(|e| e.0 < u).count()).collect();
        check!(format!("n = {n}, edges = {edges:?}"), (got, g.parts().0.to_vec()), (want, offsets));
    }
}

#[test]
fn scale_200k_nodes() {
    let n = 200_000;
    let edges: Vec<(usize, usize)> = (0..n).rev().map(|i| (i * 7 % n, i)).collect();
    let g = Csr::from_edges(n, &edges);
    // Node 0 gets exactly one edge (from i = 0); the last source written is 7·1 % n = 7 → 1.
    check!("n = 200000, edges = [(i·7 % n, i) for i in n-1..=0]", (g.parts().0[n], g.neighbors(0).to_vec(), g.neighbors(7).to_vec()), (200_000, vec![0], vec![1]));
}
