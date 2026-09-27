use solution::*;

use std::collections::HashMap;

fn cfg(pairs: &[(&str, &str)]) -> HashMap<String, String> {
    pairs.iter().map(|&(k, v)| (k.to_string(), v.to_string())).collect()
}

fn srv(host: &str, port: u16, tls: bool, name: &str, workers: usize) -> Result<Server, String> {
    Ok(Server { host: host.to_string(), port, tls, name: name.to_string(), workers })
}

#[test]
fn host_beats_bind() {
    check!(r#"host = "a", bind = "b", port = "1""#, server(&cfg(&[("host", "a"), ("bind", "b"), ("port", "1")])), srv("a", 1, false, "", 1));
}

#[test]
fn bind_only() {
    check!(r#"bind = "b", port = "1""#, server(&cfg(&[("bind", "b"), ("port", "1")])), srv("b", 1, false, "", 1));
}

#[test]
fn host_and_bind_both_empty() {
    check!(r#"host = "", bind = "", port = "1""#, server(&cfg(&[("host", ""), ("bind", ""), ("port", "1")])), srv("127.0.0.1", 1, false, "", 1));
}

#[test]
fn port_bounds() {
    check!(r#"port = "65535", then port = "65536""#, (server(&cfg(&[("port", "65535")])), server(&cfg(&[("port", "65536")]))), (srv("127.0.0.1", 65535, false, "", 1), Err("invalid port: 65536".to_string())));
}

#[test]
fn port_not_trimmed_or_signed() {
    check!(r#"port = " 80", then port = "-1""#, (server(&cfg(&[("port", " 80")])), server(&cfg(&[("port", "-1")]))), (Err("invalid port:  80".to_string()), Err("invalid port: -1".to_string())));
}

#[test]
fn empty_port_is_invalid_not_missing() {
    check!(r#"port = """#, server(&cfg(&[("port", "")])), Err("invalid port: ".to_string()));
}

#[test]
fn workers_zero() {
    check!(r#"port = "80", workers = "0""#, server(&cfg(&[("port", "80"), ("workers", "0")])), Err("invalid workers: 0".to_string()));
}

#[test]
fn workers_garbage_is_not_the_default() {
    check!(r#"port = "80", workers = "many""#, server(&cfg(&[("port", "80"), ("workers", "many")])), Err("invalid workers: many".to_string()));
}

#[test]
fn empty_workers_is_invalid() {
    check!(r#"port = "80", workers = """#, server(&cfg(&[("port", "80"), ("workers", "")])), Err("invalid workers: ".to_string()));
}

#[test]
fn port_checked_before_workers() {
    check!(r#"port = "x", workers = "0""#, server(&cfg(&[("port", "x"), ("workers", "0")])), Err("invalid port: x".to_string()));
}

#[test]
fn missing_port_before_workers() {
    check!(r#"workers = "0""#, server(&cfg(&[("workers", "0")])), Err("missing port".to_string()));
}

#[test]
fn tls_only_exactly_on() {
    check!(r#"tls = "ON" / "true" / "on""#, [server(&cfg(&[("port", "1"), ("tls", "ON")])), server(&cfg(&[("port", "1"), ("tls", "true")])), server(&cfg(&[("port", "1"), ("tls", "on")]))].map(|r| r.map(|s| s.tls)), [Ok(false), Ok(false), Ok(true)]);
}

#[test]
fn unicode_values() {
    check!(r#"host = "прокси", name = "café ☕", port = "443""#, server(&cfg(&[("host", "прокси"), ("name", "café ☕"), ("port", "443")])), srv("прокси", 443, false, "café ☕", 1));
}

#[test]
fn empty_config() {
    check!(r#"{}"#, server(&HashMap::new()), Err("missing port".to_string()));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7101);
    let keys = ["host", "bind", "port", "tls", "name", "workers"];
    let values = ["", "a", "on", "0", "1", "80", "65535", "65536", "-1", " 8", "x"];
    for _ in 0..400 {
        let mut pairs: Vec<(&str, &str)> = Vec::new();
        for &k in &keys {
            if rng.below(3) > 0 {
                pairs.push((k, *rng.pick(&values)));
            }
        }
        let get = |k: &str| pairs.iter().find(|(pk, _)| *pk == k).map(|(_, v)| *v);
        let want = (|| {
            let port = match get("port") {
                None => return Err("missing port".to_string()),
                Some(v) => match v.parse::<u16>() {
                    Ok(p) if p > 0 => p,
                    _ => return Err(format!("invalid port: {v}")),
                },
            };
            let workers = match get("workers") {
                None => 1,
                Some(v) => match v.parse::<usize>() {
                    Ok(w) if w > 0 => w,
                    _ => return Err(format!("invalid workers: {v}")),
                },
            };
            let host = match (get("host"), get("bind")) {
                (Some(h), _) if !h.is_empty() => h,
                (_, Some(b)) if !b.is_empty() => b,
                _ => "127.0.0.1",
            };
            srv(host, port, get("tls") == Some("on"), get("name").unwrap_or(""), workers)
        })();
        check!(format!("cfg = {pairs:?}"), server(&cfg(&pairs)), want);
    }
}
