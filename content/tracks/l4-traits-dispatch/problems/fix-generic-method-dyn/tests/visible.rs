use solution::*;

#[test]
fn put_and_get_each_store() {
    let mut got = Vec::new();
    for mut s in all_stores() {
        s.put("n", &5);
        s.put("s", &"hi");
        got.push((s.get("n"), s.get("s")));
    }
    check!(r#"for each of all_stores(): put("n", &5), put("s", &"hi")"#, got, vec![(Some("5".to_string()), Some("hi".to_string())), (Some("5".to_string()), Some("HI".to_string()))]);
}

#[test]
fn keys_sorted() {
    let mut s: Box<dyn Store> = Box::new(MemStore::default());
    for k in ["b", "a", "c"] {
        s.put(k, &1);
    }
    check!(r#"put b, a, c"#, s.keys().collect::<Vec<_>>(), vec!["a", "b", "c"]);
}

#[test]
fn prefixed_view() {
    let mut p = Prefixed { prefix: "user:".into(), inner: Box::new(MemStore::default()) };
    p.put("name", &"ann");
    check!(r#"Prefixed("user:") over MemStore; put name=ann"#, (p.get("name"), p.inner.get("user:name")), (Some("ann".to_string()), Some("ann".to_string())));
}

#[test]
fn prefixed_keys() {
    let mut inner = MemStore::default();
    for k in ["user:b", "zzz", "user:a"] {
        inner.put(k, &0);
    }
    let p = Prefixed { prefix: "user:".into(), inner: Box::new(inner) };
    check!(r#"inner keys user:a, user:b, zzz"#, p.keys().collect::<Vec<_>>(), vec!["a", "b"]);
}

#[test]
fn missing_key() {
    check!(r#"get("x") on an empty store"#, MemStore::default().get("x"), None);
}
