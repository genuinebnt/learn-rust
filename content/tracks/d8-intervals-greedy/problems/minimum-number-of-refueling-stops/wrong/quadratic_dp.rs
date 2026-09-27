pub fn min_refuel_stops(target: u64, start_fuel: u64, stations: &[(u64, u64)]) -> Option<usize> {
    let n = stations.len();
    // far[t]: the farthest position reachable with t stops.
    let mut far = vec![0u64; n + 1];
    far[0] = start_fuel;
    for (i, &(pos, fuel)) in stations.iter().enumerate() {
        for t in (0..=i).rev() {
            if far[t] >= pos {
                far[t + 1] = far[t + 1].max(far[t] + fuel);
            }
        }
    }
    (0..=n).find(|&t| far[t] >= target)
}
