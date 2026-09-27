/// How many nodes can be reached from `start`, including `start`.
pub fn count_reachable(adj: &[Vec<usize>], start: usize) -> usize {
    fn dfs(adj: &[Vec<usize>], seen: &[bool], u: usize) -> usize {
        if seen[u] {
            return 0;
        }
        let mut seen = seen.to_vec();
        seen[u] = true;
        1 + adj[u].iter().map(|&v| dfs(adj, &seen, v)).sum::<usize>()
    }

    dfs(adj, &vec![false; adj.len()], start)
}
