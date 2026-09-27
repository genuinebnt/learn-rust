pub fn max_profit(prices: &[u32], fee: u32) -> u64 {
    prices.windows(2).map(|w| w[1].saturating_sub(w[0]).saturating_sub(fee) as u64).sum()
}
