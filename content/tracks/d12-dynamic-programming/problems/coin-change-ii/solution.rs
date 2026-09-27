pub fn change(amount: u32, coins: &[u32]) -> u64 {
    let amount = amount as usize;
    // ways[a] = combinations of the coins seen so far that make a.
    let mut ways = vec![0u64; amount + 1];
    ways[0] = 1;
    // Coins outside: each combination is built in coin order, so it is counted once.
    for &c in coins {
        for a in c as usize..=amount {
            ways[a] += ways[a - c as usize];
        }
    }
    ways[amount]
}
