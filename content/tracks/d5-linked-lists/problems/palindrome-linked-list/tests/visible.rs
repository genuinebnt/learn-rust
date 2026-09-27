use solution::*;

#[test]
fn even() {
    check!(r#"[1,2,2,1]"#, is_palindrome(list(&[1, 2, 2, 1])), true);
}

#[test]
fn no() {
    check!(r#"[1,2]"#, is_palindrome(list(&[1, 2])), false);
}

#[test]
fn empty() {
    check!(r#"[]"#, is_palindrome(None), true);
}

#[test]
fn single() {
    check!(r#"[5]"#, is_palindrome(list(&[5])), true);
}

#[test]
fn odd() {
    check!(r#"[1,2,3,2,1]"#, is_palindrome(list(&[1, 2, 3, 2, 1])), true);
}
