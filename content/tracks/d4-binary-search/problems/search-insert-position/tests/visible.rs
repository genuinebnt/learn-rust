use solution::*;

#[test]
fn present() {
    check!(r#"[1,3,5,6], 5"#, insert_position(&[1, 3, 5, 6], 5), 2);
}

#[test]
fn between() {
    check!(r#"[1,3,5,6], 2"#, insert_position(&[1, 3, 5, 6], 2), 1);
}
