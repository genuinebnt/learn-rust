pub fn find_cheapest_price(n: usize, flights: &[(usize, usize, u32)], src: usize, dst: usize, k: usize) -> Option<u32> {
    let mut best = vec![u32::MAX; n];
    best[src] = 0;
    for _ in 0..=k {
        let prev = best.to_vec();
        for &(u, v, price) in flights {
            if prev[u] != u32::MAX && prev[u] + price < best[v] {
                best[v] = prev[u] + price;
            }
        }
    }
    (best[dst] != u32::MAX).then_some(best[dst])
}
