pub fn knapsack(items: &[(usize, u64)], capacity: usize) -> u64 {
    let mut best = vec![0u64; capacity + 1];
    for &(weight, value) in items {
        for c in weight.max(1)..=capacity {
            best[c] = best[c].max(best[c - weight] + value);
        }
    }
    best[capacity]
}
