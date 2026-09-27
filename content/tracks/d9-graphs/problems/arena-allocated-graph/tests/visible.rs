use solution::*;

#[test]
fn cycle_and_edit() {
    let mut g = Graph::new();
    let a = g.add_node("a".to_string());
    let b = g.add_node("b".to_string());
    let c = g.add_node("c".to_string());
    g.add_edge(a, b);
    g.add_edge(b, c);
    g.add_edge(c, a);
    g.value_mut(b).push('!');
    let names: Vec<String> = g.reachable(a).into_iter().map(|id| g.value(id).to_string()).collect();
    check!(r#"a → b → c → a; append "!" to b; values reachable from a"#, names, vec!["a", "b!", "c"]);
}

#[test]
fn neighbours() {
    let mut g = Graph::new();
    let a = g.add_node(1);
    let b = g.add_node(2);
    let c = g.add_node(3);
    g.add_edge(a, c);
    g.add_edge(a, b);
    check!(r#"a → c, a → b"#, (g.neighbors(a) == [c, b], g.neighbors(b).is_empty()), (true, true));
}

#[test]
fn lone_node_reaches_itself() {
    let mut g = Graph::new();
    let a = g.add_node("a");
    check!(r#"a single node a"#, (g.reachable(a) == [a], *g.value(a)), (true, "a"));
}

#[test]
fn edges_are_directed() {
    let mut g = Graph::new();
    let a = g.add_node("a");
    let b = g.add_node("b");
    g.add_edge(a, b);
    check!(r#"a → b; reachable from b"#, g.reachable(b) == [b], true);
}

#[test]
fn breadth_first() {
    let mut g = Graph::new();
    let ids: Vec<NodeId> = ["a", "b", "c", "d", "e"].into_iter().map(|v| g.add_node(v)).collect();
    for (x, y) in [(0, 1), (0, 2), (1, 3), (2, 4)] {
        g.add_edge(ids[x], ids[y]);
    }
    let vals: Vec<&str> = g.reachable(ids[0]).into_iter().map(|id| *g.value(id)).collect();
    check!(r#"a → b, a → c, b → d, c → e; values reachable from a"#, vals, vec!["a", "b", "c", "d", "e"]);
}
