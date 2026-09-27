use solution::*;

#[test]
fn three() {
    check!(r#"target 12, position [10,8,0,5,3], speed [2,4,1,1,3]"#, car_fleet(12, &[10, 8, 0, 5, 3], &[2, 4, 1, 1, 3]), 3);
}

#[test]
fn one_car() {
    check!(r#"target 10, position [3], speed [3]"#, car_fleet(10, &[3], &[3]), 1);
}

#[test]
fn all_merge() {
    check!(r#"target 100, position [0,2,4], speed [4,2,1]"#, car_fleet(100, &[0, 2, 4], &[4, 2, 1]), 1);
}

#[test]
fn meet_at_target() {
    check!(r#"target 10, position [0,5], speed [2,1]"#, car_fleet(10, &[0, 5], &[2, 1]), 1);
}

#[test]
fn none() {
    check!(r#"no cars"#, car_fleet(5, &[], &[]), 0);
}
