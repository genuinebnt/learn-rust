use solution::*;

#[test]
fn self_loop() {
    check!(r#"n = 1, edges = [(0, 0)]"#, adjacency_list(1, &[(0, 0)]), vec![vec![0]]);
}

#[test]
fn sorted() {
    check!(r#"n = 4, edges = [(0, 3), (0, 1), (0, 2)]"#, adjacency_list(4, &[(0, 3), (0, 1), (0, 2)])[0].clone(), vec![1, 2, 3]);
}

#[test]
fn zero_nodes() {
    check!(r#"n = 0, edges = []"#, adjacency_list(0, &[]), Vec::<Vec<usize>>::new());
}

#[test]
fn self_loop_among_others() {
    check!(r#"n = 2, edges = [(1, 1), (0, 1), (1, 1)]"#, adjacency_list(2, &[(1, 1), (0, 1), (1, 1)]), vec![vec![1], vec![0, 1]]);
}

#[test]
fn complete_k4() {
    check!(r#"n = 4, every pair once"#, adjacency_list(4, &[(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]), vec![vec![1, 2, 3], vec![0, 2, 3], vec![0, 1, 3], vec![0, 1, 2]]);
}

#[test]
fn isolated_middle() {
    check!(r#"n = 5, edges = [(4, 0)]"#, adjacency_list(5, &[(4, 0)]), vec![vec![4], vec![], vec![], vec![], vec![0]]);
}

#[test]
fn both_directions_listed() {
    check!(r#"n = 3, edges = [(2, 1), (2, 0), (1, 0)]"#, adjacency_list(3, &[(2, 1), (2, 0), (1, 0)]), vec![vec![1, 2], vec![0, 2], vec![0, 1]]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(901);
    for _ in 0..300 {
        let n = 1 + rng.below(8);
        let m = rng.below(15);
        let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
        let want: Vec<Vec<usize>> = (0..n)
            .map(|u| (0..n).filter(|&v| edges.iter().any(|&(a, b)| (a, b) == (u, v) || (a, b) == (v, u))).collect())
            .collect();
        check!(format!("n = {n}, edges = {edges:?}"), adjacency_list(n, &edges), want);
    }
}

#[test]
fn scale_star_200k() {
    // Node 0 touches every other node, each edge listed in both directions.
    let n = 200_001;
    let edges: Vec<(usize, usize)> = (1..n).rev().flat_map(|i| [(i, 0), (0, i)]).collect();
    let adj = adjacency_list(n, &edges);
    check!("star: 0 joined to 1..=200000, each edge twice", (adj[0].len(), adj[0][0], adj[0][199_999], adj[200_000].clone()), (200_000, 1, 200_000, vec![0]));
}
