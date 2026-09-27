use solution::*;

#[test]
fn default_unused() {
    let m = std::collections::HashMap::from([(2, "two".to_string())]);
    check!(r#"labels = {2: "two"}, id = 2"#, label_or(&m, 2, "?"), "two");
}
