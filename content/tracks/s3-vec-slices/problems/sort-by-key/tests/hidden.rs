use solution::*;

#[test]
fn same_length() {
    check!(r#"["b", "a", "c"]"#, { let mut w: Vec<String> = ["b", "a", "c"].map(String::from).to_vec(); by_len_then_alpha(&mut w); w }, vec!["a", "b", "c"]);
}

#[test]
fn single() {
    check!(r#"["x"]"#, { let mut w = vec!["x".to_string()]; by_len_then_alpha(&mut w); w }, vec!["x"]);
}

#[test]
fn empty_string_first() {
    check!(r#"["a", ""]"#, { let mut w: Vec<String> = ["a", ""].map(String::from).to_vec(); by_len_then_alpha(&mut w); w }, vec!["", "a"]);
}

#[test]
fn uppercase_before_lowercase() {
    check!(r#"["b", "B", "a"]"#, { let mut w: Vec<String> = ["b", "B", "a"].map(String::from).to_vec(); by_len_then_alpha(&mut w); w }, vec!["B", "a", "b"]);
}

#[test]
fn already_sorted() {
    check!(r#"["a", "bb", "ccc"]"#, { let mut w: Vec<String> = ["a", "bb", "ccc"].map(String::from).to_vec(); by_len_then_alpha(&mut w); w }, vec!["a", "bb", "ccc"]);
}

#[test]
fn reverse_sorted() {
    check!(r#"["ccc", "bb", "a"]"#, { let mut w: Vec<String> = ["ccc", "bb", "a"].map(String::from).to_vec(); by_len_then_alpha(&mut w); w }, vec!["a", "bb", "ccc"]);
}

#[test]
fn prefix_ties() {
    check!(r#"["abd", "abc", "ab"]"#, { let mut w: Vec<String> = ["abd", "abc", "ab"].map(String::from).to_vec(); by_len_then_alpha(&mut w); w }, vec!["ab", "abc", "abd"]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2303);
    for _ in 0..300 {
        let n = rng.below(8);
        let mut words = Vec::new();
        for _ in 0..n {
            let len = rng.below(4);
            words.push(rng.string(len, "abc"));
        }
        let mut want = words.clone();
        want.sort_by_key(|w| (w.len(), w.clone()));
        let mut got = words.clone();
        by_len_then_alpha(&mut got);
        check!(format!("words = {words:?}"), got, want);
    }
}

#[test]
fn scale_200k() {
    let mut w: Vec<String> = (0..200_000u32).rev().map(|i| format!("{:x}", i.wrapping_mul(2_654_435_761))).collect();
    by_len_then_alpha(&mut w);
    let ok = w.windows(2).all(|p| (p[0].len(), &p[0]) <= (p[1].len(), &p[1]));
    check!("200000 hex strings", (w.len(), ok), (200_000, true));
}
