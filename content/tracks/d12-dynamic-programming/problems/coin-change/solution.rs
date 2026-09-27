pub fn coin_change(coins: &[u32], amount: u32) -> Option<u32> {
    let amount = amount as usize;
    // fewest[a] = the fewest coins that make a, or None if a can't be made.
    let mut fewest: Vec<Option<u32>> = vec![None; amount + 1];
    fewest[0] = Some(0);
    for a in 1..=amount {
        fewest[a] = coins
            .iter()
            .filter(|&&c| c as usize <= a)
            .filter_map(|&c| fewest[a - c as usize])
            .min()
            .map(|n| n + 1);
    }
    fewest[amount]
}
