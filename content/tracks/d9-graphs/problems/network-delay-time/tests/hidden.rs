use solution::network_delay;

#[test]
fn dense_n100() {
    // Nodes 1..=77 are fully connected; 78..=100 have no incoming edges.
    let mut times = Vec::new();
    for u in 1..=77usize {
        for v in 1..=77usize {
            if u != v {
                times.push((u, v, ((u * 7 + v * 13) % 100) as u32));
            }
        }
    }
    check!("n = 100, 5852 edges, nodes 78..=100 unreachable", network_delay(&times, 100, 1), None);
}
