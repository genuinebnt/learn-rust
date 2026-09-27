use std::collections::VecDeque;

pub fn can_finish(n: usize, prereqs: &[(usize, usize)]) -> bool {
    let mut adj = vec![Vec::new(); n];
    let mut indeg = vec![0u32; n];
    for &(a, b) in prereqs {
        adj[a].push(b);
        indeg[b] += 1;
    }
    let mut ready: VecDeque<usize> = (0..n).filter(|&u| indeg[u] == 0).collect();
    let mut taken = 0;
    while let Some(u) = ready.pop_front() {
        taken += 1;
        for &v in &adj[u] {
            indeg[v] -= 1;
            if indeg[v] == 0 {
                ready.push_back(v);
            }
        }
    }
    taken == n
}
