use solution::*;

#[test]
fn single() {
    check!(r#"v = [5]"#, is_mirror(&[5]), true);
}

#[test]
fn even() {
    check!(r#"v = [3, 4, 4, 3]"#, is_mirror(&[3, 4, 4, 3]), true);
}
