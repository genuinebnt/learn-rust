use solution::*;

#[test]
fn found() {
    check!(r#"names = ["a", "b"], id("b")"#, Registry::new(&["a", "b"]).id("b"), Some(1));
}

#[test]
fn missing() {
    check!(r#"names = ["a"], id("z")"#, Registry::new(&["a"]).id("z"), None);
}
