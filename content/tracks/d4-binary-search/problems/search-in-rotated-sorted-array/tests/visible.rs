use solution::*;

#[test]
fn found() {
    check!(r#"[4,5,6,7,0,1,2], 0"#, search_rotated(&[4, 5, 6, 7, 0, 1, 2], 0), Some(4));
}

#[test]
fn missing() {
    check!(r#"[4,5,6,7,0,1,2], 3"#, search_rotated(&[4, 5, 6, 7, 0, 1, 2], 3), None);
}
