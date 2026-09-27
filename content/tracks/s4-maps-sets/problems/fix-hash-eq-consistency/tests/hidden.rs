use solution::*;

#[test]
fn single() {
    check!(r#"["x"]"#, distinct(&["x"]), 1);
}

#[test]
fn non_ascii_is_case_sensitive() {
    check!(r#"["É", "é"]"#, distinct(&["É", "é"]), 2);
}

#[test]
fn digits() {
    check!(r#"["User1", "USER1", "user2"]"#, distinct(&["User1", "USER1", "user2"]), 2);
}

#[test]
fn empty_names() {
    check!(r#"["", ""]"#, distinct(&["", ""]), 1);
}

#[test]
fn four_spellings() {
    check!(r#"["ab", "AB", "aB", "Ab"]"#, distinct(&["ab", "AB", "aB", "Ab"]), 1);
}

#[test]
fn set_lookup() {
    check!(r#"insert "alice", look up "ALICE""#, { let set: std::collections::HashSet<Username> = [Username("alice".to_string())].into_iter().collect(); set.contains(&Username("ALICE".to_string())) }, true);
}

#[test]
fn equal_names_hash_equal() {
    check!(r#"hash "Bob" and "bOB""#, { use std::hash::{BuildHasher, RandomState}; let s = RandomState::new(); s.hash_one(Username("Bob".to_string())) == s.hash_one(Username("bOB".to_string())) }, true);
}

#[test]
fn many() {
    check!(r#"1000 names in three spellings each"#, { let ws: Vec<String> = (0..1000).flat_map(|i| [format!("user{i}"), format!("USER{i}"), format!("User{i}")]).collect(); let refs: Vec<&str> = ws.iter().map(|w| w.as_str()).collect(); distinct(&refs) }, 1000);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(4006);
    for _ in 0..300 {
        let n = rng.below(8);
        let names: Vec<String> = (0..n).map(|_| { let l = rng.below(3); rng.string(l, "aAbBé") }).collect();
        let refs: Vec<&str> = names.iter().map(|w| w.as_str()).collect();
        let want = names.iter().map(|w| w.to_ascii_lowercase()).collect::<std::collections::HashSet<_>>().len();
        check!(format!("names = {refs:?}"), distinct(&refs), want);
    }
}

#[test]
fn scale_200k_same_length_names() {
    let names: Vec<String> = (0..200_000).map(|i| format!("user{i:06}")).collect();
    let refs: Vec<&str> = names.iter().map(|w| w.as_str()).collect();
    check!("200000 distinct names, all 10 bytes long", distinct(&refs), 200_000);
}
