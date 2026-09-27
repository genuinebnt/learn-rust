use solution::*;

#[test]
fn empty() {
    check!(r#"new registry"#, Registry::new().len(), 0);
}
