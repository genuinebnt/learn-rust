use solution::*;

#[test]
fn empty() {
    let mut w: Vec<String> = vec![];
    check!(r#"[]"#, { shout_all(&mut w); drop_short(&mut w, 1); let best = longest(&w).map(str::len); (best, into_sentence(w)) }, (None, String::new()));
}

#[test]
fn count_min_zero() {
    let w = vec![String::new(), "a".to_string()];
    check!(r#"["", "a"], min = 0"#, count_long(&w, 0), 2);
}

#[test]
fn count_bytes_not_chars() {
    let w = vec!["é".to_string(), "ab".to_string(), "日".to_string()];
    check!(r#"["é", "ab", "日"], min = 3 (é is 2 bytes, 日 is 3)"#, count_long(&w, 3), 1);
}

#[test]
fn longest_bytes() {
    let w = vec!["日".to_string(), "abcd".to_string(), "ab".to_string()];
    check!(r#"["日", "abcd", "ab"] (日 is 3 bytes)"#, longest(&w), Some("abcd"));
}

#[test]
fn longest_points_into_words() {
    let w = vec!["a".to_string(), "bbb".to_string()];
    check!(r#"longest(&w) is a slice of w's own String"#, longest(&w).map(|s| s.as_ptr()) == Some(w[1].as_ptr()), true);
}

#[test]
fn shout_mixed() {
    let mut w = vec!["aB1".to_string(), "x-y".to_string()];
    check!(r#"["aB1", "x-y"]"#, { shout_all(&mut w); w }, vec!["AB1", "X-Y"]);
}

#[test]
fn drop_all() {
    let mut w = vec!["a".to_string(), "b".to_string()];
    check!(r#"["a", "b"], min = 5"#, { drop_short(&mut w, 5); w }, Vec::<String>::new());
}

#[test]
fn drop_keeps_buffer() {
    let mut w = vec!["a".to_string(), "bb".to_string(), "c".to_string()];
    let ptr = w.as_ptr();
    check!(r#"drop_short changes the caller's Vec in place"#, { drop_short(&mut w, 2); (w.as_ptr() == ptr, w.len()) }, (true, 1));
}

#[test]
fn sentence_empty_words() {
    check!(r#"["", ""]"#, into_sentence(vec![String::new(), String::new()]), " ".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(6105);
    for _ in 0..300 {
        let n = rng.below(6);
        let mut words = Vec::new();
        for _ in 0..n {
            let len = rng.below(5);
            words.push(rng.string(len, "abé日"));
        }
        let min = rng.below(7);
        let input = format!("words = {words:?}, min = {min}");
        let want_count = words.iter().filter(|w| w.len() >= min).count();
        let mut want_best: Option<String> = None;
        for w in &words {
            if want_best.as_ref().map_or(true, |b| w.len() >= b.len()) {
                want_best = Some(w.clone());
            }
        }
        let want_sentence = words.iter().filter(|w| w.len() >= min).map(|w| w.to_ascii_uppercase()).collect::<Vec<_>>().join(" ");
        let count = count_long(&words, min);
        let best = longest(&words).map(str::to_string);
        shout_all(&mut words);
        drop_short(&mut words, min);
        check!(input, (count, best, into_sentence(words)), (want_count, want_best, want_sentence));
    }
}
