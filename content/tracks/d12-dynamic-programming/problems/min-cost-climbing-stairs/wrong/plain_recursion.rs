fn best(cost: &[u32], at: usize) -> u64 {
    if at >= cost.len() { return 0; }
    cost[at] as u64 + best(cost, at + 1).min(best(cost, at + 2))
}

pub fn min_cost_climbing_stairs(cost: &[u32]) -> u64 {
    best(cost, 0).min(best(cost, 1))
}
