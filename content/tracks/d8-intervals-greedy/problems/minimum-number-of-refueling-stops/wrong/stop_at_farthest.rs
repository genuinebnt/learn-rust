pub fn min_refuel_stops(target: u64, start_fuel: u64, stations: &[(u64, u64)]) -> Option<usize> {
    let mut used = vec![false; stations.len()];
    let mut reach = start_fuel;
    let mut stops = 0;
    while reach < target {
        let pick = (0..stations.len()).rev().find(|&i| !used[i] && stations[i].0 <= reach)?;
        used[pick] = true;
        reach += stations[pick].1;
        stops += 1;
    }
    Some(stops)
}
