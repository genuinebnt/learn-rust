use solution::network_delay;

#[test]
fn single_node() {
    check!("times = [], n = 1, k = 1", network_delay(&[], 1, 1), Some(0));
}

#[test]
fn chain_of_four() {
    check!(
        "times = [(2,1,1), (2,3,1), (3,4,1)], n = 4, k = 2",
        network_delay(&[(2, 1, 1), (2, 3, 1), (3, 4, 1)], 4, 2),
        Some(2)
    );
}

#[test]
fn unreachable_returns_none() {
    check!("times = [(1,2,1)], n = 3, k = 1", network_delay(&[(1, 2, 1)], 3, 1), None);
}

#[test]
fn zero_weight_edges() {
    check!("times = [(1,2,0), (2,3,0)], n = 3, k = 1", network_delay(&[(1, 2, 0), (2, 3, 0)], 3, 1), Some(0));
}

#[test]
fn duplicate_edges_takes_min() {
    check!("times = [(1,2,9), (1,2,3)], n = 2, k = 1", network_delay(&[(1, 2, 9), (1, 2, 3)], 2, 1), Some(3));
}
