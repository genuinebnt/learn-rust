pub fn can_complete_circuit(gas: &[u32], cost: &[u32]) -> Option<usize> {
    let (mut total, mut tank, mut start) = (0i64, 0i64, 0usize);
    for (i, (&g, &c)) in gas.iter().zip(cost).enumerate() {
        let diff = g as i64 - c as i64;
        total += diff;
        tank += diff;
        if tank < 0 {
            // No start from `start` to `i` gets past `i`.
            start = i + 1;
            tank = 0;
        }
    }
    (total >= 0).then_some(start)
}
