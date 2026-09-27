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
    let n = adj.len();
    let mut dist: Vec<Option<W>> = vec![None; n];
    let mut done = vec![false; n];
    dist[src] = Some(W::ZERO);
    loop {
        let mut pick: Option<(W, usize)> = None;
        for u in 0..n {
            if let (false, Some(d)) = (done[u], dist[u]) {
                if pick.map_or(true, |(best, _)| d < best) {
                    pick = Some((d, u));
                }
            }
        }
        let Some((d, u)) = pick else { break };
        done[u] = true;
        for &(v, w) in &adj[u] {
            if dist[v].is_none_or(|best| d + w < best) {
                dist[v] = Some(d + w);
            }
        }
    }
    dist
}
