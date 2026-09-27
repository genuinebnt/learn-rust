use solution::*;

use std::collections::HashMap;

fn cfg(pairs: &[(&str, &str)]) -> HashMap<String, String> {
    pairs.iter().map(|&(k, v)| (k.to_string(), v.to_string())).collect()
}

fn srv(host: &str, port: u16, tls: bool, name: &str, workers: usize) -> Result<Server, String> {
    Ok(Server { host: host.to_string(), port, tls, name: name.to_string(), workers })
}

#[test]
fn everything_set() {
    check!(r#"host = "db.local", port = "5432", tls = "on", name = "primary", workers = "8""#, server(&cfg(&[("host", "db.local"), ("port", "5432"), ("tls", "on"), ("name", "primary"), ("workers", "8")])), srv("db.local", 5432, true, "primary", 8));
}

#[test]
fn only_a_port() {
    check!(r#"port = "80""#, server(&cfg(&[("port", "80")])), srv("127.0.0.1", 80, false, "", 1));
}

#[test]
fn missing_port() {
    check!(r#"host = "a""#, server(&cfg(&[("host", "a")])), Err("missing port".to_string()));
}

#[test]
fn empty_host_falls_back_to_bind() {
    check!(r#"host = "", bind = "0.0.0.0", port = "80""#, server(&cfg(&[("host", ""), ("bind", "0.0.0.0"), ("port", "80")])), srv("0.0.0.0", 80, false, "", 1));
}

#[test]
fn port_zero_is_invalid() {
    check!(r#"port = "0""#, server(&cfg(&[("port", "0")])), Err("invalid port: 0".to_string()));
}
