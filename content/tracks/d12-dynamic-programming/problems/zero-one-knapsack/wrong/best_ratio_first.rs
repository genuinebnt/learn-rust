pub fn knapsack(items: &[(usize, u64)], capacity: usize) -> u64 {
    let mut sorted = items.to_vec();
    sorted.sort_by(|a, b| (b.1 * a.0.max(1) as u64).cmp(&(a.1 * b.0.max(1) as u64)));
    let (mut left, mut total) = (capacity, 0);
    for (w, v) in sorted {
        if w <= left {
            left -= w;
            total += v;
        }
    }
    total
}
