use solution::*;

#[test]
fn found() {
    check!(r#"[-1,0,3,5,9,12], 9"#, search(&[-1, 0, 3, 5, 9, 12], 9), Some(4));
}

#[test]
fn missing() {
    check!(r#"[-1,0,3,5,9,12], 2"#, search(&[-1, 0, 3, 5, 9, 12], 2), None);
}
