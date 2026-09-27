use solution::*;

#[test]
fn empty() {
    check!(r#"double an empty cart"#, { let mut c = Cart::new(); c.double_all(); (c.items(), c.total()) }, (vec![], 0));
}
