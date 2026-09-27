use solution::*;

#[test]
fn read_then_change_then_consume() {
    let mut words = vec!["hi".to_string(), "there".to_string()];
    let long = count_long(&words, 3);
    shout_all(&mut words);
    let sentence = into_sentence(words);
    check!("[\"hi\", \"there\"]", (long, sentence), (1, "HI THERE".to_string()));
}

#[test]
fn count_only() {
    check!(r#"["a", "bbb"], min = 2"#, { let w = vec!["a".to_string(), "bbb".to_string()]; count_long(&w, 2) }, 1);
}

#[test]
fn shout_in_place() {
    check!(r#"["ab", "c"]"#, { let mut w = vec!["ab".to_string(), "c".to_string()]; shout_all(&mut w); w }, vec!["AB", "C"]);
}

#[test]
fn sentence() {
    check!(r#"["a", "b", "c"]"#, into_sentence(vec!["a".to_string(), "b".to_string(), "c".to_string()]), "a b c".to_string());
}

#[test]
fn count_at_least() {
    check!(r#"["ab", "abc", "a"], min = 2 (at least, so "ab" counts)"#, { let w = vec!["ab".to_string(), "abc".to_string(), "a".to_string()]; count_long(&w, 2) }, 2);
}
