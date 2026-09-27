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

#[test]
fn mixed() {
    check!(r#"[84,-37,32,40,95], k = 167"#, shortest_subarray(&[84, -37, 32, 40, 95], 167), Some(3));
}

#[test]
fn whole_array() {
    check!(r#"[1,1,1], k = 3"#, shortest_subarray(&[1, 1, 1], 3), Some(3));
}
