pub fn max_profit(prices: &[u32]) -> u32 {
    let Some(&first) = prices.first() else { return 0 };
    prices.iter().map(|&p| p.saturating_sub(first)).max().unwrap_or(0)
}
