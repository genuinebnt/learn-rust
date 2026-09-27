use solution::*;

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
