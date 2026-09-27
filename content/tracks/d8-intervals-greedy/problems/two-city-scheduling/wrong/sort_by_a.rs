pub fn two_city_sched_cost(costs: &[(u32, u32)]) -> u64 {
    let mut sorted = costs.to_vec();
    sorted.sort_unstable();
    let (to_a, to_b) = sorted.split_at(costs.len() / 2);
    to_a.iter().map(|&(a, _)| a as u64).sum::<u64>() + to_b.iter().map(|&(_, b)| b as u64).sum::<u64>()
}
