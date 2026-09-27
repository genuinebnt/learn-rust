pub fn is_bipartite(adj: &[Vec<usize>]) -> bool {
    fn paint(u: usize, s: bool, adj: &[Vec<usize>], side: &mut [Option<bool>]) -> bool {
        side[u] = Some(s);
        for &v in &adj[u] {
            match side[v] {
                None => {
                    if !paint(v, !s, adj, side) {
                        return false;
                    }
                }
                Some(t) if t == s => return false,
                Some(_) => {}
            }
        }
        true
    }
    let mut side = vec![None; adj.len()];
    (0..adj.len()).all(|u| side[u].is_some() || paint(u, false, adj, &mut side))
}
