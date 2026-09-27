pub fn max_profit(prices: &[u32]) -> u64 {
    let mut runs: Vec<u64> = Vec::new();
    let mut start = 0;
    for i in 1..=prices.len() {
        if i == prices.len() || prices[i] <= prices[i - 1] {
            if i - 1 > start {
                runs.push((prices[i - 1] - prices[start]) as u64);
            }
            start = i;
        }
    }
    runs.sort_unstable_by(|a, b| b.cmp(a));
    runs.iter().take(2).sum()
}
