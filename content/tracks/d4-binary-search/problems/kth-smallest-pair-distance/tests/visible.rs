use solution::*;

#[test]
fn zero() {
    check!(r#"[1,3,1], k = 1"#, smallest_distance_pair(&[1, 3, 1], 1), 0);
}

#[test]
fn largest() {
    check!(r#"[1,6,1], k = 3"#, smallest_distance_pair(&[1, 6, 1], 3), 5);
}
