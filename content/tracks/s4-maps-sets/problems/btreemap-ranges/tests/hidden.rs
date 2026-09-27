use solution::*;

#[test]
fn empty_map() {
    let m: std::collections::BTreeMap<u32, String> = std::collections::BTreeMap::new();
    check!(r#"no events; from 0 to 10"#, between(&m, 0, 10), Vec::<&str>::new());
}

#[test]
fn everything() {
    let m = std::collections::BTreeMap::from([(u32::MAX, "c".to_string()), (0, "a".to_string()), (7, "b".to_string())]);
    check!(r#"events at 0, 7, u32::MAX; from 0 to u32::MAX"#, between(&m, 0, u32::MAX), vec!["a", "b", "c"]);
}

#[test]
fn max_point() {
    let m = std::collections::BTreeMap::from([(u32::MAX, "z".to_string())]);
    check!(r#"event at u32::MAX; from u32::MAX to u32::MAX"#, between(&m, u32::MAX, u32::MAX), vec!["z"]);
}

#[test]
fn zero_point() {
    let m = std::collections::BTreeMap::from([(0, "z".to_string())]);
    check!(r#"event at 0; from 0 to 0"#, between(&m, 0, 0), vec!["z"]);
}

#[test]
fn after_everything() {
    let m = std::collections::BTreeMap::from([(1, "a".to_string()), (2, "b".to_string())]);
    check!(r#"events at 1, 2; from 3 to 9"#, between(&m, 3, 9), Vec::<&str>::new());
}

#[test]
fn before_everything() {
    let m = std::collections::BTreeMap::from([(5, "a".to_string()), (6, "b".to_string())]);
    check!(r#"events at 5, 6; from 0 to 4"#, between(&m, 0, 4), Vec::<&str>::new());
}

#[test]
fn unicode_names() {
    let m = std::collections::BTreeMap::from([(1, "é".to_string()), (2, "日本".to_string())]);
    check!(r#"events at 1 → "é", 2 → "日本""#, between(&m, 1, 2), vec!["é", "日本"]);
}

#[test]
fn borrows_the_map() {
    let m = std::collections::BTreeMap::from([(1, "a".to_string())]);
    check!(r#"the result points into the map"#, std::ptr::eq(between(&m, 1, 1)[0], m[&1].as_str()), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4005);
    for _ in 0..300 {
        let n = rng.below(8);
        let m: std::collections::BTreeMap<u32, String> = (0..n).map(|i| (rng.below(20) as u32, format!("e{i}"))).collect();
        let (from, to) = (rng.below(22) as u32, rng.below(22) as u32);
        let want: Vec<&str> = m.iter().filter(|(k, _)| from <= **k && **k <= to).map(|(_, v)| v.as_str()).collect();
        check!(format!("events = {m:?}, from {from} to {to}"), between(&m, from, to), want);
    }
}

#[test]
fn scale_100k_queries() {
    let m: std::collections::BTreeMap<u32, String> = (0..200_000u32).map(|i| (i * 2, i.to_string())).collect();
    let mut total = 0;
    for q in 0..100_000u32 {
        total += between(&m, q * 4, q * 4 + 3).len();
    }
    check!("200000 events at even times; 100000 queries of width 4", total, 200_000);
}
