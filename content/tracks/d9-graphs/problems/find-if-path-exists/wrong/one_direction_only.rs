pub fn valid_path(n: usize, edges: &[(usize, usize)], source: usize, destination: usize) -> bool {
    let mut adj = vec![Vec::new(); n];
    for &(a, b) in edges {
        adj[a].push(b);
    }
    let mut seen = vec![false; n];
    seen[source] = true;
    let mut stack = vec![source];
    while let Some(u) = stack.pop() {
        if u == destination {
            return true;
        }
        for &v in &adj[u] {
            if !seen[v] {
                seen[v] = true;
                stack.push(v);
            }
        }
    }
    false
}
