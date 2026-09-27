use solution::*;

#[test]
fn counts() {
    check!(r#"visit 3 times"#, { let n = Node::new("a"); n.visit(); n.visit(); (n.visit(), n.visits()) }, (3, 3));
}

#[test]
fn shared_refs() {
    check!(r#"two &Node to the same node"#, { let n = Node::new("a"); let (x, y) = (&n, &n); x.visit(); y.visit(); n.visits() }, 2);
}
