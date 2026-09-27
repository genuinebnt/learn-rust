use solution::*;

#[test]
fn outlives_prefix() {
    let c = Config::new("app", &["env:prod", "team:core"]);
    let found;
    {
        let p = String::from("team:");
        found = c.tag_with_prefix(&p);
    }
    check!(r#"tags ["env:prod", "team:core"], prefix "team:" dropped before use"#, found, Some("team:core"));
}

#[test]
fn name() {
    check!(r#"name "app""#, Config::new("app", &[]).name().to_string(), "app".to_string());
}
