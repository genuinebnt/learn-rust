use solution::*;

#[test]
fn default_not_used_twice() {
    check!(r#"call twice for key 3"#, { let mut m = std::collections::HashMap::new(); get_or_insert(&mut m, 3, "a"); get_or_insert(&mut m, 3, "b").clone() }, "a".to_string());
}
