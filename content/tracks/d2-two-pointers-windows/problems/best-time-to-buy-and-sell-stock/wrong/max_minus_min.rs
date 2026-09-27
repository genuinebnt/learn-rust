pub fn max_profit(prices: &[u32]) -> u32 {
    let hi = prices.iter().copied().max().unwrap_or(0);
    let lo = prices.iter().copied().min().unwrap_or(0);
    hi - lo
}
