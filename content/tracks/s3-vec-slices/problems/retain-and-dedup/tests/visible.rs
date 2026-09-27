use solution::*;

#[test]
fn mixed() {
    check!(r#"v = [1, 1, -2, 1, 3, 3, -3, 3]"#, { let mut v = vec![1, 1, -2, 1, 3, 3, -3, 3]; clean(&mut v); v }, vec![1, 3]);
}

#[test]
fn no_change() {
    check!(r#"v = [1, 2]"#, { let mut v = vec![1, 2]; clean(&mut v); v }, vec![1, 2]);
}
