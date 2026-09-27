use solution::*;

#[test]
fn empty() {
    check!(r#"[], n = 0"#, { let mut v = vec![]; first_long_or_push(&mut v, 0).clone() }, "fallback".to_string());
}
