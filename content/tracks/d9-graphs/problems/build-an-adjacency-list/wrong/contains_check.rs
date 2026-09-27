pub fn adjacency_list(n: usize, edges: &[(usize, usize)]) -> Vec<Vec<usize>> {
    let mut adj: Vec<Vec<usize>> = vec![Vec::new(); n];
    for &(u, v) in edges {
        if !adj[u].contains(&v) {
            adj[u].push(v);
        }
        if !adj[v].contains(&u) {
            adj[v].push(u);
        }
    }
    for list in &mut adj {
        list.sort_unstable();
    }
    adj
}
