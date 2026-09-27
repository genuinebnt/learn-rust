pub fn can_finish(n: usize, prereqs: &[(usize, usize)]) -> bool {
    fn has_cycle(u: usize, adj: &[Vec<usize>], state: &mut [u8]) -> bool {
        state[u] = 1;
        for &v in &adj[u] {
            if state[v] == 1 || (state[v] == 0 && has_cycle(v, adj, state)) {
                return true;
            }
        }
        state[u] = 2;
        false
    }
    let mut adj = vec![Vec::new(); n];
    for &(a, b) in prereqs {
        adj[a].push(b);
    }
    let mut state = vec![0u8; n];
    (0..n).all(|u| state[u] != 0 || !has_cycle(u, &adj, &mut state))
}
