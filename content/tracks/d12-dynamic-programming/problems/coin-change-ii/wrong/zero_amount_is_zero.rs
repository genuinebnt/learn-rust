pub fn change(amount: u32, coins: &[u32]) -> u64 {
    if amount == 0 {
        return 0;
    }
    let amount = amount as usize;
    let mut ways = vec![0u64; amount + 1];
    ways[0] = 1;
    for &c in coins {
        for a in c as usize..=amount {
            ways[a] += ways[a - c as usize];
        }
    }
    ways[amount]
}
