use solution::*;

#[test]
fn name() {
    check!(r#""Ada", "Lovelace""#, full_name("Ada".into(), "Lovelace".into()), "Lovelace, Ada".to_string());
}

#[test]
fn tagged() {
    check!(r#""ferris", 7"#, tag("ferris", 7), "ferris#7".to_string());
}

#[test]
fn tag_two_digits() {
    check!(r#""x", 42"#, tag("x", 42), "x#42".to_string());
}

#[test]
fn empty_last() {
    check!(r#""Ada", """#, full_name("Ada".into(), String::new()), ", Ada".to_string());
}

#[test]
fn last_comes_first() {
    check!(r#""Grace", "Hopper""#, full_name("Grace".into(), "Hopper".into()), "Hopper, Grace".to_string());
}
