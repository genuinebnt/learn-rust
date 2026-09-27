use solution::*;

#[test]
fn found() {
    check!(r#"names = ["a", "b"], id("b")"#, Registry::new(&["a", "b"]).id("b"), Some(1));
}

#[test]
fn missing() {
    check!(r#"names = ["a"], id("z")"#, Registry::new(&["a"]).id("z"), None);
}

#[test]
fn first() {
    check!(r#"names = ["x", "y"], id("x")"#, Registry::new(&["x", "y"]).id("x"), Some(0));
}

#[test]
fn case_sensitive() {
    check!(r#"names = ["A"], id("a")"#, Registry::new(&["A"]).id("a"), None);
}

#[test]
fn empty_registry() {
    check!(r#"names = [], id("a")"#, Registry::new(&[]).id("a"), None);
}
