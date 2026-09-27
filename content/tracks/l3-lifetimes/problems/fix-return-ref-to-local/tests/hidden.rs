use solution::*;

#[test]
fn empty() {
    check!(r#""""#, slug(""), String::new());
}
