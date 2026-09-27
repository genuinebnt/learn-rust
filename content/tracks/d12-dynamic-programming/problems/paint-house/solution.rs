pub fn min_cost(costs: &[[u32; 3]]) -> u64 {
    // best[c] = the cheapest way to paint the houses so far, the last one in colour c.
    let mut best = [0u64; 3];
    for house in costs {
        best = [
            house[0] as u64 + best[1].min(best[2]),
            house[1] as u64 + best[0].min(best[2]),
            house[2] as u64 + best[0].min(best[1]),
        ];
    }
    best.into_iter().min().unwrap()
}
