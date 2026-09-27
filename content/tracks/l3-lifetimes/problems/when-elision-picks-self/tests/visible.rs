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

#[test]
fn first_match() {
    check!(r#"tags ["env:prod", "team:core"], prefix "env:""#, Config::new("app", &["env:prod", "team:core"]).tag_with_prefix("env:").map(str::to_string), Some("env:prod".to_string()));
}

#[test]
fn no_tags() {
    check!(r#"tags [], prefix "env:""#, Config::new("app", &[]).tag_with_prefix("env:").is_none(), true);
}

#[test]
fn prefix_not_substring() {
    check!(r#"tags ["env:prod"], prefix "prod""#, Config::new("app", &["env:prod"]).tag_with_prefix("prod").is_none(), true);
}
