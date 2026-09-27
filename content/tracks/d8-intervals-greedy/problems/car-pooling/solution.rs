pub fn car_pooling(trips: &[(u32, u32, u32)], capacity: u32) -> bool {
    let mut events: Vec<(u32, i64)> = Vec::with_capacity(2 * trips.len());
    for &(people, from, to) in trips {
        events.push((from, people as i64));
        events.push((to, -(people as i64)));
    }
    // At the same stop, the negative (drop-off) changes sort first.
    events.sort_unstable();
    let mut load = 0i64;
    for (_, change) in events {
        load += change;
        if load > capacity as i64 {
            return false;
        }
    }
    true
}
