use solution::*;

#[test]
fn no_fuel_no_stations() {
    check!(r#"target = 5, start_fuel = 0, stations = []"#, min_refuel_stops(5, 0, &[]), None);
}

#[test]
fn no_fuel_to_first_station() {
    check!(r#"target = 5, start_fuel = 0, stations = [(1, 10)]"#, min_refuel_stops(5, 0, &[(1, 10)]), None);
}

#[test]
fn station_out_of_reach() {
    check!(r#"target = 10, start_fuel = 1, stations = [(2, 100)]"#, min_refuel_stops(10, 1, &[(2, 100)]), None);
}

#[test]
fn forced_every_stop() {
    check!(r#"target = 100, start_fuel = 25, stations = [(25, 25), (50, 50)]"#, min_refuel_stops(100, 25, &[(25, 25), (50, 50)]), Some(2));
}

#[test]
fn leetcode_ten_none() {
    check!(r#"target = 1000, start_fuel = 83, stations = [(25, 27), (36, 187), (140, 186), (378, 6), (492, 202), (517, 89), (579, 234), (673, 86), (808, 53), (954, 49)]"#, min_refuel_stops(1000, 83, &[(25, 27), (36, 187), (140, 186), (378, 6), (492, 202), (517, 89), (579, 234), (673, 86), (808, 53), (954, 49)]), None);
}

#[test]
fn leetcode_ten_four() {
    check!(r#"target = 1000, start_fuel = 299, stations = [(13, 21), (26, 115), (100, 47), (225, 99), (299, 141), (444, 198), (608, 190), (636, 157), (647, 255), (841, 123)]"#, min_refuel_stops(1000, 299, &[(13, 21), (26, 115), (100, 47), (225, 99), (299, 141), (444, 198), (608, 190), (636, 157), (647, 255), (841, 123)]), Some(4));
}

#[test]
fn reach_past_u32() {
    check!(r#"target = 10¹², start_fuel = 10⁹, stations = (k·10⁹, 10⁹) for k in 1..1000"#, min_refuel_stops(1_000_000_000_000, 1_000_000_000, &(1..1000u64).map(|k| (k * 1_000_000_000, 1_000_000_000)).collect::<Vec<_>>()), Some(999));
}

#[test]
fn plenty_of_fuel() {
    check!(r#"target = 50, start_fuel = 100, stations = [(10, 5), (20, 5)]"#, min_refuel_stops(50, 100, &[(10, 5), (20, 5)]), Some(0));
}

#[test]
fn one_short() {
    check!(r#"target = 100, start_fuel = 50, stations = [(50, 49)]"#, min_refuel_stops(100, 50, &[(50, 49)]), None);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(828);
    for _ in 0..400 {
        let target = rng.int(1, 30) as u64;
        let start_fuel = rng.int(0, 12) as u64;
        let n = rng.below(8);
        let mut stations = Vec::new();
        let mut pos = 0u64;
        for _ in 0..n {
            pos += rng.int(1, 5) as u64;
            if pos >= target {
                break;
            }
            let fuel = rng.int(1, 10) as u64;
            stations.push((pos, fuel));
        }
        // Every set of stops, driven in order.
        let mut want: Option<usize> = None;
        for mask in 0u32..1 << stations.len() {
            let mut reach = start_fuel;
            for (i, &(pos, fuel)) in stations.iter().enumerate() {
                if pos > reach {
                    break;
                }
                if mask >> i & 1 == 1 {
                    reach += fuel;
                }
            }
            if reach >= target {
                let c = mask.count_ones() as usize;
                want = Some(want.map_or(c, |w| w.min(c)));
            }
        }
        check!(format!("target = {target}, start_fuel = {start_fuel}, stations = {stations:?}"), min_refuel_stops(target, start_fuel, &stations), want);
    }
}

#[test]
fn scale_200k() {
    let stations: Vec<(u64, u64)> = (1..=200_000).map(|p| (p, 1)).collect();
    check!(
        "stations (p, 1) for p in 1..=200000, start_fuel = 1, target = 200001 and 200002",
        (min_refuel_stops(200_001, 1, &stations), min_refuel_stops(200_002, 1, &stations)),
        (Some(200_000), None)
    );
}
