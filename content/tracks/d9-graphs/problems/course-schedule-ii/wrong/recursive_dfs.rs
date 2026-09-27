pub fn find_order(n: usize, prereqs: &[(usize, usize)]) -> Option<Vec<usize>> {
    fn visit(u: usize, adj: &[Vec<usize>], state: &mut [u8], out: &mut Vec<usize>) -> bool {
        state[u] = 1;
        for &v in &adj[u] {
            if state[v] == 1 || (state[v] == 0 && !visit(v, adj, state, out)) {
                return false;
            }
        }
        state[u] = 2;
        out.push(u);
        true
    }
    let mut adj = vec![Vec::new(); n];
    for &(a, b) in prereqs {
        adj[a].push(b);
    }
    let mut state = vec![0u8; n];
    let mut out = Vec::new();
    for u in 0..n {
        if state[u] == 0 && !visit(u, &adj, &mut state, &mut out) {
            return None;
        }
    }
    out.reverse();
    Some(out)
}
