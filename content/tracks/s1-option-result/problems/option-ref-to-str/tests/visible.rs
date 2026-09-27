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

#[test]
fn default_not_used_when_found() {
    let m = std::collections::HashMap::from([(1, "one".to_string()), (2, "two".to_string())]);
    check!(r#"labels = {1: "one", 2: "two"}, id = 2, default = "?""#, label_or(&m, 2, "?"), "two");
}

#[test]
fn empty_label_is_still_a_label() {
    let m = std::collections::HashMap::from([(3, String::new())]);
    check!(r#"labels = {3: ""}, id = 3, default = "?""#, (label(&m, 3), label_or(&m, 3, "?")), (Some(""), ""));
}
