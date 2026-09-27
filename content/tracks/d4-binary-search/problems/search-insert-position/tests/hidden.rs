use solution::*;

#[test]
fn after_all() {
    check!(r#"[1,3,5,6], 7"#, insert_position(&[1, 3, 5, 6], 7), 4);
}

#[test]
fn before_all() {
    check!(r#"[1,3,5,6], 0"#, insert_position(&[1, 3, 5, 6], 0), 0);
}

#[test]
fn empty() {
    check!(r#"[], 3"#, insert_position(&[], 3), 0);
}
