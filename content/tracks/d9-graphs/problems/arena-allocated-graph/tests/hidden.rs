use solution::*;

#[test]
fn self_edge() {
    let mut g = Graph::new();
    let a = g.add_node(());
    let b = g.add_node(());
    g.add_edge(a, a);
    g.add_edge(a, b);
    check!(r#"a → a, a → b"#, (g.reachable(a) == [a, b], g.neighbors(a) == [a, b]), (true, true));
}

#[test]
fn duplicate_edge() {
    let mut g = Graph::new();
    let a = g.add_node('a');
    let b = g.add_node('b');
    g.add_edge(a, b);
    g.add_edge(a, b);
    check!(r#"a → b twice"#, (g.neighbors(a).len(), g.reachable(a).len()), (2, 2));
}

#[test]
fn value_mut_edits_in_place() {
    let mut g = Graph::new();
    let (a, b, c) = (g.add_node(1), g.add_node(2), g.add_node(3));
    for id in [a, b, c] {
        *g.value_mut(id) += 10;
    }
    check!(r#"three nodes 1, 2, 3; add 10 to each through value_mut"#, (*g.value(a), *g.value(b), *g.value(c)), (11, 12, 13));
}

#[test]
fn ids_are_distinct() {
    let mut g = Graph::new();
    let (a, b, c) = (g.add_node(0), g.add_node(0), g.add_node(0));
    check!(r#"add three nodes with the same value"#, (a != b, b != c, a != c), (true, true, true));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(929);
    for _ in 0..300 {
        let n = 1 + rng.below(8);
        let m = rng.below(12);
        let mut g = Graph::new();
        let ids: Vec<NodeId> = (0..n).map(|i| g.add_node(i)).collect();
        let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
        for &(u, v) in &edges {
            g.add_edge(ids[u], ids[v]);
        }
        let start = rng.below(n);
        // Brute force: BFS over the edge list, in the order edges were added.
        let mut want = vec![start];
        let mut i = 0;
        while i < want.len() {
            let u = want[i];
            i += 1;
            for &(a, b) in &edges {
                if a == u && !want.contains(&b) {
                    want.push(b);
                }
            }
        }
        let got: Vec<usize> = g.reachable(ids[start]).into_iter().map(|id| *g.value(id)).collect();
        check!(format!("n = {n}, edges = {edges:?}, from {start}"), got, want);
    }
}

#[test]
fn scale_chain_200k() {
    let mut g = Graph::new();
    let ids: Vec<NodeId> = (0..200_000u32).map(|i| g.add_node(i)).collect();
    for w in ids.windows(2) {
        g.add_edge(w[0], w[1]);
    }
    let r = g.reachable(ids[0]);
    check!("chain of 200000 nodes; reachable from the first", (r.len(), *g.value(r[199_999])), (200_000, 199_999));
}

#[test]
fn unreachable() {
    let mut g = Graph::new();
    let a = g.add_node(0u8);
    let b = g.add_node(1);
    let c = g.add_node(2);
    g.add_edge(a, b);
    let r = g.reachable(a);
    check!(r#"a → b, c alone; reachable from a"#, (r.len(), r.contains(&c)), (2, false));
}

#[test]
fn bfs_order() {
    let mut g = Graph::new();
    let a = g.add_node(10);
    let b = g.add_node(20);
    let c = g.add_node(30);
    let d = g.add_node(40);
    g.add_edge(a, b);
    g.add_edge(a, c);
    g.add_edge(b, d);
    let vals: Vec<i32> = g.reachable(a).into_iter().map(|id| *g.value(id)).collect();
    check!(r#"a → b, a → c, b → d; values reachable from a"#, vals, vec![10, 20, 30, 40]);
}
