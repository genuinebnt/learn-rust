pub fn max_profit(prices: &[u32]) -> u32 {
    let mut lowest = u32::MAX;
    let mut best = 0;
    for &p in prices {
        lowest = lowest.min(p);
        best = best.max(p - lowest);
    }
    best
}
