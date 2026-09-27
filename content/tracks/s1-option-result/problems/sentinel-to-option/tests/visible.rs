use solution::*;

#[test]
fn found() {
    check!(r#"v = [4, 8, 15], x = 8"#, find(&[4, 8, 15], 8), Some(1));
}

#[test]
fn missing() {
    check!(r#"v = [4, 8, 15], x = 16"#, find(&[4, 8, 15], 16), None);
}
