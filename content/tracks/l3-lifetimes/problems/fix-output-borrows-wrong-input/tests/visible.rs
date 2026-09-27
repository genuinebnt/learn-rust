use solution::*;

#[test]
fn temporary_prefix() {
    let line = String::from("key: value");
    let rest;
    {
        let p = String::from("key: ");
        rest = after(&line, &p);
    }
    check!(r#"line "key: value", prefix dropped before use"#, rest, Some("value"));
}

#[test]
fn no_match() {
    check!(r#""abc", "x""#, after("abc", "x"), None);
}

#[test]
fn whole() {
    check!(r#""abc", "abc""#, after("abc", "abc"), Some(""));
}

#[test]
fn empty_prefix() {
    check!(r#""abc", """#, after("abc", ""), Some("abc"));
}

#[test]
fn only_at_the_start() {
    check!(r#""a key: b", "key: ""#, after("a key: b", "key: "), None);
}
