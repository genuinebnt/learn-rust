use solution::*;

#[test]
fn empty_first() {
    check!(r#""", "X""#, full_name(String::new(), "X".into()), "X, ".to_string());
}

#[test]
fn zero() {
    check!(r#""a", 0"#, tag("a", 0), "a#0".to_string());
}
