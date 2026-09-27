use std::collections::VecDeque;

pub fn find_min_height_trees(n: usize, edges: &[(usize, usize)]) -> Vec<usize> {
    let mut adj = vec![Vec::new(); n];
    for &(a, b) in edges {
        adj[a].push(b);
        adj[b].push(a);
    }
    let height = |root: usize| {
        let mut d = vec![usize::MAX; n];
        d[root] = 0;
        let mut q = VecDeque::from([root]);
        let mut far = 0;
        while let Some(u) = q.pop_front() {
            far = d[u];
            for &v in &adj[u] {
                if d[v] == usize::MAX {
                    d[v] = d[u] + 1;
                    q.push_back(v);
                }
            }
        }
        far
    };
    let h: Vec<usize> = (0..n).map(height).collect();
    let best = h.iter().copied().min().unwrap_or(0);
    (0..n).filter(|&u| h[u] == best).collect()
}
