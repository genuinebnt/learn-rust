use solution::*;

#[test]
fn full() {
    check!(r#""https://example.com:8080/a/b?x=1&y=2""#, parse_url("https://example.com:8080/a/b?x=1&y=2"), Some(Url { scheme: "https", host: "example.com", port: Some(8080), path: "/a/b", query: vec![("x", "1"), ("y", "2")] }));
}

#[test]
fn minimal() {
    check!(r#""http://h""#, parse_url("http://h"), Some(Url { scheme: "http", host: "h", port: None, path: "/", query: vec![] }));
}

#[test]
fn port_no_path() {
    check!(r#""http://h:80""#, parse_url("http://h:80"), Some(Url { scheme: "http", host: "h", port: Some(80), path: "/", query: vec![] }));
}

#[test]
fn path_no_port() {
    check!(r#""https://ex.org/docs""#, parse_url("https://ex.org/docs"), Some(Url { scheme: "https", host: "ex.org", port: None, path: "/docs", query: vec![] }));
}

#[test]
fn bad_port() {
    check!(r#""http://h:abc""#, parse_url("http://h:abc"), None);
}
