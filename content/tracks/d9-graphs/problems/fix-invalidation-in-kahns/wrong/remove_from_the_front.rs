/// Kahn's algorithm. `(a, b)` means a comes before b. Nodes are processed
/// in the order they become ready.
pub fn topo_order(n: usize, edges: &[(usize, usize)]) -> Option<Vec<usize>> {
    let mut adj = vec![Vec::new(); n];
    let mut indeg = vec![0u32; n];
    for &(a, b) in edges {
        adj[a].push(b);
        indeg[b] += 1;
    }
    let mut ready: Vec<usize> = (0..n).filter(|&u| indeg[u] == 0).collect();
    let mut order = Vec::new();
    while !ready.is_empty() {
        let u = ready.remove(0);
        order.push(u);
        for &v in &adj[u] {
            indeg[v] -= 1;
            if indeg[v] == 0 {
                ready.push(v);
            }
        }
    }
    (order.len() == n).then_some(order)
}
