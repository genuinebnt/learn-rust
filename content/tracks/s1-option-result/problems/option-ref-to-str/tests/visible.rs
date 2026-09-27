use solution::*;

#[test]
fn found() {
    let m = std::collections::HashMap::from([(1, "one".to_string())]);
    check!(r#"labels = {1: "one"}, id = 1"#, label(&m, 1), Some("one"));
}

#[test]
fn missing() {
    let m = std::collections::HashMap::new();
    check!(r#"labels = {}, id = 7"#, label(&m, 7), None);
}

#[test]
fn default() {
    let m = std::collections::HashMap::new();
    check!(r#"labels = {}, id = 7, default = "?""#, label_or(&m, 7, "?"), "?");
}
