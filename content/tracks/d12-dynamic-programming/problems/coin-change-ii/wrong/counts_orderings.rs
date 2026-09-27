pub fn change(amount: u32, coins: &[u32]) -> u64 {
    let amount = amount as usize;
    let mut ways = vec![0u64; amount + 1];
    ways[0] = 1;
    for a in 1..=amount {
        for &c in coins {
            if c as usize <= a {
                ways[a] = ways[a].wrapping_add(ways[a - c as usize]);
            }
        }
    }
    ways[amount]
}
