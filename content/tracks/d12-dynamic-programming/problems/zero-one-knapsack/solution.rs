pub fn knapsack(items: &[(usize, u64)], capacity: usize) -> u64 {
    // best[c] = the most value with total weight ≤ c, using the items seen so far.
    let mut best = vec![0u64; capacity + 1];
    for &(weight, value) in items {
        // Downwards, so best[c - weight] doesn't include this item yet: each item once.
        for c in (weight..=capacity).rev() {
            best[c] = best[c].max(best[c - weight] + value);
        }
    }
    best[capacity]
}
