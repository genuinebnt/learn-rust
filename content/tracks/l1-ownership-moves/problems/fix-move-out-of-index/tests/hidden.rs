use solution::*;

#[test]
fn keeps_length() {
    check!(r#"names = ["a", "b", "c"]"#, { let mut v = vec!["a".to_string(), "b".to_string(), "c".to_string()]; take_first(&mut v); v.len() }, 3);
}
