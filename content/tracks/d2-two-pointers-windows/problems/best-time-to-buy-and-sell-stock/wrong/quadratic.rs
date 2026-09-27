pub fn max_profit(prices: &[u32]) -> u32 {
    let mut best = 0;
    for i in 0..prices.len() {
        for j in i + 1..prices.len() {
            best = best.max(prices[j].saturating_sub(prices[i]));
        }
    }
    best
}
