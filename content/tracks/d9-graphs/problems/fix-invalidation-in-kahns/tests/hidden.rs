use solution::*;

#[test]
fn cycle() {
    check!(r#"n = 3, edges = [(0, 1), (1, 2), (2, 1)]"#, topo_order(3, &[(0, 1), (1, 2), (2, 1)]), None);
}

#[test]
fn fifo() {
    check!(r#"n = 4, edges = [(0, 3), (1, 2)]"#, topo_order(4, &[(0, 3), (1, 2)]), Some(vec![0, 1, 3, 2]));
}

#[test]
fn self_loop() {
    check!(r#"n = 1, edges = [(0, 0)]"#, topo_order(1, &[(0, 0)]), None);
}

#[test]
fn no_nodes() {
    check!(r#"n = 0, edges = []"#, topo_order(0, &[]), Some(Vec::new()));
}

#[test]
fn diamond() {
    check!(r#"n = 4, edges = [(0, 1), (0, 2), (1, 3), (2, 3)]"#, topo_order(4, &[(0, 1), (0, 2), (1, 3), (2, 3)]), Some(vec![0, 1, 2, 3]));
}

#[test]
fn duplicate_edge() {
    check!(r#"n = 2, edges = [(0, 1), (0, 1)]"#, topo_order(2, &[(0, 1), (0, 1)]), Some(vec![0, 1]));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(914);
    for _ in 0..300 {
        let n = 1 + rng.below(7);
        let m = rng.below(9);
        let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
        // Reference: Kahn's with a VecDeque.
        let mut indeg = vec![0; n];
        for &(_, b) in &edges {
            indeg[b] += 1;
        }
        let mut queue: std::collections::VecDeque<usize> = (0..n).filter(|&u| indeg[u] == 0).collect();
        let mut order = Vec::new();
        while let Some(u) = queue.pop_front() {
            order.push(u);
            for &(a, b) in &edges {
                if a == u {
                    indeg[b] -= 1;
                    if indeg[b] == 0 {
                        queue.push_back(b);
                    }
                }
            }
        }
        let want = (order.len() == n).then_some(order);
        check!(format!("n = {n}, edges = {edges:?}"), topo_order(n, &edges), want);
    }
}

#[test]
fn scale_star_1m() {
    let n = 1_000_000;
    let edges: Vec<(usize, usize)> = (1..n).map(|i| (0, i)).collect();
    let out = topo_order(n, &edges).unwrap();
    check!("n = 1000000, 0 → every other node", (out.len(), out[0], out[1], out[n - 1]), (n, 0, 1, n - 1));
}
