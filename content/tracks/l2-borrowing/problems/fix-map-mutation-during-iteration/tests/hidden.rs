use solution::*;

#[test]
fn all_zero() {
    check!(r#"{a: 0, b: 0}"#, { let mut m = std::collections::HashMap::from([("a".to_string(), 0), ("b".to_string(), 0)]); drop_zero(&mut m); m.len() }, 0);
}
