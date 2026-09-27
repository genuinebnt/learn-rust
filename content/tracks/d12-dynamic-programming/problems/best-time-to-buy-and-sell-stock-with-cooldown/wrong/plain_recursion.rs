fn best(p: &[u32], holding: bool) -> i64 {
    match p {
        [] => 0,
        [x, rest @ ..] => {
            let x = *x as i64;
            let wait = best(rest, holding);
            if holding {
                wait.max(x + best(rest.get(1..).unwrap_or(&[]), false))
            } else {
                wait.max(-x + best(rest, true))
            }
        }
    }
}

pub fn max_profit(prices: &[u32]) -> u64 {
    best(prices, false) as u64
}
