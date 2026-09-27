use std::collections::VecDeque;

pub fn build_order(n: usize, deps: &[(usize, usize)]) -> Result<Vec<usize>, Vec<usize>> {
    let mut adj = vec![Vec::new(); n];
    let mut indeg = vec![0u32; n];
    for &(a, b) in deps {
        adj[a].push(b);
        indeg[b] += 1;
    }
    let mut ready: VecDeque<usize> = (0..n).filter(|&u| indeg[u] == 0).collect();
    let mut order = Vec::with_capacity(n);
    while let Some(u) = ready.pop_front() {
        order.push(u);
        for &v in &adj[u] {
            indeg[v] -= 1;
            if indeg[v] == 0 {
                ready.push_back(v);
            }
        }
    }
    if order.len() == n {
        Ok(order)
    } else {
        Err((0..n).filter(|&u| indeg[u] > 0).collect())
    }
}
