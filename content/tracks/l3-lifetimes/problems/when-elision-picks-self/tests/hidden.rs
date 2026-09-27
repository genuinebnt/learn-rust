use solution::*;

#[test]
fn missing() {
    check!(r#"prefix "x""#, Config::new("a", &["b"]).tag_with_prefix("x").is_none(), true);
}

#[test]
fn first_of_many() {
    check!(r#"tags ["k:1", "k:2"]"#, Config::new("a", &["k:1", "k:2"]).tag_with_prefix("k:").map(str::to_string), Some("k:1".to_string()));
}
