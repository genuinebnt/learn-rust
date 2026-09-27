use solution::*;

#[test]
fn three_units() {
    check!(r#"same network, want = 3"#, min_cost_flow(4, &[(0, 1, 2, 1), (0, 2, 1, 2), (1, 2, 1, 1), (1, 3, 1, 3), (2, 3, 2, 1)], 0, 3, 3), Some(10));
}

#[test]
fn nothing() {
    check!(r#"want = 0"#, min_cost_flow(2, &[], 0, 1, 0), Some(0));
}

#[test]
fn reroute() {
    check!(r#"greedy first path must be partly undone"#, min_cost_flow(4, &[(0, 1, 1, 1), (0, 2, 1, 5), (1, 2, 1, 1), (1, 3, 1, 5), (2, 3, 1, 1)], 0, 3, 2), Some(12));
}

#[test]
fn zero_costs() {
    check!(r#"n = 3, edges = [(0,1,5,0), (1,2,5,0)], want = 5"#, min_cost_flow(3, &[(0, 1, 5, 0), (1, 2, 5, 0)], 0, 2, 5), Some(0));
}

#[test]
fn one_edge_full() {
    check!(r#"n = 2, edges = [(0,1,10000,7)], want = 10000"#, min_cost_flow(2, &[(0, 1, 10_000, 7)], 0, 1, 10_000), Some(70_000));
}

#[test]
fn one_short() {
    check!(r#"n = 2, edges = [(0,1,10000,7)], want = 10001"#, min_cost_flow(2, &[(0, 1, 10_000, 7)], 0, 1, 10_001), None);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(933);
    for _ in 0..300 {
        let n = 2 + rng.below(3);
        let m = rng.below(6);
        let edges: Vec<(usize, usize, u32, i64)> = (0..m).map(|_| (rng.below(n), rng.below(n), rng.int(0, 2) as u32, rng.int(0, 5))).collect();
        let want_units = rng.int(0, 3) as u32;
        let (s, t) = (0, n - 1);
        // Brute force: try every integer flow on every edge; keep the cheapest that balances.
        let mut want: Option<i64> = None;
        let combos: u32 = edges.iter().map(|e| e.2 + 1).product();
        for mut code in 0..combos {
            let mut net = vec![0i64; n];
            let mut cost = 0;
            for &(u, v, c, w) in &edges {
                let f = (code % (c + 1)) as i64;
                code /= c + 1;
                net[u] += f;
                net[v] -= f;
                cost += f * w;
            }
            let balanced = (0..n).all(|x| net[x] == if x == s { want_units as i64 } else if x == t { -(want_units as i64) } else { 0 });
            if balanced && want.is_none_or(|b| cost < b) {
                want = Some(cost);
            }
        }
        check!(format!("n = {n}, edges (u, v, cap, cost) = {edges:?}, s = {s}, t = {t}, want = {want_units}"), min_cost_flow(n, &edges, s, t, want_units), want);
    }
}

#[test]
fn scale_200_nodes_2000_edges() {
    let mut x: u64 = 99;
    let mut next = || { x = x.wrapping_mul(6_364_136_223_846_793_005).wrapping_add(1_442_695_040_888_963_407); x >> 33 };
    let mut edges = Vec::new();
    for _ in 0..2000 {
        let u = (next() % 200) as usize;
        let v = (next() % 200) as usize;
        let cap = (1000 + next() % 3000) as u32;
        let cost = (next() % 100) as i64;
        edges.push((u, v, cap, cost));
    }
    check!("n = 200, 2000 pseudo-random edges (LCG seed 99), s = 0, t = 199, want = 10000", min_cost_flow(200, &edges, 0, 199, 10_000), Some(911_390));
}
