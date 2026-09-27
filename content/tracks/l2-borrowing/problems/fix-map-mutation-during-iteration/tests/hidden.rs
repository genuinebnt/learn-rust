use solution::*;

#[test]
fn single_zero() {
    check!(r#"{a: 0}"#, { let mut m = std::collections::HashMap::from([("a".to_string(), 0)]); drop_zero(&mut m); m.len() }, 0);
}

#[test]
fn u32_max_kept() {
    check!(r#"{a: u32::MAX}"#, { let mut m = std::collections::HashMap::from([("a".to_string(), u32::MAX)]); drop_zero(&mut m); m }, std::collections::HashMap::from([("a".to_string(), u32::MAX)]));
}

#[test]
fn unicode_keys() {
    check!(r#"{ä: 0, ö: 1}"#, { let mut m = std::collections::HashMap::from([("ä".to_string(), 0), ("ö".to_string(), 1)]); drop_zero(&mut m); m }, std::collections::HashMap::from([("ö".to_string(), 1)]));
}

#[test]
fn empty_key() {
    check!(r#"{"": 0, x: 3}"#, { let mut m = std::collections::HashMap::from([(String::new(), 0), ("x".to_string(), 3)]); drop_zero(&mut m); m }, std::collections::HashMap::from([("x".to_string(), 3)]));
}

#[test]
fn many() {
    check!(r#"10000 keys, every third zero"#, { let mut m: std::collections::HashMap<String, u32> = (0..10_000u32).map(|i| (i.to_string(), i % 3)).collect(); drop_zero(&mut m); m.len() }, 6666);
}

#[test]
fn ones_kept() {
    check!(r#"{a: 1, b: 0}"#, { let mut m = std::collections::HashMap::from([("a".to_string(), 1), ("b".to_string(), 0)]); drop_zero(&mut m); m.contains_key("a") && !m.contains_key("b") }, true);
}

#[test]
fn called_twice() {
    check!(r#"{a: 0, b: 1}, twice"#, { let mut m = std::collections::HashMap::from([("a".to_string(), 0), ("b".to_string(), 1)]); drop_zero(&mut m); drop_zero(&mut m); m.len() }, 1);
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2021);
    for _ in 0..300 {
        let n = rng.below(8);
        let entries: Vec<(String, u32)> = (0..n).map(|_| { let k = rng.string(1, "abcde"); (k, rng.below(3) as u32) }).collect();
        let mut m: std::collections::HashMap<String, u32> = entries.iter().cloned().collect();
        let mut want: Vec<(String, u32)> = m.iter().filter(|(_, &v)| v != 0).map(|(k, &v)| (k.clone(), v)).collect();
        want.sort();
        drop_zero(&mut m);
        let mut got: Vec<(String, u32)> = m.into_iter().collect();
        got.sort();
        check!(format!("entries = {entries:?}"), got, want);
    }
}

#[test]
fn scale_200k() {
    let mut m: std::collections::HashMap<String, u32> = (0..200_000u32).map(|i| (format!("k{i}"), i % 2)).collect();
    drop_zero(&mut m);
    check!("200000 keys, every other one zero", (m.len(), m.values().all(|&v| v == 1)), (100_000, true));
}
