use solution::*;

#[test]
fn walk_the_ring() {
    let nodes = [Node::new("a"), Node::new("b"), Node::new("c")];
    ring(&nodes);
    check!(r#"ring a, b, c; walk 5 from a"#, (walk(&nodes[0], 5), nodes.iter().map(|n| n.visits()).collect::<Vec<_>>()), (vec!["a", "b", "c", "a", "b"], vec![2, 2, 1]));
}

#[test]
fn backwards() {
    let nodes = [Node::new("a"), Node::new("b"), Node::new("c")];
    ring(&nodes);
    check!(r#"ring a, b, c; prev of a, prev of that"#, nodes[0].prev().and_then(|n| n.prev()).map(|n| n.name.as_str()), Some("b"));
}

#[test]
fn unlink_middle() {
    let nodes = [Node::new("a"), Node::new("b"), Node::new("c")];
    ring(&nodes);
    nodes[1].unlink();
    check!(r#"ring a, b, c; unlink b; walk 4 from a"#, (walk(&nodes[0], 4), nodes[1].next().is_none(), nodes[2].prev().map(|n| n.name.as_str())), (vec!["a", "c", "a", "c"], true, Some("a")));
}

#[test]
fn single_node_ring() {
    let nodes = [Node::new("solo")];
    ring(&nodes);
    check!(r#"ring [solo]; walk 3"#, walk(&nodes[0], 3), vec!["solo", "solo", "solo"]);
}

#[test]
fn unlinked_node_walks_once() {
    let n = Node::new("x");
    check!(r#"a lone node, never linked; walk 3"#, (walk(&n, 3), n.visits()), (vec!["x"], 1));
}

#[test]
fn link_by_hand() {
    let (a, b) = (Node::new("a"), Node::new("b"));
    a.link(&b);
    check!(r#"a -> b by hand; walk 5 from a"#, (walk(&a, 5), b.prev().map(|n| n.name.as_str())), (vec!["a", "b"], Some("a")));
}
