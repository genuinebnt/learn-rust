pub fn coin_change(coins: &[u32], amount: u32) -> Option<u32> {
    let amount = amount as usize;
    let mut fewest = vec![u32::MAX; amount + 1];
    fewest[0] = 0;
    for a in 1..=amount {
        for &c in coins {
            if c as usize <= a {
                fewest[a] = fewest[a].min(fewest[a - c as usize] + 1);
            }
        }
    }
    (fewest[amount] != u32::MAX).then_some(fewest[amount])
}
