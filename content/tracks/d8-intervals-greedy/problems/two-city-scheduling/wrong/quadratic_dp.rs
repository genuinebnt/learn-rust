pub fn two_city_sched_cost(costs: &[(u32, u32)]) -> u64 {
    let half = costs.len() / 2;
    // best[j]: lowest cost so far with j people sent to A.
    let mut best = vec![u64::MAX; half + 1];
    best[0] = 0;
    for (i, &(a, b)) in costs.iter().enumerate() {
        for j in (0..=half.min(i + 1)).rev() {
            let via_b = if best[j] == u64::MAX { u64::MAX } else { best[j] + b as u64 };
            let via_a = if j > 0 && best[j - 1] != u64::MAX { best[j - 1] + a as u64 } else { u64::MAX };
            best[j] = via_a.min(via_b);
        }
    }
    best[half]
}
