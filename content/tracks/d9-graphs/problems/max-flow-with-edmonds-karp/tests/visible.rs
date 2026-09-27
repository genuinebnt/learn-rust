use solution::*;

#[test]
fn clrs() {
    let mut net = FlowNetwork::new(6);
    for (u, v, c) in [(0, 1, 16), (0, 2, 13), (1, 3, 12), (2, 1, 4), (2, 4, 14), (3, 2, 9), (3, 5, 20), (4, 3, 7), (4, 5, 4)] {
        net.add_edge(u, v, c);
    }
    check!(r#"CLRS network, s = 0, t = 5"#, net.max_flow(0, 5), 23);
}

#[test]
fn needs_undo() {
    let mut net = FlowNetwork::new(4);
    for (u, v, c) in [(0, 1, 1), (0, 2, 1), (1, 2, 1), (1, 3, 1), (2, 3, 1)] {
        net.add_edge(u, v, c);
    }
    check!(r#"0→1 (1), 0→2 (1), 1→2 (1), 1→3 (1), 2→3 (1)"#, net.max_flow(0, 3), 2);
}
