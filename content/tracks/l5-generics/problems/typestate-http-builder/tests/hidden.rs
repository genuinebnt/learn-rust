use solution::*;

#[test]
fn url_is_trimmed() {
    check!(r#"url("  https://t.io \n")"#, RequestBuilder::new().url("  https://t.io \n").unwrap().build().url, "https://t.io");
}

#[test]
fn empty_string() {
    check!(r#"url("")"#, RequestBuilder::new().url("").err(), Some(UrlError::Empty));
}

#[test]
fn ftp_is_rejected() {
    check!(r#"url("ftp://x")"#, RequestBuilder::new().url("ftp://x").err(), Some(UrlError::NoScheme));
}

#[test]
fn scheme_is_case_sensitive() {
    check!(r#"url("HTTPS://x")"#, RequestBuilder::new().url("HTTPS://x").err(), Some(UrlError::NoScheme));
}

#[test]
fn scheme_must_be_at_the_start() {
    check!(r#"url("see https://x")"#, RequestBuilder::new().url("see https://x").err(), Some(UrlError::NoScheme));
}

#[test]
fn repeated_header_kept_twice() {
    check!(r#"header("A", "1").header("A", "2")"#, RequestBuilder::new().header("A", "1").url("https://x").unwrap().header("A", "2").build().headers, vec![("A".to_string(), "1".to_string()), ("A".to_string(), "2".to_string())]);
}

#[test]
fn last_timeout_wins() {
    check!(r#"timeout_ms(1) before url, timeout_ms(2) after"#, RequestBuilder::new().timeout_ms(1).url("https://x").unwrap().timeout_ms(2).build().timeout_ms, 2);
}

#[test]
fn zero_timeout() {
    check!(r#"timeout_ms(0)"#, RequestBuilder::new().url("https://x").unwrap().timeout_ms(0).build().timeout_ms, 0);
}

#[test]
fn unicode_header() {
    check!(r#"header("X-Name", "Zoë")"#, RequestBuilder::new().url("https://x").unwrap().header("X-Name", "Zoë").build(), Request { url: "https://x".to_string(), headers: vec![("X-Name".to_string(), "Zoë".to_string())], timeout_ms: 30000 });
}

#[test]
fn scheme_only() {
    check!(r#"url("http://")"#, RequestBuilder::new().url("http://").unwrap().build().url, "http://");
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(4509);
    for _ in 0..300 {
        let mut log = Vec::new();
        let mut headers = Vec::new();
        let mut timeout = 30_000u64;
        let mut b = RequestBuilder::new();
        let before = rng.below(4);
        for _ in 0..before {
            if rng.bool() {
                let k = rng.string(1, "AB");
                let v = rng.below(10).to_string();
                log.push(format!("header({k:?}, {v:?})"));
                b = b.header(&k, &v);
                headers.push((k, v));
            } else {
                let t = rng.below(1000) as u64;
                log.push(format!("timeout_ms({t})"));
                b = b.timeout_ms(t);
                timeout = t;
            }
        }
        let url = format!("https://h{}.io", rng.below(10));
        log.push(format!("url({url:?})"));
        let mut b = b.url(&url).unwrap();
        let after = rng.below(4);
        for _ in 0..after {
            if rng.bool() {
                let k = rng.string(1, "AB");
                let v = rng.below(10).to_string();
                log.push(format!("header({k:?}, {v:?})"));
                b = b.header(&k, &v);
                headers.push((k, v));
            } else {
                let t = rng.below(1000) as u64;
                log.push(format!("timeout_ms({t})"));
                b = b.timeout_ms(t);
                timeout = t;
            }
        }
        check!(log.join("."), b.build(), Request { url, headers, timeout_ms: timeout });
    }
}
