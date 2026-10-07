use std::collections::VecDeque;

/// Treats every edge as one step, then adds the weights along the BFS tree.
pub fn network_delay(times: &[(usize, usize, u32)], n: usize, k: usize) -> Option<u32> {
    let mut adj = vec![Vec::new(); n + 1];
    for &(u, v, w) in times {
        adj[u].push((v, w));
    }
    let mut dist: Vec<Option<u32>> = vec![None; n + 1];
    dist[k] = Some(0);
    let mut queue = VecDeque::from([k]);
    while let Some(u) = queue.pop_front() {
        for &(v, w) in &adj[u] {
            if dist[v].is_none() {
                dist[v] = Some(dist[u].unwrap() + w);
                queue.push_back(v);
            }
        }
    }
    dist[1..].iter().copied().collect::<Option<Vec<u32>>>()?.into_iter().max()
}
