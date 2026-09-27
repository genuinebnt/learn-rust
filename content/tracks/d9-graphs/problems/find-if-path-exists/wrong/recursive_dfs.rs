pub fn valid_path(n: usize, edges: &[(usize, usize)], source: usize, destination: usize) -> bool {
    fn go(u: usize, target: usize, adj: &[Vec<usize>], seen: &mut [bool]) -> bool {
        if u == target {
            return true;
        }
        seen[u] = true;
        adj[u].iter().any(|&v| !seen[v] && go(v, target, adj, seen))
    }
    let mut adj = vec![Vec::new(); n];
    for &(a, b) in edges {
        adj[a].push(b);
        adj[b].push(a);
    }
    go(source, destination, &adj, &mut vec![false; n])
}
