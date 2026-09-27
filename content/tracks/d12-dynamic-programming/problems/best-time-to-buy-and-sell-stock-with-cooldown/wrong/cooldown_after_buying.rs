pub fn max_profit(prices: &[u32]) -> u64 {
    let (mut holding, mut just_bought, mut free) = (i64::MIN / 2, i64::MIN / 2, 0i64);
    for &p in prices {
        let p = p as i64;
        (holding, just_bought, free) = (holding.max(just_bought), free - p, free.max(holding + p));
    }
    free as u64
}
