pub fn find_redundant(edges: &[(usize, usize)]) -> Option<(usize, usize)> {
    let n = edges.len();
    let mut adj = vec![Vec::new(); n + 1];
    for (i, &(a, b)) in edges.iter().enumerate() {
        adj[a].push((b, i));
        adj[b].push((a, i));
    }
    for skip in (0..n).rev() {
        let mut seen = vec![false; n + 1];
        seen[1] = true;
        let mut stack = vec![1];
        let mut count = 1;
        while let Some(u) = stack.pop() {
            for &(v, i) in &adj[u] {
                if i != skip && !seen[v] {
                    seen[v] = true;
                    count += 1;
                    stack.push(v);
                }
            }
        }
        if count == n {
            return Some(edges[skip]);
        }
    }
    None
}
