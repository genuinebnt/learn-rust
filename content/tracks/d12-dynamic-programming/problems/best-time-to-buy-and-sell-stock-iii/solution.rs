pub fn max_profit(prices: &[u32]) -> u64 {
    // The best profit so far after the first buy, first sell, second buy, second sell.
    let impossible = i64::MIN / 2;
    let (mut buy1, mut sell1, mut buy2, mut sell2) = (impossible, 0i64, impossible, 0i64);
    for &p in prices {
        let p = p as i64;
        buy1 = buy1.max(-p);
        sell1 = sell1.max(buy1 + p);
        buy2 = buy2.max(sell1 - p);
        sell2 = sell2.max(buy2 + p);
    }
    sell2 as u64
}
