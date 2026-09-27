pub fn adjacency_list(n: usize, edges: &[(usize, usize)]) -> Vec<Vec<usize>> {
    let mut adj = vec![Vec::new(); n];
    for &(u, v) in edges {
        adj[u].push(v);
        if u != v {
            adj[v].push(u);
        }
    }
    for list in &mut adj {
        list.sort_unstable();
    }
    adj
}
