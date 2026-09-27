use solution::*;

#[test]
fn doubles() {
    check!(r#"add 3, 4; double"#, { let mut c = Cart::new(); c.add(3); c.add(4); c.double_all(); (c.items(), c.total()) }, (vec![6, 8], 14));
}

#[test]
fn double_twice() {
    check!(r#"add 1; double twice"#, { let mut c = Cart::new(); c.add(1); c.double_all(); c.double_all(); (c.items(), c.total()) }, (vec![4], 4));
}

#[test]
fn add_after_double() {
    check!(r#"add 1; double; add 5"#, { let mut c = Cart::new(); c.add(1); c.double_all(); c.add(5); (c.items(), c.total()) }, (vec![2, 5], 7));
}

#[test]
fn no_double() {
    check!(r#"add 1, 2"#, { let mut c = Cart::new(); c.add(1); c.add(2); (c.items(), c.total()) }, (vec![1, 2], 3));
}

#[test]
fn empty() {
    check!(r#"double an empty cart"#, { let mut c = Cart::new(); c.double_all(); (c.items(), c.total()) }, (vec![], 0));
}
