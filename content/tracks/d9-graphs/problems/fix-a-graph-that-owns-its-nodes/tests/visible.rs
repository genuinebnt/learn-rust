use solution::*;

#[test]
fn cycle() {
    let mut g = Graph::new();
    let a = g.add_node("a");
    let b = g.add_node("b");
    g.add_edge(a, b);
    g.add_edge(b, a);
    check!(r#"a → b, b → a; neighbors(b)"#, g.neighbors(b), vec!["a"]);
}

#[test]
fn rename_after_linking() {
    let mut g = Graph::new();
    let a = g.add_node("a");
    let b = g.add_node("b");
    g.add_edge(a, b);
    g.nodes[b].name.push('!');
    check!(r#"a → b, then rename b to "b!"; neighbors(a)"#, g.neighbors(a), vec!["b!"]);
}
