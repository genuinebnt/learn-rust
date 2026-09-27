use solution::*;

#[test]
fn single() {
    check!(r#"n = 1, edges = []"#, mst_weight(1, &[]), Some(0));
}

#[test]
fn parallel_edges() {
    check!(r#"n = 2, edges = [(0,1,9), (1,0,4)]"#, mst_weight(2, &[(0, 1, 9), (1, 0, 4)]), Some(4));
}

#[test]
fn big_weights() {
    check!(r#"n = 3, edges with weight 10¹²"#, mst_weight(3, &[(0, 1, 1_000_000_000_000), (1, 2, 1_000_000_000_000)]), Some(2_000_000_000_000));
}

#[test]
fn zero_weights() {
    check!(r#"n = 3, edges = [(0,1,0), (1,2,0), (0,2,0)]"#, mst_weight(3, &[(0, 1, 0), (1, 2, 0), (0, 2, 0)]), Some(0));
}

#[test]
fn two_islands() {
    check!(r#"n = 4, edges = [(0,1,1), (2,3,1), (0,1,2)]"#, mst_weight(4, &[(0, 1, 1), (2, 3, 1), (0, 1, 2)]), None);
}

#[test]
fn cheap_edges_listed_last() {
    check!(r#"n = 4, edges = [(0,1,10), (1,2,10), (2,3,10), (0,3,1), (0,2,1), (1,3,1)]"#, mst_weight(4, &[(0, 1, 10), (1, 2, 10), (2, 3, 10), (0, 3, 1), (0, 2, 1), (1, 3, 1)]), Some(3));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(924);
    for _ in 0..300 {
        let n = 1 + rng.below(7);
        let m = rng.below(12);
        let edges: Vec<(usize, usize, u64)> = (0..m).map(|_| (rng.below(n), rng.below(n), rng.int(0, 20) as u64)).collect();
        // Brute force: Prim's algorithm on a weight matrix.
        let mut w = vec![vec![u64::MAX; n]; n];
        for &(a, b, c) in &edges {
            if a != b {
                w[a][b] = w[a][b].min(c);
                w[b][a] = w[b][a].min(c);
            }
        }
        let mut inside = vec![false; n];
        inside[0] = true;
        let mut total = 0;
        let mut want = Some(0);
        for _ in 1..n {
            let best = (0..n).filter(|&u| inside[u]).flat_map(|u| (0..n).filter(|&v| !inside[v]).map(move |v| (u, v))).min_by_key(|&(u, v)| w[u][v]);
            match best {
                Some((u, v)) if w[u][v] != u64::MAX => {
                    inside[v] = true;
                    total += w[u][v];
                    want = Some(total);
                }
                _ => {
                    want = None;
                    break;
                }
            }
        }
        check!(format!("n = {n}, edges = {edges:?}"), mst_weight(n, &edges), want);
    }
}

#[test]
fn scale_100k_nodes() {
    // A random spanning tree plus 100000 random extra edges, weights below 10⁶ (LCG seed 7).
    let n = 100_000;
    let mut x: u64 = 7;
    let mut next = || { x = x.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407); x >> 33 };
    let mut edges: Vec<(usize, usize, u64)> = Vec::new();
    for i in 1..n {
        let j = (next() % i as u64) as usize;
        let w = next() % 1_000_000;
        edges.push((i, j, w));
    }
    for _ in 0..100_000 {
        let a = (next() % n as u64) as usize;
        let b = (next() % n as u64) as usize;
        let w = next() % 1_000_000;
        edges.push((a, b, w));
    }
    check!("n = 100000, 199999 pseudo-random edges", mst_weight(n, &edges), Some(28_601_926_593));
}
