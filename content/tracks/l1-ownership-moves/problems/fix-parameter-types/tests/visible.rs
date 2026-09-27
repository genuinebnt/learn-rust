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
