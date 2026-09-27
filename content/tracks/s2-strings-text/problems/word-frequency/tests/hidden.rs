use solution::*;

#[test]
fn invalid_utf8() {
    check!(r#"b"ok \xff""#, word_frequencies(&b"ok \xff"[..]).is_err(), true);
}

#[test]
fn punctuation_only() {
    check!(r#""-- !! ...""#, word_frequencies("-- !! ...".as_bytes()).unwrap().len(), 0);
}

#[test]
fn inner_punctuation_kept() {
    check!(r#""don't Don't""#, word_frequencies("don't Don't".as_bytes()).unwrap(), vec![("don't".to_string(), 2)]);
}
