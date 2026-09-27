pub fn coin_change(coins: &[u32], amount: u32) -> Option<u32> {
    if amount == 0 {
        return Some(0);
    }
    coins.iter().filter(|&&c| c <= amount).filter_map(|&c| coin_change(coins, amount - c)).min().map(|n| n + 1)
}
