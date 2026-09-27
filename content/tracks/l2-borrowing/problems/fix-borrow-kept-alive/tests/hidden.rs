use solution::*;

#[test]
fn one() {
    check!(r#"names = ["x"]"#, { let mut v = vec!["x".to_string()]; shout_first(&mut v); v }, vec!["X!".to_string()]);
}
