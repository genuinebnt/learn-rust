pub fn min_cost_climbing_stairs(cost: &[u32]) -> u64 {
    let (mut two_back, mut one_back) = (0u64, cost.first().map_or(0, |&c| c as u64));
    for i in 2..=cost.len() {
        let here = (one_back + cost[i - 1] as u64).min(two_back + cost[i - 2] as u64);
        (two_back, one_back) = (one_back, here);
    }
    if cost.len() < 2 { 0 } else { one_back }
}
