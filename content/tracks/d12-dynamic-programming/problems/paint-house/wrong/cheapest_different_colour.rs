pub fn min_cost(costs: &[[u32; 3]]) -> u64 {
    let mut last = 3;
    let mut total = 0u64;
    for house in costs {
        let c = (0..3).filter(|&c| c != last).min_by_key(|&c| house[c]).unwrap();
        total += house[c] as u64;
        last = c;
    }
    total
}
