pub fn two_city_sched_cost(costs: &[(u32, u32)]) -> u64 {
    let mut by_gain = costs.to_vec();
    // Most money saved by choosing A first.
    by_gain.sort_unstable_by_key(|&(a, b)| a as i64 - b as i64);
    let (to_a, to_b) = by_gain.split_at(costs.len() / 2);
    to_a.iter().map(|&(a, _)| a as u64).sum::<u64>() + to_b.iter().map(|&(_, b)| b as u64).sum::<u64>()
}
