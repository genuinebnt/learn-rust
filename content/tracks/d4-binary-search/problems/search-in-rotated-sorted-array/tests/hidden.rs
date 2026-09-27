use solution::*;

#[test]
fn left_part() {
    check!(r#"[4,5,6,7,0,1,2], 5"#, search_rotated(&[4, 5, 6, 7, 0, 1, 2], 5), Some(1));
}

#[test]
fn single_miss() {
    check!(r#"[1], 0"#, search_rotated(&[1], 0), None);
}

#[test]
fn empty() {
    check!(r#"[], 1"#, search_rotated(&[], 1), None);
}

#[test]
fn not_rotated() {
    check!(r#"[1,3,5], 5"#, search_rotated(&[1, 3, 5], 5), Some(2));
}
