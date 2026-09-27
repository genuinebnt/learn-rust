use solution::*;

#[test]
fn cycle() {
    check!(r#"n = 2, edges = [(0, 1), (1, 0)]"#, sources(2, &[(0, 1), (1, 0)]), Vec::<usize>::new());
}

#[test]
fn self_loop() {
    check!(r#"n = 1, edges = [(0, 0)]"#, degrees(1, &[(0, 0)]), vec![(1, 1)]);
}

#[test]
fn no_nodes() {
    check!(r#"n = 0, edges = []"#, (degrees(0, &[]), sources(0, &[])), (Vec::<(usize, usize)>::new(), Vec::<usize>::new()));
}

#[test]
fn parallel_edges() {
    check!(r#"n = 2, edges = [(0, 1), (0, 1)]"#, degrees(2, &[(0, 1), (0, 1)]), vec![(0, 2), (2, 0)]);
}

#[test]
fn self_loop_is_not_a_source() {
    check!(r#"n = 2, edges = [(0, 0)]"#, sources(2, &[(0, 0)]), vec![1]);
}

#[test]
fn source_is_last() {
    check!(r#"n = 3, edges = [(2, 0), (2, 1)]"#, sources(3, &[(2, 0), (2, 1)]), vec![2]);
}

#[test]
fn sink() {
    check!(r#"n = 4, edges = [(0, 3), (1, 3), (2, 3)]"#, degrees(4, &[(0, 3), (1, 3), (2, 3)]), vec![(0, 1), (0, 1), (0, 1), (3, 0)]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(902);
    for _ in 0..300 {
        let n = 1 + rng.below(8);
        let m = rng.below(15);
        let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
        let want_deg: Vec<(usize, usize)> = (0..n)
            .map(|u| (edges.iter().filter(|e| e.1 == u).count(), edges.iter().filter(|e| e.0 == u).count()))
            .collect();
        let want_src: Vec<usize> = (0..n).filter(|&u| want_deg[u].0 == 0).collect();
        check!(format!("n = {n}, edges = {edges:?}"), (degrees(n, &edges), sources(n, &edges)), (want_deg, want_src));
    }
}

#[test]
fn scale_chain_200k() {
    let n = 200_000;
    let edges: Vec<(usize, usize)> = (0..n - 1).map(|i| (i, i + 1)).collect();
    let d = degrees(n, &edges);
    let s = sources(n, &edges);
    check!("chain 0 → 1 → … → 199999", (d[0], d[100_000], d[n - 1], s), ((0, 1), (1, 1), (1, 0), vec![0]));
}
