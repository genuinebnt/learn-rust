pub fn dfs_order(adj: &[Vec<usize>], start: usize) -> Vec<usize> {
    let mut seen = vec![false; adj.len()];
    seen[start] = true;
    let mut order = Vec::new();
    let mut stack = vec![start];
    while let Some(u) = stack.pop() {
        order.push(u);
        for &v in adj[u].iter().rev() {
            if !seen[v] {
                seen[v] = true;
                stack.push(v);
            }
        }
    }
    order
}
