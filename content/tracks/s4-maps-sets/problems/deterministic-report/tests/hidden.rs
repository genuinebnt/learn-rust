use solution::*;

#[test]
fn u32_max() {
    check!(r#"{a: u32::MAX, b: 0}"#, report(&std::collections::HashMap::from([("b".to_string(), 0), ("a".to_string(), u32::MAX)])), vec!["a: 4294967295", "b: 0"]);
}

#[test]
fn names_compare_bytewise() {
    check!(r#"{B: 1, a: 1}"#, report(&std::collections::HashMap::from([("a".to_string(), 1), ("B".to_string(), 1)])), vec!["B: 1", "a: 1"]);
}

#[test]
fn unicode_names() {
    check!(r#"{é: 1, e: 1}"#, report(&std::collections::HashMap::from([("é".to_string(), 1), ("e".to_string(), 1)])), vec!["e: 1", "é: 1"]);
}

#[test]
fn empty_name() {
    check!(r#"{"": 3}"#, report(&std::collections::HashMap::from([(String::new(), 3)])), vec![": 3"]);
}

#[test]
fn digits_are_text() {
    check!(r#"{a10: 1, a9: 1}"#, report(&std::collections::HashMap::from([("a9".to_string(), 1), ("a10".to_string(), 1)])), vec!["a10: 1", "a9: 1"]);
}

#[test]
fn score_beats_name() {
    check!(r#"{a: 1, z: 2}"#, report(&std::collections::HashMap::from([("a".to_string(), 1), ("z".to_string(), 2)])), vec!["z: 2", "a: 1"]);
}

#[test]
fn many() {
    check!(r#"1000 players, scores i % 10"#, { let m: std::collections::HashMap<String, u32> = (0..1000).map(|i| (format!("p{i:03}"), i % 10)).collect(); let r = report(&m); (r.len(), r[0].clone(), r[999].clone()) }, (1000, "p009: 9".to_string(), "p990: 0".to_string()));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4008);
    for _ in 0..300 {
        let n = rng.below(8);
        let m: std::collections::HashMap<String, u32> = (0..n).map(|_| { let l = 1 + rng.below(2); (rng.string(l, "abB"), rng.below(4) as u32) }).collect();
        let mut rows: Vec<(String, u32)> = m.iter().map(|(k, &v)| (k.clone(), v)).collect();
        rows.sort_by_key(|(k, v)| (std::cmp::Reverse(*v), k.clone()));
        let want: Vec<String> = rows.iter().map(|(k, v)| format!("{k}: {v}")).collect();
        let mut sorted: Vec<_> = m.iter().collect();
        sorted.sort();
        check!(format!("scores = {sorted:?}"), report(&m), want);
    }
}

#[test]
fn scale_200k() {
    let m: std::collections::HashMap<String, u32> = (0..200_000u32).map(|i| (format!("p{i:06}"), i % 1000)).collect();
    let r = report(&m);
    check!("200000 players, scores i % 1000", (r.len(), r[0].clone(), r[199_999].clone()), (200_000, "p000999: 999".to_string(), "p199000: 0".to_string()));
}
