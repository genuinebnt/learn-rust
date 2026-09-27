use solution::*;

#[test]
fn empty_key() {
    check!(r#"key """#, { let mut m = std::collections::HashMap::new(); get_or_create(&mut m, "").push(5); m[""].clone() }, vec![5]);
}

#[test]
fn unicode_key() {
    check!(r#"key "ключ""#, { let mut m = std::collections::HashMap::new(); get_or_create(&mut m, "ключ").push(1); m.contains_key("ключ") }, true);
}

#[test]
fn mutate_through_return() {
    check!(r#"extend then retain"#, { let mut m = std::collections::HashMap::new(); let v = get_or_create(&mut m, "a"); v.extend([1, 2, 3]); v.retain(|&x| x != 2); m["a"].clone() }, vec![1, 3]);
}

#[test]
fn case_sensitive() {
    check!(r#""a" and "A""#, { let mut m = std::collections::HashMap::new(); get_or_create(&mut m, "a"); get_or_create(&mut m, "A"); m.len() }, 2);
}

#[test]
fn many_keys() {
    check!(r#"10000 keys"#, { let mut m = std::collections::HashMap::new(); for i in 0..10_000u32 { get_or_create(&mut m, &i.to_string()).push(i); } (m.len(), m["9999"].clone()) }, (10_000, vec![9999]));
}

#[test]
fn other_keys_untouched() {
    check!(r#"{a: [1]}, create "b""#, { let mut m = std::collections::HashMap::from([("a".to_string(), vec![1])]); get_or_create(&mut m, "b").push(2); (m["a"].clone(), m["b"].clone()) }, (vec![1], vec![2]));
}

#[test]
fn max_value() {
    check!(r#"push u32::MAX"#, { let mut m = std::collections::HashMap::new(); get_or_create(&mut m, "x").push(u32::MAX); m["x"].clone() }, vec![u32::MAX]);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2010);
    for _ in 0..200 {
        let mut m: std::collections::HashMap<String, Vec<u32>> = std::collections::HashMap::new();
        let mut model: Vec<(String, Vec<u32>)> = Vec::new();
        let mut log = Vec::new();
        let n = rng.below(12);
        for _ in 0..n {
            let key = rng.string(1, "abc");
            let x = rng.below(100) as u32;
            let push = rng.bool();
            let v = get_or_create(&mut m, &key);
            if push {
                v.push(x);
            }
            let pos = match model.iter().position(|(k, _)| *k == key) {
                Some(p) => p,
                None => {
                    model.push((key.clone(), vec![]));
                    model.len() - 1
                }
            };
            if push {
                model[pos].1.push(x);
            }
            log.push(if push { format!("{key} push {x}") } else { key.clone() });
        }
        let mut got: Vec<(String, Vec<u32>)> = m.into_iter().collect();
        got.sort();
        model.sort();
        check!(log.join(", "), got, model);
    }
}
