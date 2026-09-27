use solution::*;

#[test]
fn add_and_double() {
    let mut c = Cart::new();
    check!(r#"add 3, 4; double_all"#, { c.add(3); c.add(4); c.double_all(); (c.items(), c.total(), c.log()) }, (vec![6, 8], 14, ["[1] add 3", "[2] add 4", "[2] double 3 -> 6", "[2] double 4 -> 8"].map(String::from).to_vec()));
}

#[test]
fn drop_above() {
    let mut c = Cart::new();
    check!(r#"add 5, 50, 7, 70; drop_above 10"#, { for p in [5, 50, 7, 70] { c.add(p); } (c.drop_above(10), c.items(), c.total(), c.log()[4..].to_vec()) }, (2, vec![5, 7], 12, ["[4] drop 50", "[4] drop 70"].map(String::from).to_vec()));
}

#[test]
fn empty_cart() {
    let mut c = Cart::new();
    check!(r#"double and drop on an empty cart"#, { c.double_all(); (c.drop_above(0), c.total(), c.log().len()) }, (0, 0, 0));
}

#[test]
fn drop_is_strict() {
    let mut c = Cart::new();
    check!(r#"add 10; drop_above 10"#, { c.add(10); (c.drop_above(10), c.items()) }, (0, vec![10]));
}

#[test]
fn double_twice() {
    let mut c = Cart::new();
    check!(r#"add 1; double twice"#, { c.add(1); c.double_all(); c.double_all(); (c.items(), c.total()) }, (vec![4], 4));
}
