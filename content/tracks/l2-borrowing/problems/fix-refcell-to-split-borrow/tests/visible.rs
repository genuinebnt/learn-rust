use solution::*;

#[test]
fn doubles() {
    check!(r#"add 3, 4; double"#, { let mut c = Cart::new(); c.add(3); c.add(4); c.double_all(); (c.items(), c.total()) }, (vec![6, 8], 14));
}

#[test]
fn double_twice() {
    check!(r#"add 1; double twice"#, { let mut c = Cart::new(); c.add(1); c.double_all(); c.double_all(); (c.items(), c.total()) }, (vec![4], 4));
}
