use solution::*;

#[test]
fn walk_zero() {
    let nodes = [Node::new("a"), Node::new("b"), Node::new("c")];
    ring(&nodes);
    check!(r#"ring a, b, c; walk 0"#, (walk(&nodes[0], 0).len(), nodes[0].visits()), (0, 0));
}

#[test]
fn empty_ring() {
    check!(r#"ring of no nodes"#, { let nodes: [Node; 0] = []; ring(&nodes); 0 }, 0);
}

#[test]
fn unlink_solo() {
    let nodes = [Node::new("solo")];
    ring(&nodes);
    nodes[0].unlink();
    check!(r#"ring [solo]; unlink; next and prev"#, (nodes[0].next().is_none(), nodes[0].prev().is_none(), walk(&nodes[0], 3)), (true, true, vec!["solo"]));
}

#[test]
fn unlink_two_of_three() {
    let nodes = [Node::new("a"), Node::new("b"), Node::new("c")];
    ring(&nodes);
    nodes[0].unlink();
    nodes[1].unlink();
    check!(r#"ring a, b, c; unlink a, then b; walk 3 from c"#, walk(&nodes[2], 3), vec!["c", "c", "c"]);
}

#[test]
fn unlink_one_of_two() {
    let nodes = [Node::new("a"), Node::new("b")];
    ring(&nodes);
    nodes[0].unlink();
    check!(r#"ring a, b; unlink a; walk 3 from b"#, (walk(&nodes[1], 3), nodes[1].prev().map(|n| n.name.as_str())), (vec!["b", "b", "b"], Some("b")));
}

#[test]
fn relink_after_unlink() {
    let nodes = [Node::new("a"), Node::new("b"), Node::new("c")];
    ring(&nodes);
    nodes[1].unlink();
    nodes[2].link(&nodes[1]);
    nodes[1].link(&nodes[0]);
    check!(r#"ring a, b, c; unlink b; link c -> b, b -> a; walk 4 from a"#, walk(&nodes[0], 4), vec!["a", "c", "b", "a"]);
}

#[test]
fn visits_accumulate() {
    let nodes = [Node::new("a"), Node::new("b")];
    ring(&nodes);
    check!(r#"ring a, b; walk 3 twice from a"#, { walk(&nodes[0], 3); walk(&nodes[0], 3); (nodes[0].visits(), nodes[1].visits()) }, (4, 2));
}

#[test]
fn names_borrow_the_nodes() {
    let nodes = [Node::new("a"), Node::new("b"), Node::new("c")];
    ring(&nodes);
    check!(r#"walk returns the nodes' own names"#, walk(&nodes[0], 1)[0].as_ptr() == nodes[0].name.as_ptr(), true);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6233);
    for _ in 0..300 {
        let n = 1 + rng.below(6);
        let nodes: Vec<Node> = (0..n).map(|i| Node::new(&format!("n{i}"))).collect();
        ring(&nodes);
        let mut model: Vec<usize> = (0..n).collect();
        let mut ops = Vec::new();
        for _ in 0..rng.below(n) {
            let k = rng.below(n);
            nodes[k].unlink();
            model.retain(|&x| x != k);
            ops.push(format!("unlink n{k}"));
        }
        let start = rng.below(n);
        let steps = rng.below(8);
        let want: Vec<String> = match model.iter().position(|&x| x == start) {
            Some(p) => (0..steps).map(|s| format!("n{}", model[(p + s) % model.len()])).collect(),
            None => (0..steps.min(1)).map(|_| format!("n{start}")).collect(),
        };
        let got: Vec<String> = walk(&nodes[start], steps).iter().map(|s| s.to_string()).collect();
        check!(format!("ring of {n}; {}; walk {steps} from n{start}", ops.join(", ")), got, want);
    }
}

#[test]
fn big_ring() {
    let nodes: Vec<Node> = (0..100_000).map(|i| Node::new(&i.to_string())).collect();
    ring(&nodes);
    for k in (1..100_000).step_by(2) {
        nodes[k].unlink();
    }
    let w = walk(&nodes[0], 50_001);
    check!("ring of 100000, odd ones unlinked, walk 50001", (w.len(), w[49_999], w[50_000], nodes[0].visits()), (50_001, "99998", "0", 2));
}
