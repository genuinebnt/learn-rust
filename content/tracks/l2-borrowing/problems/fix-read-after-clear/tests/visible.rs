use solution::*;

#[test]
fn clears() {
    check!(r#"["a", "abc"]"#, { let mut v = vec!["a".to_string(), "abc".to_string()]; let n = longest_then_clear(&mut v); (n, v.len()) }, (3, 0));
}

#[test]
fn single() {
    check!(r#"["hello"]"#, { let mut v = vec!["hello".to_string()]; longest_then_clear(&mut v) }, 5);
}
