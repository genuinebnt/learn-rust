use solution::*;

#[test]
fn negative() {
    check!(r#"s = Some("-7")"#, parse_optional(Some("-7")), Ok(Some(-7)));
}

#[test]
fn empty_string() {
    check!(r#"s = Some("")"#, parse_optional(Some("")).is_err(), true);
}
