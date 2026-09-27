use solution::*;

#[test]
fn integers() {
    check!(r#"[3, 7, 2]"#, largest(&[3, 7, 2]), Some(&7));
}

#[test]
fn empty() {
    check!(r#"[] of i32"#, largest::<i32>(&[]), None);
}

#[test]
fn floats() {
    check!(r#"[1.5, -2.0, 0.25]"#, largest(&[1.5, -2.0, 0.25]), Some(&1.5));
}

#[test]
fn strs() {
    check!(r#"["pear", "apple", "zoo"]"#, largest(&["pear", "apple", "zoo"]), Some(&"zoo"));
}

#[test]
fn tie_returns_the_first() {
    let v = [5, 1, 5];
    check!(r#"[5, 1, 5]: which 5?"#, std::ptr::eq(largest(&v).unwrap(), &v[0]), true);
}
