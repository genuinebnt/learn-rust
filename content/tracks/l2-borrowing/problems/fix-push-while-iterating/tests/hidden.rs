use solution::*;

#[test]
fn none() {
    check!(r#"["x"]"#, { let mut v = vec!["x".to_string()]; expand(&mut v); v.len() }, 1);
}
