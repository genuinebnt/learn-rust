use solution::*;

#[test]
fn self_edge() {
    let mut g = Graph::new();
    let a = g.add_node("a");
    g.add_edge(a, a);
    check!(r#"a → a"#, g.neighbors(a), vec!["a"]);
}

#[test]
fn fan_out() {
    let mut g = Graph::new();
    let a = g.add_node("a");
    let b = g.add_node("b");
    let c = g.add_node("c");
    g.add_edge(a, b);
    g.add_edge(a, c);
    check!(r#"a → b, a → c"#, g.neighbors(a), vec!["b", "c"]);
}

#[test]
fn ids_are_sequential() {
    let mut g = Graph::new();
    let a = g.add_node("a");
    let b = g.add_node("b");
    let c = g.add_node("c");
    check!(r#"add three nodes"#, (a, b, c), (0, 1, 2));
}

#[test]
fn rename_seen_by_every_edge() {
    let mut g = Graph::new();
    let a = g.add_node("a");
    let b = g.add_node("b");
    let c = g.add_node("c");
    g.add_edge(a, c);
    g.add_edge(b, c);
    g.nodes[c].name = "z".to_string();
    check!(r#"a → c, b → c, rename c to "z""#, (g.neighbors(a), g.neighbors(b)), (vec!["z"], vec!["z"]));
}

#[test]
fn unicode_names() {
    let mut g = Graph::new();
    let a = g.add_node("é");
    let b = g.add_node("日本");
    g.add_edge(a, b);
    check!(r#""é" → "日本""#, g.neighbors(a), vec!["日本"]);
}

#[test]
fn edge_added_before_later_node_renamed() {
    let mut g = Graph::new();
    let a = g.add_node("a");
    let b = g.add_node("b");
    g.add_edge(a, b);
    let c = g.add_node("c");
    g.add_edge(b, c);
    g.nodes[a].name.push('?');
    check!(r#"a → b, add c, b → c, rename a; neighbors(b)"#, (g.neighbors(b), g.neighbors(a)), (vec!["c"], vec!["b"]));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(904);
    for _ in 0..200 {
        let n = 1 + rng.below(6);
        let m = rng.below(12);
        let names: Vec<String> = (0..n).map(|i| format!("n{i}")).collect();
        let mut g = Graph::new();
        for name in &names {
            g.add_node(name);
        }
        let edges: Vec<(usize, usize)> = (0..m).map(|_| (rng.below(n), rng.below(n))).collect();
        for &(u, v) in &edges {
            g.add_edge(u, v);
        }
        for u in 0..n {
            let want: Vec<&str> = edges.iter().filter(|e| e.0 == u).map(|e| names[e.1].as_str()).collect();
            check!(format!("n = {n}, edges = {edges:?}; neighbors({u})"), g.neighbors(u), want);
        }
    }
}

#[test]
fn long_ring() {
    let mut g = Graph::new();
    let ids: Vec<usize> = (0..100_000).map(|i| g.add_node(&i.to_string())).collect();
    for i in 0..ids.len() {
        g.add_edge(ids[i], ids[(i + 1) % ids.len()]);
    }
    check!("ring of 100000 nodes; neighbors(99999)", g.neighbors(ids[99_999]), vec!["0"]);
}
