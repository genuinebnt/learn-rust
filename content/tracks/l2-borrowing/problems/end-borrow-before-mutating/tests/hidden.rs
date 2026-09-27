use solution::*;

#[test]
fn longest_in_middle() {
    check!(r#"["a", "abcd", "ab"]"#, { let mut v = vec!["a".to_string(), "abcd".to_string(), "ab".to_string()]; append_longest(&mut v); v.last().cloned() }, Some("abcd!".to_string()));
}

#[test]
fn tie_takes_last() {
    check!(r#"["aa", "bb", "c"]"#, { let mut v = vec!["aa".to_string(), "bb".to_string(), "c".to_string()]; append_longest(&mut v); v.last().cloned() }, Some("bb!".to_string()));
}

#[test]
fn empty_word() {
    check!(r#"[""]"#, { let mut v = vec![String::new()]; append_longest(&mut v); v }, vec![String::new(), "!".to_string()]);
}

#[test]
fn unicode() {
    check!(r#"["日本語", "ab"]"#, { let mut v = vec!["日本語".to_string(), "ab".to_string()]; append_longest(&mut v); v.last().cloned() }, Some("日本語!".to_string()));
}

#[test]
fn grows_by_one() {
    check!(r#"10 words"#, { let mut v: Vec<String> = (0..10).map(|i| i.to_string()).collect(); append_longest(&mut v); v.len() }, 11);
}

#[test]
fn original_untouched() {
    check!(r#"["b", "aaa", "c"]"#, { let mut v = vec!["b".to_string(), "aaa".to_string(), "c".to_string()]; append_longest(&mut v); v }, vec!["b".to_string(), "aaa".to_string(), "c".to_string(), "aaa!".to_string()]);
}

#[test]
fn called_twice() {
    check!(r#"["ab"], twice"#, { let mut v = vec!["ab".to_string()]; append_longest(&mut v); append_longest(&mut v); v }, vec!["ab".to_string(), "ab!".to_string(), "ab!!".to_string()]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2008);
    for _ in 0..300 {
        let n = rng.below(6);
        let words: Vec<String> = (0..n).map(|_| { let l = rng.below(5); rng.string(l, "ab") }).collect();
        let mut want = words.clone();
        if let Some(m) = words.iter().map(|w| w.len()).max() {
            let i = words.iter().rposition(|w| w.len() == m).unwrap();
            want.push(format!("{}!", words[i]));
        }
        let mut got = words.clone();
        append_longest(&mut got);
        check!(format!("words = {words:?}"), got, want);
    }
}
