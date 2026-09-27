use solution::*;

#[test]
fn appends() {
    check!(r#"["hi", "hello"]"#, { let mut v = vec!["hi".to_string(), "hello".to_string()]; append_longest(&mut v); v }, vec!["hi".to_string(), "hello".to_string(), "hello!".to_string()]);
}

#[test]
fn first_longest_wins() {
    check!(r#"["ab", "cd"]"#, { let mut v = vec!["ab".to_string(), "cd".to_string()]; append_longest(&mut v); v.last().cloned() }, Some("cd!".to_string()));
}
