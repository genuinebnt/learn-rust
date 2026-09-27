use solution::*;

#[test]
fn all_equal() {
    check!(r#"[1,1,1], k = 2"#, smallest_distance_pair(&[1, 1, 1], 2), 0);
}

#[test]
fn extremes() {
    check!(r#"[i32::MIN, i32::MAX], k = 1"#, smallest_distance_pair(&[i32::MIN, i32::MAX], 1), u32::MAX);
}

#[test]
fn many() {
    let v: Vec<i32> = (0..10_000).collect();
    check!(r#"0..10⁴, k = 10⁶"#, smallest_distance_pair(&v, 1_000_000), 101);
}
