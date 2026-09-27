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

#[test]
fn no_edges() {
    let mut g = Graph::new();
    let a = g.add_node("a");
    check!(r#"a alone; neighbors(a)"#, g.neighbors(a), Vec::<&str>::new());
}

#[test]
fn edges_in_insertion_order() {
    let mut g = Graph::new();
    let a = g.add_node("a");
    let b = g.add_node("b");
    let c = g.add_node("c");
    g.add_edge(a, c);
    g.add_edge(a, b);
    check!(r#"a → c, then a → b; neighbors(a)"#, g.neighbors(a), vec!["c", "b"]);
}

#[test]
fn repeated_edge_listed_twice() {
    let mut g = Graph::new();
    let a = g.add_node("a");
    let b = g.add_node("b");
    g.add_edge(a, b);
    g.add_edge(a, b);
    check!(r#"a → b twice; neighbors(a)"#, g.neighbors(a), vec!["b", "b"]);
}
