use solution::*;

#[test]
fn empty() {
    check!(r#"[]"#, parse_all(&[]), Ok(vec![]));
}

#[test]
fn overflow() {
    check!(r#"["99999999999"]"#, parse_all(&["99999999999"]), Err("bad number: 99999999999".to_string()));
}
