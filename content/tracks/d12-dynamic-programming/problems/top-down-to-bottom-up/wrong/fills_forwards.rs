/// The cheapest way from stone 0 to the last stone, jumping 1 to k stones forward each time.
pub fn min_cost(heights: &[i32], k: usize) -> u64 {
    let n = heights.len();
    if n == 0 {
        return 0;
    }
    let mut cost = vec![0u64; n];
    for i in 0..n - 1 {
        cost[i] = (i + 1..n.min(i + k + 1))
            .map(|j| heights[i].abs_diff(heights[j]) as u64 + cost[j])
            .min()
            .unwrap();
    }
    cost[0]
}
