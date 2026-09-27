use solution::*;

#[test]
fn default_not_used_twice() {
    check!(r#"call twice for key 3"#, { let mut m = std::collections::HashMap::new(); get_or_insert(&mut m, 3, "a"); get_or_insert(&mut m, 3, "b").clone() }, "a".to_string());
}

#[test]
fn many_keys() {
    check!(r#"1000 keys"#, { let mut m = std::collections::HashMap::new(); for k in 0..1000 { get_or_insert(&mut m, k, "v"); } m.len() }, 1000);
}

#[test]
fn u32_max_key() {
    check!(r#"key u32::MAX"#, { let mut m = std::collections::HashMap::new(); get_or_insert(&mut m, u32::MAX, "big").clone() }, "big".to_string());
}

#[test]
fn unicode_default() {
    check!(r#"default "ünï""#, { let mut m = std::collections::HashMap::new(); get_or_insert(&mut m, 7, "ünï").clone() }, "ünï".to_string());
}

#[test]
fn returns_the_stored_value() {
    check!(r#"the result points into the map"#, { let mut m = std::collections::HashMap::new(); let p: *const String = get_or_insert(&mut m, 5, "v"); p == &m[&5] as *const String }, true);
}

#[test]
fn existing_empty_value() {
    check!(r#"{4: ""}, key 4, default "d""#, { let mut m = std::collections::HashMap::from([(4, String::new())]); get_or_insert(&mut m, 4, "d").clone() }, String::new());
}

#[test]
fn others_untouched() {
    check!(r#"{1: "a"}, key 2"#, { let mut m = std::collections::HashMap::from([(1, "a".to_string())]); get_or_insert(&mut m, 2, "b"); m[&1].clone() }, "a".to_string());
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2027);
    for _ in 0..200 {
        let mut m = std::collections::HashMap::new();
        let mut model: Vec<(u32, String)> = Vec::new();
        let mut log = Vec::new();
        let n = rng.below(10);
        for _ in 0..n {
            let key = rng.below(5) as u32;
            let d = rng.string(2, "xy");
            log.push(format!("({key}, {d:?})"));
            let got = get_or_insert(&mut m, key, &d).clone();
            let want = match model.iter().find(|(k, _)| *k == key) {
                Some((_, v)) => v.clone(),
                None => {
                    model.push((key, d.clone()));
                    d.clone()
                }
            };
            check!(log.join(", "), got, want);
        }
        check!(log.join(", "), m.len(), model.len());
    }
}
