pub fn car_pooling(trips: &[(u32, u32, u32)], capacity: u32) -> bool {
    trips.iter().all(|&(_, x, _)| {
        trips.iter().filter(|t| t.1 <= x && x < t.2).map(|t| t.0 as u64).sum::<u64>() <= capacity as u64
    })
}
