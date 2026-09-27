use solution::*;

#[test]
fn out_of_order() {
    let mut m = TimeMap::new();
    m.set("k", "five", 5);
    m.set("k", "two", 2);
    check!(r#"set @5 then @2; get @3"#, m.get("k", 3), Some("two"));
}

#[test]
fn unknown_key() {
    check!(r#"get a key never set"#, TimeMap::new().get("nope", 1).is_none(), true);
}

#[test]
fn overwrite() {
    let mut m = TimeMap::new();
    m.set("k", "old", 1);
    m.set("k", "new", 1);
    check!(r#"set @1 twice"#, m.get("k", 1), Some("new"));
}
