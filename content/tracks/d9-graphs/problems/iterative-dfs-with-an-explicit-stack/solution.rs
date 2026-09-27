pub fn dfs_order(adj: &[Vec<usize>], start: usize) -> Vec<usize> {
    let mut seen = vec![false; adj.len()];
    let mut order = Vec::new();
    let mut stack = vec![start];
    while let Some(u) = stack.pop() {
        if seen[u] {
            continue;
        }
        seen[u] = true;
        order.push(u);
        stack.extend(adj[u].iter().rev().filter(|&&v| !seen[v]));
    }
    order
}
