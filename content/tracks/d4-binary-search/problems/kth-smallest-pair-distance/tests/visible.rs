use solution::*;

#[test]
fn zero() {
    check!(r#"[1,3,1], k = 1"#, smallest_distance_pair(&[1, 3, 1], 1), 0);
}

#[test]
fn largest() {
    check!(r#"[1,6,1], k = 3"#, smallest_distance_pair(&[1, 6, 1], 3), 5);
}

#[test]
fn equal_values() {
    check!(r#"[1,1,1], k = 2"#, smallest_distance_pair(&[1, 1, 1], 2), 0);
}

#[test]
fn one_pair() {
    check!(r#"[5,1], k = 1"#, smallest_distance_pair(&[5, 1], 1), 4);
}

#[test]
fn repeated_distances_count_separately() {
    check!(r#"[1,1,2], k = 3"#, smallest_distance_pair(&[1, 1, 2], 3), 1);
}
