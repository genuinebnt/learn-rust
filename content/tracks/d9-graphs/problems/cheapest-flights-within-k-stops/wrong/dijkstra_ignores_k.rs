use std::cmp::Reverse;
use std::collections::BinaryHeap;

pub fn find_cheapest_price(n: usize, flights: &[(usize, usize, u32)], src: usize, dst: usize, _k: usize) -> Option<u32> {
    let mut adj = vec![Vec::new(); n];
    for &(u, v, p) in flights {
        adj[u].push((v, p));
    }
    let mut dist = vec![u32::MAX; n];
    dist[src] = 0;
    let mut heap = BinaryHeap::from([Reverse((0u32, src))]);
    while let Some(Reverse((d, u))) = heap.pop() {
        if d > dist[u] {
            continue;
        }
        for &(v, p) in &adj[u] {
            if d + p < dist[v] {
                dist[v] = d + p;
                heap.push(Reverse((d + p, v)));
            }
        }
    }
    (dist[dst] != u32::MAX).then_some(dist[dst])
}
