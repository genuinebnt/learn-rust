use solution::*;

#[test]
fn name() {
    check!(r#""Ada", "Lovelace""#, full_name("Ada".into(), "Lovelace".into()), "Lovelace, Ada".to_string());
}

#[test]
fn tagged() {
    check!(r#""ferris", 7"#, tag("ferris", 7), "ferris#7".to_string());
}
