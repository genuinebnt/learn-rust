pub fn min_cost(costs: &[[u32; 3]]) -> u64 {
    costs.iter().map(|h| *h.iter().min().unwrap() as u64).sum()
}
