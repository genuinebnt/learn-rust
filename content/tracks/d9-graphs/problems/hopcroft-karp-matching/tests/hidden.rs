use solution::*;

#[test]
fn no_edges() {
    check!(r#"left = 3, right = 2, edges = []"#, max_matching(3, 2, &[]), 0);
}

#[test]
fn duplicate_edges() {
    check!(r#"left = 1, right = 1, edges = [(0,0), (0,0)]"#, max_matching(1, 1, &[(0, 0), (0, 0)]), 1);
}

#[test]
fn long_augmenting_path() {
    check!(r#"left = 4, right = 4, edges = [(0,0), (1,0), (1,1), (2,1), (2,2), (3,2), (3,3)] listed so greedy picks badly"#, max_matching(4, 4, &[(0, 0), (1, 0), (1, 1), (2, 1), (2, 2), (3, 2), (3, 3)]), 4);
}

#[test]
fn isolated_right_nodes() {
    check!(r#"left = 2, right = 5, edges = [(0,4), (1,4)]"#, max_matching(2, 5, &[(0, 4), (1, 4)]), 1);
}

#[test]
fn random_vs_brute_force() {
    fn try_kuhn(u: usize, adj: &[Vec<usize>], seen: &mut [bool], owner: &mut [Option<usize>]) -> bool {
        for &v in &adj[u] {
            if !seen[v] {
                seen[v] = true;
                if owner[v].is_none_or(|w| try_kuhn(w, adj, seen, owner)) {
                    owner[v] = Some(u);
                    return true;
                }
            }
        }
        false
    }
    let mut rng = anneal_prelude::Rng::new(932);
    for _ in 0..300 {
        let (left, right) = (rng.below(6), 1 + rng.below(6));
        let m = if left == 0 { 0 } else { rng.below(12) };
        let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(left), rng.below(right))).collect();
        // Reference: Kuhn's algorithm, one augmenting path at a time.
        let mut adj = vec![Vec::new(); left];
        for &(u, v) in &edges {
            adj[u].push(v);
        }
        let mut owner = vec![None; right];
        let want = (0..left).filter(|&u| try_kuhn(u, &adj, &mut vec![false; right], &mut owner)).count();
        check!(format!("left = {left}, right = {right}, edges = {edges:?}"), max_matching(left, right, &edges), want);
    }
}

#[test]
fn scale_staircase_2500() {
    // Left i joins right 0..=i, lowest first: one augmenting path at a time costs O(V³).
    let n = 2500;
    let edges: Vec<(usize, usize)> = (0..n).flat_map(|i| (0..=i).map(move |j| (i, j))).collect();
    check!("left = right = 2500, left i joined to right 0..=i", max_matching(n, n, &edges), n);
}

#[test]
fn scale_many_hopeless_left_nodes() {
    // Left i < 5000 joins right i and i + 1, so the first 5000 match perfectly. Then 500000 more left nodes
    // all want right 0: each one-path-at-a-time search walks the whole chain and fails.
    let k = 5000;
    let mut edges: Vec<(usize, usize)> = (0..k).flat_map(|i| if i + 1 < k { vec![(i, i), (i, i + 1)] } else { vec![(i, i)] }).collect();
    edges.extend((k..k + 500_000).map(|u| (u, 0)));
    check!("left = 505000, right = 5000: a chain of 5000, then 500000 left nodes joined only to right 0", max_matching(k + 500_000, k, &edges), k);
}

#[test]
fn perfect_ring() {
    let edges: Vec<(usize, usize)> = (0..5000).flat_map(|i| [(i, (i + 1) % 5000), (i, i)]).collect();
    check!(r#"5000 × 5000, i → i and i → i + 1"#, max_matching(5000, 5000, &edges), 5000);
}

#[test]
fn dense_block() {
    let edges: Vec<(usize, usize)> = (0..5000).flat_map(|i| (0..20).map(move |k| (i, (i * 7 + k * 251) % 5000))).collect();
    check!(r#"5000 × 5000, each left node to 20 right nodes"#, max_matching(5000, 5000, &edges), 5000);
}
