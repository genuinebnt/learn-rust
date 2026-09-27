pub fn car_fleet(target: u32, position: &[u32], speed: &[u32]) -> usize {
    let mut cars: Vec<(u64, u64)> = position
        .iter()
        .zip(speed)
        .map(|(&p, &s)| (u64::from(target - p), u64::from(s)))
        .collect();
    cars.sort_unstable();
    let mut fleets = 0;
    let mut lead: Option<(u64, u64)> = None;
    for (d, s) in cars {
        if lead.is_none_or(|(ld, ls)| d * ls >= ld * s) {
            fleets += 1;
            lead = Some((d, s));
        }
    }
    fleets
}
