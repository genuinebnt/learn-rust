fn cheapest(costs: &[[u32; 3]], last: usize) -> u64 {
    match costs {
        [] => 0,
        [house, rest @ ..] => (0..3).filter(|&c| c != last).map(|c| house[c] as u64 + cheapest(rest, c)).min().unwrap(),
    }
}

pub fn min_cost(costs: &[[u32; 3]]) -> u64 {
    cheapest(costs, 3)
}
