pub fn mst_weight(n: usize, edges: &[(usize, usize, u64)]) -> Option<u64> {
    let mut adj = vec![Vec::new(); n];
    for &(a, b, w) in edges {
        adj[a].push((b, w));
        adj[b].push((a, w));
    }
    let mut best = vec![u64::MAX; n];
    let mut inside = vec![false; n];
    best[0] = 0;
    let mut total = 0;
    for _ in 0..n {
        let u = (0..n).filter(|&u| !inside[u]).min_by_key(|&u| best[u])?;
        if best[u] == u64::MAX {
            return None;
        }
        inside[u] = true;
        total += best[u];
        for &(v, w) in &adj[u] {
            if !inside[v] && w < best[v] {
                best[v] = w;
            }
        }
    }
    Some(total)
}
