use solution::*;

#[test]
fn full() {
    check!(r#""https://example.com:8080/a/b?x=1&y=2""#, parse_url("https://example.com:8080/a/b?x=1&y=2"), Some(Url { scheme: "https", host: "example.com", port: Some(8080), path: "/a/b", query: vec![("x", "1"), ("y", "2")] }));
}

#[test]
fn minimal() {
    check!(r#""http://h""#, parse_url("http://h"), Some(Url { scheme: "http", host: "h", port: None, path: "/", query: vec![] }));
}
