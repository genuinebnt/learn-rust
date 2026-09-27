use std::cmp::Reverse;
use std::collections::BinaryHeap;
use std::ops::Add;

/// What Dijkstra needs from a weight. Weights must never be "negative":
/// `a + w >= a` for every weight `w`.
pub trait Weight: Copy + Ord + Add<Output = Self> {
    const ZERO: Self;
}

impl Weight for u32 {
    const ZERO: u32 = 0;
}

impl Weight for u64 {
    const ZERO: u64 = 0;
}

pub fn dijkstra<W: Weight>(adj: &[Vec<(usize, W)>], src: usize) -> Vec<Option<W>> {
    let mut dist: Vec<Option<W>> = vec![None; adj.len()];
    dist[src] = Some(W::ZERO);
    let mut heap = BinaryHeap::from([Reverse((W::ZERO, src))]);
    while let Some(Reverse((d, u))) = heap.pop() {
        for &(v, w) in &adj[u] {
            if dist[v].is_none() {
                dist[v] = Some(d + w);
                heap.push(Reverse((d + w, v)));
            }
        }
    }
    dist
}
