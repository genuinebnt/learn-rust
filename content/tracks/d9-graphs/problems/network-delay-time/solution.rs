use std::cmp::Reverse;
use std::collections::BinaryHeap;

/// How long a signal sent from `k` takes to reach every node, or `None` if
/// some node never hears it. Nodes are labelled `1..=n`; `(u, v, w)` is a
/// directed edge that takes `w` ms.
pub fn network_delay(times: &[(usize, usize, u32)], n: usize, k: usize) -> Option<u32> {
    let mut adj = vec![Vec::new(); n + 1];
    for &(u, v, w) in times {
        adj[u].push((v, w));
    }

    let mut dist = vec![u32::MAX; n + 1];
    let mut heap = BinaryHeap::new();
    dist[k] = 0;
    heap.push(Reverse((0, k)));

    while let Some(Reverse((d, u))) = heap.pop() {
        if d > dist[u] {
            continue;
        }
        for &(v, w) in &adj[u] {
            let nd = d + w;
            if nd < dist[v] {
                dist[v] = nd;
                heap.push(Reverse((nd, v)));
            }
        }
    }

    let max = *dist[1..].iter().max()?;
    (max != u32::MAX).then_some(max)
}
