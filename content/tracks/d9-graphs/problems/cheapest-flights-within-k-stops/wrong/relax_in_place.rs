pub fn find_cheapest_price(n: usize, flights: &[(usize, usize, u32)], src: usize, dst: usize, k: usize) -> Option<u32> {
    let mut best = vec![u32::MAX; n];
    best[src] = 0;
    for _ in 0..=k {
        for &(u, v, price) in flights {
            if best[u] != u32::MAX && best[u] + price < best[v] {
                best[v] = best[u] + price;
            }
        }
    }
    (best[dst] != u32::MAX).then_some(best[dst])
}
