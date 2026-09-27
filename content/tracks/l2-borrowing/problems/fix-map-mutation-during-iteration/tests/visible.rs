use solution::*;

#[test]
fn drops() {
    check!(r#"{a: 0, b: 2}"#, { let mut m = std::collections::HashMap::from([("a".to_string(), 0), ("b".to_string(), 2)]); drop_zero(&mut m); m }, std::collections::HashMap::from([("b".to_string(), 2)]));
}

#[test]
fn empty() {
    check!(r#"{}"#, { let mut m: std::collections::HashMap<String, u32> = std::collections::HashMap::new(); drop_zero(&mut m); m.len() }, 0);
}
