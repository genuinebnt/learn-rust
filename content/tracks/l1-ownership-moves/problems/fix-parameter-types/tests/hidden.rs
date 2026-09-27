use solution::*;

#[test]
fn empty() {
    check!(r#"[]"#, { let mut w: Vec<String> = vec![]; shout_all(&mut w); into_sentence(w) }, String::new());
}

#[test]
fn count_empty() {
    check!(r#"[], min = 1"#, count_long(&[], 1), 0);
}

#[test]
fn count_min_zero() {
    check!(r#"["", "a"], min = 0"#, { let w = vec![String::new(), "a".to_string()]; count_long(&w, 0) }, 2);
}

#[test]
fn count_exact_length() {
    check!(r#"["abc", "ab"], min = 3"#, { let w = vec!["abc".to_string(), "ab".to_string()]; count_long(&w, 3) }, 1);
}

#[test]
fn count_bytes_not_chars() {
    check!(r#"["é", "ab", "日"], min = 3 (é is 2 bytes, 日 is 3)"#, { let w = vec!["é".to_string(), "ab".to_string(), "日".to_string()]; count_long(&w, 3) }, 1);
}

#[test]
fn shout_mixed() {
    check!(r#"["aB1", "x-y"]"#, { let mut w = vec!["aB1".to_string(), "x-y".to_string()]; shout_all(&mut w); w }, vec!["AB1", "X-Y"]);
}

#[test]
fn shout_twice() {
    check!(r#"shout_all twice"#, { let mut w = vec!["go".to_string()]; shout_all(&mut w); shout_all(&mut w); w }, vec!["GO"]);
}

#[test]
fn sentence_single() {
    check!(r#"["one"]"#, into_sentence(vec!["one".to_string()]), "one".to_string());
}

#[test]
fn sentence_empty_words() {
    check!(r#"["", ""]"#, into_sentence(vec![String::new(), String::new()]), " ".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1105);
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
        let want_sentence = words.iter().map(|w| w.to_ascii_uppercase()).collect::<Vec<_>>().join(" ");
        let count = count_long(&words, min);
        shout_all(&mut words);
        check!(input, (count, into_sentence(words)), (want_count, want_sentence));
    }
}
