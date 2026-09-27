use solution::*;

#[test]
fn shortest_path_must_be_undone() {
    let mut net = FlowNetwork::new(8);
    for (u, v) in [(0, 1), (1, 2), (2, 3), (1, 4), (4, 5), (5, 3), (0, 6), (6, 7), (7, 2)] {
        net.add_edge(u, v, 1);
    }
    check!(r#"0→1→2→3 is the shortest path, but both units need 1→4→5→3 and 0→6→7→2→3 (all capacity 1)"#, net.max_flow(0, 3), 2);
}

#[test]
fn zero_capacity() {
    let mut net = FlowNetwork::new(3);
    net.add_edge(0, 1, 0);
    net.add_edge(1, 2, 7);
    check!(r#"0→1 (0), 1→2 (7)"#, net.max_flow(0, 2), 0);
}

#[test]
fn huge_capacities() {
    let mut net = FlowNetwork::new(5);
    for m in 1..=3 {
        net.add_edge(0, m, 1_000_000_000_000_000);
        net.add_edge(m, 4, 1_000_000_000_000_000);
    }
    check!(r#"three parallel routes of 10¹⁵"#, net.max_flow(0, 4), 3_000_000_000_000_000);
}

#[test]
fn source_after_sink() {
    let mut net = FlowNetwork::new(4);
    net.add_edge(3, 1, 4);
    net.add_edge(1, 0, 6);
    net.add_edge(3, 0, 1);
    check!(r#"3→1 (4), 1→0 (6), 3→0 (1); s = 3, t = 0"#, net.max_flow(3, 0), 5);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(931);
    for _ in 0..300 {
        let n = 2 + rng.below(5);
        let m = rng.below(10);
        let edges: Vec<(usize, usize, u64)> = (0..m).map(|_| (rng.below(n), rng.below(n), rng.int(0, 9) as u64)).collect();
        let (s, t) = (0, n - 1);
        // Brute force: max flow equals the smallest cut, over every set holding s but not t.
        let want = (0..1usize << n)
            .filter(|&mask| mask >> s & 1 == 1 && mask >> t & 1 == 0)
            .map(|mask| edges.iter().filter(|&&(u, v, _)| mask >> u & 1 == 1 && mask >> v & 1 == 0).map(|e| e.2).sum::<u64>())
            .min()
            .unwrap();
        let mut net = FlowNetwork::new(n);
        for &(u, v, c) in &edges {
            net.add_edge(u, v, c);
        }
        check!(format!("n = {n}, edges (u, v, cap) = {edges:?}, s = {s}, t = {t}"), net.max_flow(s, t), want);
    }
}

#[test]
fn no_path() {
    let mut net = FlowNetwork::new(3);
    net.add_edge(0, 1, 5);
    check!(r#"0→1 (5), t = 2"#, net.max_flow(0, 2), 0);
}

#[test]
fn parallel() {
    let mut net = FlowNetwork::new(2);
    net.add_edge(0, 1, 3);
    net.add_edge(0, 1, 4);
    check!(r#"two 0→1 edges (3 and 4)"#, net.max_flow(0, 1), 7);
}

#[test]
fn layered() {
    let mut net = FlowNetwork::new(500);
    for i in 0..10 {
        net.add_edge(0, 1 + i, 1);
        for layer in 0..48 {
            net.add_edge(1 + layer * 10 + i, 1 + (layer + 1) * 10 + i, 1);
        }
        net.add_edge(1 + 48 * 10 + i, 499, 1);
    }
    check!(r#"500 nodes in layers, capacity 1 per edge"#, net.max_flow(0, 499), 10);
}
