use solution::*;

#[test]
fn valid() {
    check!(r#"port = "8080""#, port(&std::collections::HashMap::from([("port".to_string(), "8080".to_string())])), Ok(8080));
}

#[test]
fn missing() {
    check!(r#"no port key"#, port(&std::collections::HashMap::new()), Err("missing port".to_string()));
}

#[test]
fn not_a_number() {
    check!(r#"port = "abc""#, port(&std::collections::HashMap::from([("port".to_string(), "abc".to_string())])), Err("invalid port: abc".to_string()));
}
