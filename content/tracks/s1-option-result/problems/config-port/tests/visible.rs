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

#[test]
fn zero() {
    check!(r#"port = "0""#, port(&std::collections::HashMap::from([("port".to_string(), "0".to_string())])), Ok(0));
}

#[test]
fn too_big_for_u16() {
    check!(r#"port = "65536""#, port(&std::collections::HashMap::from([("port".to_string(), "65536".to_string())])), Err("invalid port: 65536".to_string()));
}
