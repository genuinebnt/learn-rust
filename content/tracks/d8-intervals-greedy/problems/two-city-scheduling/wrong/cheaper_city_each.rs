pub fn two_city_sched_cost(costs: &[(u32, u32)]) -> u64 {
    costs.iter().map(|&(a, b)| a.min(b) as u64).sum()
}
