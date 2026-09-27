use solution::*;

#[test]
fn clears() {
    check!(r#"["a", "abc"]"#, { let mut v = vec!["a".to_string(), "abc".to_string()]; let n = longest_then_clear(&mut v); (n, v.len()) }, (3, 0));
}

#[test]
fn single() {
    check!(r#"["hello"]"#, { let mut v = vec!["hello".to_string()]; longest_then_clear(&mut v) }, 5);
}

#[test]
fn tie() {
    check!(r#"["ab", "cd", "e"]"#, { let mut v = vec!["ab".to_string(), "cd".to_string(), "e".to_string()]; let n = longest_then_clear(&mut v); (n, v.len()) }, (2, 0));
}

#[test]
fn longest_first() {
    check!(r#"["ccc", "a"]"#, { let mut v = vec!["ccc".to_string(), "a".to_string()]; longest_then_clear(&mut v) }, 3);
}

#[test]
fn empty() {
    check!(r#"[]"#, { let mut v: Vec<String> = vec![]; longest_then_clear(&mut v) }, 0);
}
