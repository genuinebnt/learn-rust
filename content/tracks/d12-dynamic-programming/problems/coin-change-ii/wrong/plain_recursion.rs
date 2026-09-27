fn count(coins: &[u32], amount: u32) -> u64 {
    match coins {
        [] => (amount == 0) as u64,
        [c, rest @ ..] => {
            let skip = count(rest, amount);
            if *c <= amount { skip + count(coins, amount - c) } else { skip }
        }
    }
}

pub fn change(amount: u32, coins: &[u32]) -> u64 {
    count(coins, amount)
}
