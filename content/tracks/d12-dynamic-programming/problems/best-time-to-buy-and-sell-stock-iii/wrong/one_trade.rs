pub fn max_profit(prices: &[u32]) -> u64 {
    let (mut low, mut best) = (u32::MAX, 0u32);
    for &p in prices {
        low = low.min(p);
        best = best.max(p - low);
    }
    best as u64
}
