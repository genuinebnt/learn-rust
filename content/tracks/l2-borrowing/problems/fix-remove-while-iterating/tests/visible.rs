use solution::*;

#[test]
fn removes() {
    check!(r#"["tmp_a", "keep", "tmp_b"], prefix "tmp""#, { let mut v: Vec<String> = ["tmp_a", "keep", "tmp_b"].map(String::from).to_vec(); remove_prefixed(&mut v, "tmp"); v }, vec!["keep".to_string()]);
}

#[test]
fn nothing_matches() {
    check!(r#"["a"], prefix "z""#, { let mut v = vec!["a".to_string()]; remove_prefixed(&mut v, "z"); v.len() }, 1);
}
