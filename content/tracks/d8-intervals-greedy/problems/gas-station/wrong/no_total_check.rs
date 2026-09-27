pub fn can_complete_circuit(gas: &[u32], cost: &[u32]) -> Option<usize> {
    let (mut tank, mut start) = (0i64, 0usize);
    for i in 0..gas.len() {
        tank += gas[i] as i64 - cost[i] as i64;
        if tank < 0 {
            start = i + 1;
            tank = 0;
        }
    }
    (start < gas.len()).then_some(start)
}
