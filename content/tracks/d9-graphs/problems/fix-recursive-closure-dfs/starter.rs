/// How many nodes can be reached from `start`, including `start`.
pub fn count_reachable(adj: &[Vec<usize>], start: usize) -> usize {
    let mut seen = vec![false; adj.len()];
    let mut dfs = |u: usize| {
        if seen[u] {
            return;
        }
        seen[u] = true;
        for &v in &adj[u] {
            dfs(v);
        }
    };
    dfs(start);
    seen.iter().filter(|&&s| s).count()
}
