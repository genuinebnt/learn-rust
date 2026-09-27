use solution::*;

#[test]
fn counts() {
    check!(r#"visit 3 times"#, { let n = Node::new("a"); n.visit(); n.visit(); (n.visit(), n.visits()) }, (3, 3));
}

#[test]
fn shared_refs() {
    check!(r#"two &Node to the same node"#, { let n = Node::new("a"); let (x, y) = (&n, &n); x.visit(); y.visit(); n.visits() }, 2);
}

#[test]
fn new_is_zero() {
    check!(r#"new node "x""#, Node::new("x").visits(), 0);
}

#[test]
fn visit_returns_new_count() {
    check!(r#"first visit"#, Node::new("x").visit(), 1);
}

#[test]
fn independent_nodes() {
    check!(r#"visit a twice, b never"#, { let a = Node::new("a"); let b = Node::new("b"); a.visit(); a.visit(); (a.visits(), b.visits()) }, (2, 0));
}
