pub fn coin_change(coins: &[u32], amount: u32) -> Option<u32> {
    let mut sorted = coins.to_vec();
    sorted.sort_unstable_by(|a, b| b.cmp(a));
    let (mut left, mut used) = (amount, 0);
    for c in sorted {
        used += left / c;
        left %= c;
    }
    (left == 0).then_some(used)
}
