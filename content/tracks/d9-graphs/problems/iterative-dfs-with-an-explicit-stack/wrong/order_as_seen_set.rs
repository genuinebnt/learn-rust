pub fn dfs_order(adj: &[Vec<usize>], start: usize) -> Vec<usize> {
    let mut order: Vec<usize> = Vec::new();
    let mut stack = vec![start];
    while let Some(u) = stack.pop() {
        if order.contains(&u) {
            continue;
        }
        order.push(u);
        stack.extend(adj[u].iter().rev().filter(|v| !order.contains(v)));
    }
    order
}
