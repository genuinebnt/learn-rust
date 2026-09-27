use solution::*;

#[test]
fn existing() {
    check!(r#"{1: "one"}, key 1"#, { let mut m = std::collections::HashMap::from([(1, "one".to_string())]); get_or_insert(&mut m, 1, "x").clone() }, "one".to_string());
}

#[test]
fn missing() {
    check!(r#"{}, key 2"#, { let mut m = std::collections::HashMap::new(); let v = get_or_insert(&mut m, 2, "two").clone(); (v, m.len()) }, ("two".to_string(), 1));
}

#[test]
fn empty_default() {
    check!(r#"{}, key 0, default """#, { let mut m = std::collections::HashMap::new(); let v = get_or_insert(&mut m, 0, "").clone(); (v, m.len()) }, (String::new(), 1));
}

#[test]
fn existing_not_replaced() {
    check!(r#"{1: "one"}, key 1, default "x""#, { let mut m = std::collections::HashMap::from([(1, "one".to_string())]); get_or_insert(&mut m, 1, "x"); (m[&1].clone(), m.len()) }, ("one".to_string(), 1));
}

#[test]
fn different_keys() {
    check!(r#"keys 1 then 2"#, { let mut m = std::collections::HashMap::new(); get_or_insert(&mut m, 1, "a"); let v = get_or_insert(&mut m, 2, "b").clone(); (v, m.len()) }, ("b".to_string(), 2));
}
