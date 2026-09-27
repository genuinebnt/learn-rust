/// How many nodes can be reached from `start`, including `start`.
pub fn count_reachable(adj: &[Vec<usize>], start: usize) -> usize {
    fn dfs(adj: &[Vec<usize>], seen: &mut [bool], u: usize) {
        if seen[u] {
            return;
        }
        seen[u] = true;
        for &v in &adj[u] {
            dfs(adj, seen, v);
        }
    }

    let mut seen = vec![false; adj.len()];
    dfs(adj, &mut seen, start);
    seen.iter().filter(|&&s| s).count()
}
