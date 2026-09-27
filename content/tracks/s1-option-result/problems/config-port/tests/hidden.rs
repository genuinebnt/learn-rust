use solution::*;

#[test]
fn out_of_range() {
    check!(r#"port = "70000""#, port(&std::collections::HashMap::from([("port".to_string(), "70000".to_string())])), Err("invalid port: 70000".to_string()));
}

#[test]
fn largest() {
    check!(r#"port = "65535""#, port(&std::collections::HashMap::from([("port".to_string(), "65535".to_string())])), Ok(65535));
}

#[test]
fn negative() {
    check!(r#"port = "-1""#, port(&std::collections::HashMap::from([("port".to_string(), "-1".to_string())])), Err("invalid port: -1".to_string()));
}

#[test]
fn surrounding_space() {
    check!(r#"port = " 80""#, port(&std::collections::HashMap::from([("port".to_string(), " 80".to_string())])), Err("invalid port:  80".to_string()));
}

#[test]
fn empty_value() {
    check!(r#"port = """#, port(&std::collections::HashMap::from([("port".to_string(), "".to_string())])), Err("invalid port: ".to_string()));
}

#[test]
fn other_keys_only() {
    check!(r#"host = "localhost", Port = "80""#, port(&std::collections::HashMap::from([("host".to_string(), "localhost".to_string()), ("Port".to_string(), "80".to_string())])), Err("missing port".to_string()));
}

#[test]
fn unicode_digits() {
    check!(r#"port = "８０" (full-width digits)"#, port(&std::collections::HashMap::from([("port".to_string(), "８０".to_string())])), Err("invalid port: ８０".to_string()));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1301);
    for _ in 0..400 {
        let len = rng.below(7);
        let v = rng.string(len, "0123456789012345678x-");
        let mut cfg = std::collections::HashMap::new();
        let present = rng.below(5) > 0;
        if present {
            cfg.insert("port".to_string(), v.clone());
        }
        // Brute force: digits only, no sign, value at most 65535.
        let want = if !present {
            Err("missing port".to_string())
        } else if !v.is_empty() && v.bytes().all(|b| b.is_ascii_digit()) && v.bytes().fold(0u64, |n, b| (n * 10 + u64::from(b - b'0')).min(1 << 20)) <= 65_535 {
            Ok(v.bytes().fold(0u16, |n, b| n * 10 + u16::from(b - b'0')))
        } else {
            Err(format!("invalid port: {v}"))
        };
        check!(format!("cfg = {cfg:?}"), port(&cfg), want);
    }
}
