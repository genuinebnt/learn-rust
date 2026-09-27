use solution::*;

#[test]
fn single() {
    check!(r#"[1], k = 1"#, shortest_subarray(&[1], 1), Some(1));
}

#[test]
fn impossible() {
    check!(r#"[1,2], k = 4"#, shortest_subarray(&[1, 2], 4), None);
}

#[test]
fn negative_inside() {
    check!(r#"[2,-1,2], k = 3"#, shortest_subarray(&[2, -1, 2], 3), Some(3));
}
