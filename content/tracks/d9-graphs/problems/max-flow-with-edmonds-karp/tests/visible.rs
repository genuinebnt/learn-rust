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

#[test]
fn single_edge() {
    let mut net = FlowNetwork::new(2);
    net.add_edge(0, 1, 5);
    check!(r#"0→1 (5)"#, net.max_flow(0, 1), 5);
}

#[test]
fn bottleneck_in_series() {
    let mut net = FlowNetwork::new(4);
    net.add_edge(0, 1, 10);
    net.add_edge(1, 2, 3);
    net.add_edge(2, 3, 10);
    check!(r#"0→1 (10), 1→2 (3), 2→3 (10)"#, net.max_flow(0, 3), 3);
}

#[test]
fn edges_are_directed() {
    let mut net = FlowNetwork::new(2);
    net.add_edge(1, 0, 5);
    check!(r#"1→0 (5); flow from 0 to 1"#, net.max_flow(0, 1), 0);
}
