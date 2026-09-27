pub fn min_cost_climbing_stairs(cost: &[u32]) -> u64 {
    // reach[i] = cheapest way to stand on step i; reach[0] = reach[1] = 0.
    let (mut two_back, mut one_back) = (0u64, 0u64);
    for i in 2..=cost.len() {
        let here = (one_back + cost[i - 1] as u64).min(two_back + cost[i - 2] as u64);
        (two_back, one_back) = (one_back, here);
    }
    one_back
}
