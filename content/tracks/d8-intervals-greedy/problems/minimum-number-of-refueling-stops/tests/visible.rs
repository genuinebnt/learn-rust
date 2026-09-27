use solution::*;

#[test]
fn leetcode_already_there() {
    check!(r#"target = 1, start_fuel = 1, stations = []"#, min_refuel_stops(1, 1, &[]), Some(0));
}

#[test]
fn leetcode_cannot_reach() {
    check!(r#"target = 100, start_fuel = 1, stations = [(10, 100)]"#, min_refuel_stops(100, 1, &[(10, 100)]), None);
}

#[test]
fn leetcode_two_stops() {
    check!(r#"target = 100, start_fuel = 10, stations = [(10, 60), (20, 30), (30, 30), (60, 40)]"#, min_refuel_stops(100, 10, &[(10, 60), (20, 30), (30, 30), (60, 40)]), Some(2));
}

#[test]
fn exact_fuel_no_stations() {
    check!(r#"target = 10, start_fuel = 10, stations = []"#, min_refuel_stops(10, 10, &[]), Some(0));
}

#[test]
fn arrive_empty_at_a_station() {
    check!(r#"target = 100, start_fuel = 50, stations = [(50, 50)]"#, min_refuel_stops(100, 50, &[(50, 50)]), Some(1));
}

#[test]
fn richest_not_farthest() {
    check!(r#"target = 100, start_fuel = 50, stations = [(10, 50), (50, 10)]"#, min_refuel_stops(100, 50, &[(10, 50), (50, 10)]), Some(1));
}
