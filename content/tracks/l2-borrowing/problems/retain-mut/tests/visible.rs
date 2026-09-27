use solution::*;

#[test]
fn mixed() {
    check!(r#"[4, 0, 6, 0]"#, { let mut v = vec![4, 0, 6, 0]; drop_zeros_and_halve(&mut v); v }, vec![2, 3]);
}

#[test]
fn all_zero() {
    check!(r#"[0, 0]"#, { let mut v = vec![0, 0]; drop_zeros_and_halve(&mut v); v }, vec![]);
}
