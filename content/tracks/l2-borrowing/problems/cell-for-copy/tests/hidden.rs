use solution::*;

#[test]
fn in_a_vec() {
    check!(r#"visit through a Vec<&Node>"#, { let a = Node::new("a"); let b = Node::new("b"); let all = vec![&a, &b, &a]; for n in &all { n.visit(); } (a.visits(), b.visits()) }, (2, 1));
}

#[test]
fn name_kept() {
    check!(r#"name "héllo""#, Node::new("héllo").name, "héllo".to_string());
}

#[test]
fn empty_name() {
    check!(r#"name """#, Node::new("").name, String::new());
}

#[test]
fn visits_does_not_count() {
    check!(r#"call visits() three times"#, { let n = Node::new("a"); n.visits(); n.visits(); n.visits() }, 0);
}

#[test]
fn many() {
    check!(r#"10000 visits"#, { let n = Node::new("a"); for _ in 0..10_000 { n.visit(); } n.visits() }, 10_000);
}

#[test]
fn through_rc() {
    check!(r#"two Rc handles to one node"#, { let n = std::rc::Rc::new(Node::new("a")); let m = std::rc::Rc::clone(&n); n.visit(); m.visit(); n.visits() }, 2);
}

#[test]
fn returns_sequence() {
    check!(r#"visit three times"#, { let n = Node::new("a"); (n.visit(), n.visit(), n.visit()) }, (1, 2, 3));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2030);
    for _ in 0..200 {
        let k = 1 + rng.below(4);
        let nodes: Vec<Node> = (0..k).map(|i| Node::new(&i.to_string())).collect();
        let mut model = vec![0u32; k];
        let mut log = Vec::new();
        let steps = rng.below(12);
        for _ in 0..steps {
            let i = rng.below(k);
            log.push(i);
            model[i] += 1;
            check!(format!("visits {log:?}"), nodes[i].visit(), model[i]);
        }
        check!(format!("visits {log:?}"), nodes.iter().map(|n| n.visits()).collect::<Vec<_>>(), model);
    }
}
