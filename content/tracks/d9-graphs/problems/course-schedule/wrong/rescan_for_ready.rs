pub fn can_finish(n: usize, prereqs: &[(usize, usize)]) -> bool {
    let mut adj = vec![Vec::new(); n];
    let mut indeg = vec![0u32; n];
    for &(a, b) in prereqs {
        adj[a].push(b);
        indeg[b] += 1;
    }
    let mut taken = vec![false; n];
    for _ in 0..n {
        let Some(u) = (0..n).find(|&u| !taken[u] && indeg[u] == 0) else {
            return false;
        };
        taken[u] = true;
        for &v in &adj[u] {
            indeg[v] -= 1;
        }
    }
    true
}
