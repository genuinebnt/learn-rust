use solution::*;

#[test]
fn found() {
    check!(r#"["a", "long"], n = 2"#, { let mut v = vec!["a".to_string(), "long".to_string()]; first_long_or_push(&mut v, 2).clone() }, "long".to_string());
}

#[test]
fn fallback() {
    check!(r#"["a"], n = 5"#, { let mut v = vec!["a".to_string()]; let r = first_long_or_push(&mut v, 5).clone(); (r, v.len()) }, ("fallback".to_string(), 2));
}

#[test]
fn exactly_n_is_not_longer() {
    check!(r#"["abc"], n = 3"#, { let mut v = vec!["abc".to_string()]; let r = first_long_or_push(&mut v, 3).clone(); (r, v.len()) }, ("fallback".to_string(), 2));
}

#[test]
fn first_of_several() {
    check!(r#"["aaa", "bbbb", "ccccc"], n = 2"#, { let mut v = vec!["aaa".to_string(), "bbbb".to_string(), "ccccc".to_string()]; first_long_or_push(&mut v, 2).clone() }, "aaa".to_string());
}

#[test]
fn empty() {
    check!(r#"[], n = 0"#, { let mut v = vec![]; first_long_or_push(&mut v, 0).clone() }, "fallback".to_string());
}
