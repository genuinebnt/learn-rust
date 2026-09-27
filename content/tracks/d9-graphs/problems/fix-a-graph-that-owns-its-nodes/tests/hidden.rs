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
