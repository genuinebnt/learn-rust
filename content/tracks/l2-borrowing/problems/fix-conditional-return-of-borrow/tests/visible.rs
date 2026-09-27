use solution::*;

#[test]
fn found() {
    check!(r#"["a", "long"], n = 2"#, { let mut v = vec!["a".to_string(), "long".to_string()]; first_long_or_push(&mut v, 2).clone() }, "long".to_string());
}

#[test]
fn fallback() {
    check!(r#"["a"], n = 5"#, { let mut v = vec!["a".to_string()]; let r = first_long_or_push(&mut v, 5).clone(); (r, v.len()) }, ("fallback".to_string(), 2));
}
