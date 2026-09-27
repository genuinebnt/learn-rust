use solution::*;

#[test]
fn in_a_vec() {
    check!(r#"visit through a Vec<&Node>"#, { let a = Node::new("a"); let b = Node::new("b"); let all = vec![&a, &b, &a]; for n in &all { n.visit(); } (a.visits(), b.visits()) }, (2, 1));
}
