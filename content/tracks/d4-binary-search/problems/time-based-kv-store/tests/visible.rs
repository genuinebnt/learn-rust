use solution::*;

#[test]
fn latest_before() {
    let mut m = TimeMap::new();
    m.set("foo", "bar", 1);
    m.set("foo", "bar2", 4);
    check!(r#"set foo=bar@1, foo=bar2@4; get @1, @3, @4, @5"#, (m.get("foo", 1), m.get("foo", 3), m.get("foo", 4), m.get("foo", 5)), (Some("bar"), Some("bar"), Some("bar2"), Some("bar2")));
}

#[test]
fn too_early() {
    let mut m = TimeMap::new();
    m.set("a", "x", 10);
    check!(r#"set a=x@10; get @9"#, m.get("a", 9), None);
}
