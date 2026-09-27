fn one_trade(prices: &[u32]) -> u64 {
    let (mut low, mut best) = (u32::MAX, 0u32);
    for &p in prices {
        low = low.min(p);
        best = best.max(p - low);
    }
    best as u64
}

pub fn max_profit(prices: &[u32]) -> u64 {
    (0..=prices.len()).map(|k| one_trade(&prices[..k]) + one_trade(&prices[k..])).max().unwrap_or(0)
}
