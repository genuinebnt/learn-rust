use solution::*;

#[test]
fn missing() {
    check!(r#"prefix "x""#, Config::new("a", &["b"]).tag_with_prefix("x").is_none(), true);
}

#[test]
fn first_of_many() {
    check!(r#"tags ["k:1", "k:2"]"#, Config::new("a", &["k:1", "k:2"]).tag_with_prefix("k:").map(str::to_string), Some("k:1".to_string()));
}

#[test]
fn empty_prefix() {
    check!(r#"tags ["a", "b"], prefix """#, Config::new("x", &["a", "b"]).tag_with_prefix("").map(str::to_string), Some("a".to_string()));
}

#[test]
fn whole_tag() {
    check!(r#"tags ["env"], prefix "env""#, Config::new("x", &["env"]).tag_with_prefix("env").map(str::to_string), Some("env".to_string()));
}

#[test]
fn prefix_longer_than_tag() {
    check!(r#"tags ["en"], prefix "env""#, Config::new("x", &["en"]).tag_with_prefix("env").is_none(), true);
}

#[test]
fn case_sensitive() {
    check!(r#"tags ["Env:x", "env:y"], prefix "env""#, Config::new("x", &["Env:x", "env:y"]).tag_with_prefix("env").map(str::to_string), Some("env:y".to_string()));
}

#[test]
fn unicode() {
    check!(r#"tags ["été:1", "éte:2"], prefix "ét""#, Config::new("x", &["été:1", "éte:2"]).tag_with_prefix("ét").map(str::to_string), Some("été:1".to_string()));
}

#[test]
fn empty_name() {
    check!(r#"name """#, Config::new("", &["t"]).name().to_string(), String::new());
}

#[test]
fn name_from_temporaries() {
    let c = Config::new(&String::from("svc-été"), &[&String::from("t")]);
    let n = c.name();
    check!(r#"name read from a Config built from temporaries"#, n, "svc-été");
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(301);
    for _ in 0..300 {
        let n = rng.below(5);
        let tags: Vec<String> = (0..n).map(|_| { let len = rng.below(4); rng.string(len, "ab:") }).collect();
        let plen = rng.below(3);
        let prefix = rng.string(plen, "ab:");
        let refs: Vec<&str> = tags.iter().map(String::as_str).collect();
        let c = Config::new("x", &refs);
        let want = tags.iter().find(|t| t.starts_with(prefix.as_str())).cloned();
        check!(format!("tags = {tags:?}, prefix = {prefix:?}"), c.tag_with_prefix(&prefix).map(str::to_string), want);
    }
}
