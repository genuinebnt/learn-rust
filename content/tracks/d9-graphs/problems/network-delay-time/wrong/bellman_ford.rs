pub fn network_delay(times: &[(usize, usize, u32)], n: usize, k: usize) -> Option<u32> {
    let mut dist = vec![u32::MAX; n + 1];
    dist[k] = 0;
    for _ in 1..n {
        let mut changed = false;
        for &(u, v, w) in times {
            if dist[u] != u32::MAX && dist[u] + w < dist[v] {
                dist[v] = dist[u] + w;
                changed = true;
            }
        }
        if !changed {
            break;
        }
    }
    let max = *dist[1..].iter().max()?;
    (max != u32::MAX).then_some(max)
}
