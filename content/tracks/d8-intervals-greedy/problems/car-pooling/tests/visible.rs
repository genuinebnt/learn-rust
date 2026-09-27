use solution::*;

#[test]
fn leetcode_too_many() {
    check!(r#"trips = [(2, 1, 5), (3, 3, 7)], capacity = 4"#, car_pooling(&[(2, 1, 5), (3, 3, 7)], 4), false);
}

#[test]
fn leetcode_fits() {
    check!(r#"trips = [(2, 1, 5), (3, 3, 7)], capacity = 5"#, car_pooling(&[(2, 1, 5), (3, 3, 7)], 5), true);
}

#[test]
fn leetcode_three() {
    check!(r#"trips = [(3, 2, 7), (3, 7, 9), (8, 3, 9)], capacity = 11"#, car_pooling(&[(3, 2, 7), (3, 7, 9), (8, 3, 9)], 11), true);
}

#[test]
fn no_trips() {
    check!(r#"trips = [], capacity = 0"#, car_pooling(&[], 0), true);
}

#[test]
fn one_trip_too_big() {
    check!(r#"trips = [(5, 0, 1)], capacity = 4"#, car_pooling(&[(5, 0, 1)], 4), false);
}

#[test]
fn drop_off_first() {
    check!(r#"trips = [(3, 1, 5), (3, 5, 9)], capacity = 3"#, car_pooling(&[(3, 1, 5), (3, 5, 9)], 3), true);
}
