use solution::*;

#[test]
fn present() {
    check!(r#"[1,3,5,6], 5"#, insert_position(&[1, 3, 5, 6], 5), 2);
}

#[test]
fn between() {
    check!(r#"[1,3,5,6], 2"#, insert_position(&[1, 3, 5, 6], 2), 1);
}

#[test]
fn past_the_end() {
    check!(r#"[1,3,5,6], 7"#, insert_position(&[1, 3, 5, 6], 7), 4);
}

#[test]
fn before_the_start() {
    check!(r#"[2,4], 1"#, insert_position(&[2, 4], 1), 0);
}

#[test]
fn empty_slice() {
    check!(r#"[], 5"#, insert_position(&[], 5), 0);
}
