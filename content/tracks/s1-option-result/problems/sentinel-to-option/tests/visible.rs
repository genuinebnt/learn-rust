use solution::*;

#[test]
fn found() {
    check!(r#"v = [4, 8, 15], x = 8"#, find(&[4, 8, 15], 8), Some(1));
}

#[test]
fn missing() {
    check!(r#"v = [4, 8, 15], x = 16"#, find(&[4, 8, 15], 16), None);
}

#[test]
fn empty_slice() {
    check!(r#"v = [], x = 0"#, find(&[], 0), None);
}

#[test]
fn index_zero_is_found() {
    check!(r#"v = [7, 3], x = 7"#, find(&[7, 3], 7), Some(0));
}

#[test]
fn searching_for_minus_one() {
    check!(r#"v = [5, -1], x = -1"#, find(&[5, -1], -1), Some(1));
}
