use solution::*;

#[test]
fn appends() {
    check!(r#"["hi", "hello"]"#, { let mut v = vec!["hi".to_string(), "hello".to_string()]; append_longest(&mut v); v }, vec!["hi".to_string(), "hello".to_string(), "hello!".to_string()]);
}

#[test]
fn first_longest_wins() {
    check!(r#"["ab", "cd"]"#, { let mut v = vec!["ab".to_string(), "cd".to_string()]; append_longest(&mut v); v.last().cloned() }, Some("cd!".to_string()));
}

#[test]
fn single() {
    check!(r#"["x"]"#, { let mut v = vec!["x".to_string()]; append_longest(&mut v); v }, vec!["x".to_string(), "x!".to_string()]);
}

#[test]
fn longest_first() {
    check!(r#"["abc", "a", "b"]"#, { let mut v = vec!["abc".to_string(), "a".to_string(), "b".to_string()]; append_longest(&mut v); v }, vec!["abc".to_string(), "a".to_string(), "b".to_string(), "abc!".to_string()]);
}

#[test]
fn empty() {
    check!(r#"[]"#, { let mut v: Vec<String> = vec![]; append_longest(&mut v); v.len() }, 0);
}
