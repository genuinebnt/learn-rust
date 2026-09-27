pub fn max_profit(prices: &[u32]) -> u64 {
    let mut total = 0u32;
    for w in prices.windows(2) {
        total = total.wrapping_add(w[1].saturating_sub(w[0]));
    }
    total as u64
}
