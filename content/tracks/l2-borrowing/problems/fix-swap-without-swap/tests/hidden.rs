use solution::*;

#[test]
fn middle() {
    check!(r#"["a", "b", "c", "d"], 1 ↔ 2"#, { let mut v = ["a", "b", "c", "d"].map(String::from); swap_items(&mut v, 1, 2); v }, ["a", "c", "b", "d"].map(String::from));
}

#[test]
fn empty_strings() {
    check!(r#"["", "x"], 0 ↔ 1"#, { let mut v = ["", "x"].map(String::from); swap_items(&mut v, 0, 1); v }, ["x", ""].map(String::from));
}

#[test]
fn same_values() {
    check!(r#"["a", "a"], 0 ↔ 1"#, { let mut v = ["a", "a"].map(String::from); swap_items(&mut v, 0, 1); v }, ["a", "a"].map(String::from));
}

#[test]
fn last_first() {
    check!(r#"5 names, 4 ↔ 0"#, { let mut v = ["a", "b", "c", "d", "e"].map(String::from); swap_items(&mut v, 4, 0); v }, ["e", "b", "c", "d", "a"].map(String::from));
}

#[test]
fn swap_back() {
    check!(r#"0 ↔ 2 twice"#, { let mut v = ["a", "b", "c"].map(String::from); swap_items(&mut v, 0, 2); swap_items(&mut v, 2, 0); v }, ["a", "b", "c"].map(String::from));
}

#[test]
fn single_same() {
    check!(r#"["z"], 0 ↔ 0"#, { let mut v = ["z"].map(String::from); swap_items(&mut v, 0, 0); v }, ["z"].map(String::from));
}

#[test]
fn in_a_vec() {
    check!(r#"1000 names, 0 ↔ 999"#, { let mut v: Vec<String> = (0..1000).map(|i| i.to_string()).collect(); swap_items(&mut v, 0, 999); (v[0].clone(), v[999].clone(), v[500].clone()) }, ("999".to_string(), "0".to_string(), "500".to_string()));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(2025);
    for _ in 0..300 {
        let n = 1 + rng.below(6);
        let v0: Vec<String> = (0..n).map(|_| { let l = rng.below(3); rng.string(l, "ab") }).collect();
        let i = rng.below(n);
        let j = rng.below(n);
        let mut want = v0.clone();
        want.swap(i, j);
        let mut got = v0.clone();
        swap_items(&mut got, i, j);
        check!(format!("v = {v0:?}, {i} ↔ {j}"), got, want);
    }
}
