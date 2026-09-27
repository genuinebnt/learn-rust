pub fn count_components(n: usize, edges: &[(usize, usize)]) -> usize {
    fn visit(u: usize, adj: &[Vec<usize>], seen: &mut [bool]) {
        seen[u] = true;
        for &v in &adj[u] {
            if !seen[v] {
                visit(v, adj, seen);
            }
        }
    }
    let mut adj = vec![Vec::new(); n];
    for &(a, b) in edges {
        adj[a].push(b);
        adj[b].push(a);
    }
    let mut seen = vec![false; n];
    let mut count = 0;
    for u in 0..n {
        if !seen[u] {
            count += 1;
            visit(u, &adj, &mut seen);
        }
    }
    count
}
