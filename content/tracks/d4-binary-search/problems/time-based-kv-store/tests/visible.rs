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

#[test]
fn key_never_set() {
    let mut m = TimeMap::new();
    m.set("a", "x", 1);
    check!(r#"set a=x@1; get b@5"#, m.get("b", 5), None);
}

#[test]
fn keys_are_separate() {
    let mut m = TimeMap::new();
    m.set("a", "1", 1);
    m.set("b", "2", 2);
    check!(r#"set a=1@1, b=2@2; get a@5 and b@5"#, (m.get("a", 5), m.get("b", 5)), (Some("1"), Some("2")));
}

#[test]
fn sets_out_of_time_order() {
    let mut m = TimeMap::new();
    m.set("k", "late", 9);
    m.set("k", "early", 3);
    check!(r#"set k=late@9, then k=early@3; get @5 and @10"#, (m.get("k", 5), m.get("k", 10)), (Some("early"), Some("late")));
}
