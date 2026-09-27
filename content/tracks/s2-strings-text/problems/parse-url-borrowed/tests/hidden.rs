use solution::*;

#[test]
fn empty_host() {
    check!(r#""ftp://:21/""#, parse_url("ftp://:21/"), None);
}

#[test]
fn port_too_big() {
    check!(r#""http://h:99999/""#, parse_url("http://h:99999/"), None);
}

#[test]
fn no_scheme() {
    check!(r#""example.com/x""#, parse_url("example.com/x"), None);
}

#[test]
fn flag_query() {
    check!(r#""http://h?flag&&a=""#, parse_url("http://h?flag&&a=").map(|u| (u.path, u.query)), Some(("/", vec![("flag", ""), ("a", "")])));
}

#[test]
fn borrows_input() {
    let s = String::from("http://host/p");
    let u = parse_url(&s).unwrap();
    let same = std::ptr::eq(u.host.as_ptr(), s[7..].as_ptr());
    check!(r#"host points into the input"#, same, true);
}
