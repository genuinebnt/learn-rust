pub fn max_profit(prices: &[u32], fee: u32) -> u64 {
    let fee = fee as i64;
    // The best profit so far if, at the end of today, you are holding a share / not.
    let (mut holding, mut free) = (i64::MIN / 2, 0i64);
    for &p in prices {
        let p = p as i64;
        (holding, free) = (holding.max(free - p), free.max(holding + p - fee));
    }
    free as u64
}
