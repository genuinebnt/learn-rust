use solution::*;

#[test]
fn by_type() {
    let mut s = Stash::new();
    s.put(format!("user-{}", 42));
    s.put(5u32);
    s.put("lit");
    s.put(7u32);
    check!(r#"put String, 5u32, "lit", 7u32; all::<u32>()"#, s.all::<u32>(), vec![&5, &7]);
}

#[test]
fn runtime_string_is_static() {
    let mut s = Stash::new();
    s.put(format!("user-{}", 42));
    s.put("lit");
    check!(r#"the String built with format!"#, (s.all::<String>()[0].as_str(), s.all::<&str>()), ("user-42", vec![&"lit"]));
}
