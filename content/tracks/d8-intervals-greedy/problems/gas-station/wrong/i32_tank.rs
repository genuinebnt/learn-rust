pub fn can_complete_circuit(gas: &[u32], cost: &[u32]) -> Option<usize> {
    let (mut total, mut tank, mut start) = (0i32, 0i32, 0usize);
    for i in 0..gas.len() {
        let diff = gas[i] as i32 - cost[i] as i32;
        total += diff;
        tank += diff;
        if tank < 0 {
            start = i + 1;
            tank = 0;
        }
    }
    (total >= 0).then_some(start)
}
