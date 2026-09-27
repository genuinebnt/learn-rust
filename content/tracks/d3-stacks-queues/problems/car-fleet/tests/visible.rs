use solution::*;

#[test]
fn three() {
    check!(r#"target 12, position [10,8,0,5,3], speed [2,4,1,1,3]"#, car_fleet(12, &[10, 8, 0, 5, 3], &[2, 4, 1, 1, 3]), 3);
}

#[test]
fn one_car() {
    check!(r#"target 10, position [3], speed [3]"#, car_fleet(10, &[3], &[3]), 1);
}
