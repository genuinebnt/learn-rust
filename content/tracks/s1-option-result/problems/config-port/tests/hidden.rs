use solution::*;

#[test]
fn out_of_range() {
    check!(r#"port = "70000""#, port(&std::collections::HashMap::from([("port".to_string(), "70000".to_string())])), Err("invalid port: 70000".to_string()));
}
