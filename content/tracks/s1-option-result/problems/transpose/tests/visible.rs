use solution::*;

#[test]
fn none() {
    check!(r#"s = None"#, parse_optional(None), Ok(None));
}

#[test]
fn number() {
    check!(r#"s = Some("42")"#, parse_optional(Some("42")), Ok(Some(42)));
}

#[test]
fn bad() {
    check!(r#"s = Some("x")"#, parse_optional(Some("x")).is_err(), true);
}
