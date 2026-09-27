use solution::*;

#[test]
fn first() {
    check!(r#"names = ["x", "y"], id("x")"#, Registry::new(&["x", "y"]).id("x"), Some(0));
}
