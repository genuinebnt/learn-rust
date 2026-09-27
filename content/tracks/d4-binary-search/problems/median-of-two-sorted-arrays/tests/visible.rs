use solution::*;

#[test]
fn odd() {
    check!(r#"[1,3], [2]"#, median(&[1, 3], &[2]), Some(2.0));
}

#[test]
fn even() {
    check!(r#"[1,2], [3,4]"#, median(&[1, 2], &[3, 4]), Some(2.5));
}
