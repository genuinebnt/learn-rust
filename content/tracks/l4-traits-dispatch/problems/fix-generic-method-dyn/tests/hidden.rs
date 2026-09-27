use solution::*;

#[test]
fn floats_and_chars() {
    let mut s: Box<dyn Store> = Box::new(UpperStore::default());
    s.put("f", &2.5);
    s.put("c", &'é');
    check!(r#"put("f", &2.5), put("c", &'é') in UpperStore"#, (s.get("f"), s.get("c")), (Some("2.5".to_string()), Some("É".to_string())));
}

#[test]
fn overwrite() {
    let mut s: Box<dyn Store> = Box::new(MemStore::default());
    s.put("k", &1);
    s.put("k", &2);
    check!(r#"put k=1 then k=2"#, (s.get("k"), s.keys().count()), (Some("2".to_string()), 1));
}

#[test]
fn upper_keeps_keys() {
    let mut s = UpperStore::default();
    s.put("key", &"v");
    check!(r#"UpperStore put("key", &"v")"#, (s.keys().collect::<Vec<_>>(), s.get("key")), (vec!["key"], Some("V".to_string())));
}

#[test]
fn empty_keys() {
    check!(r#"MemStore::default().keys()"#, MemStore::default().keys().count(), 0);
}

#[test]
fn prefixed_over_upper() {
    let mut p = Prefixed { prefix: "p/".into(), inner: Box::new(UpperStore::default()) };
    p.put("x", &"abc");
    check!(r#"Prefixed("p/") over UpperStore; put x=abc"#, (p.get("x"), p.inner.keys().collect::<Vec<_>>()), (Some("ABC".to_string()), vec!["p/x"]));
}

#[test]
fn nested_prefixed() {
    let inner = Prefixed { prefix: "b/".into(), inner: Box::new(MemStore::default()) };
    let mut p = Prefixed { prefix: "a/".into(), inner: Box::new(inner) };
    p.put("k", &1);
    check!(r#"Prefixed("a/", Prefixed("b/", MemStore)); put k"#, (p.get("k"), p.keys().collect::<Vec<_>>()), (Some("1".to_string()), vec!["k"]));
}

#[test]
fn empty_prefix() {
    let mut inner = MemStore::default();
    inner.put("y", &0);
    inner.put("x", &0);
    let p = Prefixed { prefix: String::new(), inner: Box::new(inner) };
    check!(r#"Prefixed("") sees every key"#, p.keys().collect::<Vec<_>>(), vec!["x", "y"]);
}

#[test]
fn user_display_type() {
    struct Point(i32, i32);
    impl std::fmt::Display for Point {
        fn fmt(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
            write!(f, "({}, {})", self.0, self.1)
        }
    }
    let mut s: Box<dyn Store> = Box::new(MemStore::default());
    s.put("p", &Point(1, -2));
    check!("put(\"p\", &Point(1, -2))", s.get("p"), Some("(1, -2)".to_string()));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(4412);
    for _ in 0..200 {
        let mut p = Prefixed { prefix: "u:".into(), inner: Box::new(MemStore::default()) };
        let mut model = std::collections::BTreeMap::new();
        for _ in 0..8 {
            let k = rng.string(1, "abc");
            let v = rng.int(0, 99);
            p.put(&k, &v);
            model.insert(k, v.to_string());
        }
        let keys: Vec<String> = p.keys().map(String::from).collect();
        check!(format!("model = {model:?}"), keys, model.keys().cloned().collect::<Vec<_>>());
        for (k, v) in &model {
            check!(format!("get({k:?})"), p.get(k), Some(v.clone()));
        }
    }
}
