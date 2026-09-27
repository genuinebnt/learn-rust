fn best(p: &[u32], fee: i64, holding: bool) -> i64 {
    match p {
        [] => 0,
        [x, rest @ ..] => {
            let x = *x as i64;
            let wait = best(rest, fee, holding);
            if holding { wait.max(x - fee + best(rest, fee, false)) } else { wait.max(-x + best(rest, fee, true)) }
        }
    }
}

pub fn max_profit(prices: &[u32], fee: u32) -> u64 {
    best(prices, fee as i64, false) as u64
}
