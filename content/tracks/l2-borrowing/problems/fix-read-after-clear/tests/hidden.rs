use solution::*;

#[test]
fn empty_strings() {
    check!(r#"["", ""]"#, { let mut v = vec![String::new(), String::new()]; longest_then_clear(&mut v) }, 0);
}

#[test]
fn unicode_bytes() {
    check!(r#"["日本"]"#, { let mut v = vec!["日本".to_string()]; longest_then_clear(&mut v) }, 6);
}

#[test]
fn longest_last() {
    check!(r#"["a", "bb", "ccc"]"#, { let mut v = vec!["a".to_string(), "bb".to_string(), "ccc".to_string()]; longest_then_clear(&mut v) }, 3);
}

#[test]
fn reuse_after_clear() {
    check!(r#"clear, push "z", clear again"#, { let mut v = vec!["abc".to_string()]; longest_then_clear(&mut v); v.push("z".to_string()); (longest_then_clear(&mut v), v.is_empty()) }, (1, true));
}

#[test]
fn many() {
    check!(r#"1000 words of lengths i % 50"#, { let mut v: Vec<String> = (0..1000).map(|i| "x".repeat(i % 50)).collect(); (longest_then_clear(&mut v), v.len()) }, (49, 0));
}

#[test]
fn one_long_many_short() {
    check!(r#"["a" × 5, "abcdefgh"]"#, { let mut v = vec!["a".to_string(); 5]; v.push("abcdefgh".to_string()); longest_then_clear(&mut v) }, 8);
}

#[test]
fn single_empty() {
    check!(r#"[""]"#, { let mut v = vec![String::new()]; (longest_then_clear(&mut v), v.len()) }, (0, 0));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2009);
    for _ in 0..300 {
        let n = rng.below(8);
        let words: Vec<String> = (0..n).map(|_| { let l = rng.below(6); rng.string(l, "aé") }).collect();
        let want = words.iter().map(|w| w.len()).max().unwrap_or(0);
        let mut v = words.clone();
        let got = longest_then_clear(&mut v);
        check!(format!("words = {words:?}"), (got, v.len()), (want, 0));
    }
}
