use solution::*;

#[test]
fn default_unused() {
    let m = std::collections::HashMap::from([(2, "two".to_string())]);
    check!(r#"labels = {2: "two"}, id = 2"#, label_or(&m, 2, "?"), "two");
}

#[test]
fn other_id() {
    let m = std::collections::HashMap::from([(1, "one".to_string())]);
    check!(r#"labels = {1: "one"}, id = 2"#, label(&m, 2), None);
}

#[test]
fn id_zero() {
    let m = std::collections::HashMap::from([(0, "zero".to_string())]);
    check!(r#"labels = {0: "zero"}, id = 0"#, label(&m, 0), Some("zero"));
}

#[test]
fn id_max() {
    let m = std::collections::HashMap::from([(u32::MAX, "max".to_string())]);
    check!(r#"labels = {u32::MAX: "max"}, id = u32::MAX"#, label_or(&m, u32::MAX, "?"), "max");
}

#[test]
fn empty_default() {
    let m = std::collections::HashMap::new();
    check!(r#"labels = {}, id = 1, default = """#, label_or(&m, 1, ""), "");
}

#[test]
fn unicode_label() {
    let m = std::collections::HashMap::from([(5, "café ☕".to_string())]);
    check!(r#"labels = {5: "café ☕"}, id = 5"#, label(&m, 5), Some("café ☕"));
}

#[test]
fn borrows_from_the_map() {
    let m = std::collections::HashMap::from([(1, "one".to_string())]);
    check!(r#"labels = {1: "one"}, id = 1"#, std::ptr::eq(label_or(&m, 1, "?").as_ptr(), m[&1].as_ptr()), true);
}

#[test]
fn returns_the_default_itself() {
    let m = std::collections::HashMap::new(); let d = "fallback";
    check!(r#"labels = {}, id = 1, default = d"#, std::ptr::eq(label_or(&m, 1, d).as_ptr(), d.as_ptr()), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1305);
    for _ in 0..300 {
        let n = rng.below(6);
        let mut m = std::collections::HashMap::new();
        let mut pairs: Vec<(u32, String)> = Vec::new();
        for _ in 0..n {
            let k = rng.below(8) as u32;
            let len = rng.below(3);
            let v = rng.string(len, "ab");
            m.insert(k, v.clone());
            pairs.retain(|(pk, _)| *pk != k);
            pairs.push((k, v));
        }
        let id = rng.below(8) as u32;
        let want = pairs.iter().find(|(k, _)| *k == id).map(|(_, v)| v.as_str());
        check!(format!("labels = {m:?}, id = {id}"), label(&m, id), want);
        check!(format!("labels = {m:?}, id = {id}, default = \"-\""), label_or(&m, id, "-"), want.unwrap_or("-"));
    }
}

#[test]
fn scale_many_lookups() {
    let n: u32 = 200_000;
    let m: std::collections::HashMap<u32, String> = (0..n).map(|i| (i * 2, "x".to_string())).collect();
    let mut found = 0usize;
    for id in 0..2 * n {
        if label_or(&m, id, "").len() == 1 {
            found += 1;
        }
    }
    check!("200000 labels (even ids), look up every id below 400000", found, 200_000);
}
