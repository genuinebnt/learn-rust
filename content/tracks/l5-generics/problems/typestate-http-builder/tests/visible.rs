use solution::*;

#[test]
fn minimal() {
    check!(r#"new().url("https://a.io")?.build()"#, RequestBuilder::new().url("https://a.io").unwrap().build(), Request { url: "https://a.io".to_string(), headers: vec![], timeout_ms: 30000 });
}

#[test]
fn full_chain() {
    let b: RequestBuilder<HasUrl> = RequestBuilder::new().url("https://a.io/x").unwrap();
    check!(r#"headers and a timeout after the URL"#, b.header("Accept", "json").timeout_ms(500).header("X-Id", "7").build(), Request { url: "https://a.io/x".to_string(), headers: vec![("Accept".to_string(), "json".to_string()), ("X-Id".to_string(), "7".to_string())], timeout_ms: 500 });
}

#[test]
fn settings_before_the_url_are_kept() {
    let b: RequestBuilder<NoUrl> = RequestBuilder::new().header("K", "v").timeout_ms(10);
    check!(r#"header and timeout before url()"#, b.url("http://b.io").unwrap().build(), Request { url: "http://b.io".to_string(), headers: vec![("K".to_string(), "v".to_string())], timeout_ms: 10 });
}

#[test]
fn empty_url() {
    check!(r#"url("  ")"#, RequestBuilder::new().url("  ").err(), Some(UrlError::Empty));
}

#[test]
fn no_scheme() {
    check!(r#"url("a.io")"#, RequestBuilder::new().url("a.io").err(), Some(UrlError::NoScheme));
}
