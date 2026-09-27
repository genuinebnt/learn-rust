pub fn max_profit(k: usize, prices: &[u32]) -> u64 {
    let mut buy = vec![i64::MIN / 2; k + 1];
    let mut sell = vec![0i64; k + 1];
    for &p in prices {
        let p = p as i64;
        for j in 1..=k {
            buy[j] = buy[j].max(sell[j - 1] - p);
            sell[j] = sell[j].max(buy[j] + p);
        }
    }
    sell[k] as u64
}
