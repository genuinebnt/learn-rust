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

#[test]
fn empty_string_is_an_error_not_none() {
    check!(r#"s = Some("")"#, parse_optional(Some("")).is_err(), true);
}

#[test]
fn too_big_for_i32() {
    check!(r#"s = Some("2147483648")"#, parse_optional(Some("2147483648")).is_err(), true);
}
