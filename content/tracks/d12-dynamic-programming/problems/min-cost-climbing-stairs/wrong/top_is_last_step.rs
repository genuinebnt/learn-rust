pub fn min_cost_climbing_stairs(cost: &[u32]) -> u64 {
    let n = cost.len();
    if n < 2 { return 0; }
    let mut pay = vec![0u64; n];
    pay[0] = cost[0] as u64;
    pay[1] = cost[1] as u64;
    for i in 2..n {
        pay[i] = cost[i] as u64 + pay[i - 1].min(pay[i - 2]);
    }
    pay[n - 1]
}
