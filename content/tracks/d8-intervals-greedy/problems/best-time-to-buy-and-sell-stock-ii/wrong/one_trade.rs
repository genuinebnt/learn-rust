pub fn max_profit(prices: &[u32]) -> u64 {
    let mut low = u32::MAX;
    let mut best = 0u64;
    for &p in prices {
        low = low.min(p);
        best = best.max((p - low) as u64);
    }
    best
}
