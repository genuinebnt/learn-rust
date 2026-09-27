use std::collections::BinaryHeap;

pub fn min_refuel_stops(target: u64, start_fuel: u64, stations: &[(u64, u64)]) -> Option<usize> {
    let mut passed = BinaryHeap::new();
    let mut reach = start_fuel;
    let (mut stops, mut next) = (0, 0);
    while reach < target {
        while next < stations.len() && stations[next].0 < reach {
            passed.push(stations[next].1);
            next += 1;
        }
        reach += passed.pop()?;
        stops += 1;
    }
    Some(stops)
}
