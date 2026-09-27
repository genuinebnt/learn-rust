use solution::*;

#[test]
fn existing() {
    check!(r#"{1: "one"}, key 1"#, { let mut m = std::collections::HashMap::from([(1, "one".to_string())]); get_or_insert(&mut m, 1, "x").clone() }, "one".to_string());
}

#[test]
fn missing() {
    check!(r#"{}, key 2"#, { let mut m = std::collections::HashMap::new(); let v = get_or_insert(&mut m, 2, "two").clone(); (v, m.len()) }, ("two".to_string(), 1));
}
