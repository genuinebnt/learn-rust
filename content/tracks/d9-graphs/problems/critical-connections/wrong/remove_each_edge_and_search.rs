pub fn critical_connections(n: usize, edges: &[(usize, usize)]) -> Vec<(usize, usize)> {
    let mut adj = vec![Vec::new(); n];
    for (id, &(a, b)) in edges.iter().enumerate() {
        adj[a].push((b, id));
        adj[b].push((a, id));
    }
    let mut out = Vec::new();
    for (skip, &(a, b)) in edges.iter().enumerate() {
        let mut seen = vec![false; n];
        seen[a] = true;
        let mut stack = vec![a];
        while let Some(u) = stack.pop() {
            if u == b {
                break;
            }
            for &(v, id) in &adj[u] {
                if id != skip && !seen[v] {
                    seen[v] = true;
                    stack.push(v);
                }
            }
        }
        if !seen[b] {
            out.push((a.min(b), a.max(b)));
        }
    }
    out.sort_unstable();
    out
}
