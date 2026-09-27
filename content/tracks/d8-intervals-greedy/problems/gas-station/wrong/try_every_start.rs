pub fn can_complete_circuit(gas: &[u32], cost: &[u32]) -> Option<usize> {
    let n = gas.len();
    (0..n).find(|&s| {
        let mut tank = 0i64;
        (0..n).all(|k| {
            let i = (s + k) % n;
            tank += gas[i] as i64 - cost[i] as i64;
            tank >= 0
        })
    })
}
