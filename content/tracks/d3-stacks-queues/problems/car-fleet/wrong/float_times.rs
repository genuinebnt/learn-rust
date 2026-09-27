pub fn car_fleet(target: u32, position: &[u32], speed: &[u32]) -> usize {
    let mut cars: Vec<(u32, f64)> = position.iter().zip(speed).map(|(&p, &s)| (p, f64::from(target - p) / f64::from(s))).collect();
    cars.sort_by(|a, b| b.0.cmp(&a.0));
    let mut fleets = 0;
    let mut lead = 0.0f64;
    for (_, t) in cars {
        if t > lead {
            fleets += 1;
            lead = t;
        }
    }
    fleets
}
