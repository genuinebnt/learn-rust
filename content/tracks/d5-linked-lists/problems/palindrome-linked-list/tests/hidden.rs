use solution::*;

#[test]
fn odd() {
    check!(r#"[1,2,3,2,1]"#, is_palindrome(list(&[1, 2, 3, 2, 1])), true);
}

#[test]
fn empty() {
    check!(r#"[]"#, is_palindrome(None), true);
}

#[test]
fn near_miss() {
    check!(r#"[1,2,3,1]"#, is_palindrome(list(&[1, 2, 3, 1])), false);
}

#[test]
fn long() {
    let v: Vec<i32> = (0..5_000).chain((0..5_000).rev()).collect();
    check!(r#"10⁴ symmetric values"#, is_palindrome(list(&v)), true);
}
