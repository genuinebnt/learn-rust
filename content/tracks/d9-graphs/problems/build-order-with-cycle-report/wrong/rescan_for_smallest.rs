pub fn build_order(n: usize, deps: &[(usize, usize)]) -> Result<Vec<usize>, Vec<usize>> {
    let mut adj = vec![Vec::new(); n];
    let mut indeg = vec![0u32; n];
    for &(a, b) in deps {
        adj[a].push(b);
        indeg[b] += 1;
    }
    let mut built = vec![false; n];
    let mut order = Vec::with_capacity(n);
    while let Some(u) = (0..n).find(|&u| !built[u] && indeg[u] == 0) {
        built[u] = true;
        order.push(u);
        for &v in &adj[u] {
            indeg[v] -= 1;
        }
    }
    if order.len() == n {
        Ok(order)
    } else {
        Err((0..n).filter(|&u| !built[u]).collect())
    }
}
