use solution::*;

#[test]
fn removes() {
    check!(r#"["tmp_a", "keep", "tmp_b"], prefix "tmp""#, { let mut v: Vec<String> = ["tmp_a", "keep", "tmp_b"].map(String::from).to_vec(); remove_prefixed(&mut v, "tmp"); v }, vec!["keep".to_string()]);
}

#[test]
fn nothing_matches() {
    check!(r#"["a"], prefix "z""#, { let mut v = vec!["a".to_string()]; remove_prefixed(&mut v, "z"); v.len() }, 1);
}

#[test]
fn empty_prefix() {
    check!(r#"["a", "b"], prefix """#, { let mut v = vec!["a".to_string(), "b".to_string()]; remove_prefixed(&mut v, ""); v }, Vec::<String>::new());
}

#[test]
fn contains_not_prefix() {
    check!(r#"["a_tmp"], prefix "tmp""#, { let mut v = vec!["a_tmp".to_string()]; remove_prefixed(&mut v, "tmp"); v }, vec!["a_tmp".to_string()]);
}

#[test]
fn adjacent() {
    check!(r#"["x1", "x2", "y"], prefix "x""#, { let mut v: Vec<String> = ["x1", "x2", "y"].map(String::from).to_vec(); remove_prefixed(&mut v, "x"); v }, vec!["y".to_string()]);
}
