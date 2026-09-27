use solution::*;

#[test]
fn no_path() {
    let mut net = FlowNetwork::new(3);
    net.add_edge(0, 1, 5);
    check!(r#"0→1 (5), t = 2"#, net.max_flow(0, 2), 0);
}

#[test]
fn parallel() {
    let mut net = FlowNetwork::new(2);
    net.add_edge(0, 1, 3);
    net.add_edge(0, 1, 4);
    check!(r#"two 0→1 edges (3 and 4)"#, net.max_flow(0, 1), 7);
}

#[test]
fn layered() {
    let mut net = FlowNetwork::new(500);
    for i in 0..10 {
        net.add_edge(0, 1 + i, 1);
        for layer in 0..48 {
            net.add_edge(1 + layer * 10 + i, 1 + (layer + 1) * 10 + i, 1);
        }
        net.add_edge(1 + 48 * 10 + i, 499, 1);
    }
    check!(r#"500 nodes in layers, capacity 1 per edge"#, net.max_flow(0, 499), 10);
}
