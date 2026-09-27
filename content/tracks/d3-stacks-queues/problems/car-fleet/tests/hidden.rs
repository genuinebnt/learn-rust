use solution::*;

#[test]
fn all_merge() {
    check!(r#"target 100, position [0,2,4], speed [4,2,1]"#, car_fleet(100, &[0, 2, 4], &[4, 2, 1]), 1);
}

#[test]
fn meet_at_target() {
    check!(r#"target 10, position [0,5], speed [2,1]"#, car_fleet(10, &[0, 5], &[2, 1]), 1);
}

#[test]
fn float_trap() {
    check!(r#"target 10⁹; arrival times 10⁻¹⁸ apart, equal in f64"#, car_fleet(1_000_000_000, &[0, 1], &[1_000_000_001, 1_000_000_000]), 2);
}

#[test]
fn none() {
    check!(r#"no cars"#, car_fleet(5, &[], &[]), 0);
}
