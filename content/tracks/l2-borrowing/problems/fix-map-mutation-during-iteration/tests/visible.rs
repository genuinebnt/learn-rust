use solution::*;

#[test]
fn drops() {
    check!(r#"{a: 0, b: 2}"#, { let mut m = std::collections::HashMap::from([("a".to_string(), 0), ("b".to_string(), 2)]); drop_zero(&mut m); m }, std::collections::HashMap::from([("b".to_string(), 2)]));
}

#[test]
fn empty() {
    check!(r#"{}"#, { let mut m: std::collections::HashMap<String, u32> = std::collections::HashMap::new(); drop_zero(&mut m); m.len() }, 0);
}

#[test]
fn none_zero() {
    check!(r#"{a: 1, b: 2}"#, { let mut m = std::collections::HashMap::from([("a".to_string(), 1), ("b".to_string(), 2)]); drop_zero(&mut m); m }, std::collections::HashMap::from([("a".to_string(), 1), ("b".to_string(), 2)]));
}

#[test]
fn all_zero() {
    check!(r#"{a: 0, b: 0}"#, { let mut m = std::collections::HashMap::from([("a".to_string(), 0), ("b".to_string(), 0)]); drop_zero(&mut m); m.len() }, 0);
}

#[test]
fn values_untouched() {
    check!(r#"{a: 5, b: 0, c: 7}"#, { let mut m = std::collections::HashMap::from([("a".to_string(), 5), ("b".to_string(), 0), ("c".to_string(), 7)]); drop_zero(&mut m); m }, std::collections::HashMap::from([("a".to_string(), 5), ("c".to_string(), 7)]));
}
