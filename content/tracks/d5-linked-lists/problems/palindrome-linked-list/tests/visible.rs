use solution::*;

#[test]
fn even() {
    check!(r#"[1,2,2,1]"#, is_palindrome(list(&[1, 2, 2, 1])), true);
}

#[test]
fn no() {
    check!(r#"[1,2]"#, is_palindrome(list(&[1, 2])), false);
}
