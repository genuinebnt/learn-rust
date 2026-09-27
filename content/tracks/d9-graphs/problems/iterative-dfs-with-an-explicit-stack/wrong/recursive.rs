pub fn dfs_order(adj: &[Vec<usize>], start: usize) -> Vec<usize> {
    fn go(adj: &[Vec<usize>], u: usize, seen: &mut [bool], out: &mut Vec<usize>) {
        seen[u] = true;
        out.push(u);
        for &v in &adj[u] {
            if !seen[v] {
                go(adj, v, seen, out);
            }
        }
    }
    let mut out = Vec::new();
    go(adj, start, &mut vec![false; adj.len()], &mut out);
    out
}
