pub fn max_profit(prices: &[u32]) -> u64 {
    // The best profit so far if, at the end of today, you are…
    let impossible = i64::MIN / 2; // below any real profit, and safe to add to
    let mut holding = impossible; // …holding a share
    let mut cooling = impossible; // …not holding, having sold today
    let mut free = 0i64; // …not holding, free to buy tomorrow
    for &p in prices {
        let p = p as i64;
        (holding, cooling, free) = (holding.max(free - p), holding + p, free.max(cooling));
    }
    free.max(cooling) as u64
}
