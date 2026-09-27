use solution::*;

#[test]
fn filters() {
    let owned = vec![String::from("red"), String::from("blue")];
    let allowed: Vec<&str> = owned.iter().map(|s| s.as_str()).collect();
    let f = make_filter(&allowed);
    check!(r#"allowed ["red", "blue"] built from Strings"#, (f("red"), f("green")), (true, false));
}

#[test]
fn empty() {
    check!(r#"allowed []"#, make_filter(&[])("x"), false);
}
