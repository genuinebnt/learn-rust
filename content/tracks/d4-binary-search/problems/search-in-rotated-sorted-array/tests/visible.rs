use solution::*;

#[test]
fn found() {
    check!(r#"[4,5,6,7,0,1,2], 0"#, search_rotated(&[4, 5, 6, 7, 0, 1, 2], 0), Some(4));
}

#[test]
fn missing() {
    check!(r#"[4,5,6,7,0,1,2], 3"#, search_rotated(&[4, 5, 6, 7, 0, 1, 2], 3), None);
}

#[test]
fn single_missing() {
    check!(r#"[1], 0"#, search_rotated(&[1], 0), None);
}

#[test]
fn in_the_first_run() {
    check!(r#"[4,5,6,7,0,1,2], 6"#, search_rotated(&[4, 5, 6, 7, 0, 1, 2], 6), Some(2));
}

#[test]
fn empty_slice() {
    check!(r#"[], 5"#, search_rotated(&[], 5), None);
}
