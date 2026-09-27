pub fn max_matching(left: usize, right: usize, edges: &[(usize, usize)]) -> usize {
    fn augment(u: usize, adj: &[Vec<usize>], seen: &mut [bool], owner: &mut [Option<usize>]) -> bool {
        for &v in &adj[u] {
            if !seen[v] {
                seen[v] = true;
                if owner[v].is_none_or(|w| augment(w, adj, seen, owner)) {
                    owner[v] = Some(u);
                    return true;
                }
            }
        }
        false
    }
    let mut adj = vec![Vec::new(); left];
    for &(u, v) in edges {
        adj[u].push(v);
    }
    let mut owner = vec![None; right];
    (0..left).filter(|&u| augment(u, &adj, &mut vec![false; right], &mut owner)).count()
}
