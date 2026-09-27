pub fn find_cheapest_price(n: usize, flights: &[(usize, usize, u32)], src: usize, dst: usize, k: usize) -> Option<u32> {
    fn walk(adj: &[Vec<(usize, u32)>], at: usize, dst: usize, left: usize, cost: u32, best: &mut Option<u32>) {
        if at == dst {
            *best = Some(best.map_or(cost, |b| b.min(cost)));
            return;
        }
        if left == 0 {
            return;
        }
        for &(v, p) in &adj[at] {
            walk(adj, v, dst, left - 1, cost + p, best);
        }
    }
    let mut adj = vec![Vec::new(); n];
    for &(u, v, p) in flights {
        adj[u].push((v, p));
    }
    let mut best = None;
    walk(&adj, src, dst, k + 1, 0, &mut best);
    best
}
